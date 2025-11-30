"""
Section schemas
"""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class SectionSchema(BaseModel):
    id: str
    title: str
    page_range: Optional[str] = None
    purpose: Optional[str] = None

    class Config:
        from_attributes = True


class SectionSummarySchema(BaseModel):
    """Section with LOE summary"""
    id: str
    title: str
    total_sub_areas: int
    total_hours: Optional[Decimal] = None
    avg_confidence: Optional[float] = None

    class Config:
        from_attributes = True
