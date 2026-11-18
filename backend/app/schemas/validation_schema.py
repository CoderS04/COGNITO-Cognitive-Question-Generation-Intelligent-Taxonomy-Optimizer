from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ValidationMetrics(BaseModel):
    syllabus_coverage: float
    bloom_compliance: float
    difficulty_compliance: float
    marks_compliance: float
    repetition_score: float
    template_compliance: float

class ValidationAuditResponse(BaseModel):
    id: Optional[int] = None
    paper_id: int
    cas_score: float
    status: str # PASSED, WARNING, FAILED
    metrics: ValidationMetrics
    violations: List[str] = []
    recommendations: List[str] = []
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class AutoRefineResponse(BaseModel):
    paper_id: int
    iterations: int
    initial_cas: float
    final_cas: float
    status: str
    actions_taken: List[str]
    audit: ValidationAuditResponse
