# Deployment Notes

## Database Migrations Required

**IMPORTANT:** The following SQL must be run on any environment where the database schema is not up to date:

### 1. Add chapter_number to sections table (if missing)
```sql
ALTER TABLE sections ADD COLUMN IF NOT EXISTS chapter_number INTEGER;
```

### 2. Add Project fields (if missing)
```sql
ALTER TABLE projects ADD COLUMN IF NOT EXISTS grantee_name VARCHAR(255);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS grant_number VARCHAR(100);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS review_type VARCHAR(50);
```

### 3. Rename questions table (if needed)
```sql
-- Check if 'questions' table exists and 'questionnaire_questions' doesn't
ALTER TABLE IF EXISTS questions RENAME TO questionnaire_questions;
```

### 4. Add missing columns to questionnaire_questions (if needed)
```sql
ALTER TABLE questionnaire_questions ADD COLUMN IF NOT EXISTS question_number INTEGER UNIQUE;
ALTER TABLE questionnaire_questions ADD COLUMN IF NOT EXISTS category VARCHAR(100);
```

### 5. Populate chapter_numbers (if needed)
See production database for reference values (1-23).

## CORS Configuration

The application uses environment variable `ALLOWED_ORIGINS` for CORS configuration:

- **Default:** `*` (allows all origins)
- **Production:** Set to specific frontend URLs (comma-separated)
- **Example:** `ALLOWED_ORIGINS=https://yourapp.com,https://www.yourapp.com`

## New Dependencies

Added to `requirements.txt`:
- `openpyxl==3.1.5` - For Excel workbook generation

Run `pip install -r requirements.txt` after deployment.

## New Feature: Excel Workbook Export

Users can now export project assessment results as Excel workbooks:
- Endpoint: `GET /api/projects/{project_id}/export-workbook`
- Format: One tab per section with applicable sub-areas and indicators
- Filename: `{ProjectName}-Scoping Workbook-{timestamp}.xlsx`
