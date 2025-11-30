"""
SubArea model
"""

from sqlalchemy import Column, String, Text, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class SubArea(Base):
    __tablename__ = "sub_areas"

    id = Column(String(50), primary_key=True)
    section_id = Column(String(50), ForeignKey("sections.id"), nullable=False)
    question = Column(Text, nullable=False)
    basic_requirement = Column(Text)
    applicability = Column(Text)
    detailed_explanation = Column(Text)
    instructions_for_reviewer = Column(Text)
    loe_hours = Column(Numeric(5, 2))
    loe_confidence = Column(String(20))
    loe_confidence_score = Column(Integer)
    loe_reasoning = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    section = relationship("Section", back_populates="sub_areas")
    indicators = relationship("IndicatorOfCompliance", back_populates="sub_area", lazy="joined")
    deficiencies = relationship("Deficiency", back_populates="sub_area", lazy="joined")
    rules = relationship("ApplicabilityRule", back_populates="sub_area")
