"""
Assessment API endpoints (without creating a project)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from decimal import Decimal
import json

from app.database.connection import get_db
from app.models import SubArea, Section
from app.schemas import AssessmentRequestSchema, AssessmentResultSchema, SubAreaSchema

router = APIRouter(prefix="/api/assess", tags=["assessment"])


@router.post("", response_model=AssessmentResultSchema)
def assess_applicability(assessment: AssessmentRequestSchema, db: Session = Depends(get_db)):
    """
    Assess which sub-areas are applicable based on answers
    Does not create a project - just returns applicable sub-areas
    """
    # Convert answers to JSONB format
    answers_jsonb = json.dumps(assessment.answers)

    # Use database function to evaluate rules
    # Since we don't have a project, we'll check rules directly
    query = text("""
        SELECT DISTINCT ar.sub_area_id
        FROM applicability_rules ar
        WHERE ar.is_active = TRUE
        AND evaluate_rule(ar.id, :answers::jsonb)
    """)

    result = db.execute(query, {"answers": answers_jsonb})
    applicable_sub_area_ids = [row[0] for row in result]

    # Get sub-area details
    sub_areas = db.query(SubArea).filter(SubArea.id.in_(applicable_sub_area_ids)).all()

    # Calculate totals
    total_hours = sum(sa.loe_hours for sa in sub_areas if sa.loe_hours) or Decimal('0')
    avg_confidence = sum(sa.loe_confidence_score for sa in sub_areas if sa.loe_confidence_score) / len(sub_areas) if sub_areas else 0

    # Get summary by section
    section_summaries = db.query(
        Section.id,
        Section.title,
        func.count(SubArea.id).label('count'),
        func.sum(SubArea.loe_hours).label('hours')
    ).join(SubArea, Section.id == SubArea.section_id)\
    .filter(SubArea.id.in_(applicable_sub_area_ids))\
    .group_by(Section.id, Section.title)\
    .order_by(func.sum(SubArea.loe_hours).desc().nullslast())\
    .all()

    sections_summary = [
        {
            "section_id": s.id,
            "section_title": s.title,
            "sub_area_count": s.count,
            "total_hours": float(s.hours) if s.hours else 0.0
        }
        for s in section_summaries
    ]

    return AssessmentResultSchema(
        total_sub_areas=len(sub_areas),
        applicable_sub_areas=[SubAreaSchema.from_orm(sa) for sa in sub_areas],
        total_hours=total_hours,
        avg_confidence=float(avg_confidence),
        sections_summary=sections_summary
    )
