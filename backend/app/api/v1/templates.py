from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.template import ExamTemplate
from app.schemas.template_schema import ExamTemplateCreate, ExamTemplateResponse

router = APIRouter(prefix="/templates", tags=["Institutional Templates & Rules"])

@router.get("", response_model=List[ExamTemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    """Retrieves standard academic examination templates and policies."""
    return db.query(ExamTemplate).order_by(ExamTemplate.name).all()

@router.post("", response_model=ExamTemplateResponse)
def create_template(payload: ExamTemplateCreate, db: Session = Depends(get_db)):
    """Creates a new institutional exam template with custom sections and constraints."""
    tpl = ExamTemplate(
        name=payload.name,
        description=payload.description,
        total_marks=payload.total_marks,
        duration_minutes=payload.duration_minutes,
        instructions=payload.instructions,
        sections_config=payload.sections_config,
        bloom_targets=payload.bloom_targets,
        difficulty_targets=payload.difficulty_targets
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl

@router.get("/{template_id}", response_model=ExamTemplateResponse)
def get_template_detail(template_id: int, db: Session = Depends(get_db)):
    """Retrieves specific template blueprint and rules."""
    tpl = db.query(ExamTemplate).filter(ExamTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Exam template not found.")
    return tpl

@router.put("/{template_id}", response_model=ExamTemplateResponse)
def update_template(template_id: int, payload: ExamTemplateCreate, db: Session = Depends(get_db)):
    tpl = db.query(ExamTemplate).filter(ExamTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Exam template not found.")
    for field, value in payload.model_dump().items():
        setattr(tpl, field, value)
    db.commit()
    db.refresh(tpl)
    return tpl

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    tpl = db.query(ExamTemplate).filter(ExamTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Exam template not found.")
    db.delete(tpl)
    db.commit()
    return {"status": "success", "template_id": template_id}
