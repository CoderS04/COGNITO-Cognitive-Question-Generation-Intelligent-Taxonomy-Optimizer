from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ExamTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    total_marks: int = 100
    duration_minutes: int = 180
    instructions: Optional[str] = None
    sections_config: List[Dict[str, Any]]
    bloom_targets: Dict[str, float] # e.g. {"L1": 10, "L2": 20, "L3": 30, "L4": 25, "L5": 10, "L6": 5}
    difficulty_targets: Dict[str, float] # e.g. {"Easy": 30, "Medium": 50, "Hard": 20}

class ExamTemplateCreate(ExamTemplateBase):
    pass

class ExamTemplateResponse(ExamTemplateBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
