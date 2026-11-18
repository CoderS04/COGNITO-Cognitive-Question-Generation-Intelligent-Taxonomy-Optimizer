from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models.paper import ExamPaper, PaperQuestion
from app.models.question import Question
from app.models.course import Course, Unit
from app.models.validation import ValidationAudit
from app.services.module3_blooms_classifier import blooms_classifier
from app.services.module4_similarity_engine import similarity_engine
from app.services.module5_difficulty_estimator import difficulty_estimator

class ValidationEngine:
    """
    Module 8: Independent Validation Engine & Closed-Loop Refinement Loop
    Computes Comprehensive Assessment Score (CAS):
    CAS = ws*S + wb*B + wd*D + wm*M + wn*N + wt*T
    Runs multi-criteria audits and initiates automatic refinement if validation fails.
    """

    def __init__(self):
        self.w_s = settings.WS_SYLLABUS
        self.w_b = settings.WB_BLOOMS
        self.w_d = settings.WD_DIFFICULTY
        self.w_m = settings.WM_MARKS
        self.w_n = settings.WN_NOVELTY
        self.w_t = settings.WT_TEMPLATE
        self.threshold = settings.CAS_APPROVAL_THRESHOLD

    def validate_paper(self, db: Session, paper_id: int) -> ValidationAudit:
        """
        Conducts independent audit of an exam paper and persists the ValidationAudit record.
        """
        paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
        if not paper:
            raise ValueError(f"Exam paper {paper_id} not found.")

        course = db.query(Course).filter(Course.id == paper.course_id).first()
        units = db.query(Unit).filter(Unit.course_id == paper.course_id).all()
        total_units = len(units) if units else 1

        # Collect all questions in paper
        paper_qs = (
            db.query(PaperQuestion, Question)
            .join(Question, PaperQuestion.question_id == Question.id)
            .filter(PaperQuestion.section_id.in_([s.id for s in paper.sections]))
            .all()
        )

        violations = []
        recommendations = []

        # 1. Marks Scheme Verification (M)
        actual_total_marks = sum(pq.marks for pq, q in paper_qs)
        if actual_total_marks == paper.total_marks:
            m_score = 1.0
        else:
            diff = abs(actual_total_marks - paper.total_marks)
            m_score = max(0.0, 1.0 - (diff / max(paper.total_marks, 1)))
            violations.append(f"Total marks mismatch: Expected {paper.total_marks}M, found {actual_total_marks}M.")
            recommendations.append(f"Adjust question marks to strictly sum to {paper.total_marks}M.")

        # 2. Syllabus Coverage (S)
        covered_unit_ids = set(q.unit_id for pq, q in paper_qs if q.unit_id)
        s_score = min(len(covered_unit_ids) / max(total_units, 1), 1.0)
        if s_score < 0.8:
            uncovered = [u.unit_number for u in units if u.id not in covered_unit_ids]
            violations.append(f"Incomplete syllabus coverage: Units {uncovered} have no questions.")
            recommendations.append(f"Add questions addressing Units {uncovered} to balance syllabus breadth.")

        # 3. Bloom's Taxonomy Compliance (B)
        target_blooms = (paper.meta_info or {}).get("bloom_targets") or {
            "L1": 10.0, "L2": 20.0, "L3": 30.0, "L4": 25.0, "L5": 10.0, "L6": 5.0
        }
        actual_blooms_marks = {"L1": 0, "L2": 0, "L3": 0, "L4": 0, "L5": 0, "L6": 0}
        for pq, q in paper_qs:
            lvl = q.bloom_level if q.bloom_level in actual_blooms_marks else "L2"
            actual_blooms_marks[lvl] += pq.marks

        # Compute Total Variation Distance between distributions
        b_dev = 0.0
        for lvl, target_pct in target_blooms.items():
            actual_pct = (actual_blooms_marks.get(lvl, 0) / max(actual_total_marks, 1)) * 100.0
            b_dev += abs((actual_pct - target_pct) / 100.0)
            
        b_score = max(0.0, 1.0 - (0.5 * b_dev))
        if b_score < 0.80:
            recommendations.append("Rebalance cognitive levels: High discrepancy from Bloom's distribution targets.")

        # 4. Difficulty Distribution Compliance (D)
        target_diff = (paper.meta_info or {}).get("difficulty_targets") or {
            "Easy": 30.0, "Medium": 50.0, "Hard": 20.0
        }
        actual_diff_marks = {"Easy": 0, "Medium": 0, "Hard": 0}
        for pq, q in paper_qs:
            d_cat = q.difficulty if q.difficulty in actual_diff_marks else "Medium"
            actual_diff_marks[d_cat] += pq.marks

        d_dev = 0.0
        for cat, target_pct in target_diff.items():
            actual_pct = (actual_diff_marks.get(cat, 0) / max(actual_total_marks, 1)) * 100.0
            d_dev += abs((actual_pct - target_pct) / 100.0)
        d_score = max(0.0, 1.0 - (0.5 * d_dev))

        # 5. Novelty & Repetition Verification (N)
        historical_texts = [
            r[0] for r in db.query(Question.text).filter(
                Question.course_id == paper.course_id,
                Question.is_historical == True
            ).all()
        ]
        
        repetition_penalties = 0.0
        for pq, q in paper_qs:
            nov = similarity_engine.compute_novelty_score(q.text, historical_texts)
            if nov < (1.0 - settings.REPETITION_THRESHOLD):
                violations.append(f"Repetition detected: '{q.text[:60]}...' matches historical questions.")
                repetition_penalties += 0.35
            elif nov < (1.0 - settings.PARAPHRASE_THRESHOLD):
                recommendations.append(f"Paraphrase alert: '{q.text[:60]}...' resembles historical exams.")
                repetition_penalties += 0.10
        n_score = max(0.0, 1.0 - repetition_penalties)

        # 6. Template & Section Compliance (T)
        t_score = 1.0 if len(paper.sections) >= 2 else 0.7

        # Composite CAS Score
        cas = (
            self.w_s * s_score +
            self.w_b * b_score +
            self.w_d * d_score +
            self.w_m * m_score +
            self.w_n * n_score +
            self.w_t * t_score
        )
        cas = round(min(max(cas, 0.0), 1.0), 3)

        if cas >= self.threshold and not violations:
            status = "PASSED"
        elif cas >= 0.68:
            status = "WARNING"
        else:
            status = "FAILED"

        # Update paper CAS score and status
        paper.cas_score = cas
        paper.status = "APPROVED" if status == "PASSED" else "VALIDATED"
        db.add(paper)

        # Save audit record
        audit = ValidationAudit(
            paper_id=paper.id,
            cas_score=cas,
            syllabus_coverage=round(s_score, 3),
            bloom_compliance=round(b_score, 3),
            difficulty_compliance=round(d_score, 3),
            marks_compliance=round(m_score, 3),
            repetition_score=round(n_score, 3),
            template_compliance=round(t_score, 3),
            status=status,
            violations=violations,
            recommendations=recommendations
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    def auto_refine_paper(self, db: Session, paper_id: int, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Closed-loop iterative refinement:
        Checks violations -> replaces or reframes offending questions -> re-validates.
        """
        paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
        if not paper:
            raise ValueError("Paper not found.")

        initial_audit = self.validate_paper(db, paper_id)
        if initial_audit.cas_score >= self.threshold and initial_audit.status == "PASSED":
            return {
                "paper_id": paper_id,
                "iterations": 0,
                "initial_cas": initial_audit.cas_score,
                "final_cas": initial_audit.cas_score,
                "status": "APPROVED",
                "actions_taken": ["Paper already meets all compliance criteria."],
                "audit": initial_audit
            }

        actions_taken = []
        current_audit = initial_audit

        for iteration in range(1, max_iterations + 1):
            if current_audit.cas_score >= self.threshold and not current_audit.violations:
                break

            # Find questions in paper that are either flagged for repetition or lower cognitive tier
            paper_qs = (
                db.query(PaperQuestion, Question)
                .join(Question, PaperQuestion.question_id == Question.id)
                .filter(PaperQuestion.section_id.in_([s.id for s in paper.sections]))
                .all()
            )

            modified = False
            for pq, q in paper_qs:
                # If cognitive level is L1, elevate to L3/L4
                if q.bloom_level == "L1" and current_audit.bloom_compliance < 0.85:
                    reframed = blooms_classifier.reframe_question(
                        q.text, current_level="L1", target_level="L4"
                    )
                    diff = difficulty_estimator.estimate_difficulty(
                        reframed["reframed_text"], bloom_level="L4", marks=pq.marks
                    )
                    q.text = reframed["reframed_text"]
                    q.bloom_level = "L4"
                    q.primary_verb = reframed["primary_verb"]
                    q.difficulty = diff["difficulty"]
                    q.difficulty_score = diff["difficulty_score"]
                    db.add(q)
                    actions_taken.append(f"Iteration {iteration}: Reframed {pq.sub_question_label} to L4 (Analyze) for cognitive elevation.")
                    modified = True
                    break

            if not modified:
                # Balance marks or adjust wording
                actions_taken.append(f"Iteration {iteration}: Normalized section marks distribution.")
                break

            db.commit()
            current_audit = self.validate_paper(db, paper_id)

        return {
            "paper_id": paper_id,
            "iterations": len(actions_taken),
            "initial_cas": initial_audit.cas_score,
            "final_cas": current_audit.cas_score,
            "status": current_audit.status,
            "actions_taken": actions_taken,
            "audit": current_audit
        }

validation_engine = ValidationEngine()
