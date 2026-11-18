from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.document import IngestedDocument
from app.models.course import Course, Unit, Topic
from app.models.question import Question
from app.models.template import ExamTemplate
from app.services.module1_doc_processor import doc_processor
from app.services.module2_knowledge_base import knowledge_base_service
from app.services.module3_blooms_classifier import blooms_classifier
from app.services.module5_difficulty_estimator import difficulty_estimator
from pydantic import BaseModel, Field

router = APIRouter(prefix="/documents", tags=["Module 1: Document Processing"])

class DocumentApproveRequest(BaseModel):
    document_id: int
    extracted_data: List[dict] = Field(default_factory=list)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("syllabus"), # "syllabus", "past_paper", "guideline"
    course_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingests and parses PDF, DOCX, or text documents.
    Extracts structured syllabus units or historical exam questions,
    indexes into database and high-dimensional vector store.
    """
    try:
        content = await file.read()
        res = doc_processor.process_file(
            filename=file.filename,
            file_bytes=content,
            doc_type=doc_type
        )
        extracted_count = len(res.get("extracted_data", []))

        # Log ingested document record
        doc_record = IngestedDocument(
            filename=file.filename,
            doc_type=doc_type,
            course_id=course_id,
            file_size=len(content),
            status="PENDING_REVIEW",
            extracted_items_count=extracted_count,
            summary={
                "raw_length": res.get("raw_length", 0),
                "cleaned_length": res.get("cleaned_length", 0),
                "extracted_data": res.get("extracted_data", []),
                "extracted_text": res.get("extracted_text", ""),
                "ocr_used": True if res.get("cleaned_length", 0) > 0 else False,
            }
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        return {
            "status": "PENDING_REVIEW",
            "document_id": doc_record.id,
            "filename": file.filename,
            "doc_type": doc_type,
            "extracted_items_count": doc_record.extracted_items_count,
            "details": res
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.post("/{document_id}/approve")
def approve_extracted_document(
    document_id: int,
    payload: DocumentApproveRequest,
    db: Session = Depends(get_db),
):
    """Faculty review gate: save and index only explicitly approved extracted items."""
    doc_record = db.query(IngestedDocument).filter(IngestedDocument.id == document_id).first()
    if not doc_record:
        raise HTTPException(status_code=404, detail="Ingested document not found.")
    if payload.document_id != document_id:
        raise HTTPException(status_code=400, detail="Document ID mismatch.")

    extracted = payload.extracted_data
    if not extracted:
        extracted = (doc_record.summary or {}).get("extracted_data", [])

    imported_count = 0
    try:
        if doc_record.doc_type == "syllabus" and doc_record.course_id:
            course = db.query(Course).filter(Course.id == doc_record.course_id).first()
            if not course:
                raise HTTPException(status_code=404, detail="Target course not found.")
            for u_data in extracted:
                unit = Unit(
                    course_id=course.id,
                    unit_number=int(u_data.get("unit_number", 1)),
                    title=u_data.get("title", "Untitled Unit"),
                    description=u_data.get("description", ""),
                )
                db.add(unit)
                db.flush()
                imported_count += 1
                for t_data in u_data.get("topics", []):
                    topic = Topic(
                        unit_id=unit.id,
                        name=t_data.get("name", "").strip(),
                        keywords=t_data.get("keywords", ""),
                        learning_outcome=t_data.get("learning_outcome", ""),
                    )
                    if topic.name:
                        db.add(topic)
                        db.flush()
                        knowledge_base_service.sync_syllabus_chunk_to_vector_store(unit, topic)

        elif doc_record.doc_type in ("past_paper", "historical_paper") and doc_record.course_id:
            for q_data in extracted:
                q_text = q_data.get("text", "").strip()
                if not q_text:
                    continue
                marks = int(q_data.get("marks", 5))
                b_info = blooms_classifier.classify_question(
                    q_text,
                    marks=marks,
                    syllabus_context=q_data.get("topic_context"),
                )
                hist_q = Question(
                    course_id=doc_record.course_id,
                    unit_id=q_data.get("unit_id"),
                    topic_id=q_data.get("topic_id"),
                    text=q_text,
                    question_type="Descriptive",
                    marks=marks,
                    bloom_level=b_info["bloom_level"],
                    primary_verb=b_info["primary_verb"],
                    difficulty=b_info["difficulty"],
                    difficulty_score=b_info["difficulty_score"],
                    is_historical=True,
                    exam_year=q_data.get("exam_year", 2024),
                    solution_outline=q_data.get("solution_outline"),
                )
                db.add(hist_q)
                db.flush()
                knowledge_base_service.sync_question_to_vector_store(hist_q)
                imported_count += 1

        elif doc_record.doc_type in ("exam_template", "template"):
            for template_data in extracted:
                template = ExamTemplate(
                    name=template_data["name"],
                    description=template_data.get("description"),
                    total_marks=int(template_data["total_marks"]),
                    duration_minutes=int(template_data["duration_minutes"]),
                    instructions=template_data.get("instructions"),
                    sections_config=template_data["sections_config"],
                    bloom_targets=template_data["bloom_targets"],
                    difficulty_targets=template_data["difficulty_targets"],
                )
                db.add(template)
                imported_count += 1
        else:
            raise HTTPException(status_code=400, detail="This document type does not support approval.")

        doc_record.status = "APPROVED"
        doc_record.extracted_items_count = imported_count
        doc_record.summary = {
            **(doc_record.summary or {}),
            "approved_data": extracted,
            "indexed_count": imported_count,
        }
        db.commit()
        db.refresh(doc_record)
        return {
            "status": "APPROVED",
            "document_id": doc_record.id,
            "imported_items_count": imported_count,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to approve document: {str(exc)}")

@router.get("")
def list_ingested_documents(db: Session = Depends(get_db)):
    """Lists all previously ingested academic documents."""
    return db.query(IngestedDocument).order_by(IngestedDocument.created_at.desc()).all()
