"""
Populate applicability rules from FTA JSON data
Parses natural language applicability criteria into structured database rules
"""

import json
import os
import re
import psycopg2
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

def parse_applicability(applicability_text):
    """
    Parse natural language applicability into structured conditions
    Returns list of condition tuples: (question_key, operator, expected_value)
    """
    if not applicability_text:
        return []

    text_lower = applicability_text.lower()
    conditions = []

    # Rule: All recipients
    if text_lower == 'all recipients':
        return [('recipient_type', 'in', 'all,state,non_state')]

    # Rule: $750,000 threshold
    if '$750,000' in text_lower or '750,000' in text_lower:
        conditions.append(('federal_assistance_amount', 'equals', 'gte_750k'))

    # Rule: Subrecipients
    if 'subrecipient' in text_lower:
        conditions.append(('has_subrecipients', 'equals', 'yes'))

    # Rule: Contractors and lessees
    if 'contractor' in text_lower or 'lessee' in text_lower:
        conditions.append(('has_contractors_lessees', 'equals', 'yes'))

    # Rule: Tier I
    if re.search(r'\btier\s*i\b', text_lower) and 'tier ii' not in text_lower:
        conditions.append(('tier_level', 'equals', 'tier_1'))

    # Rule: Tier II
    if 'tier ii' in text_lower:
        conditions.append(('tier_level', 'equals', 'tier_2'))

    # Rule: State recipients
    if re.search(r'\bnon-state\b', text_lower):
        conditions.append(('recipient_type', 'equals', 'non_state'))
    elif re.search(r'\bstate\s+recipient', text_lower) and 'non-state' not in text_lower:
        conditions.append(('recipient_type', 'equals', 'state'))

    # Rule: Section 5310 funds
    if re.search(r'\b5310\b', text_lower):
        conditions.append(('fund_types', 'in', '5310'))

    # Rule: Section 5311 funds
    if re.search(r'\b5311\b', text_lower):
        conditions.append(('fund_types', 'in', '5311'))

    # Rule: Section 5307 funds
    if re.search(r'\b5307\b', text_lower):
        conditions.append(('fund_types', 'in', '5307'))

    # Rule: Section 5337 funds
    if re.search(r'\b5337\b', text_lower):
        conditions.append(('fund_types', 'in', '5337'))

    # Rule: Designated recipient
    if 'designated recipient' in text_lower:
        conditions.append(('is_designated_recipient', 'equals', 'yes'))

    # Rule: Fixed-route service
    if 'fixed-route' in text_lower or 'fixed route' in text_lower:
        # Check if it excludes commuter
        if 'other than commuter' in text_lower or 'excluding commuter' in text_lower:
            # This requires fixed-route but NOT commuter rail/bus
            # We'll need multiple rules for this
            pass  # Handle complex case separately
        else:
            conditions.append(('service_type', 'in', 'fixed_route'))

    # Rule: Demand response
    if 'demand response' in text_lower:
        conditions.append(('service_type', 'in', 'demand_response'))

    # Rule: Commuter rail
    if 'commuter rail' in text_lower:
        conditions.append(('service_type', 'in', 'commuter_rail'))

    # Rule: Commuter bus
    if 'commuter bus' in text_lower:
        conditions.append(('service_type', 'in', 'commuter_bus'))

    # Rule: Public operator/provider
    if 'public operator' in text_lower or 'public provider' in text_lower:
        conditions.append(('is_public_operator', 'equals', 'yes'))

    # Rule: Group plan participant
    if 'group plan participant' in text_lower:
        conditions.append(('group_plan', 'equals', 'participant'))

    # Rule: Group plan sponsor
    if 'group plan sponsor' in text_lower:
        conditions.append(('group_plan', 'equals', 'sponsor'))

    # Rule: DBE overall goal
    if 'overall goal' in text_lower or 'dbe goal' in text_lower:
        conditions.append(('has_dbe_goal', 'equals', 'yes'))

    # Rule: Direct control over assets
    if 'direct control' in text_lower and 'asset' in text_lower:
        conditions.append(('asset_control', 'equals', 'yes'))

    # Rule: FTA-funded real property
    if 'fta-funded real property' in text_lower:
        conditions.append(('asset_control', 'equals', 'yes'))

    # Rule: FTA-funded equipment
    if 'fta-funded equipment' in text_lower and 'real property' not in text_lower:
        conditions.append(('asset_control', 'equals', 'yes'))

    return conditions

def create_rule(cursor, sub_area_id, applicability_text, conditions):
    """Create an applicability rule with conditions"""

    # If no specific conditions, this applies to all
    if not conditions:
        conditions = [('recipient_type', 'in', 'all,state,non_state')]

    # Create the rule
    cursor.execute("""
        INSERT INTO applicability_rules (
            sub_area_id,
            rule_description,
            priority,
            is_active
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        sub_area_id,
        applicability_text or 'All recipients',
        0,
        True
    ))

    rule_id = cursor.fetchone()[0]

    # Create conditions
    for question_key, operator, expected_value in conditions:
        cursor.execute("""
            INSERT INTO rule_conditions (
                rule_id,
                question_key,
                operator,
                expected_value,
                is_active
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            rule_id,
            question_key,
            operator,
            expected_value,
            True
        ))

    return rule_id

def populate_rules(conn):
    """Populate applicability rules from FTA JSON"""
    cursor = conn.cursor()

    # Load FTA data
    fta_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'FTA_Complete_Extraction.json')
    with open(fta_file, 'r') as f:
        fta_data = json.load(f)

    print("\n" + "=" * 80)
    print("POPULATING APPLICABILITY RULES")
    print("=" * 80)

    total_rules = 0
    total_conditions = 0
    sections_processed = 0

    # Track ID renaming for duplicates
    id_counter = {}

    for section in fta_data['sections']:
        section_id = section['section']['id']
        sections_processed += 1

        print(f"\n[{sections_processed}/23] Section: {section_id}")

        for sub_area in section.get('sub_areas', []):
            original_id = sub_area['id']

            # Handle duplicate IDs (same logic as LOE script)
            id_counter[original_id] = id_counter.get(original_id, 0) + 1
            if id_counter[original_id] > 1:
                sub_area_id = f"{original_id}_{id_counter[original_id]}"
            else:
                sub_area_id = original_id

            applicability_text = sub_area.get('applicability', '')

            # Parse applicability into conditions
            conditions = parse_applicability(applicability_text)

            # Create rule
            rule_id = create_rule(cursor, sub_area_id, applicability_text, conditions)
            total_rules += 1
            total_conditions += len(conditions) if conditions else 0

            cond_str = ', '.join([f"{c[0]}={c[2]}" for c in conditions[:2]]) if conditions else "all"
            if len(conditions) > 2:
                cond_str += "..."

            print(f"  {sub_area_id:15} → Rule #{rule_id:3} ({len(conditions)} conditions): {cond_str}")

        conn.commit()

    print("\n" + "=" * 80)
    print(f"✓ Created {total_rules} rules with {total_conditions} conditions")
    print("=" * 80)

def display_summary(conn):
    """Display summary of rules"""
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM applicability_rules WHERE is_active = TRUE")
    rule_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM rule_conditions WHERE is_active = TRUE")
    condition_count = cursor.fetchone()[0]

    print(f"\nSummary:")
    print(f"  Rules: {rule_count}")
    print(f"  Conditions: {condition_count}")

    # Sample rules
    cursor.execute("""
        SELECT
            ar.id,
            ar.sub_area_id,
            ar.rule_description,
            COUNT(rc.id) as condition_count
        FROM applicability_rules ar
        LEFT JOIN rule_conditions rc ON ar.id = rc.rule_id AND rc.is_active = TRUE
        WHERE ar.is_active = TRUE
        GROUP BY ar.id, ar.sub_area_id, ar.rule_description
        ORDER BY ar.id
        LIMIT 10
    """)

    print("\n" + "-" * 80)
    print("Sample Rules:")
    print("-" * 80)
    for row in cursor.fetchall():
        rule_id, sub_area_id, desc, cond_count = row
        print(f"  Rule #{rule_id:3} | {sub_area_id:15} | {cond_count} conds | {desc[:35]}...")

    cursor.close()

def main():
    print("FTA Comprehensive Review - Applicability Rules Population")
    print("=" * 80)

    conn = get_db_connection()

    try:
        # Clear existing rules
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rule_conditions")
        cursor.execute("DELETE FROM applicability_rules")
        conn.commit()
        cursor.close()
        print("✓ Cleared existing rules")

        populate_rules(conn)
        display_summary(conn)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
