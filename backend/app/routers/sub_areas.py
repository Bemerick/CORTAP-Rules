"""
Sub-areas API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.models import SubArea
from app.schemas import SubAreaSchema, SubAreaDetailSchema

router = APIRouter(prefix="/api/sub-areas", tags=["sub-areas"])


@router.get("", response_model=List[SubAreaSchema])
def get_sub_areas(
    section_id: Optional[str] = Query(None, description="Filter by section ID"),
    db: Session = Depends(get_db)
):
    """Get all sub-areas, optionally filtered by section"""
    query = db.query(SubArea)

    if section_id:
        query = query.filter(SubArea.section_id == section_id)

    sub_areas = query.order_by(SubArea.section_id, SubArea.id).all()
    return sub_areas


@router.get("/{sub_area_id}", response_model=SubAreaDetailSchema)
def get_sub_area(sub_area_id: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific sub-area"""
    sub_area = db.query(SubArea).filter(SubArea.id == sub_area_id).first()

    if not sub_area:
        raise HTTPException(status_code=404, detail="Sub-area not found")

    return sub_area
