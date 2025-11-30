-- Questionnaire and Applicability Schema
-- This schema supports dynamic questionnaires and rule-based applicability assessment

-- ============================================================================
-- QUESTIONNAIRE TABLES
-- ============================================================================

-- Assessment questions
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    question_key VARCHAR(50) UNIQUE NOT NULL,  -- e.g., 'recipient_type', 'federal_assistance_amount'
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL,  -- 'radio', 'checkbox', 'text', 'number'
    help_text TEXT,  -- Optional explanatory text
    display_order INTEGER NOT NULL,
    is_required BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Question options (for radio/checkbox questions)
CREATE TABLE question_options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    option_value VARCHAR(100) NOT NULL,  -- Internal value (e.g., 'tier_1', 'yes')
    option_label VARCHAR(255) NOT NULL,  -- Display label (e.g., 'Tier I', 'Yes')
    display_order INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(question_id, option_value)
);

-- ============================================================================
-- APPLICABILITY RULES
-- ============================================================================

-- Applicability rules define when sub-areas apply based on answers
CREATE TABLE applicability_rules (
    id SERIAL PRIMARY KEY,
    sub_area_id VARCHAR(50) NOT NULL REFERENCES sub_areas(id) ON DELETE CASCADE,
    rule_description TEXT,  -- Human-readable description
    priority INTEGER DEFAULT 0,  -- Higher priority rules evaluated first
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rule conditions (AND logic within a rule, multiple rules = OR logic)
CREATE TABLE rule_conditions (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER NOT NULL REFERENCES applicability_rules(id) ON DELETE CASCADE,
    question_key VARCHAR(50) NOT NULL,
    operator VARCHAR(20) NOT NULL,  -- 'equals', 'contains', 'not_equals', 'greater_than', 'less_than', 'in', 'not_in'
    expected_value VARCHAR(255),  -- Value to compare against (can be JSON array for 'in' operator)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PROJECT ANSWERS
-- ============================================================================

-- Store individual answers for each project (normalized instead of JSONB)
CREATE TABLE project_answers (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    question_key VARCHAR(50) NOT NULL,
    answer_value TEXT NOT NULL,  -- Store as text, can be JSON array for checkbox
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, question_key)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_questions_active ON questions(is_active, display_order);
CREATE INDEX idx_question_options_question ON question_options(question_id, display_order);
CREATE INDEX idx_applicability_rules_sub_area ON applicability_rules(sub_area_id);
CREATE INDEX idx_rule_conditions_rule ON rule_conditions(rule_id);
CREATE INDEX idx_project_answers_project ON project_answers(project_id);
CREATE INDEX idx_project_answers_question ON project_answers(question_key);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for questions with their options
CREATE VIEW questions_with_options AS
SELECT
    q.id as question_id,
    q.question_key,
    q.question_text,
    q.question_type,
    q.help_text,
    q.display_order,
    q.is_required,
    json_agg(
        json_build_object(
            'id', qo.id,
            'value', qo.option_value,
            'label', qo.option_label,
            'display_order', qo.display_order
        ) ORDER BY qo.display_order
    ) FILTER (WHERE qo.id IS NOT NULL) as options
FROM questions q
LEFT JOIN question_options qo ON q.id = qo.question_id AND qo.is_active = TRUE
WHERE q.is_active = TRUE
GROUP BY q.id, q.question_key, q.question_text, q.question_type, q.help_text, q.display_order, q.is_required
ORDER BY q.display_order;

-- View for rules with their conditions
CREATE VIEW rules_with_conditions AS
SELECT
    ar.id as rule_id,
    ar.sub_area_id,
    ar.rule_description,
    ar.priority,
    json_agg(
        json_build_object(
            'question_key', rc.question_key,
            'operator', rc.operator,
            'expected_value', rc.expected_value
        ) ORDER BY rc.id
    ) as conditions
FROM applicability_rules ar
LEFT JOIN rule_conditions rc ON ar.id = rc.rule_id AND rc.is_active = TRUE
WHERE ar.is_active = TRUE
GROUP BY ar.id, ar.sub_area_id, ar.rule_description, ar.priority
ORDER BY ar.sub_area_id, ar.priority DESC;

-- View for project answers in a more usable format
CREATE VIEW project_answers_summary AS
SELECT
    p.id as project_id,
    p.name as project_name,
    json_object_agg(pa.question_key, pa.answer_value) as answers
FROM projects p
LEFT JOIN project_answers pa ON p.id = pa.project_id
GROUP BY p.id, p.name;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to evaluate if a rule matches given answers
CREATE OR REPLACE FUNCTION evaluate_rule(
    p_rule_id INTEGER,
    p_answers JSONB
) RETURNS BOOLEAN AS $$
DECLARE
    v_condition RECORD;
    v_answer TEXT;
    v_expected TEXT;
BEGIN
    -- Loop through all conditions for this rule (all must match - AND logic)
    FOR v_condition IN
        SELECT question_key, operator, expected_value
        FROM rule_conditions
        WHERE rule_id = p_rule_id AND is_active = TRUE
    LOOP
        -- Get the answer value
        v_answer := p_answers ->> v_condition.question_key;
        v_expected := v_condition.expected_value;

        -- If no answer provided for a required condition, rule fails
        IF v_answer IS NULL THEN
            RETURN FALSE;
        END IF;

        -- Evaluate based on operator
        CASE v_condition.operator
            WHEN 'equals' THEN
                IF v_answer != v_expected THEN
                    RETURN FALSE;
                END IF;
            WHEN 'not_equals' THEN
                IF v_answer = v_expected THEN
                    RETURN FALSE;
                END IF;
            WHEN 'contains' THEN
                IF v_answer NOT LIKE '%' || v_expected || '%' THEN
                    RETURN FALSE;
                END IF;
            WHEN 'in' THEN
                -- For checkbox answers (JSON array)
                IF NOT (v_answer::jsonb ? v_expected) THEN
                    RETURN FALSE;
                END IF;
            WHEN 'not_in' THEN
                IF v_answer::jsonb ? v_expected THEN
                    RETURN FALSE;
                END IF;
            ELSE
                -- Unknown operator
                RETURN FALSE;
        END CASE;
    END LOOP;

    -- All conditions matched
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get applicable sub-areas for a project
CREATE OR REPLACE FUNCTION get_applicable_sub_areas(
    p_project_id INTEGER
) RETURNS TABLE(sub_area_id VARCHAR) AS $$
DECLARE
    v_answers JSONB;
BEGIN
    -- Get all answers for the project as JSONB
    SELECT json_object_agg(question_key, answer_value)::jsonb
    INTO v_answers
    FROM project_answers
    WHERE project_id = p_project_id;

    -- Return distinct sub-areas where at least one rule matches
    RETURN QUERY
    SELECT DISTINCT ar.sub_area_id
    FROM applicability_rules ar
    WHERE ar.is_active = TRUE
    AND evaluate_rule(ar.id, v_answers);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE questions IS 'Assessment questions for determining project applicability';
COMMENT ON TABLE question_options IS 'Available options for radio and checkbox questions';
COMMENT ON TABLE applicability_rules IS 'Rules defining when sub-areas apply to projects';
COMMENT ON TABLE rule_conditions IS 'Individual conditions that make up a rule (AND logic)';
COMMENT ON TABLE project_answers IS 'Normalized storage of project questionnaire answers';
COMMENT ON FUNCTION evaluate_rule IS 'Evaluates if a rule matches given answers (all conditions must match)';
COMMENT ON FUNCTION get_applicable_sub_areas IS 'Returns list of applicable sub-area IDs for a project';
