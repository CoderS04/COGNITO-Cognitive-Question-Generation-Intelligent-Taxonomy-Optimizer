from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ExamTemplate(Base):
    __tablename__ = "exam_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    total_marks = Column(Integer, nullable=False, default=100)
    duration_minutes = Column(Integer, nullable=False, default=180)
    instructions = Column(Text, nullable=True)
    
    # Structural configuration: sections, mandatory vs choice rules
    # e.g., [{"section_name": "Section A", "marks": 20, "instructions": "Answer all questions"}]
    sections_config = Column(JSON, nullable=False)
    
    # Target Bloom's taxonomy percentages: {"L1": 10, "L2": 20, "L3": 30, "L4": 25, "L5": 10, "L6": 5}
    bloom_targets = Column(JSON, nullable=False)
    
    # Target difficulty percentages: {"Easy": 30, "Medium": 50, "Hard": 20}
    difficulty_targets = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    papers = relationship("ExamPaper", back_populates="template")
