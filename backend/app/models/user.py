"""
QuantVision - User Models (Pydantic + SQLAlchemy)
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Boolean, DateTime
from ..core.database import Base


# SQLAlchemy Models (Database)
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(UUID))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL for OAuth-only
    name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    auth_provider = Column(String(20), default="email")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(String(36), primary_key=True)
    xp = Column(String(20), default="0")  # Stored as string to avoid overflow
    level = Column(String(50), default="Beginner")
    streak_days = Column(String(20), default="0")
    last_activity_date = Column(String(10), nullable=True)
    total_lessons_completed = Column(String(20), default="0")
    total_quizzes_passed = Column(String(20), default="0")
    total_research_sessions = Column(String(20), default="0")
    total_trades = Column(String(20), default="0")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Models (API)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    auth_provider: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse