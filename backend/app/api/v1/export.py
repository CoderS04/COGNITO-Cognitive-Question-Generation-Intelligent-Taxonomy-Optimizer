from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.paper import ExamPaper
from app.services.module9_reporting import reporting_service

router = APIRouter(prefix="/export", tags=["Module 9: Publication & Export"])

@router.get("/paper/{paper_id}/pdf")
def export_paper_pdf(paper_id: int, db: Session = Depends(get_db)):
    """Downloads formatted examination paper as a PDF."""
    try:
        pdf_bytes = reporting_service.generate_pdf(db, paper_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=cognito_exam_paper_{paper_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/paper/{paper_id}/docx")
def export_paper_docx(paper_id: int, db: Session = Depends(get_db)):
    """Downloads formatted examination paper as a Microsoft Word document (.docx)."""
    try:
        docx_bytes = reporting_service.generate_docx(db, paper_id)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=cognito_exam_paper_{paper_id}.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(e)}")

@router.get("/paper/{paper_id}/json")
def export_paper_json(paper_id: int, db: Session = Depends(get_db)):
    """Exports structured question paper with metadata as JSON."""
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    payload = {
        "id": paper.id,
        "title": paper.title,
        "course_id": paper.course_id,
        "course_title": paper.course.title if paper.course else "",
        "semester": paper.semester,
        "academic_year": paper.academic_year,
        "total_marks": paper.total_marks,
        "cas_score": paper.cas_score,
        "status": paper.status,
        "sections": [
            {
                "section_name": s.section_name,
                "instructions": s.instructions,
                "total_marks": s.total_marks,
                "questions": [
                    {
                        "label": pq.sub_question_label,
                        "marks": pq.marks,
                        "text": pq.question.text,
                        "bloom_level": pq.question.bloom_level,
                        "primary_verb": pq.question.primary_verb,
                        "difficulty": pq.question.difficulty
                    }
                    for pq in s.questions
                ]
            }
            for s in paper.sections
        ]
    }
    return JSONResponse(content=payload)
