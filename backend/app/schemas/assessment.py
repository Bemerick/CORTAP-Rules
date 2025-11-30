"""
Assessment schemas
"""

from pydantic import BaseModel
from typing import Dict, List
from decimal import Decimal
from .sub_area import SubAreaSchema


class AssessmentRequestSchema(BaseModel):
    """Schema for assessment without creating a project"""
    answers: Dict[str, str]  # question_key: answer_value


class AssessmentResultSchema(BaseModel):
    """Result of assessment"""
    total_sub_areas: int
    applicable_sub_areas: List[SubAreaSchema]
    total_hours: Decimal
    avg_confidence: float
    sections_summary: List[Dict[str, any]]  # Summary by section
