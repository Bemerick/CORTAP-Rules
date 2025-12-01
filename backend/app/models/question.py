"""
Question model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class Question(Base):
    __tablename__ = "questionnaire_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_number = Column(Integer, unique=True, nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
