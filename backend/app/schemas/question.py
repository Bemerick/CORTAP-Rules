"""
Question schemas
"""

from pydantic import BaseModel
from typing import List, Optional


class QuestionOptionSchema(BaseModel):
    id: int
    option_value: str
    option_label: str
    display_order: int

    class Config:
        from_attributes = True
        # Allow population from ORM models with different attribute names
        populate_by_name = True


class QuestionSchema(BaseModel):
    id: int
    question_key: str
    question_text: str
    question_type: str
    help_text: Optional[str] = None
    display_order: int
    is_required: bool

    class Config:
        from_attributes = True


class QuestionWithOptionsSchema(QuestionSchema):
    options: List[QuestionOptionSchema] = []

    class Config:
        from_attributes = True
