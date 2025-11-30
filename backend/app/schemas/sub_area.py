"""
Sub-area schemas
"""

from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class IndicatorSchema(BaseModel):
    id: int
    indicator_id: str
    text: str

    class Config:
        from_attributes = True


class DeficiencySchema(BaseModel):
    id: int
    code: str
    title: str
    determination: Optional[str] = None
    suggested_corrective_action: Optional[str] = None

    class Config:
        from_attributes = True


class SubAreaSchema(BaseModel):
    """Basic sub-area information"""
    id: str
    section_id: str
    question: str
    applicability: Optional[str] = None
    loe_hours: Optional[Decimal] = None
    loe_confidence: Optional[str] = None
    loe_confidence_score: Optional[int] = None

    class Config:
        from_attributes = True


class SubAreaDetailSchema(SubAreaSchema):
    """Detailed sub-area with all related data"""
    basic_requirement: Optional[str] = None
    detailed_explanation: Optional[str] = None
    instructions_for_reviewer: Optional[str] = None
    loe_reasoning: Optional[str] = None
    indicators: List[IndicatorSchema] = []
    deficiencies: List[DeficiencySchema] = []

    class Config:
        from_attributes = True
