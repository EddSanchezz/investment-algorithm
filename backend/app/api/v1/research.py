"""
QuantVision - Research Endpoints (Algoritmos existentes)
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime
import httpx
import numpy as np

from ..core.config import get_settings
from ..models.research import (
    CompareResponse, CorrelationMatrixResponse,
    VolatilityRankingResponse, VolatilityRankingItem,
    PatternResponse, BenchmarkResponse
)

settings = get_settings()
router = APIRouter(prefix="/research", tags=["research"])


# ============================================
# HELPER: Get price data from Yahoo Finance
# ============================================

async def get_yf_prices(symbol: str, period: str = "2y") -> tuple[List[str], List[float]]:
    end = int(datetime.now().timestamp())
    start = end - 5 * 365 * 86400
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={start}&period2={end}&interval=1d"
    )
    async with httpx.AsyncClient(timeout=settings.YF_TIMEOUT) as client:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return [], []
        data = resp.json()
        chart = data.get("chart", {}).get("result", [{}])[0]
        timestamps = chart.get("timestamp", [])
        ohlc = chart.get("indicators", {}).get("quote", [{}])[0]
        closes = ohlc.get("close", [])
        dates = [datetime.fromtimestamp(t).strftime("%Y-%m-%d") for t, c in zip(timestamps, closes) if c is not None]
        valid_closes = [c for c in closes if c is not None]
        return dates, valid_closes


async def get_all_prices() -> dict:
    symbols = ["VOO", "VTI", "QQQ", "SPY", "VEA", "VWO", "BND", "EFA", "EEM",
               "TLT", "IVV", "SCHD", "DIA", "IWM", "XLF", "XLK", "KO", "PEP",
               "PFE", "ECOPETROL", "ISA", "GEB", "NUTRESA", "BTC", "ETH"]
    all_prices = {}
    for sym in symbols:
        dates, closes = await get_yf_prices(sym)
        if dates and closes:
            all_prices[sym] = {"dates": dates, "closes": closes}
    return all_prices


# ============================================
# SIMILARITY ALGORITHMS (desde tu código)
# ============================================

def euclidean_distance(prices1: List[float], prices2: List[float]) -> dict:
    n = min(len(prices1), len(prices2))
    if n == 0:
        return {"distance": None, "complexity": "O(n)"}
    diffs = [(prices1[i] - prices2[i]) ** 2 for i in range(n)]
    dist = sum(diffs) ** 0.5
    return {
        "distance": round(dist, 6),
        "formula": "d(x,y) = sqrt(sum((xi-yi)^2))",
        "complexity": "O(n)",
        "description": "Distancia euclidiana entre dos series de precios",
        "interpretation": f"Distancia = {dist:.4f}. Valores más bajos = más similares.",
    }


def pearson_correlation(returns1: List[float], returns2: List[float]) -> dict:
    n = min(len(returns1), len(returns2))
    if n < 2:
        return {"correlation": None, "complexity": "O(n)"}
    r1, r2 = returns1[:n], returns2[:n]
    mean1, mean2 = sum(r1) / n, sum(r2) / n
    cov = sum((r1[i] - mean1) * (r2[i] - mean2) for i in range(n))
    std1 = (sum((x - mean1) ** 2 for x in r1) / (n - 1)) ** 0.5
    std2 = (sum((x - mean2) ** 2 for x in r2) / (n - 1)) ** 0.5
    if std1 == 0 or std2 == 0:
        return {"correlation": 0.0, "complexity": "O(n)"}
    corr = cov / (n - 1) / (std1 * std2)
    return {
        "correlation": round(corr, 4),
        "covariance": round(cov / (n - 1), 6),
        "formula": "r = sum((xi-x)(yi-y)) / sqrt(sum((xi-x)^2) * sum((yi-y)^2))",
        "complexity": "O(n)",
        "description": "Correlación de Pearson (relación lineal)",
        "interpretation": f"r = {corr:.4f}. +1 = correlación perfecta, 0 = sin relación, -1 = correlación inversa.",
    }


def cosine_similarity(v1: List[float], v2: List[float]) -> dict:
    n = min(len(v1), len(v2))
    if n == 0:
        return {"similarity": None, "complexity": "O(n)"}
    dot = sum(v1[i] * v2[i] for i in range(n))
    norm1 = sum(x ** 2 for x in v1[:n]) ** 0.5
    norm2 = sum(x ** 2 for x in v2[:n]) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return {"similarity": 0.0, "angle_degrees": 90.0, "complexity": "O(n)"}
    sim = dot / (norm1 * norm2)
    angle = 57.2958 * (0 if sim >= 1 else (1.5708 if sim <= -1 else np.arccos(sim)))
    return {
        "similarity": round(sim, 4),
        "angle_degrees": round(angle, 2),
        "formula": "cos(theta) = (x.y) / (||x|| * ||y||)",
        "complexity": "O(n)",
        "description": "Similitud por coseno (orientación de vectores)",
        "interpretation": f"Similitud = {sim:.4f}. +1 = misma dirección, 0 = ortogonales, -1 = opuestos.",
    }


def dtw_distance(s1: List[float], s2: List[float], window: Optional[int] = None) -> dict:
    n, m = len(s1), len(s2)
    if n == 0 or m == 0:
        return {"distance": None, "normalized_distance": None, "complexity": "O(n*m)"}
    if window is None:
        window = max(n, m)
    window = max(window, abs(n - m) + 1)

    INF = float("inf")
    prev_row = [INF] * (m + 1)
    curr_row = [INF] * (m + 1)
    prev_row[0] = 0.0

    for i in range(1, n + 1):
        curr_row[0] = INF
        j_start = max(1, i - window)
        j_end = min(m, i + window)
        for j in range(1, m + 1):
            if j < j_start or j > j_end:
                curr_row[j] = INF
                continue
            cost = abs(s1[i - 1] - s2[j - 1])
            curr_row[j] = cost + min(prev_row[j], curr_row[j - 1], prev_row[j - 1])
        prev_row, curr_row = curr_row, prev_row

    dist = prev_row[m]
    path_len = n + m
    norm = dist / path_len if path_len > 0 else dist
    return {
        "distance": round(dist, 6),
        "normalized_distance": round(norm, 6),
        "path_length": path_len,
        "formula": "DTW(x,y) = min(sum(|xi-yj|) over warping path)",
        "complexity": f"O(n*w) = O({n}*{window})",
        "description": "Dynamic Time Warping (permite desfases temporales)",
        "interpretation": f"Distancia normalizada = {norm:.6f}. Valores más bajos = mayor similitud temporal.",
    }


def _returns(prices: List[float]) -> List[float]:
    if len(prices) < 2:
        return []
    return [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]


# ============================================
# ENDPOINTS
# ============================================

@router.get("/compare")
async def compare_assets(
    s1: str = Query(...),
    s2: str = Query(...),
    window: int = Query(default=252, description="Últimos N días para comparar"),
):
    """Compara dos activos usando los 4 algoritmos de similitud."""
    dates1, closes1 = await get_yf_prices(s1)
    dates2, closes2 = await get_yf_prices(s2)

    common_dates = sorted(set(dates1) & set(dates2))
    if len(common_dates) < 2:
        return {"error": f"No hay suficientes datos comunes para {s1} y {s2}"}

    price_map1 = dict(zip(dates1, closes1))
    price_map2 = dict(zip(dates2, closes2))
    p1 = [price_map1[d] for d in common_dates]
    p2 = [price_map2[d] for d in common_dates]

    if len(p1) > window:
        p1 = p1[-window:]
        p2 = p2[-window:]
        common_dates = common_dates[-window:]

    r1 = _returns(p1)
    r2 = _returns(p2)

    return {
        "symbol1": s1,
        "symbol2": s2,
        "common_dates": len(common_dates),
        "euclidean": euclidean_distance(p1, p2),
        "pearson": pearson_correlation(r1, r2),
        "dtw": dtw_distance(p1, p2, window=min(50, len(p1) // 10)),
        "cosine": cosine_similarity(r1, r2),
    }


@router.get("/correlation-matrix")
async def correlation_matrix(symbols: str = Query(..., description="Símbolos separados por coma")):
    """Calcula la matriz de correlación de Pearson para un grupo de símbolos."""
    sym_list = [s.strip().upper() for s in symbols.split(",")]
    all_prices = {}
    dates_set = set()

    for sym in sym_list:
        dates, closes = await get_yf_prices(sym)
        if dates and closes:
            all_prices[sym] = dict(zip(dates, closes))
            dates_set.update(dates)

    common_dates = sorted(dates_set)
    if len(common_dates) < 10:
        return {"error": "No hay suficientes datos", "symbols": sym_list, "matrix": []}

    n = len(sym_list)
    matrix = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            s1, s2 = sym_list[i], sym_list[j]
            if s1 in all_prices and s2 in all_prices:
                p1 = [all_prices[s1].get(d) for d in common_dates if all_prices[s1].get(d) is not None]
                p2 = [all_prices[s2].get(d) for d in common_dates if all_prices[s2].get(d) is not None]
                r1, r2 = _returns(p1), _returns(p2)
                result = pearson_correlation(r1, r2)
                val = result.get("correlation", 0)
                if val is not None:
                    matrix[i][j] = round(val, 4)
                    matrix[j][i] = round(val, 4)

    return {"symbols": sym_list, "matrix": matrix}


@router.get("/volatility-ranking")
async def volatility_ranking(symbols: str = Query(default="VOO,VTI,QQQ,SPY,BND,KO,PEP,PFE", description="Símbolos separados por coma")):
    """Calcula la volatilidad anualizada y clasifica por riesgo."""
    sym_list = [s.strip().upper() for s in symbols.split(",")]
    ranking = []

    for sym in sym_list:
        dates, closes = await get_yf_prices(sym)
        if not closes or len(closes) < 30:
            continue
        returns = _returns(closes)
        if len(returns) < 2:
            continue
        mean_ret = sum(returns) / len(returns)
        variance = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
        std_daily = variance ** 0.5
        vol_annual = std_daily * (252 ** 0.5)
        daily_pct = std_daily * 100
        mean_pct = mean_ret * 100
        cat = "Conservador" if vol_annual < 0.15 else ("Moderado" if vol_annual < 0.30 else "Agresivo")
        ranking.append({
            "symbol": sym,
            "annualized_volatility_pct": round(vol_annual * 100, 2),
            "daily_std": round(daily_pct, 3),
            "mean_daily_return_pct": round(mean_pct, 3),
            "risk_category": cat,
        })

    ranking.sort(key=lambda x: x["annualized_volatility_pct"])
    avg_vol = sum(r["annualized_volatility_pct"] for r in ranking) / len(ranking) if ranking else 0
    cats = {"Conservador": 0, "Moderado": 0, "Agresivo": 0}
    for r in ranking:
        cats[r["risk_category"]] = cats.get(r["risk_category"], 0) + 1

    return {
        "ranking": ranking,
        "summary": {
            "total_symbols": len(ranking),
            "average_volatility_pct": round(avg_vol, 2),
            "categories": cats,
        },
    }


@router.get("/patterns")
async def detect_patterns(
    symbol: str = Query(...),
    pattern_type: str = Query(default="consecutive_up"),
    min_days: int = Query(default=3, ge=2, le=10),
):
    """Detecta patrones en series temporales de precios."""
    dates, closes = await get_yf_prices(symbol)
    if not closes:
        return {"error": f"No se encontraron datos para {symbol}"}

    occurrences = []
    by_year = {}

    if pattern_type == "consecutive_up":
        for i in range(1, len(closes)):
            if closes[i] > closes[i - 1]:
                count = 1
                while i + count < len(closes) and closes[i + count] > closes[i + count - 1]:
                    count += 1
                if count >= min_days:
                    year = dates[i][:4]
                    by_year[year] = by_year.get(year, 0) + 1
                    occurrences.append({
                        "date": dates[i],
                        "start_date": dates[i - count + 1],
                        "end_date": dates[i],
                        "duration": count,
                        "change_pct": round((closes[i] - closes[i - count + 1]) / closes[i - count + 1] * 100, 2),
                    })

    elif pattern_type == "gap_up":
        threshold = 0.02
        for i in range(1, len(closes)):
            if closes[i] > closes[i - 1] * (1 + threshold):
                year = dates[i][:4]
                by_year[year] = by_year.get(year, 0) + 1
                occurrences.append({
                    "date": dates[i],
                    "gap_pct": round((closes[i] - closes[i - 1]) / closes[i - 1] * 100, 2),
                })

    return {
        "symbol": symbol,
        "pattern_type": pattern_type,
        "total_occurrences": len(occurrences),
        "occurrences": occurrences[-20:],
        "frequency_by_year": dict(sorted(by_year.items())),
    }


@router.get("/benchmark")
async def sorting_benchmark(n: int = Query(default=1000, ge=100, le=5000)):
    """Benchmark de algoritmos de ordenamiento sobre datos financieros."""
    import random
    data = [random.uniform(100, 200) for _ in range(n)]
    results = []

    # Selection Sort
    arr = data.copy()
    start = datetime.now()
    for i in range(len(arr)):
        min_j = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_j]:
                min_j = j
        arr[i], arr[min_j] = arr[min_j], arr[i]
    results.append({"algorithm": "Selection Sort", "time_ms": (datetime.now() - start).total_seconds() * 1000, "complexity": "O(n^2)"})

    # Bubble Sort
    arr = data.copy()
    start = datetime.now()
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    results.append({"algorithm": "Bubble Sort", "time_ms": (datetime.now() - start).total_seconds() * 1000, "complexity": "O(n^2)"})

    # Insertion Sort
    arr = data.copy()
    start = datetime.now()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    results.append({"algorithm": "Insertion Sort", "time_ms": (datetime.now() - start).total_seconds() * 1000, "complexity": "O(n^2)"})

    # Merge Sort
    def merge_sort(arr):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left, right = merge_sort(arr[:mid]), merge_sort(arr[mid:])
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    arr = data.copy()
    start = datetime.now()
    merge_sort(arr)
    results.append({"algorithm": "Merge Sort", "time_ms": (datetime.now() - start).total_seconds() * 1000, "complexity": "O(n log n)"})

    results.sort(key=lambda x: x["time_ms"])
    return {"dataset_size": n, "results": results}