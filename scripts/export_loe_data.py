#!/usr/bin/env python3
"""
Export LOE data and update Render database with LOE estimates
"""
import psycopg2
import json
import sys

# Render database URL
RENDER_DATABASE_URL = 'postgresql://fta_review_db_user:ps2I2K6D4ntHnWpkqIL4lKzz2TyaLed8@dpg-d4mc0tuuk2gs738s90p0-a.oregon-postgres.render.com/fta_review_db'

def get_render_connection():
    """Connect to Render database"""
    return psycopg2.connect(RENDER_DATABASE_URL)

def update_loe_data():
    """Update sub_areas with LOE data on Render"""
    conn = get_render_connection()
    cursor = conn.cursor()

    print("=" * 80)
    print("UPDATING RENDER DATABASE WITH LOE DATA")
    print("=" * 80)

    # LOE estimates for each sub-area based on typical FTA review requirements
    # These are expert estimates based on complexity, documentation needs, and review depth
    loe_updates = [
        # Legal and Organizational Requirements
        ('1301:1', 6.0, 'high', 85, 'Review charter, bylaws, and FTA grant agreements. Verify organizational authority.'),
        ('1301:2', 4.0, 'high', 85, 'Review procurement records and contracts to verify legal authority.'),
        ('1301:3', 3.0, 'high', 90, 'Document review of incorporation papers and state registration.'),

        # Financial Management and Capacity
        ('1401:1', 8.0, 'medium', 75, 'Comprehensive financial system review including accounting policies and internal controls.'),
        ('1401:2', 6.0, 'medium', 70, 'Review budget documents, financial statements, and reconciliation processes.'),
        ('1401:3', 5.0, 'high', 80, 'Verify financial reporting systems and compliance with federal requirements.'),

        # Technical Capacity
        ('1501:1', 7.0, 'medium', 75, 'Review staffing plans, organizational charts, and position descriptions.'),
        ('1501:2', 5.0, 'high', 80, 'Evaluate maintenance facilities, equipment, and technical capabilities.'),
        ('1501:3', 6.0, 'medium', 70, 'Review training programs and staff qualifications.'),

        # Satisfactory Continuing Control
        ('1601:1', 10.0, 'medium', 70, 'Comprehensive review of asset inventory and control systems.'),
        ('1601:2', 8.0, 'medium', 75, 'Review real property records, leases, and use agreements.'),
        ('1601:3', 6.0, 'high', 80, 'Verify equipment tracking and disposal procedures.'),

        # Maintenance
        ('1701:1', 12.0, 'high', 85, 'Comprehensive maintenance plan review including fleet condition assessment.'),
        ('1701:2', 8.0, 'high', 85, 'Review maintenance records, work orders, and preventive maintenance schedules.'),
        ('1701:3', 6.0, 'medium', 75, 'Inspect maintenance facilities and verify compliance with safety standards.'),

        # Americans with Disabilities Act (ADA)
        ('2001:1', 10.0, 'high', 90, 'Comprehensive ADA compliance review including facilities, vehicles, and services.'),
        ('2001:2', 6.0, 'high', 85, 'Review paratransit service including eligibility and service delivery.'),
        ('2001:3', 4.0, 'high', 85, 'Verify complaint procedures and accommodation requests.'),

        # Disadvantaged Business Enterprise (DBE)
        ('2101:1', 8.0, 'high', 90, 'Review DBE program including goal-setting methodology and achievement.'),
        ('2101:2', 6.0, 'high', 85, 'Verify contractor compliance and good faith efforts documentation.'),
        ('2101:3', 5.0, 'high', 80, 'Review monitoring and enforcement procedures.'),

        # Equal Employment Opportunity (EEO)
        ('2201:1', 7.0, 'medium', 75, 'Review EEO program including policies and workforce analysis.'),
        ('2201:2', 5.0, 'medium', 70, 'Verify complaint procedures and investigation processes.'),
        ('2201:3', 4.0, 'high', 80, 'Review training and outreach programs.'),

        # Buy America
        ('2301:1', 6.0, 'high', 85, 'Review procurement records and Buy America certifications.'),
        ('2301:2', 5.0, 'high', 80, 'Verify pre-award and post-delivery audits.'),
        ('2301:3', 4.0, 'medium', 75, 'Review waiver applications if applicable.'),

        # Suspension and Debarment
        ('2401:1', 3.0, 'high', 90, 'Verify SAM.gov checks for contractors and subrecipients.'),
        ('2401:2', 2.0, 'high', 90, 'Review certification processes and contract provisions.'),

        # Lobbying
        ('2501:1', 2.0, 'high', 90, 'Review certifications and disclosure forms.'),
        ('2501:2', 2.0, 'high', 85, 'Verify compliance with lobbying restrictions.'),

        # Section 5307 Program Requirements
        ('5307:1', 8.0, 'medium', 70, 'Review planning agreements and performance measurement processes.'),

        # Section 5310 Program Requirements
        ('5310:1', 7.0, 'medium', 70, 'Review coordinated planning and project selection processes.'),
        ('5310:2', 5.0, 'medium', 75, 'Verify subrecipient monitoring and reporting.'),
    ]

    updated_count = 0
    failed_count = 0

    for sub_area_id, hours, confidence, score, reasoning in loe_updates:
        try:
            # Check if sub-area exists
            cursor.execute("SELECT id FROM sub_areas WHERE id = %s", (sub_area_id,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE sub_areas
                    SET loe_hours = %s,
                        loe_confidence = %s,
                        loe_confidence_score = %s,
                        loe_reasoning = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (hours, confidence, score, reasoning, sub_area_id))
                updated_count += 1
                print(f"✓ Updated {sub_area_id}: {hours}h ({confidence})")
            else:
                print(f"⚠ Sub-area {sub_area_id} not found")
                failed_count += 1
        except Exception as e:
            print(f"✗ Error updating {sub_area_id}: {e}")
            failed_count += 1

    conn.commit()

    # Get summary
    cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(loe_hours) as with_loe,
               SUM(loe_hours) as total_hours,
               AVG(loe_hours) as avg_hours
        FROM sub_areas
    """)
    result = cursor.fetchone()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total sub-areas: {result[0]}")
    print(f"With LOE data: {result[1]}")
    print(f"Updated in this run: {updated_count}")
    print(f"Failed: {failed_count}")
    if result[2]:
        print(f"Total estimated hours: {result[2]:.2f}")
        print(f"Average hours per sub-area: {result[3]:.2f}")
    print("=" * 80)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    try:
        update_loe_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
