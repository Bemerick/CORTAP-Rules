"""Quick fix to analyze the missing LOE for DBE1"""

import json
import os
import psycopg2
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'fta_review')
    )

def analyze_sub_area_loe(sub_area):
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

Based on this information, estimate the number of hours and confidence level.

Respond in JSON format only:
{{
  "hours": <decimal number>,
  "confidence_level": "<high/medium/low>",
  "confidence_score": <integer 0-100>,
  "reasoning": "<brief explanation>"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

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

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON. Response was: {response_text}")
        raise

# Load FTA data
fta_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'FTA_Complete_Extraction.json')
with open(fta_file, 'r') as f:
    fta_data = json.load(f)

# Find DBE section and DBE1 sub-area
conn = get_db_connection()
cursor = conn.cursor()

for section in fta_data['sections']:
    if section['section']['id'] == 'DBE':
        for sub_area in section.get('sub_areas', []):
            if sub_area['id'] == 'DBE1':
                print(f"Analyzing {sub_area['id']}...")
                loe_data = analyze_sub_area_loe(sub_area)
                print(f"Result: {loe_data['hours']} hrs ({loe_data['confidence_level']} confidence)")

                # Update database
                cursor.execute("""
                    UPDATE sub_areas
                    SET loe_hours = %s, loe_confidence = %s, loe_confidence_score = %s, loe_reasoning = %s
                    WHERE id = %s
                """, (
                    loe_data['hours'],
                    loe_data['confidence_level'],
                    loe_data['confidence_score'],
                    loe_data['reasoning'],
                    'DBE1'
                ))
                conn.commit()
                print("✓ Database updated")
                break

cursor.close()
conn.close()
print("Done!")
