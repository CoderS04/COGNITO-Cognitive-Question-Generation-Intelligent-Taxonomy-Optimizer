from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="SET NULL"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    
    text = Column(Text, nullable=False)
    question_type = Column(String(32), default="Descriptive") # MCQ, Short, Descriptive, Numerical
    marks = Column(Integer, nullable=False, default=5)
    bloom_level = Column(String(8), nullable=False, default="L2", index=True) # L1, L2, L3, L4, L5, L6
    primary_verb = Column(String(64), nullable=True)
    difficulty = Column(String(16), nullable=False, default="Medium", index=True) # Easy, Medium, Hard
    difficulty_score = Column(Float, nullable=False, default=0.5)
    is_historical = Column(Boolean, default=False)
    exam_year = Column(Integer, nullable=True)
    embedding_id = Column(String(128), nullable=True)
    solution_outline = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="questions")
    unit = relationship("Unit", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    paper_mappings = relationship("PaperQuestion", back_populates="question")
