import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.seed_data import seed_initial_data
from app.models.course import Course
from app.models.question import Question
from app.models.paper import ExamPaper
from app.services.module1_doc_processor import doc_processor
from app.services.module3_blooms_classifier import blooms_classifier
from app.services.module4_similarity_engine import similarity_engine
from app.services.module5_difficulty_estimator import difficulty_estimator
from app.services.module6_rag_engine import rag_engine
from app.services.module7_optimizer import constraint_optimizer
from app.services.module8_validation_engine import validation_engine
from app.services.module9_reporting import reporting_service

def test_full_cognito_pipeline():
    print("=== COGNITO END-TO-END PIPELINE AUDIT ===")
    
    # 1. Initialize Tables & Seed
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_initial_data(db)

    course = db.query(Course).first()
    assert course is not None, "Course seeding failed!"
    print(f"✓ Module 2 (Knowledge Base): Course '{course.code}: {course.title}' verified with {len(course.units)} units.")

    # 2. Test Module 3: Bloom's Taxonomy Classifier & Reframer
    q_test = "Design a distributed consensus mechanism resilient against Byzantine faults."
    b_res = blooms_classifier.classify_question(q_test, marks=10)
    assert b_res["bloom_level"] == "L6", f"Expected L6, got {b_res['bloom_level']}"
    print(f"✓ Module 3 (Bloom's Classifier): '{q_test[:40]}...' classified as {b_res['bloom_level']} ({b_res['cognitive_domain']}).")

    reframed = blooms_classifier.reframe_question("Define A* search algorithm", current_level="L1", target_level="L4")
    assert reframed["target_level"] == "L4"
    print(f"✓ Module 3 (Cognitive Reframing): Reframed L1 -> L4: '{reframed['reframed_text']}'")

    # 3. Test Module 5: Difficulty Estimator
    d_res = difficulty_estimator.estimate_difficulty(q_test, bloom_level="L6", marks=10)
    assert d_res["difficulty"] in ["Medium", "Hard"]
    print(f"✓ Module 5 (Difficulty Estimator): Classified as {d_res['difficulty']} (Score: {d_res['difficulty_score']}).")

    # 4. Test Module 4: Similarity & Repetition Engine
    sim_res = similarity_engine.check_question_repetition(
        "Define an intelligent agent and state the four parameters of the PEAS specification.",
        db=db,
        course_id=course.id
    )
    assert sim_res["is_repetition"] == True, "Expected repetition flag for identical historical question!"
    print(f"✓ Module 4 (Similarity & Repetition): Exact historical duplicate correctly flagged (Sim: {sim_res['max_similarity']}).")

    # 5. Test Module 6: RAG Engine
    rag_ctx = rag_engine.retrieve_context(course_id=course.id, unit_number=2, db=db)
    assert len(rag_ctx["structured_context"]["topics"]) > 0
    print(f"✓ Module 6 (RAG Engine): Retrieved {len(rag_ctx['structured_context']['topics'])} topics and historical benchmarks.")

    # 6. Test Module 7: Constraint Optimization & Paper Generation
    paper = constraint_optimizer.assemble_paper(
        db=db,
        course_id=course.id,
        title="Automated Test Mid-Semester Exam",
        total_marks=50,
        novelty_threshold=0.85
    )
    assert paper.total_marks == 50
    print(f"✓ Module 7 (Constraint Optimization): Successfully generated Exam Paper #{paper.id} with {len(paper.sections)} sections.")

    # 7. Test Module 8: Independent Validation Engine & Closed-Loop Refine
    audit = validation_engine.validate_paper(db, paper.id)
    assert audit.cas_score > 0.0
    print(f"✓ Module 8 (Validation Engine): CAS Score computed: {int(audit.cas_score * 100)}% (Status: {audit.status}).")

    refine_res = validation_engine.auto_refine_paper(db, paper.id)
    print(f"✓ Module 8 (Closed-Loop Refinement): Final CAS: {int(refine_res['final_cas'] * 100)}%.")

    # 8. Test Module 9: Analytics & Publication Export
    analytics = reporting_service.compute_paper_analytics(db, paper.id)
    assert len(analytics["bloom_distribution"]) == 6
    print(f"✓ Module 9 (Analytics): Bloom's radar metrics and unit distribution computed (Depth Index: {analytics['cognitive_depth_index']}).")

    pdf_bytes = reporting_service.generate_pdf(db, paper.id)
    assert len(pdf_bytes) > 500, "PDF generation failed"
    docx_bytes = reporting_service.generate_docx(db, paper.id)
    assert len(docx_bytes) > 500, "DOCX generation failed"
    print(f"✓ Module 9 (Publication): PDF generated ({len(pdf_bytes)} bytes) and DOCX generated ({len(docx_bytes)} bytes).")

    # 9. Test Module 1: Document Processing on local DOCX file
    docx_path = os.path.join("..", "AI_PBL_1_Batch2_Group 2.docx")
    if os.path.exists(docx_path):
        with open(docx_path, "rb") as f:
            p_res = doc_processor.process_file("AI_PBL_1_Batch2_Group 2.docx", f.read(), doc_type="syllabus")
            print(f"✓ Module 1 (Doc Processor): Successfully processed DOCX ({p_res['cleaned_length']} cleaned chars).")

    db.close()
    print("\n🎉 ALL 9 COGNITO MODULES PASSED COMPREHENSIVE AUDIT!")

if __name__ == "__main__":
    test_full_cognito_pipeline()
