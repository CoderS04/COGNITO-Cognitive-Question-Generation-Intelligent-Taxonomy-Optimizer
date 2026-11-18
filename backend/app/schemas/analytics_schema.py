from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class BloomDistribution(BaseModel):
    level: str
    target_pct: float
    actual_pct: float
    marks: int
    question_count: int

class DifficultyDistribution(BaseModel):
    category: str
    target_pct: float
    actual_pct: float
    marks: int
    question_count: int

class UnitCoverageStat(BaseModel):
    unit_number: int
    title: str
    target_pct: float
    actual_pct: float
    marks: int
    questions_count: int

class PaperAnalyticsSummary(BaseModel):
    paper_id: int
    title: str
    total_marks: int
    cas_score: float
    status: str
    bloom_distribution: List[BloomDistribution]
    difficulty_distribution: List[DifficultyDistribution]
    unit_coverage: List[UnitCoverageStat]
    average_similarity_to_history: float
    high_similarity_flags_count: int
    cognitive_depth_index: float # 1.0 (pure L1) to 6.0 (pure L6)

class SystemStats(BaseModel):
    total_courses: int
    total_questions: int
    historical_questions_count: int
    total_papers_generated: int
    approved_papers_count: int
    average_cas_score: float
    recent_papers: List[Dict[str, Any]]
