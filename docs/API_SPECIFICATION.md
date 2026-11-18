# COGNITO: REST API Specification

Base URL: `http://localhost:8000/api/v1`

---

## 1. Document Ingestion (`/documents`)
- **POST `/documents/upload`**: Multipart file upload (`.pdf`, `.docx`, `.txt`).
  - Form Fields: `file` (UploadFile), `course_id` (int), `doc_type` (`"syllabus" | "historical_paper" | "guideline" | "template"`).
  - Response: `{ status: "success", document_id: int, extracted_chunks: int, summary: dict }`
- **GET `/documents`**: Retrieve list of processed documents with status and metadata.
- **GET `/documents/{doc_id}/chunks`**: Retrieve parsed chunks and extracted questions/topics.

---

## 2. Knowledge Base & Syllabus (`/courses`, `/syllabus`)
- **GET `/courses`**: List all registered courses and academic disciplines.
- **POST `/courses`**: Create a new course.
- **GET `/courses/{id}/units`**: Retrieve units and topics structure.
- **POST `/courses/{id}/units`**: Create or update unit and syllabus topics.

---

## 3. Question Bank & Taxonomy Analysis (`/questions`)
- **GET `/questions`**: Query questions with filters (`course_id`, `bloom_level`, `difficulty`, `unit_id`, `min_marks`, `max_marks`).
- **POST `/questions`**: Add a new question with auto-tagging.
- **POST `/questions/analyze`**: Run Bloom's Taxonomy and difficulty classifier on arbitrary question text.
  - Request: `{ "text": "string", "marks": 5, "course_id": 1 }`
  - Response: `{ "bloom_level": "L4", "primary_verb": "differentiate", "confidence": 0.94, "difficulty": "Medium", "difficulty_score": 0.62 }`
- **POST `/questions/reframe`**: Elevate or adapt a question to a specified target Bloom's level.
  - Request: `{ "question_id": int, "target_level": "L5" }`
  - Response: `{ "original": "...", "reframed": "...", "target_level": "L5", "explanation": "..." }`
- **POST `/questions/similarity-check`**: Check question text for repetition against repository.
  - Request: `{ "text": "string", "threshold": 0.85 }`
  - Response: `{ "is_repeated": true, "max_similarity": 0.92, "matching_questions": [...] }`

---

## 4. Institutional Templates & Assessment Rules (`/templates`)
- **GET `/templates`**: List standard templates (e.g. In-Semester Examination, End-Semester Examination, Class Quiz).
- **POST `/templates`**: Create customized template with sections, marks, and constraints.
- **GET `/templates/{id}`**: Retrieve detailed structural schema and Bloom's target bounds.

---

## 5. Question Paper Generation & Optimization (`/papers`)
- **POST `/papers/generate`**: Generate, optimize, and assemble a new question paper.
  - Request:
    ```json
    {
      "course_id": 1,
      "template_id": 1,
      "title": "Artificial Intelligence End-Semester Exam",
      "total_marks": 50,
      "bloom_targets": { "L1": 10, "L2": 20, "L3": 30, "L4": 25, "L5": 10, "L6": 5 },
      "difficulty_targets": { "Easy": 30, "Medium": 50, "Hard": 20 },
      "unit_weights": { "1": 25, "2": 25, "3": 25, "4": 25 },
      "novelty_threshold": 0.85,
      "enable_optimization": true
    }
    ```
  - Response: Paper details, sections, selected questions, and preliminary compliance summary.
- **GET `/papers`**: List generated papers.
- **GET `/papers/{id}`**: Get complete question paper with full metadata.
- **PUT `/papers/{id}/replace-question`**: Swap a question with a candidate satisfying identical constraints.

---

## 6. Independent Validation Engine (`/validation`)
- **POST `/validation/validate/{paper_id}`**: Run comprehensive CAS audit.
  - Response:
    ```json
    {
      "paper_id": 1,
      "cas_score": 0.94,
      "status": "APPROVED",
      "metrics": {
        "syllabus_coverage": 0.96,
        "bloom_compliance": 0.92,
        "difficulty_compliance": 0.94,
        "marks_verification": 1.0,
        "repetition_score": 0.90,
        "template_compliance": 0.98
      },
      "violations": [],
      "recommendations": []
    }
    ```
- **POST `/validation/auto-refine/{paper_id}`**: Trigger closed-loop refinement loop.

---

## 7. Analytics & Export (`/analytics`, `/export`)
- **GET `/analytics/course/{course_id}`**: Cognitive distribution trends across historical semesters.
- **GET `/papers/{id}/export/pdf`**: Download publication-ready formatted PDF.
- **GET `/papers/{id}/export/docx`**: Download editable Word document (.docx).
- **GET `/papers/{id}/export/json`**: Download raw JSON with full audit metadata.
