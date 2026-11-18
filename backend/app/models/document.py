from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from app.core.database import Base

class IngestedDocument(Base):
    __tablename__ = "ingested_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    doc_type = Column(String(64), nullable=False) # 'syllabus', 'past_paper', 'guideline'
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    file_size = Column(Integer, nullable=False, default=0)
    status = Column(String(32), default="PROCESSED")
    extracted_items_count = Column(Integer, default=0)
    summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
