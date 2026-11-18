import re
from typing import List, Dict, Any, Optional, Literal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.config import settings
from app.services.llm_service import llm_service
from app.services.module6_rag_engine import rag_engine
from app.models.course import Course, Unit, Topic
from app.models.question import Question
from app.core.vector_store import vector_store

class ReframedQuestionResult(BaseModel):
    original_text: str
    original_level: str
    target_level: Literal["L1", "L2", "L3", "L4", "L5", "L6"]
    reframed_text: str = Field(..., description="The redesigned question prompt strictly aligned to the target cognitive level.")
    primary_verb: str = Field(..., description="Action verb initiating the question.")
    suggested_marks: int = Field(..., ge=1, le=25, description="Recommended marks weightage.")
    explanation: str = Field(..., description="Pedagogical justification explaining how the question was elevated.")
    rubric_outline: Optional[str] = Field(default=None, description="Expected grading criteria and solution outline.")
    source_context_ids: List[str] = Field(default_factory=list)

class GeneratedQuestionCandidate(BaseModel):
    text: str = Field(..., description="Question statement.")
    bloom_level: Literal["L1", "L2", "L3", "L4", "L5", "L6"]
    difficulty: Literal["Easy", "Medium", "Hard"]
    marks: int = Field(..., ge=1, le=25)
    primary_verb: str
    solution_rubric: str
    explanation: str
    source_context_ids: List[str] = Field(default_factory=list)
    source_question_ids: List[int] = Field(default_factory=list)

class GenerationEngine:
    """
    Grounded Question Generation & Cognitive Reframing Module
    Utilizes LLMs grounded by RAG context (syllabus units, topics, learning outcomes,
    and historical exam benchmarks) with anti-hallucination guardrails.
    """

    ANTI_HALLUCINATION_PROMPT = """You are an expert academic assessment designer.
Generate or reframe questions strictly within the boundaries of the provided syllabus unit and institutional guidelines.
Do not introduce out-of-scope concepts or make unsupported assumptions.
Strictly satisfy Bloom's Revised Taxonomy levels:
- L1 Remember: Define, State, List, Recall.
- L2 Understand: Explain, Describe, Discuss, Clarify.
- L3 Apply: Calculate, Solve, Execute, Apply to problem instance.
- L4 Analyze: Compare, Contrast, Differentiate, Deconstruct trade-offs.
- L5 Evaluate: Justify, Critique, Defend, Appraise against criteria.
- L6 Create: Design, Formulate, Architect, Devise a novel system/protocol."""

    def reframe_question(
        self,
        question_text: str,
        current_level: str,
        target_level: str,
        db: Optional[Session] = None,
        course_id: Optional[int] = None,
        unit_id: Optional[int] = None,
        custom_prompt: Optional[str] = None,
    ) -> ReframedQuestionResult:
        """
        Elevates or adapts an examination question to a higher Bloom's level
        grounded in syllabus context retrieved via RAG.
        """
        # 1. Retrieve Grounded RAG Context
        syllabus_context = "No syllabus context was retrieved; do not invent one."
        context_ids: List[str] = []
        if db and (course_id or unit_id):
            u_num = None
            if unit_id:
                u_obj = db.query(Unit).filter(Unit.id == unit_id).first()
                if u_obj:
                    u_num = u_obj.unit_number
            rag_res = rag_engine.retrieve_context(
                course_id=course_id or 1,
                unit_number=u_num,
                db=db
            )
            topics_list = rag_res["structured_context"].get("topics", [])
            outcomes = rag_res["structured_context"].get("learning_outcomes", [])
            syllabus_hits = rag_res.get("syllabus_hits", [])
            context_ids = [str(hit["id"]) for hit in syllabus_hits if hit.get("id")]
            syllabus_context = (
                f"Course: {rag_res['structured_context'].get('course_title', '')}\n"
                f"Unit: {rag_res['structured_context'].get('unit_title', '')}\n"
                f"Topics: {', '.join(topics_list)}\n"
                f"Learning Outcomes: {'; '.join(outcomes)}\n"
                f"Retrieved syllabus excerpts: {' | '.join(hit.get('text', '') for hit in syllabus_hits)}"
            )

        # 2. Construct Grounded Prompt
        user_prompt = f"""ACADEMIC CONTEXT:
Syllabus Context: {syllabus_context}

ORIGINAL QUESTION:
Question Text: "{question_text}"
Current Bloom's Level: {current_level}

TASK:
Reframe the above question to target Bloom's Cognitive Level: {target_level}.
Maintain strict alignment with the syllabus topic. Elevate the cognitive demand appropriately (e.g. if targeting L4/L5, ask for trade-off analysis or evaluation; if targeting L6, require designing a system architecture under operational constraints).
Faculty custom instruction: {custom_prompt or "None"}"""


        # print(f"Reframing Question Prompt:\n{user_prompt}\n")  # Debugging output

        messages = [
            {"role": "system", "content": self.ANTI_HALLUCINATION_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        def fallback_fn() -> ReframedQuestionResult:
            return self._heuristic_reframe_fallback(question_text, current_level, target_level)

        result: ReframedQuestionResult = llm_service.generate_structured(
            messages=messages,
            response_model=ReframedQuestionResult,
            temperature=settings.LLM_TEMPERATURE,
            fallback_fn=fallback_fn
        )
        result.source_context_ids = context_ids
        return result

    def generate_candidate_question(
        self,
        course_name: str,
        unit_number: int,
        unit_title: str,
        topic_name: str,
        target_bloom: str,
        target_difficulty: str,
        marks: int,
        historical_questions: List[str],
        db: Optional[Session] = None,
        course_id: Optional[int] = None
    ) -> GeneratedQuestionCandidate:
        """
        Generates a candidate question strictly grounded in syllabus boundaries
        and avoiding repetition against historical exam questions.
        """
        context_ids: List[str] = []
        historical_ids: List[int] = []
        retrieved_context = ""
        if db and course_id:
            rag_res = rag_engine.retrieve_context(
                course_id=course_id,
                unit_number=unit_number,
                topic_name=topic_name,
                db=db,
            )
            hits = rag_res.get("syllabus_hits", [])
            context_ids = [str(hit["id"]) for hit in hits if hit.get("id")]
            retrieved_context = "\n".join(hit.get("text", "") for hit in hits)
            historical_ids = [
                int(question.id)
                for question in db.query(Question).filter(
                    Question.course_id == course_id,
                    Question.is_historical.is_(True),
                ).limit(6).all()
            ]
            if not historical_questions:
                historical_questions = [
                    question.text
                    for question in db.query(Question).filter(
                        Question.id.in_(historical_ids)
                    ).all()
                ]

        hist_avoid = "\n".join([f"- {h}" for h in historical_questions[:6]]) if historical_questions else "None recorded."

        user_prompt = f"""ACADEMIC BOUNDARIES:
- Course: {course_name}
- Unit {unit_number}: {unit_title}
- Target Topic: {topic_name}
- Target Bloom's Taxonomy Level: {target_bloom}
- Target Difficulty: {target_difficulty}
- Allocated Marks: {marks} Marks
- Retrieved syllabus context (authoritative boundary):
{retrieved_context or "None retrieved; use only the target topic name."}

PREVIOUS EXAM QUESTIONS TO AVOID REPEATING (Ensure Novelty):
{hist_avoid}

Use only the supplied course, unit, and topic boundaries. Historical questions are
novelty references, not syllabus authority.

TASK:
Generate a rigorous, publication-quality examination question satisfying the specified Bloom's level ({target_bloom}) and marks ({marks}M).
Provide an explicit solution rubric breakdown."""

        messages = [
            {"role": "system", "content": self.ANTI_HALLUCINATION_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        def fallback_fn() -> GeneratedQuestionCandidate:
            return GeneratedQuestionCandidate(
                text=f"Analyze the computational trade-offs and performance characteristics of {topic_name} in enterprise scenarios.",
                bloom_level=target_bloom if target_bloom in ["L1", "L2", "L3", "L4", "L5", "L6"] else "L4",
                difficulty=target_difficulty if target_difficulty in ["Easy", "Medium", "Hard"] else "Medium",
                marks=marks,
                primary_verb="analyze",
                solution_rubric=f"1. Conceptual basis (2M)\n2. Performance comparison (3M)\n3. Critical trade-offs (3M)",
                explanation=f"Grounded question synthesized for {topic_name} targeting {target_bloom}.",
                source_context_ids=context_ids,
                source_question_ids=historical_ids,
            )

        candidate: GeneratedQuestionCandidate = llm_service.generate_structured(
            messages=messages,
            response_model=GeneratedQuestionCandidate,
            temperature=settings.LLM_TEMPERATURE,
            fallback_fn=fallback_fn
        )

        candidate.source_context_ids = context_ids
        candidate.source_question_ids = historical_ids
        return candidate

    def _heuristic_reframe_fallback(
        self,
        question_text: str,
        current_level: str,
        target_level: str
    ) -> ReframedQuestionResult:
        """Deterministic heuristic reframing fallback."""
        clean = re.sub(r'^(what is|define|state|list|explain|describe|discuss|how does)\s+', '', question_text.strip(), flags=re.I).rstrip('?.')
        
        marks_map = {"L1": 2, "L2": 4, "L3": 6, "L4": 8, "L5": 10, "L6": 12}
        suggested_marks = marks_map.get(target_level, 6)

        if target_level == "L1":
            verb = "Define"
            reframed = f"State and define the core formal properties of {clean}."
            exp = "Reframed to test direct recall and precise definition."
        elif target_level == "L2":
            verb = "Explain"
            reframed = f"Explain the operating principles and structural workflow of {clean} with a conceptual diagram."
            exp = "Reframed to assess comprehensive descriptive understanding."
        elif target_level == "L3":
            verb = "Apply"
            reframed = f"Demonstrate the practical application of {clean} to solve a concrete problem instance with intermediate steps."
            exp = "Reframed to evaluate computational and procedural execution."
        elif target_level == "L4":
            verb = "Analyze"
            reframed = f"Analyze the behavioral characteristics and performance trade-offs of {clean} under dynamic load constraints."
            exp = "Reframed to demand analytical deconstruction, comparison, and trade-off evaluation."
        elif target_level == "L5":
            verb = "Evaluate"
            reframed = f"Critically evaluate and justify the adoption of {clean} over competing alternatives in mission-critical applications."
            exp = "Reframed to assess critical appraisal, evidence-based judgment, and justification."
        else: # L6
            verb = "Design"
            reframed = f"Design a resilient, fault-tolerant architecture integrating {clean} to fulfill high-availability real-world requirements."
            exp = "Reframed to test novel synthesis and architectural engineering."

        return ReframedQuestionResult(
            original_text=question_text,
            original_level=current_level,
            target_level=target_level,
            reframed_text=reframed,
            primary_verb=verb,
            suggested_marks=suggested_marks,
            explanation=exp,
            rubric_outline=f"Marking Scheme ({suggested_marks}M):\n- Methodological design (40%)\n- Theoretical rigor (30%)\n- Analysis of edge cases (30%)"
        )

generation_engine = GenerationEngine()
