"""
Section model
"""

from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class Section(Base):
    __tablename__ = "sections"

    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    page_range = Column(String(50))
    purpose = Column(Text)
    chapter_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sub_areas = relationship("SubArea", back_populates="section", lazy="joined")
