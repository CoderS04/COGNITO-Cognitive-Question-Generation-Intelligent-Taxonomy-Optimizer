from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.paper import ExamPaper, PaperSection, PaperQuestion
from app.models.question import Question
from app.schemas.paper_schema import ExamPaperResponse, GeneratePaperRequest, ReplaceQuestionRequest, SavePaperQuestionsRequest
from app.services.module7_optimizer import constraint_optimizer
from app.services.module8_validation_engine import validation_engine
from app.services.module3_blooms_classifier import blooms_classifier
from app.services.module2_knowledge_base import knowledge_base_service

router = APIRouter(prefix="/papers", tags=["Module 7: Question Paper Generation & Optimization"])

@router.get("", response_model=List[ExamPaperResponse])
def get_papers(db: Session = Depends(get_db)):
    """Retrieves all generated question papers with their validation status."""
    return db.query(ExamPaper).order_by(ExamPaper.created_at.desc()).all()

@router.post("/generate", response_model=ExamPaperResponse)
def generate_paper(payload: GeneratePaperRequest, db: Session = Depends(get_db)):
    """
    Executes the Constraint Optimization Pipeline:
    Retrieves syllabus context, scores candidates against academic constraints,
    assembles optimal paper, and computes initial CAS validation score.
    """
    try:
        paper = constraint_optimizer.assemble_paper(
            db=db,
            course_id=payload.course_id,
            title=payload.title,
            total_marks=payload.total_marks,
            template_id=payload.template_id,
            bloom_targets=payload.bloom_targets,
            difficulty_targets=payload.difficulty_targets,
            unit_weights=payload.unit_weights,
            novelty_threshold=payload.novelty_threshold or 0.85
        )
        # Run immediate validation audit
        validation_engine.validate_paper(db, paper.id)
        db.refresh(paper)
        return paper
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/{paper_id}", response_model=ExamPaperResponse)
def get_paper_detail(paper_id: int, db: Session = Depends(get_db)):
    """Retrieves complete question paper with sections and questions."""
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Question paper not found.")
    return paper

@router.put("/{paper_id}/replace-question", response_model=ExamPaperResponse)
def replace_question(
    paper_id: int,
    payload: ReplaceQuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Replaces a specific question in the paper with an alternative candidate
    matching the same marks and unit.
    """
    pq = db.query(PaperQuestion).filter(
        PaperQuestion.id == payload.paper_question_id,
        PaperQuestion.section.has(paper_id=paper_id),
    ).first()
    if not pq:
        raise HTTPException(status_code=404, detail="PaperQuestion item not found.")

    if payload.replacement_question_id:
        new_q = db.query(Question).filter(Question.id == payload.replacement_question_id).first()
        if not new_q:
            raise HTTPException(status_code=404, detail="Replacement question not found.")
        pq.question_id = new_q.id
    elif payload.replacement_text:
        curr_q = pq.question
        bloom_level = payload.target_level or curr_q.bloom_level
        analysis = blooms_classifier.classify_question(
            payload.replacement_text,
            marks=payload.marks or pq.marks,
            course_title=None,
        )
        new_q = Question(
            course_id=curr_q.course_id,
            unit_id=curr_q.unit_id,
            topic_id=curr_q.topic_id,
            text=payload.replacement_text,
            question_type=curr_q.question_type,
            marks=payload.marks or pq.marks,
            bloom_level=bloom_level,
            primary_verb=payload.primary_verb or analysis["primary_verb"],
            difficulty=analysis["difficulty"],
            difficulty_score=analysis["difficulty_score"],
            is_historical=False,
            solution_outline=payload.solution_outline or curr_q.solution_outline,
        )
        db.add(new_q)
        db.flush()
        knowledge_base_service.sync_question_to_vector_store(new_q)
        pq.question_id = new_q.id
        pq.marks = new_q.marks
    else:
        # Pick another candidate from question bank with identical marks and unit
        curr_q = pq.question
        alt_q = db.query(Question).filter(
            Question.course_id == curr_q.course_id,
            Question.marks == pq.marks,
            Question.id != curr_q.id
        ).first()
        if not alt_q:
            raise HTTPException(status_code=400, detail="No alternative question matching marks available.")
        pq.question_id = alt_q.id

    db.commit()
    # Re-validate
    validation_engine.validate_paper(db, paper_id)
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    return paper

@router.get("/{paper_id}/questions/{paper_question_id}/alternatives")
def get_question_alternatives(
    paper_id: int,
    paper_question_id: int,
    custom_prompt: Optional[str] = None,
    target_level: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Returns bank alternatives and LLM-reframed candidates for a paper question."""
    pq = db.query(PaperQuestion).filter(
        PaperQuestion.id == paper_question_id,
        PaperQuestion.section.has(paper_id=paper_id),
    ).first()
    if not pq:
        raise HTTPException(status_code=404, detail="Paper question not found.")

    current = pq.question
    alternatives = []

    levels = [target_level] if target_level else ["L3", "L4", "L5", "L6"]
    current_index = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}.get(current.bloom_level, 2)
    for level in levels:
        level_index = {"L3": 3, "L4": 4, "L5": 5, "L6": 6}[level]
        if level_index <= current_index:
            continue
        reframed = blooms_classifier.reframe_question(
            text=current.text,
            current_level=current.bloom_level,
            target_level=level,
            db=db,
            course_id=current.course_id,
            unit_id=current.unit_id,
            custom_prompt=custom_prompt,
        )
        alternatives.append({
            "source": "LLM_REFRAME",
            "target_level": level,
            "text": reframed["reframed_text"],
            "primary_verb": reframed["primary_verb"],
            "marks": reframed["suggested_marks"] or pq.marks,
            "solution_outline": reframed.get("rubric_outline"),
            "explanation": reframed["explanation"],
        })

    bank_matches = db.query(Question).filter(
        Question.course_id == current.course_id,
        Question.id != current.id,
    ).limit(8).all()
    for match in bank_matches:
        alternatives.append({
            "source": "QUESTION_BANK",
            "question_id": match.id,
            "target_level": match.bloom_level,
            "text": match.text,
            "primary_verb": match.primary_verb,
            "marks": match.marks,
            "solution_outline": match.solution_outline,
            "explanation": f"Existing {match.bloom_level} question from the course question bank.",
        })

    return {
        "paper_id": paper_id,
        "paper_question_id": paper_question_id,
        "current_question": {
            "question_id": current.id,
            "text": current.text,
            "bloom_level": current.bloom_level,
            "marks": pq.marks,
        },
        "alternatives": alternatives,
    }

@router.post("/{paper_id}/save-questions")
def save_paper_questions(
    paper_id: int,
    payload: SavePaperQuestionsRequest,
    db: Session = Depends(get_db),
):
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Question paper not found.")

    if payload.question_ids:
        mappings = db.query(PaperQuestion).filter(
            PaperQuestion.id.in_(payload.question_ids),
            PaperQuestion.section.has(paper_id=paper_id),
        ).all()
    else:
        mappings = [
            mapping
            for section in paper.sections
            for mapping in section.questions
        ]

    saved = 0
    already_exists = 0
    for mapping in mappings:
        source = mapping.question
        duplicate = db.query(Question).filter(
            Question.course_id == paper.course_id,
            Question.text == source.text,
            Question.id != source.id,
        ).first()
        if duplicate:
            mapping.question_id = duplicate.id
            already_exists += 1
            continue
        source.is_historical = False
        knowledge_base_service.sync_question_to_vector_store(source)
        saved += 1

    db.commit()
    validation_engine.validate_paper(db, paper_id)
    return {"saved": saved, "already_exists": already_exists}

@router.delete("/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    """Deletes an examination paper."""
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    db.delete(paper)
    db.commit()
    return {"status": "success", "message": f"Paper {paper_id} deleted."}
