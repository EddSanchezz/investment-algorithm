"""
QuantVision - Asset Models (Pydantic)
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date


class AssetBase(BaseModel):
    symbol: str
    name: str
    asset_type: str  # 'stock', 'etf', 'crypto'


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    price: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None


class AssetSearchResponse(BaseModel):
    symbol: str
    name: str
    exchange: str
    asset_type: str


class OHLCResponse(BaseModel):
    dates: List[str]
    ohlc: List[dict]  # [{"open": float, "high": float, "low": float, "close": float, "volume": int}]


class HistoryResponse(BaseModel):
    symbol: str
    dates: List[str]
    closes: List[float]
    volumes: List[int]