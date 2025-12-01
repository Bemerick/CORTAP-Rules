#!/bin/bash
set -e

echo "Initializing database..."

# Check if tables exist, if not create them
psql $DATABASE_URL << 'EOF'
-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS sections (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    page_range VARCHAR(50),
    purpose TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sub_areas (
    id VARCHAR(50) PRIMARY KEY,
    section_id VARCHAR(50) NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    basic_requirement TEXT,
    applicability TEXT,
    detailed_explanation TEXT,
    instructions_for_reviewer TEXT,
    loe_hours DECIMAL(5, 2),
    loe_confidence VARCHAR(20),
    loe_confidence_score INTEGER,
    loe_reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS indicators_of_compliance (
    id SERIAL PRIMARY KEY,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    indicator_id VARCHAR(10) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deficiencies (
    id SERIAL PRIMARY KEY,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    determination TEXT,
    suggested_corrective_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    grantee_name VARCHAR(255),
    grant_number VARCHAR(100),
    review_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questionnaire_questions (
    id SERIAL PRIMARY KEY,
    question_number INTEGER NOT NULL UNIQUE,
    question_text TEXT NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applicability_rules (
    id SERIAL PRIMARY KEY,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questionnaire_questions(id) ON DELETE CASCADE,
    required_answer VARCHAR(50) NOT NULL,
    rule_type VARCHAR(50) DEFAULT 'include',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sub_area_id, question_id)
);

CREATE TABLE IF NOT EXISTS project_answers (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questionnaire_questions(id) ON DELETE CASCADE,
    answer VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, question_id)
);

CREATE TABLE IF NOT EXISTS project_applicability (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    is_applicable BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, sub_area_id)
);

-- Insert sample questions if table is empty
INSERT INTO questionnaire_questions (question_number, question_text, category)
VALUES
    (1, 'What type of recipient is this project?', 'General'),
    (2, 'What is the total Federal assistance expenditure amount in the fiscal year?', 'Financial'),
    (3, 'Does the recipient have subrecipients?', 'General'),
    (4, 'Does the recipient have management or operations contractors and lessees?', 'Operations'),
    (5, 'What tier level is the recipient?', 'Classification'),
    (6, 'Which types of FTA funds does the recipient receive?', 'Funding'),
    (7, 'What type of service does the recipient provide?', 'Service'),
    (8, 'Is this a designated recipient?', 'Classification'),
    (9, 'Does the recipient have a Disadvantaged Business Enterprise (DBE) overall goal?', 'Compliance'),
    (10, 'Is the recipient part of a group plan?', 'Planning'),
    (11, 'Does the recipient have direct control over FTA-funded assets?', 'Assets'),
    (12, 'Is the recipient a public operator?', 'Classification')
ON CONFLICT (question_number) DO NOTHING;

EOF

echo "Database initialization complete!"
