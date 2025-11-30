"""
Sections API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List

from app.database.connection import get_db
from app.models import Section, SubArea
from app.schemas import SectionSchema, SectionSummarySchema

router = APIRouter(prefix="/api/sections", tags=["sections"])


@router.get("", response_model=List[SectionSchema])
def get_sections(db: Session = Depends(get_db)):
    """Get all sections"""
    sections = db.query(Section).order_by(Section.id).all()
    return sections


@router.get("/summary", response_model=List[SectionSummarySchema])
def get_sections_summary(db: Session = Depends(get_db)):
    """Get sections with LOE summary"""
    results = db.query(
        Section.id,
        Section.title,
        func.count(SubArea.id).label('total_sub_areas'),
        func.sum(SubArea.loe_hours).label('total_hours'),
        func.avg(SubArea.loe_confidence_score).label('avg_confidence')
    ).outerjoin(SubArea, Section.id == SubArea.section_id)\
    .group_by(Section.id, Section.title)\
    .order_by(func.sum(SubArea.loe_hours).desc().nullslast())\
    .all()

    return [
        SectionSummarySchema(
            id=r.id,
            title=r.title,
            total_sub_areas=r.total_sub_areas,
            total_hours=r.total_hours,
            avg_confidence=float(r.avg_confidence) if r.avg_confidence else None
        )
        for r in results
    ]


@router.get("/{section_id}", response_model=SectionSchema)
def get_section(section_id: str, db: Session = Depends(get_db)):
    """Get a specific section"""
    section = db.query(Section).filter(Section.id == section_id).first()

    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    return section
