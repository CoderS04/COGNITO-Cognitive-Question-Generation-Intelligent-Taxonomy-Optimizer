from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QuestionBase(BaseModel):
    course_id: int
    unit_id: Optional[int] = None
    topic_id: Optional[int] = None
    text: str
    question_type: str = "Descriptive"
    marks: int = 5
    bloom_level: str = "L2"
    primary_verb: Optional[str] = None
    difficulty: str = "Medium"
    difficulty_score: float = 0.5
    is_historical: bool = False
    exam_year: Optional[int] = None
    solution_outline: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class QuestionAnalyzeRequest(BaseModel):
    text: str
    marks: Optional[int] = 5
    course_id: Optional[int] = None

class QuestionAnalyzeResponse(BaseModel):
    text: str
    bloom_level: str
    primary_verb: str
    confidence: float
    difficulty: str
    difficulty_score: float
    linguistic_score: float
    conceptual_depth: float
    cognitive_target: str
    explanation: str

class QuestionReframeRequest(BaseModel):
    question_id: Optional[int] = None
    text: Optional[str] = None
    target_level: str = Field(..., description="Target Bloom's level: L1, L2, L3, L4, L5, L6")
    custom_prompt: Optional[str] = None

class QuestionReframeResponse(BaseModel):
    original_text: str
    original_level: str
    target_level: str
    reframed_text: str
    primary_verb: str
    suggested_marks: int
    explanation: str
    rubric_outline: Optional[str] = None
    source_context_ids: List[str] = Field(default_factory=list)

class SimilarityCheckRequest(BaseModel):
    text: str
    course_id: Optional[int] = None
    question_id: Optional[int] = None
    threshold: Optional[float] = 0.85

class SimilarQuestionMatch(BaseModel):
    question_id: int
    text: str
    similarity: float
    bloom_level: str
    difficulty: str
    exam_year: Optional[int] = None
    is_historical: bool

class SimilarityCheckResponse(BaseModel):
    query_text: str
    is_repetition: bool
    is_paraphrase: bool
    max_similarity: float
    matches: List[SimilarQuestionMatch]
