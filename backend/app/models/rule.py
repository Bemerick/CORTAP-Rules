"""
Applicability Rule model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.connection import Base


class ApplicabilityRule(Base):
    __tablename__ = "applicability_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sub_area_id = Column(String(50), ForeignKey("sub_areas.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questionnaire_questions.id"), nullable=False)
    required_answer = Column(String(50), nullable=False)
    rule_type = Column(String(50), default='include')
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Alias for backwards compatibility
RuleCondition = None
