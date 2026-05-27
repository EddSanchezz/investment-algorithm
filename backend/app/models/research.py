"""
QuantVision - Research Models (Pydantic)
"""
from pydantic import BaseModel
from typing import List, Optional, Dict


class CompareResponse(BaseModel):
    symbol1: str
    symbol2: str
    common_dates: int
    euclidean: dict
    pearson: dict
    dtw: dict
    cosine: dict


class CorrelationMatrixResponse(BaseModel):
    symbols: List[str]
    matrix: List[List[float]]


class VolatilityRankingItem(BaseModel):
    symbol: str
    annualized_volatility_pct: float
    daily_std: float
    mean_daily_return_pct: float
    risk_category: str  # 'Conservador', 'Moderado', 'Agresivo'


class VolatilityRankingResponse(BaseModel):
    ranking: List[VolatilityRankingItem]
    summary: dict


class PatternResponse(BaseModel):
    symbol: str
    pattern_type: str
    occurrences: List[dict]
    frequency_by_year: Dict[str, int]
    total_occurrences: int


class BenchmarkResponse(BaseModel):
    dataset_size: int
    results: List[dict]