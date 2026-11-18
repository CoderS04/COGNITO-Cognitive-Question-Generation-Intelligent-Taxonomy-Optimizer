from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ExamPaper(Base):
    __tablename__ = "exam_papers"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(Integer, ForeignKey("exam_templates.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    academic_year = Column(String(32), default="2025-2026")
    semester = Column(String(32), default="Semester VI")
    total_marks = Column(Integer, nullable=False)
    status = Column(String(32), default="DRAFT", index=True) # DRAFT, VALIDATED, APPROVED, REJECTED
    cas_score = Column(Float, default=0.0)
    meta_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="papers")
    template = relationship("ExamTemplate", back_populates="papers")
    sections = relationship("PaperSection", back_populates="paper", cascade="all, delete-orphan", order_by="PaperSection.order_index")
    audits = relationship("ValidationAudit", back_populates="paper", cascade="all, delete-orphan", order_by="ValidationAudit.created_at.desc()")

class PaperSection(Base):
    __tablename__ = "paper_sections"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("exam_papers.id", ondelete="CASCADE"), nullable=False)
    section_name = Column(String(128), nullable=False)
    instructions = Column(Text, nullable=True)
    total_marks = Column(Integer, nullable=False)
    order_index = Column(Integer, default=1)

    paper = relationship("ExamPaper", back_populates="sections")
    questions = relationship("PaperQuestion", back_populates="section", cascade="all, delete-orphan", order_by="PaperQuestion.order_index")

class PaperQuestion(Base):
    __tablename__ = "paper_questions"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("paper_sections.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False)
    sub_question_label = Column(String(32), nullable=False) # e.g. "Q1(a)", "Q2"
    order_index = Column(Integer, default=1)
    is_optional = Column(Boolean, default=False)
    marks = Column(Integer, nullable=False)

    section = relationship("PaperSection", back_populates="questions")
    question = relationship("Question", back_populates="paper_mappings")
