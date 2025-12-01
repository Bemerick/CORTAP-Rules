"""
Question schemas
"""

from pydantic import BaseModel
from typing import Optional


class QuestionSchema(BaseModel):
    id: int
    question_number: int
    question_text: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


# Alias for backwards compatibility
QuestionWithOptionsSchema = QuestionSchema
