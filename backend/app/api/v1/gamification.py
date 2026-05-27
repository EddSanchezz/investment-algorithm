"""
QuantVision - Gamification Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..models.gamification import (
    AchievementResponse, GamificationProfileResponse, LeaderboardEntry
)

router = APIRouter(prefix="/gamification", tags=["gamification"])


ACHIEVEMENTS_DATA = [
    # Research
    {"id": 1, "slug": "first_search", "name": "First Search", "description": "Realiza tu primera busqueda",
     "icon": "\ud83d\udd0d", "xp_reward": 50, "category": "research"},
    {"id": 2, "slug": "curious", "name": "Curioso", "description": "Investiga 5 activos diferentes",
     "icon": "\ud83e\udd14", "xp_reward": 75, "category": "research"},
    {"id": 3, "slug": "diversified_research", "name": "Diversificado", "description": "Investiga 10 activos",
     "icon": "\ud83c\udf0d", "xp_reward": 100, "category": "research"},
    {"id": 4, "slug": "chart_master", "name": "Maestro de Graficos", "description": "Ve 50 graficos",
     "icon": "\ud83d\udcca", "xp_reward": 150, "category": "research"},
    # Education
    {"id": 5, "slug": "first_lesson", "name": "Primera Leccion", "description": "Completa tu primera leccion",
     "icon": "\ud83d\udcd6", "xp_reward": 50, "category": "education"},
    {"id": 6, "slug": "scholar", "name": "Erudito", "description": "Completa 3 lecciones",
     "icon": "\ud83d\udcda", "xp_reward": 100, "category": "education"},
    {"id": 7, "slug": "quiz_ace", "name": "Quiz Ace", "description": "Aprueba 10 quizzes",
     "icon": "\ud83c\udf1f", "xp_reward": 100, "category": "education"},
    {"id": 8, "slug": "streak_7", "name": "Semana Perfecta", "description": "7 dias consecutivos aprendiendo",
     "icon": "\ud83d\udd25", "xp_reward": 100, "category": "education"},
    # Portfolio
    {"id": 9, "slug": "first_trade", "name": "Primer Trade", "description": "Registra tu primera transaccion",
     "icon": "\ud83d\udcb0", "xp_reward": 50, "category": "portfolio"},
    {"id": 10, "slug": "five_positions", "name": "Carterista", "description": "5 posiciones en portfolio",
     "icon": "\ud83d\udcbc", "xp_reward": 100, "category": "portfolio"},
    # Special
    {"id": 11, "slug": "all_rounder", "name": "Completo", "description": "Completa 1 de cada categoria",
     "icon": "\ud83c\udfc6", "xp_reward": 200, "category": "special"},
    {"id": 12, "slug": "master_investor", "name": "Maestro Inversor", "description": "Alcanza nivel Master",
     "icon": "\ud83d\udc51", "xp_reward": 500, "category": "special"},
]


def _level_from_xp(xp: int) -> str:
    if xp >= 15001: return "Master"
    if xp >= 5001: return "Veteran"
    if xp >= 1501: return "Trader"
    if xp >= 501: return "Analyst"
    if xp >= 101: return "Explorer"
    return "Beginner"


def _xp_for_next_level(level: str) -> int:
    thresholds = {"Beginner": 101, "Explorer": 501, "Analyst": 1501,
                  "Trader": 5001, "Veteran": 15001, "Master": 999999}
    return thresholds.get(level, 101)


@router.get("/profile", response_model=GamificationProfileResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el perfil de gamificacion del usuario."""
    return GamificationProfileResponse(
        user_id=user_id,
        xp=0,
        level="Beginner",
        streak_days=0,
        last_activity_date=None,
        total_lessons_completed=0,
        total_quizzes_passed=0,
        total_research_sessions=0,
        total_trades=0,
        xp_to_next_level=101,
        achievements_unlocked=0,
        achievements_total=len(ACHIEVEMENTS_DATA),
    )


@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene todos los logros con su estado para el usuario."""
    return [
        AchievementResponse(
            id=a["id"],
            slug=a["slug"],
            name=a["name"],
            description=a["description"],
            icon=a["icon"],
            xp_reward=a["xp_reward"],
            category=a["category"],
            unlocked=False,
            unlocked_at=None,
        )
        for a in ACHIEVEMENTS_DATA
    ]


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 50):
    """Obtiene el leaderboard de inversores."""
    # Placeholder - real implementation would query user_progress table
    return {
        "entries": [
            LeaderboardEntry(rank=i + 1, user_id=f"user_{i}", name=f"Inversor {i + 1}",
                           avatar_url=None, level="Beginner", xp=1000 - i * 10)
            for i in range(min(limit, 10))
        ],
        "total": 10,
    }