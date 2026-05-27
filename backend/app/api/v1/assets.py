"""
QuantVision - Assets Endpoints (Yahoo Finance integration)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import httpx
from datetime import datetime

from ..core.config import get_settings
from ..models.asset import AssetSearchResponse, AssetResponse, OHLCResponse, HistoryResponse

settings = get_settings()
router = APIRouter(prefix="/assets", tags=["assets"])

SUPPORTED_SYMBOLS = [
    # BVC
    "ECOPETROL", "ISA", "GEB", "NUTRESA",
    # ETFs
    "VOO", "VTI", "QQQ", "SPY", "VEA", "VWO", "BND", "EFA", "EEM",
    "TLT", "IVV", "SCHD", "DIA", "IWM", "XLF", "XLK", "VIG", "QUAL",
    # NYSE Stocks
    "KO", "PEP", "PFE", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA",
    "NVDA", "AMD", "INTC", "NFLX", "DIS", "BA", "JPM", "BAC", "WFC", "GS", "MS",
    # Crypto
    "BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "DOT", "AVAX", "MATIC", "LINK",
    "UNI", "ATOM", "LTC", "BCH", "XLM", "ALGO", "VET", "FIL", "THETA",
]

SYMBOL_NAMES = {
    "ECOPETROL": "Ecopetrol S.A.",
    "ISA": "ISA Intercolombia",
    "GEB": "Grupo Energia Bogota",
    "NUTRESA": "Nutresa S.A.",
    "VOO": "Vanguard S&P 500 ETF",
    "VTI": "Vanguard Total Stock Market ETF",
    "QQQ": "Invesco QQQ Trust",
    "SPY": "SPDR S&P 500 ETF",
    "VEA": "Vanguard FTSE Developed Markets ETF",
    "VWO": "Vanguard FTSE Emerging Markets ETF",
    "BND": "Vanguard Total Bond Market ETF",
    "EFA": "iShares MSCI EAFE ETF",
    "EEM": "iShares MSCI Emerging Markets ETF",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "IVV": "iShares Core S&P 500 ETF",
    "SCHD": "Schwab U.S. Dividend Equity ETF",
    "DIA": "SPDR Dow Jones Industrial Average ETF",
    "IWM": "iShares Russell 2000 ETF",
    "XLF": "Financial Select Sector SPDR Fund",
    "XLK": "Technology Select Sector SPDR Fund",
    "KO": "Coca-Cola Company",
    "PEP": "PepsiCo Inc.",
    "PFE": "Pfizer Inc.",
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
}


def get_asset_type(symbol: str) -> str:
    if symbol in ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "DOT", "AVAX", "MATIC", "LINK",
                  "UNI", "ATOM", "LTC", "BCH", "XLM", "ALGO", "VET", "FIL", "THETA"]:
        return "crypto"
    if symbol in ["VOO", "VTI", "QQQ", "SPY", "VEA", "VWO", "BND", "EFA", "EEM",
                  "TLT", "IVV", "SCHD", "DIA", "IWM", "XLF", "XLK", "VIG", "QUAL"]:
        return "etf"
    return "stock"


@router.get("", response_model=List[AssetResponse])
async def list_assets():
    """Lista todos los activos disponibles con datos básicos de Yahoo Finance."""
    results = []
    async with httpx.AsyncClient(timeout=settings.YF_TIMEOUT) as client:
        symbols_str = "+".join(SUPPORTED_SYMBOLS[:50])  # Yahoo limit
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols_str}"
        try:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                quotes = data.get("quoteResponse", {}).get("result", [])
                for q in quotes:
                    symbol = q.get("symbol", "")
                    results.append(AssetResponse(
                        symbol=symbol,
                        name=SYMBOL_NAMES.get(symbol, q.get("shortName", symbol)),
                        asset_type=get_asset_type(symbol),
                        price=q.get("regularMarketPrice"),
                        change_pct=q.get("regularMarketChangePercent"),
                        volume=q.get("regularMarketVolume"),
                        market_cap=q.get("marketCap"),
                        pe_ratio=q.get("trailingPE"),
                        week_52_high=q.get("fiftyTwoWeekHigh"),
                        week_52_low=q.get("fiftyTwoWeekLow"),
                    ))
        except Exception:
            pass

    # Add symbols that couldn't be fetched
    fetched = {r.symbol for r in results}
    for sym in SUPPORTED_SYMBOLS:
        if sym not in fetched:
            results.append(AssetResponse(
                symbol=sym,
                name=SYMBOL_NAMES.get(sym, sym),
                asset_type=get_asset_type(sym),
            ))

    return results


@router.get("/search", response_model=List[AssetSearchResponse])
async def search_assets(q: str = Query(..., min_length=1)):
    """Busca activos por símbolo o nombre."""
    q_upper = q.upper()
    results = []
    for sym in SUPPORTED_SYMBOLS:
        name = SYMBOL_NAMES.get(sym, sym)
        if q_upper in sym or q_upper in name.upper():
            results.append(AssetSearchResponse(
                symbol=sym,
                name=name,
                exchange="BVC" if ".CL" in sym else "NYSE",
                asset_type=get_asset_type(sym),
            ))
    return results[:10]


@router.get("/{symbol}")
async def get_asset(symbol: str):
    """Detalle de un activo específico."""
    async with httpx.AsyncClient(timeout=settings.YF_TIMEOUT) as client:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        try:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                quotes = data.get("quoteResponse", {}).get("result", [])
                if not quotes:
                    raise HTTPException(status_code=404, detail="Activo no encontrado")
                q = quotes[0]
                return {
                    "symbol": q.get("symbol"),
                    "name": SYMBOL_NAMES.get(symbol, q.get("shortName", symbol)),
                    "asset_type": get_asset_type(symbol),
                    "price": q.get("regularMarketPrice"),
                    "change_pct": q.get("regularMarketChangePercent"),
                    "volume": q.get("regularMarketVolume"),
                    "market_cap": q.get("marketCap"),
                    "pe_ratio": q.get("trailingPE"),
                    "week_52_high": q.get("fiftyTwoWeekHigh"),
                    "week_52_low": q.get("fiftyTwoWeekLow"),
                    "day_high": q.get("regularMarketDayHigh"),
                    "day_low": q.get("regularMarketDayLow"),
                    "previous_close": q.get("regularMarketPreviousClose"),
                }
        except httpx.HTTPError:
            raise HTTPException(status_code=502, detail="Error al obtener datos de Yahoo Finance")
    raise HTTPException(status_code=404, detail="Activo no encontrado")


@router.get("/{symbol}/ohlc")
async def get_ohlc(symbol: str, period: str = "1y"):
    """Datos OHLC para gráficos (precio histórico)."""
    end = int(datetime.now().timestamp())
    if period == "1mo": start = end - 30 * 86400
    elif period == "3mo": start = end - 90 * 86400
    elif period == "6mo": start = end - 180 * 86400
    elif period == "1y": start = end - 365 * 86400
    elif period == "2y": start = end - 730 * 86400
    else: start = end - 365 * 86400

    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={start}&period2={end}&interval=1d"
    )
    async with httpx.AsyncClient(timeout=settings.YF_TIMEOUT) as client:
        try:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Error al obtener datos de Yahoo Finance")
            data = resp.json()
            chart = data.get("chart", {}).get("result", [{}])[0]
            timestamps = chart.get("timestamp", [])
            ohlc = chart.get("indicators", {}).get("quote", [{}])[0]

            dates = [datetime.fromtimestamp(t).strftime("%Y-%m-%d") for t in timestamps]
            return {
                "symbol": symbol,
                "dates": dates,
                "ohlc": [
                    {
                        "open": o.get("open"),
                        "high": o.get("high"),
                        "low": o.get("low"),
                        "close": o.get("close"),
                        "volume": o.get("volume"),
                    }
                    for o in zip(
                        ohlc.get("open", []),
                        ohlc.get("high", []),
                        ohlc.get("low", []),
                        ohlc.get("close", []),
                        ohlc.get("volume", []),
                    )
                ],
            }
        except httpx.HTTPError:
            raise HTTPException(status_code=502, detail="Error al obtener datos de Yahoo Finance")