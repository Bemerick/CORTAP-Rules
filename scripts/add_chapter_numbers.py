#!/usr/bin/env python3
"""
Add chapter numbers to sections table and update all sections
"""
import psycopg2

# Render database URL
RENDER_DATABASE_URL = 'postgresql://fta_review_db_user:ps2I2K6D4ntHnWpkqIL4lKzz2TyaLed8@dpg-d4mc0tuuk2gs738s90p0-a.oregon-postgres.render.com/fta_review_db'

def get_render_connection():
    """Connect to Render database"""
    return psycopg2.connect(RENDER_DATABASE_URL)

# Chapter number mapping based on section titles and IDs
CHAPTER_MAPPING = {
    'LEGAL': 1,
    'FINANCIAL MANAGEMENT AND CAPACITY': 2,
    'TECHNICAL CAPACITY -AWARD MANAGEMENT': 3,
    'TECHNICAL CAPACITY – AWARD MANAGEMENT': 3,  # Alternative dash
    'TECHNICAL CAPACITY -PROGRAM MANAGEMENT AND SUBRECIPIENT OVERSIGHT': 4,
    'TECHNICAL CAPACITY – PROGRAM MANAGEMENT AND SUBRECIPIENT OVERSIGHT': 4,  # Alternative dash
    'TECHNICAL CAPACITY -PROJECT MANAGEMENT': 5,
    'TECHNICAL CAPACITY – PROJECT MANAGEMENT': 5,  # Alternative dash
    'TRANSIT ASSET MANAGEMENT': 6,
    'SATISFACTORY CONTINUING CONTROL': 7,
    'MAINTENANCE': 8,
    'PROCUREMENT': 9,
    'DISADVANTAGED BUSINESS ENTERPRISE': 10,
    'DISADVANTAGED BUSINESS ENTERPRISE (DBE)': 10,
    'TITLE VI': 11,
    'AMERICANS WITH DISABILITIES ACT -GENERAL': 12,
    'AMERICANS WITH DISABILITIES ACT (ADA) - GENERAL': 12,
    'AMERICANS WITH DISABILITIES ACT -COMPLEMENTARY PARATRANSIT': 13,
    '13. AMERICANS WITH DISABILITIES ACT (ADA) COMPLEMENTARY PARATRANSIT': 13,
    'EQUAL EMPLOYMENT OPPORTUNITY': 14,
    'EQUAL EMPLOYMENT OPPORTUNITY (EEO)': 14,
    'SCHOOL BUS': 15,
    'CHARTER BUS': 16,
    'DRUG-FREE WORKPLACE ACT': 17,
    'DRUG AND ALCOHOL PROGRAM': 18,
    'SECTION 5307 PROGRAM REQUIREMENTS': 19,
    'SECTION 5310 PROGRAM REQUIREMENTS': 20,
    'SECTION 5311 PROGRAM REQUIREMENTS': 21,
    'PUBLIC TRANSPORTATION AGENCY SAFETY PLANS': 22,
    'PUBLIC TRANSPORTATION AGENCY SAFETY PLAN (PTASP)': 22,
    'CYBERSECURITY': 23,
    '23. CYBERSECURITY': 23
}

def add_chapter_numbers():
    """Add chapter_number column and update all sections"""
    conn = get_render_connection()
    cursor = conn.cursor()

    print("=" * 80)
    print("ADDING CHAPTER NUMBERS TO SECTIONS")
    print("=" * 80)

    # Add chapter_number column if it doesn't exist
    try:
        cursor.execute("""
            ALTER TABLE sections
            ADD COLUMN IF NOT EXISTS chapter_number INTEGER
        """)
        conn.commit()
        print("✓ Added chapter_number column to sections table")
    except Exception as e:
        print(f"⚠ Column may already exist: {e}")
        conn.rollback()

    # Get all sections
    cursor.execute("SELECT id, title FROM sections ORDER BY id")
    sections = cursor.fetchall()

    print(f"\nFound {len(sections)} sections to update\n")

    updated = 0
    not_found = []

    for section_id, title in sections:
        # Find matching chapter number (case-insensitive, strip whitespace)
        title_upper = title.strip().upper()
        chapter_number = None

        for section_title, chapter in CHAPTER_MAPPING.items():
            if section_title.upper() == title_upper:
                chapter_number = chapter
                break

        if chapter_number:
            cursor.execute("""
                UPDATE sections
                SET chapter_number = %s
                WHERE id = %s
            """, (chapter_number, section_id))
            updated += 1
            print(f"✓ {chapter_number:2}. {title[:60]}")
        else:
            not_found.append((section_id, title))
            print(f"⚠ NOT MAPPED: {section_id} - {title}")

    conn.commit()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total sections: {len(sections)}")
    print(f"Updated: {updated}")
    print(f"Not mapped: {len(not_found)}")

    if not_found:
        print("\n⚠ Sections without chapter numbers:")
        for section_id, title in not_found:
            print(f"  {section_id}: {title}")

    # Verify the updates
    cursor.execute("""
        SELECT chapter_number, id, title
        FROM sections
        WHERE chapter_number IS NOT NULL
        ORDER BY chapter_number
    """)

    results = cursor.fetchall()
    print("\n" + "=" * 80)
    print("VERIFICATION - Sections with Chapter Numbers:")
    print("=" * 80)
    for chapter, section_id, title in results:
        print(f"{chapter:2}. {title}")

    print("=" * 80)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    try:
        add_chapter_numbers()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
