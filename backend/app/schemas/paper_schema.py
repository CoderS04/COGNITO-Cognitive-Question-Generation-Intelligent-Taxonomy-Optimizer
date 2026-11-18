from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.question_schema import QuestionResponse

class PaperQuestionResponse(BaseModel):
    id: int
    question_id: int
    sub_question_label: str
    order_index: int
    is_optional: bool
    marks: int
    question: Optional[QuestionResponse] = None
    class Config:
        from_attributes = True

class PaperSectionResponse(BaseModel):
    id: int
    section_name: str
    instructions: Optional[str] = None
    total_marks: int
    order_index: int
    questions: List[PaperQuestionResponse] = []
    class Config:
        from_attributes = True

class ExamPaperResponse(BaseModel):
    id: int
    course_id: int
    template_id: Optional[int] = None
    title: str
    academic_year: str
    semester: str
    total_marks: int
    status: str
    cas_score: float
    meta_info: Optional[Dict[str, Any]] = None
    created_at: datetime
    sections: List[PaperSectionResponse] = []
    class Config:
        from_attributes = True

class GeneratePaperRequest(BaseModel):
    course_id: int
    template_id: Optional[int] = None
    title: str
    academic_year: Optional[str] = "2025-2026"
    semester: Optional[str] = "Semester VI"
    total_marks: int = 50
    duration_minutes: Optional[int] = 120
    instructions: Optional[str] = "Answer all questions. Figures to the right indicate full marks."
    
    # Target allocations
    bloom_targets: Optional[Dict[str, float]] = {
        "L1": 10.0,
        "L2": 20.0,
        "L3": 30.0,
        "L4": 25.0,
        "L5": 10.0,
        "L6": 5.0
    }
    difficulty_targets: Optional[Dict[str, float]] = {
        "Easy": 30.0,
        "Medium": 50.0,
        "Hard": 20.0
    }
    unit_weights: Optional[Dict[str, float]] = None # {"1": 25, "2": 25, ...}
    novelty_threshold: Optional[float] = 0.85
    enable_optimization: Optional[bool] = True

class ReplaceQuestionRequest(BaseModel):
    paper_id: int
    paper_question_id: int
    replacement_question_id: Optional[int] = None
    replacement_text: Optional[str] = None
    target_level: Optional[str] = None
    marks: Optional[int] = None
    primary_verb: Optional[str] = None
    solution_outline: Optional[str] = None

class SavePaperQuestionsRequest(BaseModel):
    question_ids: Optional[List[int]] = None
