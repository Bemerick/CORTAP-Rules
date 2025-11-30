"""
Complete LOE Analysis Script - Handles all 173 sub-areas including duplicates
This script fixes duplicate IDs by appending sequential suffixes
"""

import json
import os
import time
from typing import Dict, List, Optional
from collections import defaultdict
import psycopg2
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def get_db_connection():
    """Create and return a database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'fta_review')
    )

def load_fta_data(file_path: str) -> Dict:
    """Load FTA extraction JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_unique_ids(fta_data: Dict) -> Dict:
    """
    Create unique IDs for duplicate sub-areas by appending sequential suffixes
    Returns mapping of original_id -> list of (unique_id, sub_area_data)
    """
    id_counter = defaultdict(int)
    modified_data = {'metadata': fta_data['metadata'], 'sections': []}

    for section in fta_data['sections']:
        new_section = {
            'section': section['section'],
            'sub_areas': []
        }

        for sub_area in section.get('sub_areas', []):
            original_id = sub_area['id']
            id_counter[original_id] += 1

            # If this ID has appeared before, add suffix
            if id_counter[original_id] > 1:
                unique_id = f"{original_id}_{id_counter[original_id]}"
                print(f"  ⚠️  Duplicate ID '{original_id}' renamed to '{unique_id}'")
            else:
                unique_id = original_id

            # Create new sub-area with unique ID
            new_sub_area = sub_area.copy()
            new_sub_area['original_id'] = original_id
            new_sub_area['id'] = unique_id
            new_section['sub_areas'].append(new_sub_area)

        modified_data['sections'].append(new_section)

    return modified_data

def create_loe_prompt(sub_area: Dict) -> str:
    """Create a prompt for Claude to analyze LOE for a sub-area"""
    prompt = f"""You are an expert FTA (Federal Transit Administration) auditor and reviewer.
Analyze the following FTA Comprehensive Review sub-area and estimate the Level of Effort (LOE)
required for a reviewer to complete this review task.

**Sub-Area ID:** {sub_area.get('id', 'N/A')}

**Question:** {sub_area.get('question', 'N/A')}

**Basic Requirement:** {sub_area.get('basic_requirement', 'N/A')}

**Applicability:** {sub_area.get('applicability', 'N/A')}

**Detailed Explanation:** {sub_area.get('detailed_explanation', 'N/A')}

**Instructions for Reviewer:** {sub_area.get('instructions_for_reviewer', 'N/A')}

**Indicators of Compliance:**
{json.dumps(sub_area.get('indicators_of_compliance', []), indent=2)}

**Deficiencies:**
{json.dumps(sub_area.get('deficiencies', []), indent=2)}

Based on this information, estimate:
1. The number of hours a trained FTA reviewer would need to complete this sub-area review
2. Your confidence level in this estimate (high/medium/low)
3. A confidence score (0-100)
4. A brief reasoning for your estimate

Consider factors such as:
- Complexity of the review instructions
- Number of indicators to verify
- Document review requirements
- Interview or site visit needs
- Analysis and reporting time
- Number and complexity of potential deficiencies

Respond in the following JSON format only (no other text):
{{
  "hours": <decimal number>,
  "confidence_level": "<high/medium/low>",
  "confidence_score": <integer 0-100>,
  "reasoning": "<brief explanation>"
}}"""

    return prompt

def analyze_sub_area_loe(sub_area: Dict) -> Optional[Dict]:
    """Use Claude API to analyze LOE for a sub-area"""
    try:
        prompt = create_loe_prompt(sub_area)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the response text
        response_text = message.content[0].text.strip()

        # Try to extract JSON from response if it's wrapped in markdown
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            response_text = response_text[start:end].strip()
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.find('```', start)
            response_text = response_text[start:end].strip()

        # Parse JSON response
        loe_data = json.loads(response_text)

        return loe_data

    except Exception as e:
        print(f"    ✗ Error analyzing sub-area {sub_area.get('id')}: {e}")
        return None

def insert_section(cursor, section_data: Dict):
    """Insert a section into the database"""
    cursor.execute("""
        INSERT INTO sections (id, title, page_range, purpose)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            page_range = EXCLUDED.page_range,
            purpose = EXCLUDED.purpose,
            updated_at = CURRENT_TIMESTAMP
    """, (
        section_data.get('id'),
        section_data.get('title'),
        section_data.get('page_range'),
        section_data.get('purpose')
    ))

def insert_sub_area(cursor, section_id: str, sub_area: Dict, loe_data: Optional[Dict]):
    """Insert a sub-area with LOE data into the database"""
    cursor.execute("""
        INSERT INTO sub_areas (
            id, section_id, question, basic_requirement, applicability,
            detailed_explanation, instructions_for_reviewer,
            loe_hours, loe_confidence, loe_confidence_score, loe_reasoning
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            section_id = EXCLUDED.section_id,
            question = EXCLUDED.question,
            basic_requirement = EXCLUDED.basic_requirement,
            applicability = EXCLUDED.applicability,
            detailed_explanation = EXCLUDED.detailed_explanation,
            instructions_for_reviewer = EXCLUDED.instructions_for_reviewer,
            loe_hours = EXCLUDED.loe_hours,
            loe_confidence = EXCLUDED.loe_confidence,
            loe_confidence_score = EXCLUDED.loe_confidence_score,
            loe_reasoning = EXCLUDED.loe_reasoning,
            updated_at = CURRENT_TIMESTAMP
    """, (
        sub_area.get('id'),
        section_id,
        sub_area.get('question'),
        sub_area.get('basic_requirement'),
        sub_area.get('applicability'),
        sub_area.get('detailed_explanation'),
        sub_area.get('instructions_for_reviewer'),
        loe_data.get('hours') if loe_data else None,
        loe_data.get('confidence_level') if loe_data else None,
        loe_data.get('confidence_score') if loe_data else None,
        loe_data.get('reasoning') if loe_data else None
    ))

def insert_indicators(cursor, sub_area_id: str, indicators: List[Dict]):
    """Insert indicators of compliance"""
    # Delete existing indicators
    cursor.execute("DELETE FROM indicators_of_compliance WHERE sub_area_id = %s", (sub_area_id,))

    # Insert new indicators
    for indicator in indicators:
        cursor.execute("""
            INSERT INTO indicators_of_compliance (sub_area_id, indicator_id, text)
            VALUES (%s, %s, %s)
        """, (
            sub_area_id,
            indicator.get('indicator_id'),
            indicator.get('text')
        ))

def insert_deficiencies(cursor, sub_area_id: str, deficiencies: List[Dict]):
    """Insert deficiencies"""
    # Delete existing deficiencies
    cursor.execute("DELETE FROM deficiencies WHERE sub_area_id = %s", (sub_area_id,))

    # Insert new deficiencies
    for deficiency in deficiencies:
        cursor.execute("""
            INSERT INTO deficiencies (sub_area_id, code, title, determination, suggested_corrective_action)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            sub_area_id,
            deficiency.get('code'),
            deficiency.get('title'),
            deficiency.get('determination'),
            deficiency.get('suggested_corrective_action')
        ))

def insert_governing_directives(cursor, sub_area_id: str, directives: List[Dict]):
    """Insert governing directives"""
    # Delete existing directives
    cursor.execute("DELETE FROM governing_directives WHERE sub_area_id = %s", (sub_area_id,))

    # Insert new directives
    for directive in directives:
        cursor.execute("""
            INSERT INTO governing_directives (sub_area_id, reference, text)
            VALUES (%s, %s, %s)
        """, (
            sub_area_id,
            directive.get('reference'),
            directive.get('text')
        ))

def process_fta_data(fta_data: Dict):
    """Process FTA data and populate database with LOE analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()

    total_sections = len(fta_data.get('sections', []))
    total_sub_areas = sum(len(section.get('sub_areas', [])) for section in fta_data.get('sections', []))

    print(f"\n🚀 Starting COMPLETE LOE analysis for {total_sections} sections and {total_sub_areas} sub-areas...")
    print("=" * 80)

    processed_sub_areas = 0
    successful_analyses = 0
    failed_analyses = 0

    try:
        for section_idx, section in enumerate(fta_data.get('sections', []), 1):
            section_data = section.get('section', {})
            section_id = section_data.get('id')

            print(f"\n[{section_idx}/{total_sections}] Section: {section_id} - {section_data.get('title')}")
            print(f"  Sub-areas: {len(section.get('sub_areas', []))}")

            # Insert section
            insert_section(cursor, section_data)

            # Process sub-areas
            for sub_area in section.get('sub_areas', []):
                sub_area_id = sub_area.get('id')
                print(f"    → {sub_area_id}... ", end='', flush=True)

                # Analyze LOE using Claude
                loe_data = analyze_sub_area_loe(sub_area)

                if loe_data:
                    print(f"✓ {loe_data.get('hours')}h ({loe_data.get('confidence_level')})")
                    successful_analyses += 1
                else:
                    print(f"✗ Failed")
                    failed_analyses += 1

                # Insert sub-area with LOE data
                insert_sub_area(cursor, section_id, sub_area, loe_data)

                # Insert related data
                if sub_area.get('indicators_of_compliance'):
                    insert_indicators(cursor, sub_area_id, sub_area.get('indicators_of_compliance'))

                if sub_area.get('deficiencies'):
                    insert_deficiencies(cursor, sub_area_id, sub_area.get('deficiencies'))

                if sub_area.get('governing_directives'):
                    insert_governing_directives(cursor, sub_area_id, sub_area.get('governing_directives'))

                processed_sub_areas += 1

                # Commit after each sub-area to save progress
                conn.commit()

                # Small delay to avoid rate limiting
                time.sleep(0.5)

        print("\n" + "=" * 80)
        print(f"✓ Successfully processed {processed_sub_areas} sub-areas!")
        print(f"  ✓ Successful LOE analyses: {successful_analyses}")
        print(f"  ✗ Failed LOE analyses: {failed_analyses}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def display_summary():
    """Display a summary of LOE data from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get overall summary
        cursor.execute("""
            SELECT
                COUNT(*) as total_sub_areas,
                COUNT(loe_hours) as analyzed,
                SUM(loe_hours) as total_hours,
                AVG(loe_hours) as avg_hours,
                AVG(loe_confidence_score) as avg_confidence,
                MIN(loe_hours) as min_hours,
                MAX(loe_hours) as max_hours
            FROM sub_areas
        """)

        result = cursor.fetchone()

        print("\n" + "=" * 80)
        print("COMPLETE LOE ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Total Sub-Areas:     {result[0]}")
        print(f"Analyzed:            {result[1]}")
        print(f"Total Hours:         {result[2]:.2f} hrs")
        print(f"Average Hours:       {result[3]:.2f} hrs per sub-area")
        print(f"Average Confidence:  {result[4]:.1f}%")
        print(f"Range:               {result[5]:.2f} - {result[6]:.2f} hrs")
        print("=" * 80)

        # Get section summary
        cursor.execute("""
            SELECT section_id, section_title, total_sub_areas, total_hours, avg_confidence
            FROM section_loe_summary
            ORDER BY total_hours DESC
        """)
        sections = cursor.fetchall()

        print("\nSECTION BREAKDOWN (by total hours):")
        print("-" * 80)
        for section in sections:
            section_id, title, sub_areas, hours, confidence = section
            if hours:
                print(f"{section_id:15} {title[:45]:45} {sub_areas:3} SA  {hours:7.2f}h ({confidence:.0f}%)")
        print("=" * 80)

    finally:
        cursor.close()
        conn.close()

def main():
    """Main execution function"""
    # Path to FTA extraction file
    fta_file_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'docs',
        'FTA_Complete_Extraction.json'
    )

    print("=" * 80)
    print("FTA COMPREHENSIVE REVIEW - COMPLETE LOE ANALYSIS")
    print("=" * 80)

    # Load FTA data
    print(f"\n📁 Loading FTA data from: {fta_file_path}")
    fta_data = load_fta_data(fta_file_path)
    print(f"  ✓ Loaded {fta_data['metadata']['total_sections']} sections")

    total_sub_areas = sum(len(section.get('sub_areas', [])) for section in fta_data['sections'])
    print(f"  ✓ Found {total_sub_areas} sub-areas")

    # Fix duplicate IDs
    print(f"\n🔧 Fixing duplicate sub-area IDs...")
    fta_data = create_unique_ids(fta_data)

    # Process and analyze
    process_fta_data(fta_data)

    # Display summary
    display_summary()

if __name__ == '__main__':
    main()
