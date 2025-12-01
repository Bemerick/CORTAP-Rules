#!/usr/bin/env python3
"""
Create basic applicability rules for "All recipients" sub-areas
"""
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL') or 'postgresql://fta_review_db_user:ps2I2K6D4ntHnWpkqIL4lKzz2TyaLed8@dpg-d4mc0tuuk2gs738s90p0-a.oregon-postgres.render.com/fta_review_db'

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("Creating basic applicability rules...")

# Get question ID for "recipient_type" (question 1)
cursor.execute("SELECT id FROM questionnaire_questions WHERE question_number = 1")
recipient_type_q = cursor.fetchone()[0]

# Get all sub-areas that have "All recipients" applicability
cursor.execute("""
    SELECT id FROM sub_areas
    WHERE applicability ILIKE '%all recipients%'
""")
all_recipient_sub_areas = cursor.fetchall()

print(f"Found {len(all_recipient_sub_areas)} sub-areas applicable to all recipients")

# Create rules for "all recipients" sub-areas
# These apply when question 1 is answered with any value
rules_created = 0
for (sub_area_id,) in all_recipient_sub_areas:
    for answer in ['all', 'state', 'non_state']:
        cursor.execute("""
            INSERT INTO applicability_rules (sub_area_id, question_id, required_answer, rule_type)
            VALUES (%s, %s, %s, 'include')
            ON CONFLICT (sub_area_id, question_id) DO NOTHING
        """, (sub_area_id, recipient_type_q, answer))
        rules_created += 1

conn.commit()
print(f"✓ Created {rules_created} applicability rules for 'All recipients' sub-areas")

cursor.close()
conn.close()
