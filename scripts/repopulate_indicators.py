"""
Clean and repopulate Indicators of Compliance from JSON file

This script:
1. Removes all existing indicators from the database
2. Loads indicators from FTA_Complete_Extraction.json
3. Inserts them with proper deduplication
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

def repopulate_indicators():
    """Remove all indicators and repopulate from JSON"""
    json_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'FTA_Complete_Extraction.json')

    print("\n" + "=" * 80)
    print("REPOPULATING INDICATORS OF COMPLIANCE")
    print("=" * 80)

    with open(json_path, 'r') as f:
        data = json.load(f)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Step 1: Check current count
    cursor.execute("SELECT COUNT(*) FROM indicators_of_compliance;")
    old_count = cursor.fetchone()[0]
    print(f"\n📊 Current indicators in database: {old_count}")

    # Step 2: Count indicators in JSON
    json_indicator_count = 0
    for section_data in data['sections']:
        for sub_area in section_data.get('sub_areas', []):
            indicators = sub_area.get('indicators_of_compliance', [])
            if indicators:
                json_indicator_count += len(indicators)
    print(f"📊 Indicators in JSON file: {json_indicator_count}")

    # Step 3: Delete all existing indicators
    print(f"\n🗑️  Deleting all existing indicators...")
    cursor.execute("DELETE FROM indicators_of_compliance;")
    conn.commit()
    print(f"✓ Deleted {old_count} indicators")

    # Step 4: Insert indicators from JSON
    print(f"\n📥 Inserting indicators from JSON file...")
    indicators_inserted = 0
    sub_areas_processed = 0
    sub_areas_with_indicators = 0

    for section_data in data['sections']:
        section = section_data['section']
        section_name = section.get('title', section.get('id', 'Unknown'))

        for sub_area in section_data.get('sub_areas', []):
            sub_areas_processed += 1
            sub_area_id = sub_area.get('sub_area_id') or sub_area.get('id')

            indicators = sub_area.get('indicators_of_compliance', [])
            if not indicators:
                continue

            sub_areas_with_indicators += 1

            for indicator in indicators:
                if not indicator:  # Skip None/empty values
                    continue

                indicator_id = indicator.get('indicator_id', '')
                text = indicator.get('text', '')

                if not indicator_id or not text:
                    print(f"⚠️  Skipping invalid indicator in {sub_area_id}: {indicator}")
                    continue

                try:
                    cursor.execute("""
                        INSERT INTO indicators_of_compliance (
                            sub_area_id, indicator_id, text
                        )
                        VALUES (%s, %s, %s)
                    """, (sub_area_id, indicator_id, text))
                    indicators_inserted += 1
                except Exception as e:
                    print(f"❌ Error inserting indicator {indicator_id} for {sub_area_id}: {e}")
                    conn.rollback()
                    raise

    conn.commit()

    # Step 5: Verify the results
    cursor.execute("SELECT COUNT(*) FROM indicators_of_compliance;")
    new_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT sub_area_id) FROM indicators_of_compliance;")
    sub_areas_in_db = cursor.fetchone()[0]

    # Check for any remaining duplicates
    cursor.execute("""
        SELECT sub_area_id, indicator_id, COUNT(*) as count
        FROM indicators_of_compliance
        GROUP BY sub_area_id, indicator_id
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("✓ INDICATORS REPOPULATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"  Old count: {old_count}")
    print(f"  New count: {new_count}")
    print(f"  Expected from JSON: {json_indicator_count}")
    print(f"  Sub-areas processed: {sub_areas_processed}")
    print(f"  Sub-areas with indicators: {sub_areas_with_indicators}")
    print(f"  Sub-areas in DB with indicators: {sub_areas_in_db}")

    if duplicates:
        print(f"\n⚠️  WARNING: {len(duplicates)} duplicate indicator(s) found:")
        for dup in duplicates[:5]:
            print(f"    {dup[0]} | {dup[1]} | Count: {dup[2]}")
    else:
        print(f"\n✓ No duplicates found!")

    if new_count == json_indicator_count:
        print(f"\n✅ SUCCESS: Indicator count matches JSON file!")
    else:
        print(f"\n⚠️  WARNING: Count mismatch (DB: {new_count}, JSON: {json_indicator_count})")

    print("=" * 80)

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        repopulate_indicators()
    else:
        print("\n⚠️  This script will DELETE all existing indicators and reload from JSON.")
        print("To run this script, use: python3 repopulate_indicators.py --confirm")
        print("❌ Cancelled")
