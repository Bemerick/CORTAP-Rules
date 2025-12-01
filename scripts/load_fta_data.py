"""
Load FTA sections and sub-areas data from JSON file into the database
"""

import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Use DATABASE_URL if available (for Render), otherwise construct from individual vars
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'fta_review')}"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def load_data():
    """Load sections and sub-areas from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'FTA_Complete_Extraction.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("LOADING FTA COMPREHENSIVE REVIEW DATA")
    print("=" * 80)

    sections_loaded = 0
    sub_areas_loaded = 0
    indicators_loaded = 0
    deficiencies_loaded = 0

    for section_data in data['sections']:
        section = section_data['section']

        # Insert section
        cursor.execute("""
            INSERT INTO sections (id, title, page_range, purpose)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                page_range = EXCLUDED.page_range,
                purpose = EXCLUDED.purpose,
                updated_at = CURRENT_TIMESTAMP
        """, (
            section['id'],
            section['title'],
            section.get('page_range'),
            section.get('purpose')
        ))
        sections_loaded += 1
        print(f"\n[{sections_loaded}] Section: {section['title']}")

        # Insert sub-areas
        for sub_area in section_data.get('sub_areas', []):
            cursor.execute("""
                INSERT INTO sub_areas (
                    id, section_id, question, basic_requirement,
                    applicability, detailed_explanation, instructions_for_reviewer
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    question = EXCLUDED.question,
                    basic_requirement = EXCLUDED.basic_requirement,
                    applicability = EXCLUDED.applicability,
                    detailed_explanation = EXCLUDED.detailed_explanation,
                    instructions_for_reviewer = EXCLUDED.instructions_for_reviewer,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                sub_area['id'],
                section['id'],
                sub_area.get('question'),
                sub_area.get('basic_requirement'),
                sub_area.get('applicability'),
                sub_area.get('detailed_explanation'),
                sub_area.get('instructions_for_reviewer')
            ))
            sub_areas_loaded += 1
            print(f"  → Sub-area {sub_area['id']}: {sub_area.get('question', '')[:60]}...")

            # Insert indicators of compliance
            indicators = sub_area.get('indicators_of_compliance') or []
            for indicator in indicators:
                if indicator:  # Skip None values
                    cursor.execute("""
                        INSERT INTO indicators_of_compliance (
                            sub_area_id, indicator_id, text
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        sub_area['id'],
                        indicator.get('indicator_id'),
                        indicator.get('text')
                    ))
                    indicators_loaded += 1

            # Insert deficiencies
            deficiencies = sub_area.get('deficiencies') or []
            for deficiency in deficiencies:
                if deficiency:  # Skip None values
                    cursor.execute("""
                        INSERT INTO deficiencies (
                            sub_area_id, code, title, determination, suggested_corrective_action
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (
                        sub_area['id'],
                        deficiency.get('code'),
                        deficiency.get('title'),
                        deficiency.get('determination'),
                        deficiency.get('suggested_corrective_action')
                    ))
                    deficiencies_loaded += 1

        conn.commit()

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("✓ DATA LOADED SUCCESSFULLY!")
    print("=" * 80)
    print(f"  Sections: {sections_loaded}")
    print(f"  Sub-areas: {sub_areas_loaded}")
    print(f"  Indicators: {indicators_loaded}")
    print(f"  Deficiencies: {deficiencies_loaded}")
    print("=" * 80)

if __name__ == '__main__':
    load_data()
