"""
Questions API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.models import Question
from app.schemas import QuestionWithOptionsSchema

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=List[QuestionWithOptionsSchema])
def get_questions(db: Session = Depends(get_db)):
    """Get all active questions with their options"""
    questions = db.query(Question).filter(Question.is_active == True).order_by(Question.display_order).all()
    return questions


@router.get("/{question_key}", response_model=QuestionWithOptionsSchema)
def get_question(question_key: str, db: Session = Depends(get_db)):
    """Get a specific question by key"""
    question = db.query(Question).filter(
        Question.question_key == question_key,
        Question.is_active == True
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return question
