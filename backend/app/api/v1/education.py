"""
QuantVision - Education Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..models.education import (
    LessonResponse, QuizResponse, QuizSubmission,
    QuizResultResponse, LessonProgressResponse
)

router = APIRouter(prefix="/education", tags=["education"])


LESSONS_DATA = [
    {"id": 1, "slug": "what-is-a-stock", "title": "\u00bfQu\u00e9 es una acci\u00f3n?",
     "description": "Aprende los conceptos b\u00e1sicos de las acciones y por qu\u00e9 existen los mercados burs\u00e1tiles.",
     "xp_reward": 25, "order_index": 1, "category": "basics",
     "content": "# \u00bfQu\u00e9 es una acci\u00f3n?\n\nUna **acci\u00f3n** representa..."},
    {"id": 2, "slug": "etfs-vs-stocks", "title": "ETFs vs Acciones",
     "description": "Comprende las diferencias entre ETFs y acciones individuales.",
     "xp_reward": 25, "order_index": 2, "category": "basics",
     "content": "# ETFs vs Acciones\n\nUn **ETF** (Exchange-Traded Fund) es..."},
    {"id": 3, "slug": "reading-charts", "title": "Lectura de gr\u00e1ficos",
     "description": "Aprende a interpretar gr\u00e1ficos de precios y vol\u00famen.",
     "xp_reward": 25, "order_index": 3, "category": "basics",
     "content": "# Lectura de Gr\u00e1ficos\n\nLos gr\u00e1ficos muestran..."},
    {"id": 4, "slug": "candlesticks", "title": "Velas japonesas (Candlesticks)",
     "description": "Domina la lectura de velas japonesas para-an\u00e1lisis t\u00e9cnico.",
     "xp_reward": 25, "order_index": 4, "category": "technical",
     "content": "# Velas Japonesas\n\nLas velas muestran..."},
    {"id": 5, "slug": "volatility-risk", "title": "Volatilidad y riesgo",
     "description": "Comprende c\u00f3mo medir y gestionar el riesgo.",
     "xp_reward": 25, "order_index": 5, "category": "risk",
     "content": "# Volatilidad y Riesgo\n\nLa **volatilidad** mide..."},
    {"id": 6, "slug": "diversification", "title": "Diversificaci\u00f3n",
     "description": "Estrategias para diversificar tu portafolio.",
     "xp_reward": 25, "order_index": 6, "category": "strategies",
     "content": "# Diversificaci\u00f3n\n\nNo pongas todos los huevos..."},
    {"id": 7, "slug": "fundamental-vs-technical", "title": "An\u00e1lisis fundamental vs t\u00e9cnico",
     "description": "Dos enfoques para analizar activos financieros.",
     "xp_reward": 25, "order_index": 7, "category": "technical",
     "content": "# An\u00e1lisis Fundamental vs T\u00e9cnico\n\nEl an\u00e1lisis **fundamental**..."},
    {"id": 8, "slug": "momentum-trading", "title": "Momentum trading",
     "description": "Estrategia de seguimiento de tendencia.",
     "xp_reward": 25, "order_index": 8, "category": "strategies",
     "content": "# Momentum Trading\n\nEsta estrategia se basa..."},
    {"id": 9, "slug": "mean-reversion", "title": "Mean reversion",
     "description": "Estrategia de regreso a la media.",
     "xp_reward": 25, "order_index": 9, "category": "strategies",
     "content": "# Mean Reversion\n\nLa idea central es que..."},
    {"id": 10, "slug": "risk-management", "title": "Gesti\u00f3n de riesgo",
     "description": "Aprende a proteger tu capital.",
     "xp_reward": 25, "order_index": 10, "category": "risk",
     "content": "# Gesti\u00f3n de Riesgo\n\nLa gesti\u00f3n de riesgo es..."},
]

QUIZZES_DATA = {
    1: [
        {"id": 1, "lesson_id": 1, "question": "\u00bfQu\u00e9 representa una acci\u00f3n?",
         "options": [{"text": "Una deuda de la empresa", "correct": False},
                    {"text": "Una propiedad parcial de la empresa", "correct": True},
                    {"text": "Un bono del gobierno", "correct": False},
                    {"text": "Una moneda digital", "correct": False}],
         "explanation": "Una acci\u00f3n representa propiedad parcial de una empresa."},
        {"id": 2, "lesson_id": 1, "question": "\u00bfD\u00f3nde se negocian las acciones?",
         "options": [{"text": "En bancos", "correct": False},
                    {"text": "En mercados burstiles", "correct": True},
                    {"text": "En tiendas", "correct": False},
                    {"text": "En internet", "correct": False}],
         "explanation": "Las acciones se negocian en mercados burstiles como NYSE o NASDAQ."},
    ],
    2: [
        {"id": 3, "lesson_id": 2, "question": "\u00bfQu\u00e9 es un ETF?",
         "options": [{"text": "Un tipo de acci\u00f3n individual", "correct": False},
                    {"text": "Un fondo que cotiza en bolsa", "correct": True},
                    {"text": "Un bono corporativo", "correct": False},
                    {"text": "Una criptomoneda", "correct": False}],
         "explanation": "Un ETF (Exchange-Traded Fund) es un fondo que cotiza en bolsa."},
    ],
}


@router.get("/lessons", response_model=List[LessonResponse])
async def list_lessons(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas las lecciones con su estado de progreso."""
    completed_ids = set()

    lessons = [
        LessonResponse(
            id=l["id"],
            slug=l["slug"],
            title=l["title"],
            description=l["description"],
            xp_reward=l["xp_reward"],
            order_index=l["order_index"],
            category=l["category"],
            completed=l["id"] in completed_ids,
        )
        for l in sorted(LESSONS_DATA, key=lambda x: x["order_index"])
    ]
    return lessons


@router.get("/lessons/{slug}")
async def get_lesson(slug: str):
    """Obtiene el contenido de una lecci\u00f3n espec\u00edfica."""
    lesson = next((l for l in LESSONS_DATA if l["slug"] == slug), None)
    if not lesson:
        raise HTTPException(status_code=404, detail="Leccion no encontrada")
    return {
        "id": lesson["id"],
        "slug": lesson["slug"],
        "title": lesson["title"],
        "description": lesson["description"],
        "content": lesson["content"],
        "xp_reward": lesson["xp_reward"],
        "order_index": lesson["order_index"],
        "category": lesson["category"],
    }


@router.get("/lessons/{slug}/quiz")
async def get_lesson_quiz(slug: str):
    """Obtiene el quiz asociado a una lecci\u00f3n."""
    lesson = next((l for l in LESSONS_DATA if l["slug"] == slug), None)
    if not lesson:
        raise HTTPException(status_code=404, detail="Leccion no encontrada")

    lesson_quizzes = QUIZZES_DATA.get(lesson["id"], [])
    if not lesson_quizzes:
        return {"quizzes": [], "message": "Esta leccion no tiene quiz"}

    return {"quizzes": lesson_quizzes}


@router.post("/quiz/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: int,
    data: QuizSubmission,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Env\u00eda una respuesta de quiz y retorna el resultado."""
    all_quizzes = []
    for quizzes in QUIZZES_DATA.values():
        all_quizzes.extend(quizzes)

    quiz = next((q for q in all_quizzes if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")

    options = quiz["options"]
    if data.selected_option < 0 or data.selected_option >= len(options):
        raise HTTPException(status_code=400, detail="Opcion invalida")

    is_correct = options[data.selected_option]["correct"]
    xp_earned = 30 if is_correct else 0

    return QuizResultResponse(
        quiz_id=quiz_id,
        is_correct=is_correct,
        explanation=quiz["explanation"],
        xp_earned=xp_earned,
    )


@router.get("/progress", response_model=LessonProgressResponse)
async def get_progress(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el progreso educativo del usuario."""
    return LessonProgressResponse(
        lessons_completed=0,
        total_lessons=len(LESSONS_DATA),
        xp_from_lessons=0,
        quizzes_passed=0,
    )