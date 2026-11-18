from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.course import Course, Unit, Topic
from app.models.question import Question
from app.core.vector_store import vector_store
from app.services.module3_blooms_classifier import blooms_classifier

class KnowledgeBaseService:
    """
    Module 2: Knowledge Base & Catalog Management
    Synchronizes structured academic models in SQL with high-dimensional embeddings
    in ChromaDB/vector store.
    """

    def sync_question_to_vector_store(self, question: Question):
        """Indexes an individual question into the vector database."""
        question.embedding_id = f"q_{question.id}"
        metadata = {
            "question_id": question.id,
            "course_id": question.course_id,
            "unit_id": question.unit_id or 0,
            "bloom_level": question.bloom_level,
            "difficulty": question.difficulty,
            "marks": question.marks,
            "is_historical": question.is_historical,
            "exam_year": question.exam_year or 0
        }
        vector_store.add_question(
            doc_id=f"q_{question.id}",
            text=question.text,
            metadata=metadata
        )

    def sync_syllabus_chunk_to_vector_store(self, unit: Unit, topic: Optional[Topic] = None):
        """Indexes syllabus topic or unit overview into vector database for RAG context."""
        doc_id = f"unit_{unit.id}" if not topic else f"topic_{topic.id}"
        text = f"Unit {unit.unit_number}: {unit.title}. "
        if topic:
            text += f"Topic: {topic.name}. Keywords: {topic.keywords or ''}. Learning Outcome: {topic.learning_outcome or ''}"
        elif unit.description:
            text += unit.description
            
        metadata = {
            "unit_id": unit.id,
            "unit_number": unit.unit_number,
            "unit_title": unit.title,
            "course_id": unit.course_id,
            "topic_id": topic.id if topic else 0,
            "topic_name": topic.name if topic else ""
        }
        vector_store.add_syllabus_chunk(
            doc_id=doc_id,
            text=text,
            metadata=metadata
        )

    def populate_all_vector_stores(self, db: Session):
        """Full re-index of all courses, units, and questions in the database."""
        # Index syllabus
        units = db.query(Unit).all()
        for u in units:
            self.sync_syllabus_chunk_to_vector_store(u)
            for t in u.topics:
                self.sync_syllabus_chunk_to_vector_store(u, t)
                
        # Index questions
        questions = db.query(Question).all()
        for q in questions:
            self.sync_question_to_vector_store(q)

knowledge_base_service = KnowledgeBaseService()
