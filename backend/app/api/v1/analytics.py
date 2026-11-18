from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.models.course import Course
from app.models.question import Question
from app.models.paper import ExamPaper
from app.schemas.analytics_schema import PaperAnalyticsSummary, SystemStats
from app.services.module9_reporting import reporting_service

router = APIRouter(prefix="/analytics", tags=["Module 9: Analytics & Reporting"])

@router.get("/paper/{paper_id}", response_model=PaperAnalyticsSummary)
def get_paper_analytics(paper_id: int, db: Session = Depends(get_db)):
    """
    Retrieves complete analytics breakdown for an exam paper:
    Target vs actual Bloom's distributions, difficulty metrics, unit coverage, and CAS scores.
    """
    try:
        data = reporting_service.compute_paper_analytics(db, paper_id)
        return PaperAnalyticsSummary(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics computation failed: {str(e)}")

@router.get("/overview", response_model=SystemStats)
def get_system_stats(db: Session = Depends(get_db)):
    """
    Provides high-level institutional statistics across all indexed courses,
    historical banks, and generated exam papers.
    """
    total_courses = db.query(Course).count()
    total_questions = db.query(Question).count()
    historical_count = db.query(Question).filter(Question.is_historical == True).count()
    total_papers = db.query(ExamPaper).count()
    approved_papers = db.query(ExamPaper).filter(ExamPaper.status == "APPROVED").count()

    all_papers = db.query(ExamPaper).order_by(ExamPaper.created_at.desc()).limit(5).all()
    avg_cas = 0.0
    if total_papers > 0:
        scores = [p.cas_score for p in db.query(ExamPaper.cas_score).all() if p.cas_score]
        avg_cas = round(sum(scores) / len(scores), 2) if scores else 0.0

    recent_summary = [
        {
            "id": p.id,
            "title": p.title,
            "total_marks": p.total_marks,
            "cas_score": p.cas_score,
            "status": p.status,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for p in all_papers
    ]

    return SystemStats(
        total_courses=total_courses,
        total_questions=total_questions,
        historical_questions_count=historical_count,
        total_papers_generated=total_papers,
        approved_papers_count=approved_papers,
        average_cas_score=avg_cas,
        recent_papers=recent_summary
    )
