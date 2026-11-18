from sqlalchemy.orm import Session
from app.models.course import Course, Unit, Topic
from app.models.question import Question
from app.models.template import ExamTemplate
from app.models.paper import ExamPaper, PaperSection, PaperQuestion
from app.models.validation import ValidationAudit
from app.services.module2_knowledge_base import knowledge_base_service

def ensure_data_structures_demo(db: Session):
    """Seeds a complete Data Structures subject only when it is missing."""
    if db.query(Course).filter(Course.code == "CS3002").first():
        return

    course = Course(
        code="CS3002",
        title="Data Structures",
        department="Computer Science & Engineering",
        institution="Vishwakarma Institute of Technology",
        semester="Semester II",
        academic_year="2025-2026",
    )
    db.add(course)
    db.flush()

    units_data = [
        ("Array and Linked List Fundamentals", "Arrays, pointers, singly linked lists, doubly linked lists, and circular linked lists."),
        ("Stacks and Queues", "Stack and queue ADTs, infix conversion, expression evaluation, and deque operations."),
        ("Trees and Binary Search Trees", "Tree terminology, traversal algorithms, BST operations, and height-balanced trees."),
        ("Graphs and Traversals", "Graph representations, breadth-first search, depth-first search, shortest paths, and spanning trees."),
        ("Hashing and Searching", "Hash functions, collision resolution, linear probing, chaining, and searching complexity."),
        ("Sorting and Algorithm Analysis", "Selection, insertion, merge, quick sort, asymptotic analysis, and algorithm trade-offs."),
    ]

    unit_records = []
    topic_records = []
    for unit_number, (title, description) in enumerate(units_data, start=1):
        unit = Unit(
            course_id=course.id,
            unit_number=unit_number,
            title=title,
            description=description,
            target_weightage_pct=16.67,
        )
        db.add(unit)
        db.flush()
        unit_records.append(unit)

        topic_name = title
        topic = Topic(
            unit_id=unit.id,
            name=topic_name,
            keywords=description.lower(),
            learning_outcome=f"Apply concepts of {title.lower()} to solve computational problems.",
        )
        db.add(topic)
        db.flush()
        topic_records.append(topic)
        knowledge_base_service.sync_syllabus_chunk_to_vector_store(unit, topic)

    questions_data = [
        ("List the advantages of linked lists over arrays.", 1, "L1", "list", "Easy", 0.22, 2),
        ("Explain the difference between an array and a linked list.", 1, "L2", "explain", "Easy", 0.38, 5),
        ("Apply insertion and deletion operations to a doubly linked list.", 1, "L3", "apply", "Medium", 0.58, 6),
        ("Compare singly, doubly, and circular linked lists for insertion at the middle.", 1, "L4", "compare", "Medium", 0.68, 8),
        ("Define stack overflow and stack underflow.", 2, "L1", "define", "Easy", 0.20, 2),
        ("Convert the infix expression (A+B)*C-D/F+C into postfix notation.", 2, "L3", "convert", "Medium", 0.60, 6),
        ("Analyze the conditions in which a queue should be preferred over a stack.", 2, "L4", "analyze", "Medium", 0.70, 8),
        ("Design a circular queue supporting enqueue and dequeue operations.", 2, "L6", "design", "Hard", 0.90, 10),
        ("State the properties of a binary search tree.", 3, "L1", "state", "Easy", 0.24, 2),
        ("Explain inorder, preorder, and postorder traversal with examples.", 3, "L2", "explain", "Medium", 0.48, 5),
        ("Construct a binary search tree for 45, 20, 60, 10, 30, 50, 70.", 3, "L3", "construct", "Medium", 0.62, 8),
        ("Critically evaluate the trade-offs between AVL and red-black trees.", 3, "L5", "evaluate", "Hard", 0.86, 10),
        ("Describe the adjacency matrix and adjacency list representations.", 4, "L2", "describe", "Easy", 0.42, 5),
        ("Apply breadth-first search to the given directed graph.", 4, "L3", "apply", "Medium", 0.64, 8),
        ("Compare BFS and DFS with respect to queue/stack usage and shortest-path guarantees.", 4, "L4", "compare", "Medium", 0.72, 8),
        ("Design a graph algorithm for finding the shortest route under negative cycle constraints.", 4, "L6", "design", "Hard", 0.92, 12),
        ("List common collision resolution techniques in hashing.", 5, "L1", "list", "Easy", 0.23, 2),
        ("Explain linear probing and separate chaining.", 5, "L2", "explain", "Medium", 0.44, 5),
        ("Calculate average search probes for the provided hash table.", 5, "L3", "calculate", "Medium", 0.60, 6),
        ("Evaluate the impact of load factor on hashing performance.", 5, "L5", "evaluate", "Hard", 0.84, 10),
        ("State the time complexity of insertion sort.", 6, "L1", "state", "Easy", 0.20, 2),
        ("Compare selection sort and bubble sort step by step.", 6, "L4", "compare", "Medium", 0.70, 8),
        ("Justify why merge sort is preferred to quick sort for externally stored data.", 6, "L5", "justify", "Hard", 0.85, 10),
        ("Design a hybrid sorting algorithm optimized for nearly sorted large datasets.", 6, "L6", "design", "Hard", 0.94, 12),
    ]

    for text, unit_index, bloom, verb, difficulty, score, marks in questions_data:
        unit = unit_records[unit_index - 1]
        topic = topic_records[unit_index - 1]
        question = Question(
            course_id=course.id,
            unit_id=unit.id,
            topic_id=topic.id,
            text=text,
            question_type="Descriptive",
            marks=marks,
            bloom_level=bloom,
            primary_verb=verb,
            difficulty=difficulty,
            difficulty_score=score,
            is_historical=False,
        )
        db.add(question)
        db.flush()
        knowledge_base_service.sync_question_to_vector_store(question)

    db.commit()

def seed_initial_data(db: Session):
    # Preserve existing databases while ensuring complete demo subjects are present.
    ai_course = db.query(Course).filter(Course.code == "CS3001").first()
    if ai_course:
        ensure_data_structures_demo(db)
        return

    print("[COGNITO] Seeding realistic academic fixtures for Vishwakarma Institute of Technology...")

    # 1. Create Core AI Course
    ai_course = Course(
        code="CS3001",
        title="Artificial Intelligence",
        department="Computer Science & Engineering",
        institution="Vishwakarma Institute of Technology",
        semester="Semester VI",
        academic_year="2025-2026"
    )
    db.add(ai_course)
    db.flush()

    # 2. Units & Topics
    units_data = [
        {
            "unit_number": 1,
            "title": "Introduction to AI & Intelligent Agents",
            "description": "Foundations of AI, agent architectures, PEAS specification, and environment classifications.",
            "topics": [
                ("PEAS Model for Autonomous Agents", "peas, performance measure, environment, sensors, actuators", "Formulate PEAS descriptions for diverse agent tasks."),
                ("Rational Agent Architectures", "rationality, reflex agent, goal-based agent, utility-based", "Classify agent types based on behavioral complexity.")
            ]
        },
        {
            "unit_number": 2,
            "title": "Problem Solving & Heuristic Search",
            "description": "Uninformed search, heuristic evaluation, A* search, and game playing with Alpha-Beta pruning.",
            "topics": [
                ("A* Algorithm & Admissibility", "a* search, heuristic function, admissibility, consistency, optimality", "Apply A* search with admissible heuristics to route-finding problems."),
                ("Adversarial Search & Alpha-Beta Pruning", "minimax, alpha-beta, game trees, branching factor", "Analyze state spaces and prune non-promising branches in two-player games.")
            ]
        },
        {
            "unit_number": 3,
            "title": "Knowledge Representation & Logical Reasoning",
            "description": "Propositional logic, first-order predicate calculus, resolution refutation, and ontologies.",
            "topics": [
                ("First-Order Logic & Resolution", "fol, predicate calculus, unification, resolution refutation, cnf", "Execute resolution refutation proofs in first-order logic."),
                ("Forward & Backward Chaining", "inference engine, horn clauses, rule-based systems", "Differentiate inference mechanisms in expert systems.")
            ]
        },
        {
            "unit_number": 4,
            "title": "Probabilistic Reasoning & Uncertainty",
            "description": "Bayesian networks, conditional independence, Markov models, and exact inference.",
            "topics": [
                ("Bayesian Belief Networks", "bayes rule, conditional probability tables, d-separation, inference", "Compute posterior probabilities given observed diagnostic evidence."),
                ("Markov Decision Processes (MDP)", "bellman equation, value iteration, policy iteration, discount factor", "Formulate sequential decision-making tasks under uncertainty.")
            ]
        },
        {
            "unit_number": 5,
            "title": "Machine Learning Foundations & Neural Networks",
            "description": "Supervised learning algorithms, perceptrons, multi-layer networks, backpropagation.",
            "topics": [
                ("Backpropagation & Gradient Descent", "loss function, chain rule, learning rate, weight update", "Derive gradient descent weight update equations for multi-layer perceptrons."),
                ("Regularization & Generalization", "overfitting, l1 l2 regularization, dropout, cross-validation", "Critique model generalization techniques to prevent overfitting.")
            ]
        },
        {
            "unit_number": 6,
            "title": "Natural Language Processing & Advanced Architectures",
            "description": "Text vectorization, sequence models, self-attention mechanisms, and transformer architectures.",
            "topics": [
                ("Self-Attention & Transformer Architecture", "transformer, multi-head attention, positional encoding, qkv matrices", "Design attention-based neural architectures for sequence transduction."),
                ("AI Ethics & Explainability (XAI)", "bias, fairness, accountability, interpretability, lime, shap", "Evaluate fairness metrics and algorithmic transparency in high-stakes automated decisions.")
            ]
        }
    ]

    unit_records = []
    topic_records = []
    for u_idx, u_info in enumerate(units_data, start=1):
        u = Unit(
            course_id=ai_course.id,
            unit_number=u_info["unit_number"],
            title=u_info["title"],
            description=u_info["description"],
            target_weightage_pct=16.67
        )
        db.add(u)
        db.flush()
        unit_records.append(u)

        for t_name, t_kw, t_lo in u_info["topics"]:
            top = Topic(
                unit_id=u.id,
                name=t_name,
                keywords=t_kw,
                learning_outcome=t_lo
            )
            db.add(top)
            db.flush()
            topic_records.append(top)
            knowledge_base_service.sync_syllabus_chunk_to_vector_store(u, top)

    # 3. Comprehensive Question Bank covering L1 to L6
    questions_data = [
        # Unit 1
        ("Define an intelligent agent and state the four parameters of the PEAS specification.", 1, 0, "L1", "define", "Easy", 0.18, 2, True, 2023),
        ("Explain the fundamental differences between a Goal-Based Agent and a Utility-Based Agent with illustrative state transition diagrams.", 1, 1, "L2", "explain", "Easy", 0.35, 5, False, None),
        ("Analyze a fully autonomous vacuum cleaner agent operating in a partially observable, stochastic environment and propose its complete PEAS matrix.", 1, 0, "L4", "analyze", "Medium", 0.65, 8, False, None),
        
        # Unit 2
        ("State the admissibility criterion for a heuristic function in the A* search algorithm.", 2, 2, "L1", "state", "Easy", 0.15, 2, True, 2024),
        ("Describe the working of the Minimax algorithm and the role of the evaluation function in games with deep search trees.", 2, 3, "L2", "describe", "Easy", 0.38, 5, True, 2023),
        ("Apply the A* search algorithm to compute the shortest path on a given 8-node weighted graph where straight-line distance heuristic values are provided.", 2, 2, "L3", "apply", "Medium", 0.55, 6, False, None),
        ("Trace and demonstrate the Alpha-Beta pruning procedure on a 4-ply game tree with branching factor 2, showing exact alpha and beta cutoffs.", 2, 3, "L3", "demonstrate", "Medium", 0.60, 8, False, None),
        ("Compare and contrast Uniform Cost Search with A* search with respect to time complexity, space complexity, and optimal completeness.", 2, 2, "L4", "compare", "Medium", 0.68, 6, True, 2024),
        ("Design an admissible and consistent heuristic function for the 15-Puzzle problem that dominates the Manhattan Distance heuristic.", 2, 2, "L6", "design", "Hard", 0.88, 10, False, None),

        # Unit 3
        ("Define Horn clauses and state their significance in computational logic inference.", 3, 4, "L1", "define", "Easy", 0.22, 2, True, 2023),
        ("Explain the Unification algorithm used in First-Order Logic inference with a step-by-step example.", 3, 4, "L2", "explain", "Medium", 0.45, 5, False, None),
        ("Execute a Resolution Refutation proof to establish whether 'Marcus is dead' given a formal knowledge base of first-order predicate logic assertions.", 3, 4, "L3", "execute", "Medium", 0.58, 6, False, None),
        ("Differentiate between Forward Chaining and Backward Chaining, specifying their suitability for data-driven versus goal-driven diagnostic systems.", 3, 5, "L4", "differentiate", "Medium", 0.64, 6, True, 2024),
        ("Critique the expressiveness and inferential trade-offs of Propositional Logic versus Description Logics for large-scale enterprise ontologies.", 3, 4, "L5", "critique", "Hard", 0.82, 8, False, None),

        # Unit 4
        ("State Bayes' Theorem and write the expansion for conditional probability with three joint random variables.", 4, 6, "L1", "state", "Easy", 0.20, 2, True, 2023),
        ("Discuss the concept of conditional independence and d-separation in Directed Acyclic Graphical models.", 4, 6, "L2", "discuss", "Medium", 0.42, 5, False, None),
        ("Given a Bayesian Belief Network with nodes Alarm, Burglary, Earthquake, JohnCalls, compute the posterior probability P(Burglary | JohnCalls=True).", 4, 6, "L3", "compute", "Medium", 0.62, 8, False, None),
        ("Analyze a Markov Decision Process with 3 states and 2 actions using the Bellman Optimality Equation to determine the value iteration updates after 2 epochs.", 4, 7, "L4", "analyze", "Hard", 0.74, 8, False, None),
        ("Justify why exact probabilistic inference in polytrees is polynomial-time while general Bayesian network inference is NP-hard.", 4, 6, "L5", "justify", "Hard", 0.84, 8, False, None),

        # Unit 5
        ("Define Overfitting and list two primary regularization techniques used to mitigate it.", 5, 9, "L1", "define", "Easy", 0.22, 2, True, 2024),
        ("Explain the forward pass and backward error propagation steps in a multi-layer feedforward neural network with sigmoid activation.", 5, 8, "L2", "explain", "Medium", 0.48, 6, False, None),
        ("Calculate the updated synaptic weights after one epoch of backpropagation for a single hidden unit given target output y=1 and learning rate 0.1.", 5, 8, "L3", "calculate", "Medium", 0.65, 8, False, None),
        ("Compare L1 (Lasso) and L2 (Ridge) regularization mathematically and deconstruct why L1 leads to sparse parameter representations.", 5, 9, "L4", "compare", "Hard", 0.76, 8, False, None),
        ("Evaluate the performance vulnerabilities of Deep Neural Networks under Fast Gradient Sign Method (FGSM) adversarial perturbations.", 5, 8, "L5", "evaluate", "Hard", 0.86, 10, False, None),

        # Unit 6
        ("List the three primary projection matrices (Query, Key, Value) in the Scaled Dot-Product Attention mechanism.", 6, 10, "L1", "list", "Easy", 0.25, 2, False, None),
        ("Describe the architecture and positional encoding formula used in the original Transformer model.", 6, 10, "L2", "describe", "Medium", 0.46, 5, False, None),
        ("Deconstruct the self-attention computational complexity O(n^2) and analyze why standard Transformers struggle with ultra-long sequence lengths.", 6, 10, "L4", "deconstruct", "Hard", 0.78, 8, False, None),
        ("Critically appraise the ethical and socio-technical implications of deploying automated recidivism scoring algorithms with demographic parity disparities.", 6, 11, "L5", "appraise", "Hard", 0.88, 10, False, None),
        ("Design an end-to-end Retrieval-Augmented Generation (RAG) architecture with semantic reranking and hallucination guardrails for healthcare query answering.", 6, 10, "L6", "design", "Hard", 0.94, 12, False, None)
    ]

    for q_text, u_num, t_idx, b_lvl, p_verb, diff, d_score, marks, is_hist, year in questions_data:
        target_unit = unit_records[u_num - 1]
        target_topic = topic_records[t_idx] if t_idx < len(topic_records) else None

        q = Question(
            course_id=ai_course.id,
            unit_id=target_unit.id,
            topic_id=target_topic.id if target_topic else None,
            text=q_text,
            question_type="Descriptive",
            marks=marks,
            bloom_level=b_lvl,
            primary_verb=p_verb,
            difficulty=diff,
            difficulty_score=d_score,
            is_historical=is_hist,
            exam_year=year,
            solution_outline=f"Exemplar grading scheme and key bullet points for {b_lvl} question on {target_unit.title}."
        )
        db.add(q)
        db.flush()
        knowledge_base_service.sync_question_to_vector_store(q)

    # 4. Standard Institutional Templates
    end_sem_tpl = ExamTemplate(
        name="End-Semester Examination (100 Marks)",
        description="Standard VIT Autonomous End-Semester Examination blueprint with 3 sections.",
        total_marks=100,
        duration_minutes=180,
        instructions="Answer all questions. Figures to the right indicate full marks.",
        sections_config=[
            {"section_name": "Section A: Conceptual Foundations", "marks": 20, "instructions": "Short answer questions testing L1 and L2."},
            {"section_name": "Section B: Analytical Application", "marks": 40, "instructions": "Analytical problems testing L3 and L4."},
            {"section_name": "Section C: Advanced Synthesis & Design", "marks": 40, "instructions": "Complex engineering design tasks testing L4, L5, and L6."}
        ],
        bloom_targets={"L1": 10.0, "L2": 20.0, "L3": 30.0, "L4": 25.0, "L5": 10.0, "L6": 5.0},
        difficulty_targets={"Easy": 30.0, "Medium": 50.0, "Hard": 20.0}
    )
    db.add(end_sem_tpl)

    in_sem_tpl = ExamTemplate(
        name="In-Semester Assessment (50 Marks)",
        description="Mid-term assessment evaluating Units 1 through 3.",
        total_marks=50,
        duration_minutes=120,
        instructions="Answer all questions. Internal choices where indicated.",
        sections_config=[
            {"section_name": "Section A: Core Definitions", "marks": 10, "instructions": "Answer all questions."},
            {"section_name": "Section B: Procedural Application", "marks": 20, "instructions": "Solve all algorithmic problems."},
            {"section_name": "Section C: Critical Analysis", "marks": 20, "instructions": "Analytical synthesis."}
        ],
        bloom_targets={"L1": 10.0, "L2": 20.0, "L3": 35.0, "L4": 25.0, "L5": 10.0, "L6": 0.0},
        difficulty_targets={"Easy": 30.0, "Medium": 50.0, "Hard": 20.0}
    )
    db.add(in_sem_tpl)
    db.flush()

    # 5. Seed a Pre-Generated Validated Paper
    paper = ExamPaper(
        course_id=ai_course.id,
        template_id=in_sem_tpl.id,
        title="In-Semester Assessment Examination - Artificial Intelligence",
        academic_year="2025-2026",
        semester="Semester VI",
        total_marks=50,
        status="APPROVED",
        cas_score=0.92,
        meta_info={
            "bloom_targets": in_sem_tpl.bloom_targets,
            "difficulty_targets": in_sem_tpl.difficulty_targets
        }
    )
    db.add(paper)
    db.flush()

    # Create sections
    sec1 = PaperSection(paper_id=paper.id, section_name="Section A: Core Definitions & Recall", instructions="Answer all questions.", total_marks=10, order_index=1)
    sec2 = PaperSection(paper_id=paper.id, section_name="Section B: Procedural Application & Algorithms", instructions="Answer all questions.", total_marks=20, order_index=2)
    sec3 = PaperSection(paper_id=paper.id, section_name="Section C: Analytical Problem Solving & Evaluation", instructions="Answer all questions.", total_marks=20, order_index=3)
    db.add_all([sec1, sec2, sec3])
    db.flush()

    # Fetch some questions to map
    qs = db.query(Question).filter(Question.course_id == ai_course.id).all()
    # Sec 1 (10M): 2M + 2M + 6M (or 5M + 5M)
    pq1 = PaperQuestion(section_id=sec1.id, question_id=qs[0].id, sub_question_label="Q1.1", order_index=1, marks=2)
    pq2 = PaperQuestion(section_id=sec1.id, question_id=qs[3].id, sub_question_label="Q1.2", order_index=2, marks=2)
    pq3 = PaperQuestion(section_id=sec1.id, question_id=qs[1].id, sub_question_label="Q1.3", order_index=3, marks=6)
    
    # Sec 2 (20M): 6M + 6M + 8M
    pq4 = PaperQuestion(section_id=sec2.id, question_id=qs[5].id, sub_question_label="Q2.1", order_index=1, marks=6)
    pq5 = PaperQuestion(section_id=sec2.id, question_id=qs[11].id, sub_question_label="Q2.2", order_index=2, marks=6)
    pq6 = PaperQuestion(section_id=sec2.id, question_id=qs[6].id, sub_question_label="Q2.3", order_index=3, marks=8)

    # Sec 3 (20M): 10M + 10M
    pq7 = PaperQuestion(section_id=sec3.id, question_id=qs[8].id, sub_question_label="Q3.1", order_index=1, marks=10)
    pq8 = PaperQuestion(section_id=sec3.id, question_id=qs[25].id, sub_question_label="Q3.2", order_index=2, marks=10)

    db.add_all([pq1, pq2, pq3, pq4, pq5, pq6, pq7, pq8])
    db.flush()

    # Audit for seeded paper
    audit = ValidationAudit(
        paper_id=paper.id,
        cas_score=0.92,
        syllabus_coverage=0.94,
        bloom_compliance=0.90,
        difficulty_compliance=0.92,
        marks_compliance=1.00,
        repetition_score=0.95,
        template_compliance=0.98,
        status="PASSED",
        violations=[],
        recommendations=["Excellent balance across lower and higher order cognitive levels."]
    )
    db.add(audit)
    db.commit()

    ensure_data_structures_demo(db)

    print("[COGNITO] Successfully seeded Course, 6 Units, 12 Topics, 28 Questions, 2 Templates, and 1 Validated Exam Paper!")
