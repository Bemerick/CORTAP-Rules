"""
Populate questionnaire_questions table with assessment questions
Simplified version for new schema
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Use DATABASE_URL if available (for Render), otherwise construct from individual vars
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'fta_review')}"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Define questions based on the original application
QUESTIONS = [
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
    (12, 'Is the recipient a public operator?', 'Classification'),
]

def populate_questions(conn):
    """Populate questions table"""
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("POPULATING QUESTIONNAIRE")
    print("=" * 80)

    for question_number, question_text, category in QUESTIONS:
        print(f"\n[{question_number}] {question_text}")

        cursor.execute("""
            INSERT INTO questionnaire_questions (
                question_number, question_text, category
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (question_number) DO UPDATE SET
                question_text = EXCLUDED.question_text,
                category = EXCLUDED.category
            RETURNING id
        """, (question_number, question_text, category))

        conn.commit()

    print("\n" + "=" * 80)
    print("✓ Questions populated successfully!")
    print("=" * 80)

def display_summary(conn):
    """Display summary of populated data"""
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM questionnaire_questions")
    question_count = cursor.fetchone()[0]

    print(f"\nSummary:")
    print(f"  Questions: {question_count}")

    # Show questions
    cursor.execute("""
        SELECT question_number, category, question_text
        FROM questionnaire_questions
        ORDER BY question_number
    """)

    print("\n" + "-" * 80)
    print("Questions:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"  {row[0]:2}. [{row[1]:15}] {row[2][:60]}...")

    cursor.close()

def main():
    print("FTA Comprehensive Review - Questionnaire Population")
    print("=" * 80)

    conn = get_db_connection()

    try:
        populate_questions(conn)
        display_summary(conn)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
