"""
Providers Package - Múltiples fuentes de datos financieros.

Este package proporciona un sistema de fallback robusto que intenta
múltiples fuentes de datos en orden de prioridad hasta obtener datos.

Proveedores disponibles:
- TiingoProvider: Tiingo REST API (principal, 500 req/hora gratis)
- YahooFinanceProvider: Yahoo Finance API con rate limiting mejorado
- AlphaVantageProvider: Alpha Vantage REST API
- WebScraperProvider: Scraping de 5 sitios financieros populares
- BinanceProvider: Binance Spot API (solo para crypto)
- MultiSourceFetcher: Orquestador que prueba providers en cadena
"""

from .base import DataProvider
from .tiingo import TiingoProvider
from .yahoo_api import YahooFinanceProvider
from .alpha_vantage import AlphaVantageProvider
from .web_scraper import WebScraperProvider
from .binance import BinanceProvider
from .multi_source import MultiSourceFetcher

__all__ = [
    "DataProvider",
    "TiingoProvider",
    "YahooFinanceProvider",
    "AlphaVantageProvider",
    "WebScraperProvider",
    "BinanceProvider",
    "MultiSourceFetcher",
]