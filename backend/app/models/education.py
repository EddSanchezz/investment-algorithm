"""
QuantVision - Education Models (Pydantic)
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class LessonResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str]
    xp_reward: int
    order_index: int
    category: str
    completed: bool = False


class QuizOption(BaseModel):
    text: str
    correct: bool


class QuizResponse(BaseModel):
    id: int
    lesson_id: int
    question: str
    options: List[QuizOption]
    explanation: Optional[str]


class QuizSubmission(BaseModel):
    selected_option: int  # index into options array


class QuizResultResponse(BaseModel):
    quiz_id: int
    is_correct: bool
    explanation: Optional[str]
    xp_earned: int


class LessonProgressResponse(BaseModel):
    lessons_completed: int
    total_lessons: int
    xp_from_lessons: int
    quizzes_passed: int