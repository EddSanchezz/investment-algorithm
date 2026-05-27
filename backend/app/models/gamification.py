"""
QuantVision - Gamification Models (Pydantic)
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class AchievementResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: Optional[str]
    icon: str
    xp_reward: int
    category: str
    unlocked: bool
    unlocked_at: Optional[datetime] = None


class GamificationProfileResponse(BaseModel):
    user_id: str
    xp: int
    level: str
    streak_days: int
    last_activity_date: Optional[str]
    total_lessons_completed: int
    total_quizzes_passed: int
    total_research_sessions: int
    total_trades: int
    xp_to_next_level: int
    achievements_unlocked: int
    achievements_total: int


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    name: str
    avatar_url: Optional[str]
    level: str
    xp: int