import re
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

from app.services.llm_service import llm_service
from app.config import settings

class BloomAnalysisResult(BaseModel):
    bloom_level: Literal["L1", "L2", "L3", "L4", "L5", "L6"] = Field(
        ...,
        description="Exact Bloom's Revised Taxonomy level: L1 (Remember), L2 (Understand), L3 (Apply), L4 (Analyze), L5 (Evaluate), L6 (Create)"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    reasoning: str = Field(
        ...,
        description="Brief justification based on the cognitive processes, actions demanded, and conceptual depth"
    )
    difficulty: Literal["Easy", "Medium", "Hard"] = Field(
        ...,
        description="Cognitive and procedural difficulty classification"
    )
    primary_verb: Optional[str] = Field(
        default=None,
        description="Primary action verb or cognitive directive identifying the task"
    )
    difficulty_score: Optional[float] = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Numerical difficulty score from 0.0 to 1.0"
    )

LEVEL_DESCRIPTIONS = {
    "L1": "Remember: Retrieving, recognizing, recalling relevant knowledge from long-term memory (e.g. define, list, state, identify).",
    "L2": "Understand: Constructing meaning from messages, explaining ideas, clarifying, interpreting, summarizing (e.g. explain, describe, discuss, classify).",
    "L3": "Apply: Carrying out or using a procedure in a given situation, computational problem solving, execution (e.g. solve, calculate, demonstrate, implement).",
    "L4": "Analyze: Breaking material into constituent parts, determining relationships, comparing, deconstructing, finding trade-offs (e.g. analyze, compare, contrast, differentiate).",
    "L5": "Evaluate: Making judgments based on criteria and standards, critiquing, justifying a stand, appraisal (e.g. evaluate, justify, critique, defend).",
    "L6": "Create: Putting elements together to form a novel, coherent whole; designing systems, formulating architectures or protocols (e.g. design, formulate, devise, synthesize)."
}

LEVEL_NAMES = {
    "L1": "Remember",
    "L2": "Understand",
    "L3": "Apply",
    "L4": "Analyze",
    "L5": "Evaluate",
    "L6": "Create"
}

DIFFICULTY_NUM_MAP = {
    "Easy": 0.25,
    "Medium": 0.55,
    "Hard": 0.85
}

class AIAnalysisEngine:
    """
    LLM-Powered Bloom's Taxonomy & Difficulty Classifier
    Replaces rigid keyword-matching with prompt-engineered cognitive analysis
    strictly validated with Pydantic schemas.
    """

    SYSTEM_PROMPT = """You are a Principal Academic Assessment Specialist and Expert in Bloom's Revised Taxonomy (Anderson & Krathwohl, 2001).
Your objective is to evaluate examination questions and classify their cognitive level and difficulty with extreme precision.

Bloom's Taxonomy Levels:
- L1 (Remember): Recalling facts, basic concepts, formulas, definitions, or lists.
- L2 (Understand): Explaining ideas, concepts, mechanisms, or interpreting diagrams.
- L3 (Apply): Executing procedures, applying algorithms, calculations, or solving practical problem instances.
- L4 (Analyze): Breaking down concepts, comparing trade-offs, differentiating components, or investigating edge-case behaviors.
- L5 (Evaluate): Making critical judgments, evaluating alternatives, justifying design decisions, or critiquing limitations.
- L6 (Create): Designing novel systems, formulating original algorithms, devising architectures, or synthesizing multi-component solutions.

Difficulty Guidelines:
- Easy: Direct recall or basic descriptive explanation with minimal multi-step execution.
- Medium: Standard procedural problem solving, multi-step calculation, or standard comparative analysis.
- Hard: High-order synthesis, non-trivial mathematical derivation, critical trade-off evaluation, or open-ended system design under constraints.

Strict Grounding Rule:
Base your classification on the mental operations demanded of a university engineering student, not merely on the surface verb."""

    def analyze_question(
        self,
        question_text: str,
        marks: int = 5,
        syllabus_context: Optional[str] = None,
        course_title: Optional[str] = None
    ) -> BloomAnalysisResult:
        """
        Classifies an examination question into Bloom's Taxonomy (L1..L6)
        and Difficulty (Easy, Medium, Hard) using LLM inference with Pydantic validation.
        """
        context_str = f"Course: {course_title}\n" if course_title else ""
        if syllabus_context:
            context_str += f"Syllabus Context: {syllabus_context}\n"

        user_prompt = f"""{context_str}Analyze the following examination question:
Question: "{question_text}"
Allocated Marks: {marks} Marks

Evaluate the required cognitive domain and procedural depth. Classify into L1, L2, L3, L4, L5, or L6 and estimate difficulty (Easy, Medium, or Hard)."""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        def fallback_fn() -> BloomAnalysisResult:
            return self._heuristic_fallback(question_text, marks)

        result: BloomAnalysisResult = llm_service.generate_structured(
            messages=messages,
            response_model=BloomAnalysisResult,
            temperature=settings.LLM_TEMPERATURE,
            fallback_fn=fallback_fn
        )

        # Ensure helper fields are populated
        if not result.primary_verb:
            words = question_text.split()
            result.primary_verb = words[0].lower().rstrip("?:,.") if words else "evaluate"
            
        if result.difficulty_score is None:
            result.difficulty_score = DIFFICULTY_NUM_MAP.get(result.difficulty, 0.5)

        return result

    def _heuristic_fallback(self, question_text: str, marks: int) -> BloomAnalysisResult:
        """
        Deterministic cognitive classifier fallback used when external LLMs are unreachable.
        """
        lower = question_text.lower()
        
        # Check high-order cues
        if any(w in lower for w in ["design", "formulate", "devise", "synthesize", "architect", "propose a novel"]):
            return BloomAnalysisResult(
                bloom_level="L6",
                confidence_score=0.92,
                reasoning="Requires synthesis and original design of a computational system or framework.",
                difficulty="Hard",
                primary_verb="design",
                difficulty_score=0.88
            )
        elif any(w in lower for w in ["evaluate", "justify", "critique", "defend", "appraise", "validate"]):
            return BloomAnalysisResult(
                bloom_level="L5",
                confidence_score=0.90,
                reasoning="Demands critical appraisal, justification, and comparative evaluation against standards.",
                difficulty="Hard",
                primary_verb="evaluate",
                difficulty_score=0.82
            )
        elif any(w in lower for w in ["analyze", "compare", "contrast", "differentiate", "deconstruct", "trade-off"]):
            return BloomAnalysisResult(
                bloom_level="L4",
                confidence_score=0.88,
                reasoning="Involves analytical deconstruction of components and comparative trade-off inspection.",
                difficulty="Medium" if marks <= 7 else "Hard",
                primary_verb="analyze",
                difficulty_score=0.68
            )
        elif any(w in lower for w in ["calculate", "solve", "apply", "execute", "compute", "trace", "determine", "demonstrate"]):
            return BloomAnalysisResult(
                bloom_level="L3",
                confidence_score=0.87,
                reasoning="Calls for direct application of algorithms or mathematical calculation procedures.",
                difficulty="Medium",
                primary_verb="apply/solve",
                difficulty_score=0.58
            )
        elif any(w in lower for w in ["explain", "describe", "discuss", "summarize", "classify", "interpret"]):
            return BloomAnalysisResult(
                bloom_level="L2",
                confidence_score=0.85,
                reasoning="Assesses conceptual understanding and descriptive clarity.",
                difficulty="Easy" if marks <= 4 else "Medium",
                primary_verb="explain",
                difficulty_score=0.40
            )
        else:
            # Default to L1 or L2 based on marks
            lvl = "L1" if marks <= 3 else "L2"
            return BloomAnalysisResult(
                bloom_level=lvl,
                confidence_score=0.75,
                reasoning=f"Inferred {lvl} based on factual recall characteristics and weightage ({marks} Marks).",
                difficulty="Easy" if lvl == "L1" else "Medium",
                primary_verb="recall" if lvl == "L1" else "explain",
                difficulty_score=0.25 if lvl == "L1" else 0.42
            )

ai_analysis_engine = AIAnalysisEngine()
