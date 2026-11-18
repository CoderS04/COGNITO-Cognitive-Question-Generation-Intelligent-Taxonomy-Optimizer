from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.validation_schema import ValidationAuditResponse, AutoRefineResponse
from app.services.module8_validation_engine import validation_engine

router = APIRouter(prefix="/validation", tags=["Module 8: Independent Validation Engine"])

@router.post("/validate/{paper_id}", response_model=ValidationAuditResponse)
def validate_paper(paper_id: int, db: Session = Depends(get_db)):
    """
    Executes an independent audit calculating the Comprehensive Assessment Score (CAS):
    CAS = ws*S + wb*B + wd*D + wm*M + wn*N + wt*T
    """
    try:
        audit = validation_engine.validate_paper(db, paper_id)
        return ValidationAuditResponse(
            id=audit.id,
            paper_id=audit.paper_id,
            cas_score=audit.cas_score,
            status=audit.status,
            metrics={
                "syllabus_coverage": audit.syllabus_coverage,
                "bloom_compliance": audit.bloom_compliance,
                "difficulty_compliance": audit.difficulty_compliance,
                "marks_compliance": audit.marks_compliance,
                "repetition_score": audit.repetition_score,
                "template_compliance": audit.template_compliance
            },
            violations=audit.violations or [],
            recommendations=audit.recommendations or [],
            created_at=audit.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.post("/auto-refine/{paper_id}", response_model=AutoRefineResponse)
def auto_refine_paper(paper_id: int, db: Session = Depends(get_db)):
    """
    Triggers the closed-loop refinement loop:
    Detects constraint violations -> reframes or swaps offending questions -> re-validates.
    """
    try:
        res = validation_engine.auto_refine_paper(db, paper_id)
        audit = res["audit"]
        audit_resp = ValidationAuditResponse(
            id=audit.id,
            paper_id=audit.paper_id,
            cas_score=audit.cas_score,
            status=audit.status,
            metrics={
                "syllabus_coverage": audit.syllabus_coverage,
                "bloom_compliance": audit.bloom_compliance,
                "difficulty_compliance": audit.difficulty_compliance,
                "marks_compliance": audit.marks_compliance,
                "repetition_score": audit.repetition_score,
                "template_compliance": audit.template_compliance
            },
            violations=audit.violations or [],
            recommendations=audit.recommendations or [],
            created_at=audit.created_at
        )
        return AutoRefineResponse(
            paper_id=res["paper_id"],
            iterations=res["iterations"],
            initial_cas=res["initial_cas"],
            final_cas=res["final_cas"],
            status=res["status"],
            actions_taken=res["actions_taken"],
            audit=audit_resp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-refinement failed: {str(e)}")
