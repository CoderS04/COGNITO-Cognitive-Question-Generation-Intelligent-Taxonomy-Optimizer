from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.core.vector_store import vector_store
from app.models.question import Question

class SimilarityEngine:
    """
    Module 4: Semantic Similarity & Repetition Detection Engine
    Identifies repeated, paraphrased, or semantically redundant questions
    by calculating cosine similarity against historical exam records.
    """

    def __init__(self, repetition_threshold: float = settings.REPETITION_THRESHOLD,
                 paraphrase_threshold: float = settings.PARAPHRASE_THRESHOLD):
        self.repetition_threshold = repetition_threshold
        self.paraphrase_threshold = paraphrase_threshold

    def check_question_repetition(
        self,
        query_text: str,
        db: Session,
        course_id: Optional[int] = None,
        exclude_question_id: Optional[int] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Checks an arbitrary question against existing historical questions.
        Returns match list, max similarity, and boolean flags.
        """
        # 1. Search top matches from vector store
        vector_matches = vector_store.search_similar_questions(
            query=query_text,
            n_results=top_k * 2
        )

        # 2. Filter and enrich with database details
        matches = []
        max_similarity = 0.0

        # Also compare against database questions directly if vector store returned few results
        q_query = db.query(Question)
        if course_id:
            q_query = q_query.filter(Question.course_id == course_id)
        if exclude_question_id:
            q_query = q_query.filter(Question.id != exclude_question_id)
        candidate_db_questions = q_query.all()

        for cand in candidate_db_questions:
            sim = vector_store.cosine_similarity(query_text, cand.text)
            if sim > max_similarity:
                max_similarity = sim
            if sim >= self.paraphrase_threshold:
                matches.append({
                    "question_id": cand.id,
                    "text": cand.text,
                    "similarity": round(float(sim), 4),
                    "bloom_level": cand.bloom_level,
                    "difficulty": cand.difficulty,
                    "exam_year": cand.exam_year,
                    "is_historical": cand.is_historical
                })

        matches.sort(key=lambda x: x["similarity"], reverse=True)
        top_matches = matches[:top_k]

        is_repetition = max_similarity >= self.repetition_threshold
        is_paraphrase = (not is_repetition) and (max_similarity >= self.paraphrase_threshold)

        return {
            "query_text": query_text,
            "is_repetition": is_repetition,
            "is_paraphrase": is_paraphrase,
            "max_similarity": round(float(max_similarity), 4),
            "matches": top_matches
        }

    def compute_novelty_score(self, question_text: str, historical_questions: List[str]) -> float:
        """
        Computes novelty score N in [0.0, 1.0]:
        N = 1.0 - max(similarity(question, h) for h in historical_questions)
        """
        if not historical_questions:
            return 1.0
        
        max_sim = 0.0
        for h in historical_questions:
            sim = vector_store.cosine_similarity(question_text, h)
            if sim > max_sim:
                max_sim = sim
                
        novelty = max(0.0, 1.0 - max_sim)
        return round(float(novelty), 4)

similarity_engine = SimilarityEngine()
