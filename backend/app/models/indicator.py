"""
Indicator of Compliance model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class IndicatorOfCompliance(Base):
    __tablename__ = "indicators_of_compliance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sub_area_id = Column(String(50), ForeignKey("sub_areas.id"), nullable=False)
    indicator_id = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sub_area = relationship("SubArea", back_populates="indicators")
