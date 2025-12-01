#!/usr/bin/env python3
"""
Generate LOE estimates for all sub-areas in Render database using Claude API
"""
import psycopg2
import json
import time
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Render database URL
RENDER_DATABASE_URL = 'postgresql://fta_review_db_user:ps2I2K6D4ntHnWpkqIL4lKzz2TyaLed8@dpg-d4mc0tuuk2gs738s90p0-a.oregon-postgres.render.com/fta_review_db'

# Initialize Anthropic client
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
client = Anthropic(api_key=api_key)

def get_render_connection():
    """Connect to Render database"""
    return psycopg2.connect(RENDER_DATABASE_URL)

def create_loe_prompt(sub_area):
    """Create a prompt for Claude to analyze LOE for a sub-area"""
    prompt = f"""You are an expert FTA (Federal Transit Administration) auditor and reviewer.
Analyze the following FTA Comprehensive Review sub-area and estimate the Level of Effort (LOE)
required for a reviewer to complete this review task.

**Sub-Area ID:** {sub_area['id']}

**Question:** {sub_area.get('question', 'N/A')}

**Basic Requirement:** {sub_area.get('basic_requirement', 'N/A')}

**Applicability:** {sub_area.get('applicability', 'N/A')}

**Detailed Explanation:** {sub_area.get('detailed_explanation', 'N/A')}

**Instructions for Reviewer:** {sub_area.get('instructions_for_reviewer', 'N/A')}

Based on this information, estimate:
1. The number of hours a trained FTA reviewer would need to complete this sub-area review
2. Your confidence level in this estimate (high/medium/low)
3. A confidence score (0-100)
4. A brief reasoning for your estimate

Consider factors such as:
- Complexity of the review instructions
- Number of items to verify
- Document review requirements
- Interview or site visit needs
- Analysis and reporting time

Respond in the following JSON format only (no other text):
{{
  "hours": <decimal number>,
  "confidence_level": "<high/medium/low>",
  "confidence_score": <integer 0-100>,
  "reasoning": "<brief explanation>"
}}"""

    return prompt

def analyze_sub_area_loe(sub_area):
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
        print(f"    ✗ Error analyzing sub-area {sub_area['id']}: {e}")
        return None

def generate_all_loe():
    """Generate LOE estimates for all sub-areas"""
    conn = get_render_connection()
    cursor = conn.cursor()

    print("=" * 80)
    print("GENERATING LOE ESTIMATES FOR ALL SUB-AREAS")
    print("=" * 80)

    # Get all sub-areas that don't have LOE data
    cursor.execute("""
        SELECT id, question, basic_requirement, applicability,
               detailed_explanation, instructions_for_reviewer
        FROM sub_areas
        WHERE loe_hours IS NULL OR loe_hours = 0
        ORDER BY id
    """)

    sub_areas = cursor.fetchall()
    total = len(sub_areas)

    print(f"\nFound {total} sub-areas without LOE data")
    print("Starting analysis...\n")

    successful = 0
    failed = 0

    for idx, row in enumerate(sub_areas, 1):
        sub_area = {
            'id': row[0],
            'question': row[1],
            'basic_requirement': row[2],
            'applicability': row[3],
            'detailed_explanation': row[4],
            'instructions_for_reviewer': row[5]
        }

        print(f"[{idx}/{total}] {sub_area['id']}... ", end='', flush=True)

        # Analyze LOE using Claude
        loe_data = analyze_sub_area_loe(sub_area)

        if loe_data:
            # Update database
            try:
                cursor.execute("""
                    UPDATE sub_areas
                    SET loe_hours = %s,
                        loe_confidence = %s,
                        loe_confidence_score = %s,
                        loe_reasoning = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    loe_data['hours'],
                    loe_data['confidence_level'],
                    loe_data['confidence_score'],
                    loe_data['reasoning'],
                    sub_area['id']
                ))
                conn.commit()
                print(f"✓ {loe_data['hours']}h ({loe_data['confidence_level']})")
                successful += 1
            except Exception as e:
                print(f"✗ Failed to update: {e}")
                failed += 1
                conn.rollback()
        else:
            print(f"✗ Failed to analyze")
            failed += 1

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    # Get final summary
    cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(loe_hours) as with_loe,
               SUM(loe_hours) as total_hours,
               AVG(loe_hours) as avg_hours,
               AVG(loe_confidence_score) as avg_confidence
        FROM sub_areas
    """)
    result = cursor.fetchone()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total sub-areas: {result[0]}")
    print(f"With LOE data: {result[1]} ({result[1]/result[0]*100:.1f}%)")
    print(f"Analyzed in this run: {successful}")
    print(f"Failed: {failed}")
    if result[2]:
        print(f"\nTotal estimated hours: {result[2]:.2f}")
        print(f"Average hours per sub-area: {result[3]:.2f}")
        print(f"Average confidence score: {result[4]:.1f}%")
    print("=" * 80)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    try:
        generate_all_loe()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
