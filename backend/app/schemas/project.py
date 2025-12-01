"""
Project schemas
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from .sub_area import SubAreaSchema


class ProjectCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    grantee_name: Optional[str] = None
    grant_number: Optional[str] = None
    review_type: Optional[str] = None


class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    grantee_name: Optional[str] = None
    grant_number: Optional[str] = None
    review_type: Optional[str] = None


class ProjectAnswersSchema(BaseModel):
    """Schema for submitting project answers"""
    answers: Dict[int, str]  # question_id: answer_value


class ProjectSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    grantee_name: Optional[str] = None
    grant_number: Optional[str] = None
    review_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicableSubAreaSchema(BaseModel):
    """Simplified sub-area for applicability results"""
    section_id: str
    section_name: str
    sub_area_id: str
    question: str
    basic_requirement: str
    loe_hours: float
    loe_confidence: str
    loe_confidence_score: int


class ProjectApplicabilityResultSchema(BaseModel):
    """Result of applicability assessment"""
    project_id: int
    applicable_count: int
    applicable_sub_areas: List[ApplicableSubAreaSchema]


class SectionLOESummary(BaseModel):
    """LOE summary for a section within a project"""
    section_id: str
    section_name: str
    sub_area_count: int
    total_hours: float
    avg_confidence_score: float


class ProjectLOESummarySchema(BaseModel):
    """Complete LOE summary for a project"""
    project_id: int
    project_name: str
    total_sub_areas: int
    total_hours: float
    avg_confidence_score: float
    sections: List[SectionLOESummary]
