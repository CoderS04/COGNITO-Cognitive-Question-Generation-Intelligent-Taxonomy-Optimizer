from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.course import Course, Unit, Topic
from app.schemas.course_schema import CourseCreate, CourseResponse, UnitCreate, UnitResponse, TopicCreate, TopicResponse
from app.services.module2_knowledge_base import knowledge_base_service

router = APIRouter(prefix="/courses", tags=["Module 2: Courses & Knowledge Base"])

@router.get("", response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    """Retrieves all registered courses with their syllabus modules."""
    return db.query(Course).order_by(Course.code).all()

@router.post("", response_model=CourseResponse)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    """Creates a new academic course with syllabus units and topics."""
    existing = db.query(Course).filter(Course.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Course with code {payload.code} already exists.")

    course = Course(
        code=payload.code,
        title=payload.title,
        department=payload.department,
        institution=payload.institution,
        semester=payload.semester,
        academic_year=payload.academic_year
    )
    db.add(course)
    db.flush()

    if payload.units:
        for u_data in payload.units:
            unit = Unit(
                course_id=course.id,
                unit_number=u_data.unit_number,
                title=u_data.title,
                description=u_data.description,
                target_weightage_pct=u_data.target_weightage_pct
            )
            db.add(unit)
            db.flush()
            for t_data in u_data.topics or []:
                topic = Topic(
                    unit_id=unit.id,
                    name=t_data.name,
                    keywords=t_data.keywords,
                    learning_outcome=t_data.learning_outcome
                )
                db.add(topic)
                db.flush()
                knowledge_base_service.sync_syllabus_chunk_to_vector_store(unit, topic)

    db.commit()
    db.refresh(course)
    return course

@router.get("/{course_id}", response_model=CourseResponse)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    """Retrieves detailed syllabus breakdown for a specific course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    return course

@router.post("/{course_id}/units", response_model=UnitResponse)
def add_unit(course_id: int, payload: UnitCreate, db: Session = Depends(get_db)):
    """Adds a new unit/module to an existing course syllabus."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    unit = Unit(
        course_id=course_id,
        unit_number=payload.unit_number,
        title=payload.title,
        description=payload.description,
        target_weightage_pct=payload.target_weightage_pct
    )
    db.add(unit)
    db.flush()

    for t_data in payload.topics or []:
        topic = Topic(
            unit_id=unit.id,
            name=t_data.name,
            keywords=t_data.keywords,
            learning_outcome=t_data.learning_outcome
        )
        db.add(topic)
        db.flush()
        knowledge_base_service.sync_syllabus_chunk_to_vector_store(unit, topic)

    db.commit()
    db.refresh(unit)
    return unit
