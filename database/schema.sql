-- PostgreSQL Database Schema for FTA Comprehensive Review Application

-- Sections table (e.g., Legal, Safety, etc.)
CREATE TABLE sections (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    page_range VARCHAR(50),
    purpose TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sub-areas table with LOE data
CREATE TABLE sub_areas (
    id VARCHAR(50) PRIMARY KEY,
    section_id VARCHAR(50) NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    basic_requirement TEXT,
    applicability TEXT,
    detailed_explanation TEXT,
    instructions_for_reviewer TEXT,
    loe_hours DECIMAL(5, 2),  -- Estimated hours (e.g., 2.5)
    loe_confidence VARCHAR(20),  -- high, medium, low
    loe_confidence_score INTEGER,  -- 0-100 percentage
    loe_reasoning TEXT,  -- AI's reasoning for the estimate
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indicators of compliance
CREATE TABLE indicators_of_compliance (
    id SERIAL PRIMARY KEY,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    indicator_id VARCHAR(10) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deficiencies
CREATE TABLE deficiencies (
    id SERIAL PRIMARY KEY,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    determination TEXT,
    suggested_corrective_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    answers JSONB,  -- Store questionnaire answers
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project applicability (which sub-areas apply to which projects)
CREATE TABLE project_applicability (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    is_applicable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, sub_area_id)
);

-- Governing directives (optional - for reference)
CREATE TABLE governing_directives (
    id SERIAL PRIMARY KEY,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    reference VARCHAR(255),
    text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_sub_areas_section_id ON sub_areas(section_id);
CREATE INDEX idx_indicators_sub_area_id ON indicators_of_compliance(sub_area_id);
CREATE INDEX idx_deficiencies_sub_area_id ON deficiencies(sub_area_id);
CREATE INDEX idx_project_applicability_project_id ON project_applicability(project_id);
CREATE INDEX idx_project_applicability_sub_area_id ON project_applicability(sub_area_id);
CREATE INDEX idx_governing_directives_sub_area_id ON governing_directives(sub_area_id);

-- Create view for easy LOE summary by section
CREATE VIEW section_loe_summary AS
SELECT
    s.id AS section_id,
    s.title AS section_title,
    COUNT(sa.id) AS total_sub_areas,
    SUM(sa.loe_hours) AS total_hours,
    AVG(sa.loe_confidence_score) AS avg_confidence
FROM sections s
LEFT JOIN sub_areas sa ON s.id = sa.section_id
GROUP BY s.id, s.title
ORDER BY s.id;

-- Create view for project LOE summary
CREATE VIEW project_loe_summary AS
SELECT
    p.id AS project_id,
    p.name AS project_name,
    s.id AS section_id,
    s.title AS section_title,
    COUNT(sa.id) AS applicable_sub_areas,
    SUM(sa.loe_hours) AS section_hours,
    AVG(sa.loe_confidence_score) AS avg_confidence
FROM projects p
JOIN project_applicability pa ON p.id = pa.project_id
JOIN sub_areas sa ON pa.sub_area_id = sa.id
JOIN sections s ON sa.section_id = s.id
WHERE pa.is_applicable = TRUE
GROUP BY p.id, p.name, s.id, s.title
ORDER BY p.id, s.id;

-- Create view for project grand totals
CREATE VIEW project_grand_totals AS
SELECT
    p.id AS project_id,
    p.name AS project_name,
    COUNT(sa.id) AS total_applicable_sub_areas,
    SUM(sa.loe_hours) AS total_hours,
    AVG(sa.loe_confidence_score) AS avg_confidence
FROM projects p
JOIN project_applicability pa ON p.id = pa.project_id
JOIN sub_areas sa ON pa.sub_area_id = sa.id
WHERE pa.is_applicable = TRUE
GROUP BY p.id, p.name
ORDER BY p.id;
