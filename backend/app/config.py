from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "COGNITO: Cognitive Question Generation & Intelligent Taxonomy Optimizer"
    API_V1_STR: str = "/api/v1"
    
    # Database (Defaults to SQLite for instant local execution, configurable to PostgreSQL)
    DATABASE_URL: str = "sqlite:///./cognito.db"
    
    # Vector Database (ChromaDB persistent store)
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # Similarity & Repetition Thresholds
    REPETITION_THRESHOLD: float = 0.85
    PARAPHRASE_THRESHOLD: float = 0.70
    
    # CAS Score Threshold for Automatic Approval
    CAS_APPROVAL_THRESHOLD: float = 0.82
    
    # Constraint Optimization Weights: Score(Q) = w1*R + w2*B + w3*D + w4*N + w5*Q
    W_RELEVANCE: float = 0.25
    W_BLOOMS: float = 0.25
    W_DIFFICULTY: float = 0.20
    W_NOVELTY: float = 0.15
    W_QUALITY: float = 0.15
    
    # Validation CAS Weights: CAS = ws*S + wb*B + wd*D + wm*M + wn*N + wt*T
    WS_SYLLABUS: float = 0.25
    WB_BLOOMS: float = 0.25
    WD_DIFFICULTY: float = 0.20
    WM_MARKS: float = 0.15
    WN_NOVELTY: float = 0.10
    WT_TEMPLATE: float = 0.05

    # LLM Service Configuration
    LLM_PROVIDER: str = "auto" # "auto", "ollama", "openai", "gemini", "anthropic", "fallback"
    
    # Local Models (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_KEEP_ALIVE: str = "10m"
    
    # Cloud Models: OpenAI / Compatible (Groq, vLLM, DeepSeek, etc.)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Cloud Models: Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Cloud Models: Anthropic Claude
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # LLM Inference Parameters
    LLM_TEMPERATURE: float = Field(default=0.15, ge=0.0, le=1.0)
    LLM_TIMEOUT: float = Field(default=180.0, gt=0.0)
    LLM_MAX_RETRIES: int = 2

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
