# FTA Comprehensive Review - LOE Analysis Scripts

This directory contains scripts for analyzing and populating Level of Effort (LOE) data for FTA Comprehensive Review sub-areas using Anthropic's Claude API.

## Prerequisites

1. **PostgreSQL Database**: Install PostgreSQL locally or use a hosted instance
2. **Python 3.8+**: Ensure Python is installed
3. **Anthropic API Key**: Already configured in `.env` file

## Setup Instructions

### 1. Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create PostgreSQL User and Database

```bash
# Connect to PostgreSQL
psql postgres

# In the PostgreSQL prompt:
CREATE USER fta_admin WITH PASSWORD 'your_secure_password';
CREATE DATABASE fta_review OWNER fta_admin;
GRANT ALL PRIVILEGES ON DATABASE fta_review TO fta_admin;
\q
```

### 3. Update Environment Variables

Edit the `.env` file with your database credentials:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fta_review
DB_USER=fta_admin
DB_PASSWORD=your_secure_password
```

### 4. Install Python Dependencies

```bash
# From the scripts directory
pip install -r requirements.txt
```

## Running the LOE Analysis

### Step 1: Initialize the Database

```bash
python db_init.py
```

This will:
- Create the `fta_review` database (if it doesn't exist)
- Create all necessary tables and views
- Set up indexes for performance

### Step 2: Run LOE Analysis

```bash
python loe_analysis.py
```

This will:
- Load the FTA_Complete_Extraction.json file
- Use Claude API to analyze each sub-area
- Estimate LOE hours with confidence levels
- Populate the database with results
- Display a summary when complete

**Note:** This process may take 10-20 minutes depending on the number of sub-areas (the script includes a 0.5s delay between API calls to avoid rate limiting).

## Database Schema

### Main Tables

- **sections**: FTA review sections (Legal, Safety, etc.)
- **sub_areas**: Individual sub-areas with LOE data
- **indicators_of_compliance**: Compliance indicators for each sub-area
- **deficiencies**: Potential deficiencies for each sub-area
- **projects**: User-created review projects
- **project_applicability**: Links projects to applicable sub-areas

### Useful Views

- **section_loe_summary**: LOE totals by section
- **project_loe_summary**: LOE breakdown by project and section
- **project_grand_totals**: Total LOE for each project

## Querying LOE Data

### Get all sub-areas with LOE:

```sql
SELECT
    sa.id,
    sa.question,
    sa.loe_hours,
    sa.loe_confidence,
    sa.loe_confidence_score,
    s.title as section_title
FROM sub_areas sa
JOIN sections s ON sa.section_id = s.id
ORDER BY s.id, sa.id;
```

### Get section summaries:

```sql
SELECT * FROM section_loe_summary;
```

### Calculate total project hours:

```sql
SELECT * FROM project_grand_totals;
```

## Troubleshooting

### Database Connection Issues

If you can't connect to PostgreSQL:

1. Check if PostgreSQL is running:
   ```bash
   # macOS/Linux
   pg_isready

   # Or check service status
   brew services list | grep postgresql  # macOS
   systemctl status postgresql           # Linux
   ```

2. Verify connection parameters in `.env`

3. Test connection:
   ```bash
   psql -h localhost -U fta_admin -d fta_review
   ```

### API Rate Limiting

If you encounter rate limiting from Anthropic:
- Increase the `time.sleep()` value in `loe_analysis.py`
- The script saves progress after each sub-area, so you can restart if interrupted

### Rerunning Analysis

The script uses `ON CONFLICT` clauses, so it's safe to rerun. It will update existing records with new LOE data.

## Next Steps

After populating the LOE data, you can:

1. Build the FastAPI backend to serve this data
2. Create the React frontend for project management
3. Deploy to Render.com with PostgreSQL database

## File Structure

```
scripts/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (configured)
├── .env.example             # Template for .env
├── db_init.py               # Database initialization
└── loe_analysis.py          # Main LOE analysis script

database/
└── schema.sql               # PostgreSQL schema definition

docs/
└── FTA_Complete_Extraction.json  # Source data
```
