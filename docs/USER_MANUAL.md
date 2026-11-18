# COGNITO: Faculty & Examiner User Manual
### Cognitive Question Generation & Intelligent Taxonomy Optimizer

Welcome to **COGNITO**, the AI-powered assessment engineering platform designed for university professors, examination paper setters, and academic audit committees.

---

## 1. Quick Start Workflow
COGNITO automates the traditional examination preparation workflow:
```
1. Ingest Documents  ->  2. Configure Exam  ->  3. AI Optimization  ->  4. Validation Audit  ->  5. Export
   (Syllabus & Past)       (Marks, Bloom's)       (Constraint Solver)      (CAS 0-100% Score)       (PDF/DOCX)
```

---

## 2. Navigating the Interface

### 2.1 The Dashboard
- **Cognitive Balance Radar**: Real-time visualization of your institution's cognitive distribution across L1 to L6.
- **Repository Summary**: Quick counts of indexed courses, question bank inventory, and recent examination papers.
- **Recent Audit Alerts**: Direct links to examination papers requiring review or reframing.

### 2.2 Document Ingestion Studio
- Upload syllabus documents (`.pdf`, `.docx`) to automatically extract modules, units, sub-topics, and Course Learning Outcomes (CLOs).
- Upload historical question papers (last 3-5 years) to build the institutional vector memory for repetition prevention.

### 2.3 Interactive Question Bank & Reframing
- Search questions by cognitive level, unit, difficulty, and marks.
- **AI Cognitive Reframing**: Click **"Reframe"** on any lower-order question (e.g., L1 Remember) to automatically elevate it to higher-order cognitive tiers (L3 Apply, L4 Analyze, L6 Create) while maintaining topic alignment.
- **Repetition Check**: Real-time semantic similarity scoring against all historical questions to safeguard against duplicate examination items.

### 2.4 Question Paper Generator Studio
1. **Step 1: Select Academic Context**: Choose Course (e.g. *Artificial Intelligence*), Semester, and Examination Template (*In-Semester Assessment 30M* or *End-Semester Exam 100M*).
2. **Step 2: Define Constraints**:
   - Total Marks & Duration.
   - Target Bloom's Taxonomy percentages (e.g., 10% L1, 20% L2, 30% L3, 25% L4, 10% L5, 5% L6).
   - Difficulty Target ratio (e.g., 30% Easy, 50% Medium, 20% Hard).
   - Unit-wise weightage distribution.
   - Novelty threshold (default: flag questions $\ge 85\%$ similarity).
3. **Step 3: Run Generation & Optimization**:
   - The system retrieves grounded syllabus context via RAG.
   - The Constraint Optimization Solver ranks and selects candidates maximizing question quality while satisfying structural criteria.

### 2.5 Independent Validation Studio
Before an examination paper is approved for printing:
- **CAS Score Calculation**: Evaluates Syllabus Coverage ($S$), Bloom's Compliance ($B$), Difficulty ($D$), Marks ($M$), Novelty ($N$), and Template compliance ($T$).
- **One-Click Closed-Loop Refinement**: If validation scores detect imbalances (e.g. Unit 3 is underrepresented or L4 cognitive depth is low), click **"Auto-Refine"** to let COGNITO swap or reframe non-compliant items until CAS $\ge 0.85$.

### 2.6 Export & Publication
- **Download Standard Academic PDF**: Formatted with University title, course code, instructions, section breaks, marks column, and Bloom's tags.
- **Download Microsoft Word (.docx)**: Fully editable for departmental archives.
- **Download Compliance Report**: Complete validation breakdown for NBA / NAAC accreditation documentation.
