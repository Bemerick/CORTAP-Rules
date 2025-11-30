"""
Deficiency model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class Deficiency(Base):
    __tablename__ = "deficiencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sub_area_id = Column(String(50), ForeignKey("sub_areas.id"), nullable=False)
    code = Column(String(50), nullable=False)
    title = Column(Text, nullable=False)
    determination = Column(Text)
    suggested_corrective_action = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sub_area = relationship("SubArea", back_populates="deficiencies")
