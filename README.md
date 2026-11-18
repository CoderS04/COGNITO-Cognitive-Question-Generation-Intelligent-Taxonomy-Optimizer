# COGNITO: Cognitive Question Generation & Intelligent Taxonomy Optimizer

---

## 1. Executive Summary
**COGNITO** is an AI-powered Intelligent Question Paper Design System developed for university professors, examination paper setters, and academic audit committees. It replaces manual, error-prone exam drafting with an automated cognitive engineering pipeline:

$$\text{Understand} \longrightarrow \text{Analyze} \longrightarrow \text{Generate} \longrightarrow \text{Optimize} \longrightarrow \text{Validate} \longrightarrow \text{Report}$$

COGNITO guarantees that generated examination papers satisfy predefined academic templates, marking schemes, difficulty distributions, and learning outcomes while strictly adhering to Bloom's Revised Taxonomy (Anderson & Krathwohl, 2001).

---

## 2. System Architecture & Tech Stack

```
+----------------------------------------------------------------------------------------------------+
|                                    COGNITO Full-Stack Architecture                                 |
+----------------------------------------------------------------------------------------------------+
| Frontend: React 18, Vite, Tailwind CSS, Recharts, Lucide-React, Axios                             |
| Backend:  Python 3.11, FastAPI (REST API v1, Background Tasks, CORS)                               |
| Database: PostgreSQL / SQLite hybrid + ChromaDB / Semantic High-Dimensional Embeddings            |
| Engine:   Hybrid Action-Verb + Syntactic Classifier, Cosine Similarity Engine, Constraint Solver   |
+----------------------------------------------------------------------------------------------------+
```

### The 9 Modular Core Pipelines
1. **Module 1 (Document Processing)**: Ingests PDF, DOCX, and text files using `pypdf`, `python-docx`, and regex cleaners; removes noise, headers, and footers, and chunks into units and questions.
2. **Module 2 (Knowledge Base)**: PostgreSQL relational models + ChromaDB persistent vector store.
3. **Module 3 (AI Question Analysis & Bloom's Classifier)**: Hybrid classification across L1 (Remember) through L6 (Create) with contextual confidence and automated cognitive reframing.
4. **Module 4 (Semantic Similarity & Repetition Detection)**: Cosine similarity thresholding ($\ge 0.85$ repetition, $0.70 - 0.85$ paraphrase) against historical examination banks.
5. **Module 5 (Difficulty Estimation)**: Multi-factor difficulty model synthesizing cognitive demands ($L_{\text{bloom}}$), expected procedural steps ($S_{\text{steps}}$), conceptual depth ($C_{\text{concept}}$), and lexical complexity ($L_{\text{ling}}$) into Easy, Medium, or Hard.
6. **Module 6 (RAG Engine)**: Grounded retrieval of syllabus topics, Course Learning Outcomes (CLOs), and historical benchmarks to anchor generation.
7. **Module 7 (Constraint Optimization & Paper Assembly)**: Candidate scoring function:
   $$\text{Score}(Q) = w_1 R + w_2 B + w_3 D + w_4 N + w_5 Q_a$$
   Solves hard constraints (total marks, unit weightage, novelty) to assemble optimal examination papers.
8. **Module 8 (Independent Validation Engine & Closed-Loop Refinement)**: Computes Comprehensive Assessment Score (CAS):
   $$\text{CAS} = w_s S + w_b B + w_d D + w_m M + w_n N + w_t T$$
   Triggers closed-loop auto-refinement when $\text{CAS} < \tau_{\text{approval}}$ (default 82%).
9. **Module 9 (Analytics & Publication Engine)**: Generates publication-ready formatted PDFs (ReportLab), editable Word documents (.docx), and interactive Recharts visualizations (Radar, Donut, Bar).

---

## 3. Directory Layout
```
COGNITO/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint, SPA static serving, CORS
│   │   ├── config.py                   # Pydantic Settings & threshold definitions
│   │   ├── core/                       # Database engine, vector store, session
│   │   ├── models/                     # SQLAlchemy models (Course, Question, Paper, etc.)
│   │   ├── schemas/                    # Pydantic validation schemas
│   │   ├── services/                   # Modules 1 through 9 implementation
│   │   │   ├── module1_doc_processor.py
│   │   │   ├── module2_knowledge_base.py
│   │   │   ├── module3_blooms_classifier.py
│   │   │   ├── module4_similarity_engine.py
│   │   │   ├── module5_difficulty_estimator.py
│   │   │   ├── module6_rag_engine.py
│   │   │   ├── module7_optimizer.py
│   │   │   ├── module8_validation_engine.py
│   │   │   └── module9_reporting.py
│   │   ├── api/v1/                     # REST API route controllers
│   │   └── seed_data.py                # Academic fixtures for VIT CS3001
│   ├── test_system.py                  # Full 9-module end-to-end audit test
│   └── requirements.txt                # Python backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/                 # UI components (Radar, Pie, Gauge, Cards, Export)
│   │   ├── pages/                      # Dashboard, Generator, Detail, Bank, Ingestion, etc.
│   │   ├── services/api.js             # Centralized Axios client
│   │   ├── App.jsx                     # Top-level workspace layout
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── database/
│   ├── schema.sql                      # Production PostgreSQL DDL
│   ├── seed_fixtures.json              # Initial fixtures JSON
│   └── init_db.py                      # Database setup script
│
└── docs/
    ├── ARCHITECTURE.md                 # Detailed mathematical and module architecture
    ├── API_SPECIFICATION.md            # OpenAPI/REST contract documentation
    ├── BLOOMS_TAXONOMY_RUBRIC.md       # Cognitive level action verb rubric
    └── USER_MANUAL.md                  # Comprehensive manual for paper setters
```

---

## 4. Quick Start & Execution

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Backend Setup & Startup
```powershell
# Activate the existing virtual environment
.\.venv\Scripts\Activate.ps1

# (Optional) Seed the database fixtures
python database\init_db.py

# Launch FastAPI backend service
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Documentation (Swagger / OpenAPI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Interactive Full-Stack Application: [http://localhost:8000/](http://localhost:8000/)

### 2. Frontend Development Server (Optional)
The built frontend is already pre-compiled into `frontend/dist` and directly served by FastAPI on port 8000. If you wish to run Vite in live hot-reload development mode:
```powershell
cd frontend
npm run dev
```
- Vite Live Client: [http://localhost:5173](http://localhost:5173) (automatically proxies `/api` to port 8000).

### 3. Run Comprehensive Pipeline Verification Test
```powershell
.\.venv\Scripts\python.exe backend\test_system.py
```
This runs an automated end-to-end verification across all 9 modules: document parsing, cognitive classification, repetition detection, RAG retrieval, constraint paper generation, CAS validation, and PDF/DOCX generation.

---
