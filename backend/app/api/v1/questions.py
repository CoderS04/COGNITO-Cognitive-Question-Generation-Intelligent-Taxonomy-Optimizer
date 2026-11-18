from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.question import Question
from app.schemas.question_schema import (
    QuestionCreate, QuestionResponse, QuestionAnalyzeRequest, QuestionAnalyzeResponse,
    QuestionReframeRequest, QuestionReframeResponse, SimilarityCheckRequest, SimilarityCheckResponse
)
from pydantic import BaseModel
from typing import Any
from app.services.module2_knowledge_base import knowledge_base_service
from app.services.module3_blooms_classifier import blooms_classifier
from app.services.module4_similarity_engine import similarity_engine
from app.services.module6_rag_engine import rag_engine

router = APIRouter(prefix="/questions", tags=["Modules 3-5: Question Bank & Taxonomy Analysis"])

class QuestionUpdateRequest(BaseModel):
    text: Optional[str] = None
    marks: Optional[int] = None
    bloom_level: Optional[str] = None
    difficulty: Optional[str] = None
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None
    solution_outline: Optional[str] = None
    is_historical: Optional[bool] = None

class QuestionBulkDeleteRequest(BaseModel):
    question_ids: List[int]

@router.get("", response_model=List[QuestionResponse])
def get_questions(
    course_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    bloom_level: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_historical: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Searches and filters indexed questions across cognitive and academic tiers."""
    q = db.query(Question)
    if course_id:
        q = q.filter(Question.course_id == course_id)
    if unit_id:
        q = q.filter(Question.unit_id == unit_id)
    if bloom_level:
        q = q.filter(Question.bloom_level == bloom_level)
    if difficulty:
        q = q.filter(Question.difficulty == difficulty)
    if is_historical is not None:
        q = q.filter(Question.is_historical == is_historical)
    if search:
        q = q.filter(Question.text.ilike(f"%{search}%"))
    return q.limit(limit).all()

@router.post("", response_model=QuestionResponse)
def add_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    """
    Adds a new question to the institutional repository.
    Automatically classifies Bloom's level and difficulty if not explicitly set.
    """
    b_info = blooms_classifier.classify_question(payload.text, marks=payload.marks)
    q = Question(
        course_id=payload.course_id,
        unit_id=payload.unit_id,
        topic_id=payload.topic_id,
        text=payload.text,
        question_type=payload.question_type,
        marks=payload.marks,
        bloom_level=payload.bloom_level or b_info["bloom_level"],
        primary_verb=b_info["primary_verb"],
        difficulty=payload.difficulty or b_info["difficulty"],
        difficulty_score=b_info["difficulty_score"],
        is_historical=payload.is_historical,
        exam_year=payload.exam_year,
        solution_outline=payload.solution_outline
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    q.embedding_id = f"q_{q.id}"
    knowledge_base_service.sync_question_to_vector_store(q)
    db.commit()
    return q

@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, payload: QuestionUpdateRequest, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)
    if question.id:
        question.embedding_id = f"q_{question.id}"
        knowledge_base_service.sync_question_to_vector_store(question)
        db.commit()
    return question

@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    if question.paper_mappings:
        raise HTTPException(status_code=400, detail="Question is used by a paper. Replace it in papers before deleting.")
    db.delete(question)
    db.commit()
    return {"status": "success", "question_id": question_id}

@router.post("/bulk-delete")
def bulk_delete_questions(payload: QuestionBulkDeleteRequest, db: Session = Depends(get_db)):
    deleted = 0
    blocked = 0
    for question_id in payload.question_ids:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            continue
        if question.paper_mappings:
            blocked += 1
            continue
        db.delete(question)
        deleted += 1
    db.commit()
    return {"deleted": deleted, "blocked": blocked}

@router.post("/analyze", response_model=QuestionAnalyzeResponse)
def analyze_question(payload: QuestionAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Runs the hybrid Bloom's Taxonomy classifier and multi-factor difficulty estimator
    on an arbitrary question prompt.
    """
    syllabus_context = None
    course_title = None
    if payload.course_id:
        rag_context = rag_engine.retrieve_context(course_id=payload.course_id, db=db)
        structured = rag_context["structured_context"]
        course_title = structured.get("course_title") or None
        syllabus_context = "\n".join(
            [
                f"Unit: {structured.get('unit_title', '')}",
                f"Topics: {', '.join(structured.get('topics', []))}",
                f"Learning outcomes: {'; '.join(structured.get('learning_outcomes', []))}",
                f"Retrieved excerpts: {' | '.join(hit.get('text', '') for hit in rag_context.get('syllabus_hits', []))}",
            ]
        )

    b_res = blooms_classifier.classify_question(
        payload.text,
        marks=payload.marks or 5,
        syllabus_context=syllabus_context,
        course_title=course_title,
    )
    return QuestionAnalyzeResponse(
        text=payload.text,
        bloom_level=b_res["bloom_level"],
        primary_verb=b_res["primary_verb"],
        confidence=b_res["confidence"],
        difficulty=b_res["difficulty"],
        difficulty_score=b_res["difficulty_score"],
        linguistic_score=0.0,
        conceptual_depth=0.0,
        cognitive_target=b_res["cognitive_domain"],
        explanation=b_res["explanation"]
    )

@router.post("/reframe", response_model=QuestionReframeResponse)
def reframe_question(payload: QuestionReframeRequest, db: Session = Depends(get_db)):
    """
    Elevates or reframes a question to target a higher Bloom's cognitive level (e.g. L1 -> L4/L5/L6).
    """
    text_to_reframe = payload.text
    current_level = "L2"
    if payload.question_id:
        q = db.query(Question).filter(Question.id == payload.question_id).first()
        if not q:
            raise HTTPException(status_code=404, detail="Question not found.")
        text_to_reframe = q.text
        current_level = q.bloom_level

    if not text_to_reframe:
        raise HTTPException(status_code=400, detail="Provide either question_id or text.")

    res = blooms_classifier.reframe_question(
        text=text_to_reframe,
        current_level=current_level,
        target_level=payload.target_level,
        db=db,
        course_id=q.course_id if payload.question_id else None,
        unit_id=q.unit_id if payload.question_id else None,
        custom_prompt=payload.custom_prompt,
    )
    return QuestionReframeResponse(**res)

@router.post("/similarity-check", response_model=SimilarityCheckResponse)
def check_similarity(payload: SimilarityCheckRequest, db: Session = Depends(get_db)):
    """
    Computes semantic cosine similarity against historical exam records
    to detect repetition (>=0.85) or paraphrased duplicates (>=0.70).
    """
    res = similarity_engine.check_question_repetition(
        query_text=payload.text,
        db=db,
        course_id=payload.course_id,
        exclude_question_id=payload.question_id,
    )
    return SimilarityCheckResponse(**res)
