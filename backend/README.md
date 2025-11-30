# FTA Comprehensive Review - FastAPI Backend

RESTful API for FTA Comprehensive Review Applicability Assessment and Level of Effort (LOE) Estimation.

## Features

- **Questionnaire API**: Serve assessment questions dynamically
- **Sections & Sub-Areas**: Access FTA review sections and requirements
- **Project Management**: Create, update, and manage review projects
- **Applicability Assessment**: Determine which sub-areas apply based on answers
- **LOE Calculation**: Automatic calculation of review hours
- **Database-Driven**: PostgreSQL with SQLAlchemy ORM

## Tech Stack

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Database
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fta_review
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Ensure Database is Set Up

The database should already be initialized with:
- All tables (sections, sub_areas, questions, etc.)
- LOE data populated
- Questions and rules loaded

If not, run the scripts from the `../scripts` directory:
```bash
cd ../scripts
python3 db_init.py
python3 loe_analysis_complete.py
python3 populate_questionnaire.py
python3 populate_applicability_rules.py
```

## Running the API

### Development Mode

```bash
cd backend
python -m app.main
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### Questions

- `GET /api/questions` - Get all questions with options
- `GET /api/questions/{key}` - Get specific question

### Sections

- `GET /api/sections` - Get all sections
- `GET /api/sections/summary` - Get sections with LOE summary
- `GET /api/sections/{id}` - Get specific section

### Sub-Areas

- `GET /api/sub-areas` - Get all sub-areas
- `GET /api/sub-areas?section_id={id}` - Get sub-areas by section
- `GET /api/sub-areas/{id}` - Get detailed sub-area info

### Projects

- `GET /api/projects` - Get all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `POST /api/projects/{id}/answers` - Submit answers & calculate applicability
- `GET /api/projects/{id}/applicable-sub-areas` - Get applicable sub-areas
- `GET /api/projects/{id}/loe-summary` - Get LOE summary for project

### Assessment

- `POST /api/assess` - Assess applicability without creating project

## API Usage Examples

### Get Questions

```bash
curl http://localhost:8000/api/questions
```

### Create Project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Transit Project", "description": "Sample project"}'
```

### Submit Answers

```bash
curl -X POST http://localhost:8000/api/projects/1/answers \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "recipient_type": "non_state",
      "federal_assistance_amount": "gte_750k",
      "has_subrecipients": "yes",
      "fund_types": "[\"5307\", \"5337\"]",
      "service_type": "[\"fixed_route\"]"
    }
  }'
```

### Quick Assessment

```bash
curl -X POST http://localhost:8000/api/assess \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "recipient_type": "all",
      "has_subrecipients": "yes"
    }
  }'
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app & config
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py       # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── section.py
│   │   ├── sub_area.py
│   │   ├── indicator.py
│   │   ├── deficiency.py
│   │   ├── question.py
│   │   ├── rule.py
│   │   └── project.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── question.py
│   │   ├── section.py
│   │   ├── sub_area.py
│   │   ├── project.py
│   │   └── assessment.py
│   └── routers/                # API endpoints
│       ├── __init__.py
│       ├── questions.py
│       ├── sections.py
│       ├── sub_areas.py
│       ├── projects.py
│       └── assessment.py
├── .env                        # Environment variables
├── .env.example               # Template
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Database Schema

The API uses the following main tables:

- `sections` - FTA review sections
- `sub_areas` - Individual review requirements with LOE data
- `indicators_of_compliance` - Compliance indicators
- `deficiencies` - Potential deficiencies
- `questions` - Assessment questions
- `question_options` - Answer options
- `applicability_rules` - Rules for determining applicability
- `rule_conditions` - Conditions for each rule
- `projects` - User projects
- `project_answers` - Project answers
- `project_applicability` - Which sub-areas apply to which projects

## Development

### Adding New Endpoints

1. Create router in `app/routers/`
2. Define Pydantic schemas in `app/schemas/`
3. Add router to `app/main.py`

### Database Migrations

For schema changes:
1. Modify SQL in `database/` directory
2. Run migration script
3. Update SQLAlchemy models

## Deployment

### Render.com

1. Create new Web Service
2. Connect to your repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Add PostgreSQL database add-on

### Environment Variables for Production

```
DATABASE_URL=<provided by Render>
API_HOST=0.0.0.0
API_PORT=$PORT
ALLOWED_ORIGINS=https://your-frontend.com
```

## License

Proprietary - FTA Comprehensive Review Application

## Support

For issues or questions, contact the development team.
