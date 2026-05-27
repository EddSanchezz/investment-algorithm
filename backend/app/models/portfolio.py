"""
QuantVision - Portfolio Models (Pydantic)
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date
from decimal import Decimal


class TransactionCreate(BaseModel):
    symbol: str
    transaction_type: str  # 'BUY' or 'SELL'
    shares: float
    price_per_share: float
    transaction_date: date


class PositionResponse(BaseModel):
    symbol: str
    shares: float
    avg_price: float
    current_price: float
    current_value: float
    pnl: float
    pnl_pct: float


class PortfolioResponse(BaseModel):
    positions: List[PositionResponse]
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_pct: float


class WatchlistResponse(BaseModel):
    symbols: List[str]