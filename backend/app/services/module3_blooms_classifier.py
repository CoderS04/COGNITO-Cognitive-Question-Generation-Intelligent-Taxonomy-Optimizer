import re
from typing import Dict, Any, Optional
from app.services.ai_analysis_engine import ai_analysis_engine, BloomAnalysisResult
from app.services.generation_engine import generation_engine, ReframedQuestionResult

LEVEL_NAMES = {
    "L1": "Remember",
    "L2": "Understand",
    "L3": "Apply",
    "L4": "Analyze",
    "L5": "Evaluate",
    "L6": "Create"
}

class BloomsTaxonomyClassifier:
    """
    Module 3: LLM-Driven Bloom's Taxonomy Cognitive Level Classifier & Reframer
    Delegates to AIAnalysisEngine and GenerationEngine with Pydantic validation
    and deterministic fallback resilience.
    """

    def classify_question(
        self,
        text: str,
        marks: int = 5,
        syllabus_context: Optional[str] = None,
        course_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates question using prompt-engineered LLM cognitive analysis.
        Returns:
        - bloom_level (L1..L6)
        - cognitive_domain (Remember..Create)
        - primary_verb
        - confidence (0.0 to 1.0)
        - explanation (reasoning)
        - difficulty (Easy/Medium/Hard)
        - difficulty_score (0.0 to 1.0)
        """
        res: BloomAnalysisResult = ai_analysis_engine.analyze_question(
            question_text=text,
            marks=marks,
            syllabus_context=syllabus_context,
            course_title=course_title
        )

        domain = LEVEL_NAMES.get(res.bloom_level, "Understand")
        return {
            "bloom_level": res.bloom_level,
            "cognitive_domain": domain,
            "primary_verb": res.primary_verb or "evaluate",
            "confidence": round(res.confidence_score, 2),
            "explanation": res.reasoning,
            "difficulty": res.difficulty,
            "difficulty_score": res.difficulty_score or 0.5
        }

    def reframe_question(
        self,
        text: str,
        current_level: str,
        target_level: str,
        db: Optional[Any] = None,
        course_id: Optional[int] = None,
        unit_id: Optional[int] = None,
        custom_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Elevates or reframes a question to target a higher Bloom's level
        using grounded LLM synthesis.
        """
        res: ReframedQuestionResult = generation_engine.reframe_question(
            question_text=text,
            current_level=current_level,
            target_level=target_level,
            db=db,
            course_id=course_id,
            unit_id=unit_id,
            custom_prompt=custom_prompt,
        )

        return {
            "original_text": res.original_text,
            "original_level": res.original_level,
            "target_level": res.target_level,
            "reframed_text": res.reframed_text,
            "primary_verb": res.primary_verb,
            "suggested_marks": res.suggested_marks,
            "explanation": res.explanation,
            "rubric_outline": res.rubric_outline,
            "source_context_ids": res.source_context_ids,
        }

blooms_classifier = BloomsTaxonomyClassifier()
