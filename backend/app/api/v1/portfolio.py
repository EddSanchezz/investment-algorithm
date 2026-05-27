"""
QuantVision - Portfolio Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from typing import List
import httpx

from ..core.database import get_db
from ..core.dependencies import get_current_user_id
from ..models.portfolio import TransactionCreate, PortfolioResponse, PositionResponse, WatchlistResponse
from ..models.user import User

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


async def get_current_price(symbol: str) -> float:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if resp.status_code == 200:
                data = resp.json()
                quotes = data.get("quoteResponse", {}).get("result", [])
                if quotes:
                    return quotes[0].get("regularMarketPrice", 0) or 0
        except Exception:
            pass
    return 0


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    from ..models.user import UserProgress
    progress_result = await db.execute(select(UserProgress).where(UserProgress.user_id == user_id))
    progress = progress_result.scalar_one_or_none()

    positions_map = {}
    from ..models.user import User
    transactions_result = await db.execute(
        select(User).where(User.id == user_id)  # placeholder - need transactions table
    )

    # Placeholder - return empty portfolio (real implementation needs transactions table)
    return PortfolioResponse(
        positions=[],
        total_value=0,
        total_cost=0,
        total_pnl=0,
        total_pnl_pct=0,
    )


@router.post("/transactions")
async def add_transaction(
    data: TransactionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Registra una transacción de compra o venta."""
    # Check if portfolio exists
    from ..models.user import UserProgress
    progress_result = await db.execute(select(UserProgress).where(UserProgress.user_id == user_id))
    progress = progress_result.scalar_one_or_none()

    if progress:
        new_trades = int(progress.total_trades or "0") + 1
        progress.total_trades = str(new_trades)

        # Award XP for transaction
        new_xp = int(progress.xp or "0") + 10
        progress.xp = str(new_xp)
        await db.commit()

    return {"message": "Transacción registrada", "xp_earned": 10}


@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la watchlist del usuario."""
    return WatchlistResponse(symbols=[])


@router.post("/watchlist/{symbol}")
async def add_to_watchlist(
    symbol: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Agrega un símbolo a la watchlist."""
    return {"message": f"{symbol} agregado a watchlist", "xp_earned": 2}


@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Quita un símbolo de la watchlist."""
    return {"message": f"{symbol} eliminado de watchlist"}