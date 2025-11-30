"""
Populate questionnaire tables with assessment questions
Extracts questions from the current HTML application logic
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'fta_review')
    )

# Define questions based on the HTML application
QUESTIONS = [
    {
        'key': 'recipient_type',
        'text': 'What type of recipient is this project?',
        'type': 'radio',
        'help_text': 'Select the recipient classification for this project',
        'order': 1,
        'options': [
            {'value': 'all', 'label': 'All recipients', 'order': 1},
            {'value': 'state', 'label': 'State recipient', 'order': 2},
            {'value': 'non_state', 'label': 'Non-state recipient', 'order': 3}
        ]
    },
    {
        'key': 'federal_assistance_amount',
        'text': 'What is the total Federal assistance expenditure amount in the fiscal year?',
        'type': 'radio',
        'help_text': 'Select the Federal assistance expenditure level',
        'order': 2,
        'options': [
            {'value': 'less_750k', 'label': 'Less than $750,000', 'order': 1},
            {'value': 'gte_750k', 'label': '$750,000 or more', 'order': 2}
        ]
    },
    {
        'key': 'has_subrecipients',
        'text': 'Does the recipient have subrecipients?',
        'type': 'radio',
        'help_text': 'Indicate if this recipient passes funding to subrecipients',
        'order': 3,
        'options': [
            {'value': 'yes', 'label': 'Yes', 'order': 1},
            {'value': 'no', 'label': 'No', 'order': 2}
        ]
    },
    {
        'key': 'has_contractors_lessees',
        'text': 'Does the recipient have management or operations contractors and lessees?',
        'type': 'radio',
        'help_text': 'Indicate if this recipient uses contractors or lessees for management/operations',
        'order': 4,
        'options': [
            {'value': 'yes', 'label': 'Yes', 'order': 1},
            {'value': 'no', 'label': 'No', 'order': 2}
        ]
    },
    {
        'key': 'tier_level',
        'text': 'What tier level is the recipient?',
        'type': 'radio',
        'help_text': 'Select the recipient tier classification',
        'order': 5,
        'options': [
            {'value': 'tier_1', 'label': 'Tier I', 'order': 1},
            {'value': 'tier_2', 'label': 'Tier II', 'order': 2},
            {'value': 'na', 'label': 'Not applicable', 'order': 3}
        ]
    },
    {
        'key': 'fund_types',
        'text': 'Which types of FTA funds does the recipient receive? (Select all that apply)',
        'type': 'checkbox',
        'help_text': 'Select all applicable FTA funding programs',
        'order': 6,
        'options': [
            {'value': '5310', 'label': 'Section 5310', 'order': 1},
            {'value': '5311', 'label': 'Section 5311', 'order': 2},
            {'value': '5307', 'label': 'Section 5307', 'order': 3},
            {'value': '5337', 'label': 'Section 5337', 'order': 4},
            {'value': 'other', 'label': 'Other funds', 'order': 5}
        ]
    },
    {
        'key': 'service_type',
        'text': 'What type of service does the recipient provide? (Select all that apply)',
        'type': 'checkbox',
        'help_text': 'Select all types of transit service provided',
        'order': 7,
        'options': [
            {'value': 'fixed_route', 'label': 'Fixed-route service', 'order': 1},
            {'value': 'demand_response', 'label': 'Demand response', 'order': 2},
            {'value': 'commuter_rail', 'label': 'Commuter rail', 'order': 3},
            {'value': 'commuter_bus', 'label': 'Commuter bus', 'order': 4},
            {'value': 'other', 'label': 'Other', 'order': 5}
        ]
    },
    {
        'key': 'is_designated_recipient',
        'text': 'Is this a designated recipient?',
        'type': 'radio',
        'help_text': 'Indicate if this is a designated recipient',
        'order': 8,
        'options': [
            {'value': 'yes', 'label': 'Yes', 'order': 1},
            {'value': 'no', 'label': 'No', 'order': 2}
        ]
    },
    {
        'key': 'has_dbe_goal',
        'text': 'Does the recipient have a Disadvantaged Business Enterprise (DBE) overall goal?',
        'type': 'radio',
        'help_text': 'Indicate if the recipient has established a DBE goal',
        'order': 9,
        'options': [
            {'value': 'yes', 'label': 'Yes', 'order': 1},
            {'value': 'no', 'label': 'No', 'order': 2}
        ]
    },
    {
        'key': 'group_plan',
        'text': 'Is the recipient part of a group plan?',
        'type': 'radio',
        'help_text': 'Indicate the recipient\'s participation in a group plan',
        'order': 10,
        'options': [
            {'value': 'participant', 'label': 'Participant', 'order': 1},
            {'value': 'sponsor', 'label': 'Sponsor', 'order': 2},
            {'value': 'na', 'label': 'Not applicable', 'order': 3}
        ]
    },
    {
        'key': 'asset_control',
        'text': 'Does the recipient have direct control over FTA-funded assets?',
        'type': 'radio',
        'help_text': 'Indicate if the recipient directly controls FTA-funded assets',
        'order': 11,
        'options': [
            {'value': 'yes', 'label': 'Yes', 'order': 1},
            {'value': 'no', 'label': 'No', 'order': 2}
        ]
    },
    {
        'key': 'is_public_operator',
        'text': 'Is the recipient a public operator?',
        'type': 'radio',
        'help_text': 'Indicate if this is a public transit operator',
        'order': 12,
        'options': [
            {'value': 'yes', 'label': 'Yes', 'order': 1},
            {'value': 'no', 'label': 'No', 'order': 2}
        ]
    }
]

def populate_questions(conn):
    """Populate questions and options tables"""
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("POPULATING QUESTIONNAIRE")
    print("=" * 80)

    for q in QUESTIONS:
        print(f"\n[{q['order']}] {q['key']}: {q['text'][:60]}...")

        # Insert question
        cursor.execute("""
            INSERT INTO questions (
                question_key, question_text, question_type,
                help_text, display_order, is_required
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (question_key) DO UPDATE SET
                question_text = EXCLUDED.question_text,
                question_type = EXCLUDED.question_type,
                help_text = EXCLUDED.help_text,
                display_order = EXCLUDED.display_order,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (
            q['key'],
            q['text'],
            q['type'],
            q.get('help_text'),
            q['order'],
            True
        ))

        question_id = cursor.fetchone()[0]

        # Insert options
        if 'options' in q:
            # Delete existing options first
            cursor.execute("DELETE FROM question_options WHERE question_id = %s", (question_id,))

            for opt in q['options']:
                cursor.execute("""
                    INSERT INTO question_options (
                        question_id, option_value, option_label, display_order
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    question_id,
                    opt['value'],
                    opt['label'],
                    opt['order']
                ))
                print(f"  → {opt['label']}")

        conn.commit()

    print("\n" + "=" * 80)
    print("✓ Questions populated successfully!")
    print("=" * 80)

def display_summary(conn):
    """Display summary of populated data"""
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM questions WHERE is_active = TRUE")
    question_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM question_options WHERE is_active = TRUE")
    option_count = cursor.fetchone()[0]

    print(f"\nSummary:")
    print(f"  Questions: {question_count}")
    print(f"  Options: {option_count}")

    # Show questions
    cursor.execute("""
        SELECT question_key, question_type, question_text
        FROM questions
        WHERE is_active = TRUE
        ORDER BY display_order
    """)

    print("\n" + "-" * 80)
    print("Questions:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"  {row[0]:30} [{row[1]:8}] {row[2][:40]}...")

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
