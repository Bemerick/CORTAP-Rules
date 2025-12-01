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
    """Get all questions"""
    questions = db.query(Question).order_by(Question.question_number).all()
    return questions


@router.get("/{question_id}", response_model=QuestionWithOptionsSchema)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """Get a specific question by ID"""
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return question
