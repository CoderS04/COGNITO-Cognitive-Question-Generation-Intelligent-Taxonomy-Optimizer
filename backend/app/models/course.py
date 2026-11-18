from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False, default="Computer Science & Engineering")
    institution = Column(String(255), nullable=False, default="Vishwakarma Institute of Technology")
    semester = Column(String(32), nullable=False, default="Semester VI")
    academic_year = Column(String(32), nullable=False, default="2025-2026")
    created_at = Column(DateTime, default=datetime.utcnow)

    units = relationship("Unit", back_populates="course", cascade="all, delete-orphan", order_by="Unit.unit_number")
    questions = relationship("Question", back_populates="course", cascade="all, delete-orphan")
    papers = relationship("ExamPaper", back_populates="course", cascade="all, delete-orphan")

class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    unit_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_weightage_pct = Column(Float, default=16.67)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("course_id", "unit_number", name="uq_course_unit"),)

    course = relationship("Course", back_populates="units")
    topics = relationship("Topic", back_populates="unit", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="unit")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    keywords = Column(Text, nullable=True)
    learning_outcome = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    unit = relationship("Unit", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
