import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.vector_store import vector_store
from app.models.course import Course, Unit, Topic
from app.models.question import Question

class RAGEngine:
    """
    Module 6: Retrieval-Augmented Generation (RAG) Engine
    Retrieves syllabus sections, learning outcomes, institutional guidelines,
    and past examination benchmarks to ground question paper generation.
    """

    def retrieve_context(
        self,
        course_id: int,
        unit_number: Optional[int] = None,
        topic_name: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Retrieves syllabus topics, keywords, learning outcomes, and past questions
        for the given academic target.
        """
        query = f"Course {course_id}"
        if unit_number:
            query += f" Unit {unit_number}"
        if topic_name:
            query += f" Topic {topic_name}"

        # 1. Semantic retrieval from vector store
        syllabus_hits = vector_store.search_syllabus_context(query, n_results=4)

        # 2. Relational retrieval from SQL DB if provided
        db_context = {
            "course_title": "",
            "unit_title": "",
            "topics": [],
            "learning_outcomes": []
        }
        
        if db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                db_context["course_title"] = course.title
                if unit_number:
                    unit = db.query(Unit).filter(
                        Unit.course_id == course_id,
                        Unit.unit_number == unit_number
                    ).first()
                    if unit:
                        db_context["unit_title"] = unit.title
                        for t in unit.topics:
                            db_context["topics"].append(t.name)
                            if t.learning_outcome:
                                db_context["learning_outcomes"].append(t.learning_outcome)

        # 3. Retrieve historical questions for this unit/topic to avoid repetition
        historical_samples = []
        if db and unit_number:
            hist_qs = db.query(Question).filter(
                Question.course_id == course_id,
                Question.is_historical == True
            ).limit(6).all()
            historical_samples = [q.text for q in hist_qs]

        return {
            "query": query,
            "syllabus_hits": syllabus_hits,
            "structured_context": db_context,
            "historical_benchmarks": historical_samples
        }

    def construct_grounded_prompt(
        self,
        course_name: str,
        unit_number: int,
        unit_title: str,
        topic_name: str,
        target_bloom: str,
        target_difficulty: str,
        marks: int,
        historical_questions: List[str]
    ) -> str:
        """
        Constructs an academic engineering prompt strictly constrained to
        syllabus boundaries and Bloom's Taxonomy directives.
        """
        history_str = "\n".join([f"- {h}" for h in historical_questions[:3]]) if historical_questions else "None recorded."
        
        prompt = f"""
You are an expert Academic Question Paper Setter adhering to Bloom's Revised Taxonomy.
Create an examination question strictly within the following constraints:

ACADEMIC CONSTRAINTS:
- Course: {course_name}
- Unit {unit_number}: {unit_title}
- Target Topic: {topic_name}
- Target Bloom's Cognitive Level: {target_bloom}
- Target Difficulty: {target_difficulty}
- Allocated Marks: {marks} Marks

NOVELTY SAFEGUARDS (Do NOT repeat or closely paraphrase these previous questions):
{history_str}

OUTPUT FORMAT:
Generate the question text clearly and professionally.
Include expected solution outline and marking scheme allocation.
"""
        return prompt.strip()

rag_engine = RAGEngine()
