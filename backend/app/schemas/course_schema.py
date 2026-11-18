from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class TopicBase(BaseModel):
    name: str
    keywords: Optional[str] = None
    learning_outcome: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    unit_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class UnitBase(BaseModel):
    unit_number: int
    title: str
    description: Optional[str] = None
    target_weightage_pct: float = 16.67

class UnitCreate(UnitBase):
    topics: Optional[List[TopicCreate]] = []

class UnitResponse(UnitBase):
    id: int
    course_id: int
    topics: List[TopicResponse] = []
    created_at: datetime
    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    code: str
    title: str
    department: str = "Computer Science & Engineering"
    institution: str = "Vishwakarma Institute of Technology"
    semester: str = "Semester VI"
    academic_year: str = "2025-2026"

class CourseCreate(CourseBase):
    units: Optional[List[UnitCreate]] = []

class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    units: List[UnitResponse] = []
    class Config:
        from_attributes = True
