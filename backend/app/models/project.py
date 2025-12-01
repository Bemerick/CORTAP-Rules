"""
Project, ProjectAnswer, and ProjectApplicability models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    grantee_name = Column(String(255))
    grant_number = Column(String(100))
    review_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project_answers = relationship("ProjectAnswer", back_populates="project", cascade="all, delete-orphan")
    applicability = relationship("ProjectApplicability", back_populates="project", cascade="all, delete-orphan")


class ProjectAnswer(Base):
    __tablename__ = "project_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questionnaire_questions.id"), nullable=False)
    answer = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="project_answers")


class ProjectApplicability(Base):
    __tablename__ = "project_applicability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sub_area_id = Column(String(50), ForeignKey("sub_areas.id"), nullable=False)
    is_applicable = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="applicability")
