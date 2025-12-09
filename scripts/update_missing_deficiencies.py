#!/usr/bin/env python3
"""
Update Missing Deficiencies Script

This script extracts deficiencies from the FTA_Complete_Extraction.json file
and updates the database with missing deficiency data.

It specifically targets sub-areas that currently have no deficiency records.
"""

import json
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

# Load environment variables from scripts/.env first, then parent
load_dotenv()  # Loads from scripts/.env if it exists

# Database connection - allow override via command line argument
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:Forest12345#@localhost:5432/fta_review')


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)


def get_sub_areas_without_deficiencies(conn):
    """Get list of sub_area_ids that have no deficiencies"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT sa.id as sub_area_id, s.title as section_title
            FROM sub_areas sa
            JOIN sections s ON sa.section_id = s.id
            LEFT JOIN deficiencies d ON sa.id = d.sub_area_id
            WHERE d.id IS NULL
            ORDER BY s.title, sa.id;
        """)
        return {row[0]: row[1] for row in cur.fetchall()}


def load_json_data(json_path):
    """Load data from FTA_Complete_Extraction.json"""
    with open(json_path, 'r') as f:
        return json.load(f)


def extract_deficiencies_from_json(data, missing_sub_area_ids):
    """Extract deficiencies for missing sub-areas from JSON data"""
    # Use a dict to track sub_areas we've already processed (to handle duplicates)
    processed_sub_areas = set()
    sub_areas_without_deficiencies = set()
    deficiencies_to_add = []

    for section in data.get('sections', []):
        for sub_area in section.get('sub_areas', []):
            sub_area_id = sub_area.get('id')

            # Only process if this sub_area is in our missing list
            if sub_area_id in missing_sub_area_ids:
                deficiencies_list = sub_area.get('deficiencies', [])

                if deficiencies_list:
                    # Skip if we've already processed this sub_area with deficiencies
                    if sub_area_id in processed_sub_areas:
                        continue

                    processed_sub_areas.add(sub_area_id)
                    print(f"Found {len(deficiencies_list)} deficiencies for {sub_area_id}")

                    for deficiency in deficiencies_list:
                        deficiencies_to_add.append({
                            'sub_area_id': sub_area_id,
                            'code': deficiency.get('code', ''),
                            'title': deficiency.get('title', ''),
                            'determination': deficiency.get('determination', ''),
                            'suggested_corrective_action': deficiency.get('suggested_corrective_action', '')
                        })
                else:
                    # Track sub_areas without deficiencies
                    sub_areas_without_deficiencies.add(sub_area_id)

    # Warn about sub_areas that have no deficiencies in the JSON
    for sub_area_id in missing_sub_area_ids:
        if sub_area_id not in processed_sub_areas and sub_area_id in sub_areas_without_deficiencies:
            print(f"WARNING: No deficiencies found in JSON for {sub_area_id} ({missing_sub_area_ids[sub_area_id]})")

    return deficiencies_to_add


def insert_deficiencies(conn, deficiencies):
    """Insert deficiencies into the database"""
    if not deficiencies:
        print("No deficiencies to insert")
        return 0

    with conn.cursor() as cur:
        # Prepare data for batch insert
        values = [
            (
                d['sub_area_id'],
                d['code'],
                d['title'],
                d['determination'],
                d['suggested_corrective_action']
            )
            for d in deficiencies
        ]

        # Batch insert
        execute_values(
            cur,
            """
            INSERT INTO deficiencies (sub_area_id, code, title, determination, suggested_corrective_action)
            VALUES %s
            """,
            values
        )

        conn.commit()
        return len(values)


def main():
    """Main execution function"""
    import sys

    print("=" * 80)
    print("Update Missing Deficiencies Script")
    print("=" * 80)

    # Allow DATABASE_URL override via command line
    global DATABASE_URL
    if len(sys.argv) > 1:
        DATABASE_URL = sys.argv[1]
        print(f"\nUsing database from command line argument")

    # Show which database we're connecting to (mask password)
    db_display = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL
    print(f"Target database: {db_display}")

    # Path to JSON file
    json_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'FTA_Complete_Extraction.json')

    if not os.path.exists(json_path):
        print(f"ERROR: JSON file not found at {json_path}")
        return

    print(f"\nJSON file: {json_path}")

    # Connect to database
    print("\nConnecting to database...")
    conn = get_db_connection()

    try:
        # Get sub-areas without deficiencies
        print("\nFinding sub-areas without deficiencies...")
        missing_sub_areas = get_sub_areas_without_deficiencies(conn)
        print(f"Found {len(missing_sub_areas)} sub-areas without deficiencies:")
        for sub_area_id, section_title in missing_sub_areas.items():
            print(f"  - {sub_area_id} ({section_title})")

        # Load JSON data
        print("\nLoading JSON data...")
        json_data = load_json_data(json_path)
        print(f"Loaded {len(json_data.get('sections', []))} sections from JSON")

        # Extract deficiencies for missing sub-areas
        print("\nExtracting deficiencies from JSON...")
        deficiencies_to_add = extract_deficiencies_from_json(json_data, missing_sub_areas)
        print(f"Found {len(deficiencies_to_add)} deficiencies to add")

        if deficiencies_to_add:
            # Show preview
            print("\nDeficiencies to be added:")
            for d in deficiencies_to_add:
                print(f"  - {d['sub_area_id']}: {d['code']} - {d['title']}")

            # Confirm before inserting
            response = input("\nProceed with insertion? (yes/no): ").strip().lower()

            if response == 'yes':
                print("\nInserting deficiencies into database...")
                count = insert_deficiencies(conn, deficiencies_to_add)
                print(f"Successfully inserted {count} deficiencies")
            else:
                print("Insertion cancelled by user")
        else:
            print("\nNo deficiencies to add (all sub-areas either have deficiencies or none exist in JSON)")

    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()
        print("\nDatabase connection closed")

    print("\n" + "=" * 80)
    print("Script completed")
    print("=" * 80)


if __name__ == "__main__":
    main()
