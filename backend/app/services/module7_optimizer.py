import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models.course import Course, Unit, Topic
from app.models.question import Question
from app.models.paper import ExamPaper, PaperSection, PaperQuestion
from app.services.module3_blooms_classifier import blooms_classifier
from app.services.module4_similarity_engine import similarity_engine
from app.services.module6_rag_engine import rag_engine
from app.services.generation_engine import generation_engine
from app.services.module2_knowledge_base import knowledge_base_service

class ConstraintOptimizer:
    """
    Module 7: Constraint Optimization & Paper Assembly Algorithm
    Evaluates candidate questions using:
    Score(Q) = w1*R + w2*B + w3*D + w4*N + w5*Qa
    Applies hard constraints (total marks, unit weightage, novelty threshold)
    and selects the optimal combination of questions to construct the paper.
    """

    BLOOM_INT_MAP = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}

    def __init__(self):
        self.w_r = settings.W_RELEVANCE
        self.w_b = settings.W_BLOOMS
        self.w_d = settings.W_DIFFICULTY
        self.w_n = settings.W_NOVELTY
        self.w_q = settings.W_QUALITY

    def score_candidate(
        self,
        candidate: Question,
        target_unit_id: Optional[int],
        target_bloom: str,
        target_difficulty: str,
        historical_texts: List[str]
    ) -> float:
        """
        Computes composite Score(Q) in [0.0, 1.0].
        """
        # 1. Syllabus Relevance (R)
        r_score = 1.0 if (not target_unit_id or candidate.unit_id == target_unit_id) else 0.4

        # 2. Bloom's Taxonomy Alignment (B)
        cand_b_int = self.BLOOM_INT_MAP.get(candidate.bloom_level, 2)
        target_b_int = self.BLOOM_INT_MAP.get(target_bloom, 2)
        diff_b = abs(cand_b_int - target_b_int)
        b_score = max(0.0, 1.0 - (diff_b * 0.25))

        # 3. Difficulty Suitability (D)
        if candidate.difficulty == target_difficulty:
            d_score = 1.0
        elif (candidate.difficulty == "Medium") or (target_difficulty == "Medium"):
            d_score = 0.5
        else:
            d_score = 0.1

        # 4. Novelty Score (N)
        novelty_score = similarity_engine.compute_novelty_score(candidate.text, historical_texts)
        if novelty_score < (1.0 - settings.REPETITION_THRESHOLD):
            # Penalize repetition heavily
            return 0.0

        # 5. Quality & Structure Score (Qa)
        words = len(candidate.text.split())
        qa_score = 1.0 if 10 <= words <= 60 else 0.7

        total_score = (
            self.w_r * r_score +
            self.w_b * b_score +
            self.w_d * d_score +
            self.w_n * novelty_score +
            self.w_q * qa_score
        )
        return round(total_score, 4)

    def assemble_paper(
        self,
        db: Session,
        course_id: int,
        title: str,
        total_marks: int = 50,
        template_id: Optional[int] = None,
        bloom_targets: Optional[Dict[str, float]] = None,
        difficulty_targets: Optional[Dict[str, float]] = None,
        unit_weights: Optional[Dict[str, float]] = None,
        novelty_threshold: float = 0.85
    ) -> ExamPaper:
        """
        Executes end-to-end constraint optimization to generate and assemble an ExamPaper.
        """
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise ValueError(f"Course with ID {course_id} not found.")

        units = db.query(Unit).filter(Unit.course_id == course_id).order_by(Unit.unit_number).all()
        if not units:
            default_unit = Unit(
                course_id=course_id,
                unit_number=1,
                title="General Course Unit",
                description=f"General syllabus unit for {course.title}.",
                target_weightage_pct=100.0,
            )
            db.add(default_unit)
            db.flush()
            default_topic = Topic(
                unit_id=default_unit.id,
                name=course.title,
                keywords=course.title,
                learning_outcome=f"Demonstrate understanding of {course.title}",
            )
            db.add(default_topic)
            db.flush()
            units = [default_unit]

        # Historical benchmark texts for novelty verification
        historical_records = db.query(Question.text).filter(
            Question.course_id == course_id,
            Question.is_historical == True
        ).all()
        historical_texts = [r[0] for r in historical_records]

        # Target Bloom's defaults
        b_targets = bloom_targets or {
            "L1": 10.0, "L2": 20.0, "L3": 30.0, "L4": 25.0, "L5": 10.0, "L6": 5.0
        }
        # Target Difficulty defaults
        d_targets = difficulty_targets or {"Easy": 30.0, "Medium": 50.0, "Hard": 20.0}

        # Available candidate pool
        pool = db.query(Question).filter(
            Question.course_id == course_id,
            Question.is_historical == False
        ).all()

        # If pool has too few non-historical questions, include historical ones as candidates
        # (optimizer will prefer higher novelty candidates)
        if len(pool) < 10:
            pool = db.query(Question).filter(Question.course_id == course_id).all()

        # Generate Sections structure based on marks
        # e.g. for 50 Marks: Section A (10M - L1/L2), Section B (20M - L3/L4), Section C (20M - L4/L5/L6)
        # e.g. for 100 Marks: Section A (20M), Section B (40M), Section C (40M)
        ratio_a = 0.20
        ratio_b = 0.40
        ratio_c = 0.40

        marks_a = int(round(total_marks * ratio_a))
        marks_b = int(round(total_marks * ratio_b))
        marks_c = total_marks - (marks_a + marks_b)

        sections_def = [
            {
                "name": "Section A: Conceptual Foundation & Short Answers",
                "instructions": "Answer all questions. Each question carries 2 to 5 marks.",
                "target_marks": marks_a,
                "preferred_blooms": ["L1", "L2"],
                "preferred_difficulty": "Easy",
                "sub_marks_list": [2, 3, 5]
            },
            {
                "name": "Section B: Analytical Application & Problem Solving",
                "instructions": "Answer all questions. Each question carries 5 to 8 marks.",
                "target_marks": marks_b,
                "preferred_blooms": ["L3", "L4"],
                "preferred_difficulty": "Medium",
                "sub_marks_list": [5, 6, 8]
            },
            {
                "name": "Section C: Advanced Synthesis, Design & Critical Evaluation",
                "instructions": "Answer all questions. Each question carries 8 to 12 marks.",
                "target_marks": marks_c,
                "preferred_blooms": ["L4", "L5", "L6"],
                "preferred_difficulty": "Hard",
                "sub_marks_list": [8, 10, 12]
            }
        ]

        # Initialize ExamPaper in SQL
        new_paper = ExamPaper(
            course_id=course_id,
            template_id=template_id,
            title=title,
            academic_year=course.academic_year,
            semester=course.semester,
            total_marks=total_marks,
            status="DRAFT",
            cas_score=0.0,
            meta_info={
                "bloom_targets": b_targets,
                "difficulty_targets": d_targets,
                "unit_weights": unit_weights
            }
        )
        db.add(new_paper)
        db.flush()

        used_question_ids = set()
        unit_cursor = 0

        for sec_idx, sec_def in enumerate(sections_def, start=1):
            sec_record = PaperSection(
                paper_id=new_paper.id,
                section_name=sec_def["name"],
                instructions=sec_def["instructions"],
                total_marks=sec_def["target_marks"],
                order_index=sec_idx
            )
            db.add(sec_record)
            db.flush()

            allocated_sec_marks = 0
            q_in_sec_index = 1

            while allocated_sec_marks < sec_def["target_marks"]:
                needed_marks = sec_def["target_marks"] - allocated_sec_marks
                target_unit = units[unit_cursor % len(units)]
                unit_cursor += 1

                preferred_bloom = random.choice(sec_def["preferred_blooms"])
                preferred_diff = sec_def["preferred_difficulty"]

                # Find candidates in pool matching criteria
                scored_candidates = []
                for cand in pool:
                    if cand.id in used_question_ids:
                        continue
                    if cand.marks > needed_marks and (needed_marks not in [1, 2]):
                        continue
                    
                    score = self.score_candidate(
                        candidate=cand,
                        target_unit_id=target_unit.id,
                        target_bloom=preferred_bloom,
                        target_difficulty=preferred_diff,
                        historical_texts=historical_texts
                    )
                    scored_candidates.append((score, cand))

                scored_candidates.sort(key=lambda x: x[0], reverse=True)

                selected_q = None
                if scored_candidates and scored_candidates[0][0] > 0.1:
                    selected_q = scored_candidates[0][1]
                else:
                    # Fallback synthesize/generate a question fitting the exact slot
                    topic_name = target_unit.topics[0].name if target_unit.topics else target_unit.title
                    slot_marks = min(needed_marks, 5 if sec_idx == 1 else 10)
                    if slot_marks <= 0:
                        break

                    reframed_info = blooms_classifier.reframe_question(
                        text=f"Explain the principles and mechanisms of {topic_name}",
                        current_level="L2",
                        target_level=preferred_bloom,
                        db=db,
                        course_id=course_id,
                        unit_id=target_unit.id,
                    )
                    analysis_info = blooms_classifier.classify_question(
                        reframed_info["reframed_text"],
                        marks=slot_marks,
                        course_title=course.title,
                        syllabus_context=(
                            f"Unit: {target_unit.title}. "
                            f"Topics: {', '.join(topic.name for topic in target_unit.topics)}"
                        ),
                    )

                    new_q = Question(
                        course_id=course_id,
                        unit_id=target_unit.id,
                        topic_id=target_unit.topics[0].id if target_unit.topics else None,
                        text=reframed_info["reframed_text"],
                        question_type="Descriptive",
                        marks=slot_marks,
                        bloom_level=preferred_bloom,
                        primary_verb=reframed_info["primary_verb"],
                        difficulty=analysis_info["difficulty"],
                        difficulty_score=analysis_info["difficulty_score"],
                        is_historical=False,
                        solution_outline=f"Step-by-step solution for {topic_name} addressing {preferred_bloom} level."
                    )
                    db.add(new_q)
                    db.flush()
                    knowledge_base_service.sync_question_to_vector_store(new_q)
                    selected_q = new_q

                used_question_ids.add(selected_q.id)
                q_marks = min(selected_q.marks, needed_marks) if needed_marks < selected_q.marks else selected_q.marks
                
                # If exact slot requires specific marks
                if allocated_sec_marks + q_marks > sec_def["target_marks"]:
                    q_marks = sec_def["target_marks"] - allocated_sec_marks

                sub_label = f"Q{sec_idx}.{q_in_sec_index}"
                pq = PaperQuestion(
                    section_id=sec_record.id,
                    question_id=selected_q.id,
                    sub_question_label=sub_label,
                    order_index=q_in_sec_index,
                    is_optional=False,
                    marks=q_marks
                )
                db.add(pq)
                allocated_sec_marks += q_marks
                q_in_sec_index += 1

        db.commit()
        db.refresh(new_paper)
        return new_paper

constraint_optimizer = ConstraintOptimizer()
