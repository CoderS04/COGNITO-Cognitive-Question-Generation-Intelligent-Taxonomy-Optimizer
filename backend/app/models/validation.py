from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ValidationAudit(Base):
    __tablename__ = "validation_audits"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("exam_papers.id", ondelete="CASCADE"), nullable=False)
    
    # CAS Metrics: CAS = ws*S + wb*B + wd*D + wm*M + wn*N + wt*T
    cas_score = Column(Float, nullable=False)
    syllabus_coverage = Column(Float, nullable=False)
    bloom_compliance = Column(Float, nullable=False)
    difficulty_compliance = Column(Float, nullable=False)
    marks_compliance = Column(Float, nullable=False)
    repetition_score = Column(Float, nullable=False)
    template_compliance = Column(Float, nullable=False)
    
    status = Column(String(32), default="PASSED") # PASSED, WARNING, FAILED
    violations = Column(JSON, nullable=True) # list of violation messages
    recommendations = Column(JSON, nullable=True) # list of improvement suggestions
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("ExamPaper", back_populates="audits")
