"""
Applicability Rule and Rule Condition models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class ApplicabilityRule(Base):
    __tablename__ = "applicability_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sub_area_id = Column(String(50), ForeignKey("sub_areas.id"), nullable=False)
    rule_description = Column(Text)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sub_area = relationship("SubArea", back_populates="rules")
    conditions = relationship("RuleCondition", back_populates="rule", lazy="joined")


class RuleCondition(Base):
    __tablename__ = "rule_conditions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey("applicability_rules.id"), nullable=False)
    question_key = Column(String(50), nullable=False)
    operator = Column(String(20), nullable=False)  # 'equals', 'contains', 'in', etc.
    expected_value = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    rule = relationship("ApplicabilityRule", back_populates="conditions")
