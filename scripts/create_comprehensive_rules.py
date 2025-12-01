#!/usr/bin/env python3
"""
Create comprehensive applicability rules mapping all sub-areas to questionnaire questions
Maps natural language applicability criteria to structured database rules
"""
import psycopg2
import re

DATABASE_URL = 'postgresql://fta_review_db_user:ps2I2K6D4ntHnWpkqIL4lKzz2TyaLed8@dpg-d4mc0tuuk2gs738s90p0-a.oregon-postgres.render.com/fta_review_db'

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def create_rule(cursor, sub_area_id, question_number, required_answer):
    """Create a single applicability rule"""
    cursor.execute("""
        INSERT INTO applicability_rules (sub_area_id, question_id, required_answer, rule_type)
        SELECT %s, id, %s, 'include'
        FROM questionnaire_questions
        WHERE question_number = %s
        ON CONFLICT (sub_area_id, question_id) DO NOTHING
    """, (sub_area_id, required_answer, question_number))

def map_applicability_to_rules(applicability_text, sub_area_id, cursor):
    """
    Map natural language applicability to structured rules

    Questions:
    1. What type of recipient is this project? (all, state, non_state)
    2. Federal assistance expenditure amount? (less_750k, gte_750k)
    3. Has subrecipients? (yes, no)
    4. Has contractors/lessees? (yes, no)
    5. Tier level? (tier_1, tier_2, na)
    6. FTA fund types? (5310, 5311, 5307, 5337, other)
    7. Service type? (fixed_route, demand_response, commuter_rail, commuter_bus, other)
    8. Designated recipient? (yes, no)
    9. Has DBE goal? (yes, no)
    10. Group plan? (participant, sponsor, na)
    11. Direct control over assets? (yes, no)
    12. Public operator? (yes, no)
    """

    if not applicability_text:
        return 0

    text_lower = applicability_text.lower()
    rules_created = 0

    # Pattern: All recipients (any recipient type)
    if text_lower in ['all recipients', 'all recipients.']:
        for answer in ['all', 'state', 'non_state']:
            create_rule(cursor, sub_area_id, 1, answer)
            rules_created += 1
        return rules_created

    # Pattern: State recipients
    if 'state' in text_lower and 'non-state' not in text_lower and 'all recipients' not in text_lower:
        if 'states' == text_lower or 'states,' in text_lower or 'state recipients' in text_lower:
            create_rule(cursor, sub_area_id, 1, 'state')
            rules_created += 1

    # Pattern: Non-state recipients
    if 'non-state' in text_lower:
        create_rule(cursor, sub_area_id, 1, 'non_state')
        rules_created += 1

    # Pattern: $750,000 threshold
    if '$750,000' in applicability_text or '750,000' in text_lower:
        create_rule(cursor, sub_area_id, 2, 'gte_750k')
        rules_created += 1

    # Pattern: Subrecipients
    if 'subrecipient' in text_lower or 'sub-recipient' in text_lower:
        create_rule(cursor, sub_area_id, 3, 'yes')
        rules_created += 1

    # Pattern: Contractors and lessees
    if ('contractor' in text_lower or 'lessee' in text_lower) and 'subrecipient' not in text_lower:
        create_rule(cursor, sub_area_id, 4, 'yes')
        rules_created += 1
    elif 'contractor' in text_lower and 'subrecipient' in text_lower:
        # Both contractors AND subrecipients
        create_rule(cursor, sub_area_id, 3, 'yes')
        create_rule(cursor, sub_area_id, 4, 'yes')
        rules_created += 2

    # Pattern: Tier I
    if 'tier i' in text_lower or 'tier 1' in text_lower:
        create_rule(cursor, sub_area_id, 5, 'tier_1')
        rules_created += 1

    # Pattern: Section 5310
    if '5310' in applicability_text:
        create_rule(cursor, sub_area_id, 6, '5310')
        rules_created += 1

    # Pattern: Section 5311
    if '5311' in applicability_text:
        create_rule(cursor, sub_area_id, 6, '5311')
        rules_created += 1

    # Pattern: Section 5307
    if '5307' in applicability_text:
        create_rule(cursor, sub_area_id, 6, '5307')
        rules_created += 1

    # Pattern: Section 5337 or 5339
    if '5337' in applicability_text or '5339' in applicability_text:
        create_rule(cursor, sub_area_id, 6, '5337')
        rules_created += 1

    # Pattern: Fixed-route service
    if 'fixed-route' in text_lower or 'fixed route' in text_lower:
        create_rule(cursor, sub_area_id, 7, 'fixed_route')
        rules_created += 1

    # Pattern: Demand response service
    if 'demand-response' in text_lower or 'demand response' in text_lower or 'paratransit' in text_lower:
        create_rule(cursor, sub_area_id, 7, 'demand_response')
        rules_created += 1

    # Pattern: Commuter rail
    if 'commuter rail' in text_lower:
        create_rule(cursor, sub_area_id, 7, 'commuter_rail')
        rules_created += 1

    # Pattern: Commuter bus
    if 'commuter bus' in text_lower:
        create_rule(cursor, sub_area_id, 7, 'commuter_bus')
        rules_created += 1

    # Pattern: Rail service (light, rapid, commuter)
    if ('rail' in text_lower and 'commuter rail' not in text_lower) or 'light rail' in text_lower or 'rapid rail' in text_lower:
        create_rule(cursor, sub_area_id, 7, 'other')  # Generic rail
        rules_created += 1

    # Pattern: Bus service
    if 'bus' in text_lower and 'commuter bus' not in text_lower:
        create_rule(cursor, sub_area_id, 7, 'fixed_route')  # Most bus service is fixed-route
        rules_created += 1

    # Pattern: Ferry service
    if 'ferry' in text_lower:
        create_rule(cursor, sub_area_id, 7, 'other')
        rules_created += 1

    # Pattern: Designated recipient
    if 'designated recipient' in text_lower:
        create_rule(cursor, sub_area_id, 8, 'yes')
        rules_created += 1

    # Pattern: DBE goal
    if 'dbe' in text_lower and ('goal' in text_lower or 'overall goal' in text_lower):
        create_rule(cursor, sub_area_id, 9, 'yes')
        rules_created += 1

    # Pattern: Group plan sponsor
    if 'group plan sponsor' in text_lower or 'group tam plan sponsor' in text_lower:
        create_rule(cursor, sub_area_id, 10, 'sponsor')
        rules_created += 1

    # Pattern: Group plan participant
    if 'group plan participant' in text_lower or 'group tam plan participant' in text_lower:
        create_rule(cursor, sub_area_id, 10, 'participant')
        rules_created += 1

    # Pattern: Direct control over assets
    if 'direct control' in text_lower or 'fta-funded assets' in text_lower or 'capital assets' in text_lower:
        create_rule(cursor, sub_area_id, 11, 'yes')
        rules_created += 1

    # Pattern: Public operator
    if 'public operator' in text_lower or 'public provider' in text_lower:
        create_rule(cursor, sub_area_id, 12, 'yes')
        rules_created += 1

    # Pattern: Transit provider (generic - assume public operator)
    if 'transit provider' in text_lower and 'public operator' not in text_lower:
        create_rule(cursor, sub_area_id, 12, 'yes')
        rules_created += 1

    # Pattern: "Recipients who provide service" - generic, apply to all who provide service
    if text_lower == 'recipients who provide service':
        # These apply to recipients who provide any service
        for service_type in ['fixed_route', 'demand_response', 'commuter_rail', 'commuter_bus', 'other']:
            create_rule(cursor, sub_area_id, 7, service_type)
            rules_created += 1

    # Pattern: "Recipients that provide service" - same as above
    if 'recipients that provide service' in text_lower or 'recipients who provide service' in text_lower or 'recipients providing' in text_lower:
        if rules_created == 0:  # Only if no other rules matched
            for service_type in ['fixed_route', 'demand_response']:
                create_rule(cursor, sub_area_id, 7, service_type)
                rules_created += 2

    # Pattern: Recipients with overall goal (DBE)
    if 'overall goal' in text_lower:
        create_rule(cursor, sub_area_id, 9, 'yes')
        rules_created += 1

    # Pattern: EEO threshold - assume larger recipients
    if 'eeo' in text_lower and 'threshold' in text_lower:
        create_rule(cursor, sub_area_id, 2, 'gte_750k')  # Assume threshold is tied to funding amount
        rules_created += 1

    # Pattern: MPOs (Metropolitan Planning Organizations) - state recipients
    if 'mpo' in text_lower or 'metropolitan planning' in text_lower:
        create_rule(cursor, sub_area_id, 1, 'state')
        rules_created += 1

    # Pattern: UZA (Urbanized Area) - typically non-state
    if 'uza' in text_lower or 'urbanized' in text_lower:
        create_rule(cursor, sub_area_id, 1, 'non_state')
        rules_created += 1

    # Pattern: FTA-funded real property
    if 'fta-funded real property' in text_lower or 'fta-funded property' in text_lower:
        create_rule(cursor, sub_area_id, 11, 'yes')  # Direct control over assets
        rules_created += 1

    # Pattern: FTA-funded equipment
    if 'fta-funded equipment' in text_lower or 'operate or lease' in text_lower:
        create_rule(cursor, sub_area_id, 11, 'yes')  # Direct control over assets
        rules_created += 1

    # Pattern: Certification or certify (DBE certification)
    if 'certif' in text_lower and 'dbe' in text_lower:
        create_rule(cursor, sub_area_id, 9, 'yes')
        rules_created += 1

    # Pattern: Operating assistance
    if 'operating assistance' in text_lower:
        # Typically 5307 funds
        create_rule(cursor, sub_area_id, 6, '5307')
        rules_created += 1

    # Pattern: route-deviation
    if 'route-deviation' in text_lower or 'route deviation' in text_lower:
        create_rule(cursor, sub_area_id, 7, 'demand_response')  # Closest match
        rules_created += 1

    # Pattern: Entities that lease vehicles or rely on contracts
    if 'lease vehicles' in text_lower or 'contracts or other arrangements' in text_lower:
        create_rule(cursor, sub_area_id, 4, 'yes')  # Contractors/lessees
        rules_created += 1

    # Fallback: If still no rules and contains "all" - apply to all recipients
    if rules_created == 0 and 'all ' in text_lower:
        for answer in ['all', 'state', 'non_state']:
            create_rule(cursor, sub_area_id, 1, answer)
            rules_created += 3

    return rules_created

def main():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("=" * 80)
    print("CREATING COMPREHENSIVE APPLICABILITY RULES")
    print("=" * 80)

    # First, clear existing rules to start fresh
    cursor.execute("DELETE FROM applicability_rules")
    print("✓ Cleared existing rules")

    # Get all sub-areas with their applicability
    cursor.execute("""
        SELECT id, applicability
        FROM sub_areas
        ORDER BY id
    """)

    sub_areas = cursor.fetchall()
    total_rules = 0
    sub_areas_with_rules = 0
    sub_areas_without_rules = []

    for sub_area_id, applicability in sub_areas:
        rules_created = map_applicability_to_rules(applicability, sub_area_id, cursor)
        total_rules += rules_created

        if rules_created > 0:
            sub_areas_with_rules += 1
            app_text = (applicability or 'N/A')[:60]
            print(f"✓ {sub_area_id}: {rules_created} rule(s) - {app_text}...")
        else:
            sub_areas_without_rules.append((sub_area_id, applicability))
            app_text = (applicability or 'N/A')[:60]
            print(f"⚠ {sub_area_id}: NO RULES - {app_text}...")

    conn.commit()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total sub-areas: {len(sub_areas)}")
    print(f"Sub-areas with rules: {sub_areas_with_rules}")
    print(f"Sub-areas without rules: {len(sub_areas_without_rules)}")
    print(f"Total rules created: {total_rules}")

    if sub_areas_without_rules:
        print("\n" + "=" * 80)
        print("SUB-AREAS WITHOUT RULES (need manual review):")
        print("=" * 80)
        for sub_area_id, applicability in sub_areas_without_rules:
            print(f"{sub_area_id}: {applicability}")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
