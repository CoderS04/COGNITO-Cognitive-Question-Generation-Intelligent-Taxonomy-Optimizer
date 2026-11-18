-- ====================================================================
-- COGNITO: Cognitive Question Generation & Intelligent Taxonomy Optimizer
-- Production PostgreSQL Database Schema
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Uncomment if pgvector is enabled in production PostgreSQL:
-- CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL DEFAULT 'Computer Science & Engineering',
    institution VARCHAR(255) NOT NULL DEFAULT 'Vishwakarma Institute of Technology',
    semester VARCHAR(32) NOT NULL DEFAULT 'Semester VI',
    academic_year VARCHAR(32) NOT NULL DEFAULT '2025-2026',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Units Table
CREATE TABLE IF NOT EXISTS units (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    unit_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_weightage_pct FLOAT DEFAULT 16.67,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_course_unit UNIQUE (course_id, unit_number)
);

-- 3. Topics Table
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    keywords TEXT,
    learning_outcome VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Questions Repository
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    unit_id INTEGER REFERENCES units(id) ON DELETE SET NULL,
    topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    text TEXT NOT NULL,
    question_type VARCHAR(32) NOT NULL DEFAULT 'Descriptive', -- 'MCQ', 'Short', 'Descriptive', 'Numerical'
    marks INTEGER NOT NULL DEFAULT 5,
    bloom_level VARCHAR(8) NOT NULL DEFAULT 'L2', -- L1, L2, L3, L4, L5, L6
    primary_verb VARCHAR(64),
    difficulty VARCHAR(16) NOT NULL DEFAULT 'Medium', -- 'Easy', 'Medium', 'Hard'
    difficulty_score FLOAT NOT NULL DEFAULT 0.5,
    is_historical BOOLEAN DEFAULT FALSE,
    exam_year INTEGER,
    embedding_id VARCHAR(128),
    solution_outline TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Institutional Templates & Assessment Guidelines
CREATE TABLE IF NOT EXISTS exam_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    total_marks INTEGER NOT NULL DEFAULT 100,
    duration_minutes INTEGER NOT NULL DEFAULT 180,
    instructions TEXT,
    sections_config JSONB NOT NULL,
    bloom_targets JSONB NOT NULL,
    difficulty_targets JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Generated Question Papers
CREATE TABLE IF NOT EXISTS exam_papers (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES exam_templates(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    academic_year VARCHAR(32) NOT NULL,
    semester VARCHAR(32) NOT NULL,
    total_marks INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT', -- 'DRAFT', 'VALIDATED', 'APPROVED', 'REJECTED'
    cas_score FLOAT DEFAULT 0.0,
    meta_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Question Paper Sections
CREATE TABLE IF NOT EXISTS paper_sections (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER NOT NULL REFERENCES exam_papers(id) ON DELETE CASCADE,
    section_name VARCHAR(128) NOT NULL,
    instructions TEXT,
    total_marks INTEGER NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 1
);

-- 8. Questions Mapped to Paper Sections
CREATE TABLE IF NOT EXISTS paper_questions (
    id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL REFERENCES paper_sections(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE RESTRICT,
    sub_question_label VARCHAR(32) NOT NULL, -- '1(a)', '1(b)', etc.
    order_index INTEGER NOT NULL DEFAULT 1,
    is_optional BOOLEAN DEFAULT FALSE,
    marks INTEGER NOT NULL
);

-- 9. Validation Audits & Feedback Logs
CREATE TABLE IF NOT EXISTS validation_audits (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER NOT NULL REFERENCES exam_papers(id) ON DELETE CASCADE,
    cas_score FLOAT NOT NULL,
    syllabus_coverage FLOAT NOT NULL,
    bloom_compliance FLOAT NOT NULL,
    difficulty_compliance FLOAT NOT NULL,
    marks_compliance FLOAT NOT NULL,
    repetition_score FLOAT NOT NULL,
    template_compliance FLOAT NOT NULL,
    status VARCHAR(32) NOT NULL, -- 'PASSED', 'WARNING', 'FAILED'
    violations JSONB,
    recommendations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Ingested Documents
CREATE TABLE IF NOT EXISTS ingested_documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    doc_type VARCHAR(64) NOT NULL, -- 'syllabus', 'past_paper', 'guideline'
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    file_size INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PROCESSED',
    extracted_items_count INTEGER DEFAULT 0,
    summary JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_questions_bloom ON questions(bloom_level);
CREATE INDEX IF NOT EXISTS idx_questions_unit ON questions(unit_id);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_paper_status ON exam_papers(status);
