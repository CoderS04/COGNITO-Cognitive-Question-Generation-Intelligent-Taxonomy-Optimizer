# COGNITO: Cognitive Question Generation & Intelligent Taxonomy Optimizer
## System Architecture & Technical Specifications

```
                              +------------------------------------------------------+
                              |               COGNITO Web Frontend                   |
                              |        (React 18, Tailwind CSS, Lucide, Recharts)     |
                              +--------------------------+---------------------------+
                                                         | REST / JSON
                                                         v
+----------------------------------------------------------------------------------------------------+
|                                    COGNITO FastAPI Backend Service                                 |
|                                                                                                    |
|  [Module 1: Document Processing]  ----->  [Module 2: Knowledge Base]  ----->  [Module 3: AI Analysis]|
|  - PyMuPDF / pdfplumber parser             - PostgreSQL Relational DB          - Hybrid Bloom's L1-L6  |
|  - DOCX XML chunker                        - ChromaDB Vector Store             - Action Verb Anchor    |
|  - Noise & header/footer strip             - Course / Unit Metadata            - Semantic Profiler     |
|                                                                                                    |
|  [Module 4: Similarity Engine]    ----->  [Module 5: Difficulty Estimator] -> [Module 6: RAG Engine] |
|  - Cosine embedding distance               - Multi-factor F_diff scoring       - Context Retriever     |
|  - Paraphrase & repetition flag            - Cognitive + syntactic depth       - Syllabus/Rules Inject |
|                                                                                                    |
|  [Module 7: Optimizer & Generator] ---->  [Module 8: Validation Engine]   --> [Module 9: Reporting]   |
|  - Score(Q) candidate ranking              - Comprehensive CAS scoring         - PDF & DOCX export     |
|  - Constraint Satisfaction Solver          - Closed-loop auto-refinement       - Interactive Analytics |
+----------------------------------------------------------------------------------------------------+
```

---

## 1. Architectural Layers

### 1.1 Ingestion & Document Processing (Module 1)
- **Input Channels**: PDF syllabus files, historical examination DOCX files, institutional rubric PDFs, raw text prompts.
- **Normalization Engine**:
  - Regular expression parser identifying Question numbering (`Q1.`, `1(a)`, `Question 2:`).
  - Sub-question and marks extractor (`[5 Marks]`, `(10M)`).
  - Header/footer filter stripping institutional watermarks, dates, and administrative disclaimers.

### 1.2 Knowledge Base & Vector Representation (Module 2)
- **Relational Storage**: PostgreSQL (with automatic SQLite fallback for lightweight development) storing:
  - Courses, Units, and Syllabus Topics.
  - Historical Question Bank with validated metadata.
  - Examination Templates (e.g., In-Semester Assessment 30M, End-Semester 100M).
  - Assessment Policy Rules and validation audit trails.
- **Vector Storage**: ChromaDB / Local Semantic Embedding Vector Store:
  - Persistent embeddings for high-speed similarity search, repetition detection, and RAG retrieval.

### 1.3 AI Question Analysis & Bloom's Taxonomy Classifier (Module 3)
A hybrid pipeline combining rule-based linguistic feature matching with contextual embedding classification:
1. **Verb Anchor Matching**: Detects Bloom's verbs across L1 (Remember) through L6 (Create).
2. **Contextual Complexity Weights**: Examines presence of mathematical formulations, scenario conditions, and comparative directives.
3. **Cognitive Profile Generation**: Outputs a structured profile `(L1..L6, confidence, primary_verb, cognitive_target)`.

### 1.4 Semantic Similarity & Repetition Detection (Module 4)
- Questions are vectorized into semantic space $\mathbf{v}_q$.
- Given historical questions $\{\mathbf{v}_h\}$, cosine similarity is calculated:
  $$\text{Sim}(q_1, q_2) = \frac{\mathbf{v}_{q_1} \cdot \mathbf{v}_{q_2}}{\|\mathbf{v}_{q_1}\| \|\mathbf{v}_{q_2}\|}$$
- **Thresholds**:
  - $\text{Sim} \ge 0.85$: Flagged as **Direct Repetition** (Violates institutional novelty).
  - $0.70 \le \text{Sim} < 0.85$: Flagged as **Paraphrased / Near-Duplicate**.
  - $\text{Sim} < 0.70$: Classified as **Novel Question**.

### 1.5 Multi-Factor Difficulty Estimation (Module 5)
Estimates difficulty category $\in \{\text{Easy}, \text{Medium}, \text{Hard}\}$ and numerical score $D \in [0.0, 1.0]$:
$$D = w_b \cdot L_{\text{bloom}} + w_l \cdot L_{\text{ling}} + w_s \cdot S_{\text{steps}} + w_c \cdot C_{\text{concept}}$$
- $L_{\text{bloom}}$: Normalized Bloom's level ($L_1=0.16 \dots L_6=1.00$).
- $L_{\text{ling}}$: Lexical complexity (sentence length, technical term density).
- $S_{\text{steps}}$: Required solution depth / multi-part structure.
- $C_{\text{concept}}$: Topic abstraction level.

### 1.6 Retrieval-Augmented Generation (RAG) (Module 6)
- Retrieves matching syllabus topics, associated Learning Outcomes (CLOs/PLOs), and institutional guidelines.
- Grounded prompts guarantee questions do not hallucinate out-of-syllabus concepts.

### 1.7 Question Paper Generation & Constraint Optimization (Module 7)
Given target examination specification:
- Total Marks $M_{\text{target}}$
- Unit Distribution Targets $U_i$
- Bloom's Distribution Targets $\{P_{L1}, \dots, P_{L6}\}$
- Difficulty Distribution Targets $\{P_{\text{Easy}}, P_{\text{Med}}, P_{\text{Hard}}\}$

Each candidate question is scored:
$$\text{Score}(Q) = w_1 R + w_2 B + w_3 D + w_4 N + w_5 Q_a$$
Where:
- $R$: Syllabus Relevance
- $B$: Bloom's Target Alignment
- $D$: Difficulty Suitability
- $N$: Novelty Score ($1 - \max \text{Sim}$)
- $Q_a$: Quality & Clarity Score

A combinatorial optimization algorithm (Integer Linear Programming / Greedy Knapsack with Branch-and-Prune) selects the optimal question set satisfying total marks and structural constraints.

### 1.8 Independent Validation Engine (Module 8)
Computes the **Comprehensive Assessment Score (CAS)**:
$$\text{CAS} = w_s S + w_b B + w_d D + w_m M + w_n N + w_t T$$
- $S$: Syllabus Coverage ($\frac{\text{Topics Covered}}{\text{Required Topics}} \times 100$)
- $B$: Bloom's Distribution Compliance
- $D$: Difficulty Distribution Compliance
- $M$: Marks Scheme Verification ($1.00$ if exact match)
- $N$: Novelty & Non-Repetition Score
- $T$: Institutional Template Compliance

**Closed-Loop Refinement**: If $\text{CAS} < \tau_{\text{approval}}$ (e.g. 0.85), the engine identifies offending questions, triggers automated reframing or replacement from the candidate pool, and re-validates iteratively.

### 1.9 Visual Analytics & Publication Engine (Module 9)
- Export professional examination papers to PDF (standard academic layout with University header, marks allocation, instructions, and Bloom's tags).
- Export to Microsoft Word (.docx) and structured JSON.
- Generates interactive visual charts for faculty review:
  - Radar chart for Target vs Actual Bloom's Distribution
  - Difficulty Pie Chart
  - Unit-wise marks breakdown bar chart
  - Compliance checklist with actionable recommendations
