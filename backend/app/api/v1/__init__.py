# QuantVision API v1</from .auth import router as auth_router
from .assets import router as assets_router
from .research import router as research_router
from .portfolio import router as portfolio_router
from .news import router as news_router
from .education import router as education_router
from .gamification import router as gamification_router

routers = [
    auth_router,
    assets_router,
    research_router,
    portfolio_router,
    news_router,
    education_router,
    gamification_router,
]

__all__ = ["routers"]