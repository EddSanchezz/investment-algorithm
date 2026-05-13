"""
Multi-Source Fetcher - Orquestador de múltiples proveedores de datos.

Este es el componente principal que intenta proveedores en secuencia
hasta obtener datos exitosos.

Orden de providers:
1. Tiingo API - Principal, 500 req/hora gratis, datos de alta calidad
2. Yahoo Finance API - Rate limiting mejorado
3. Alpha Vantage - API REST con key proporcionada
4. Web Scraper (5 sitios) - Scraping ético como último recurso
5. Binance - Solo para crypto
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable

from .base import DataProvider
from .tiingo import TiingoProvider
from .yahoo_api import YahooFinanceProvider
from .alpha_vantage import AlphaVantageProvider
from .stooq import StooqProvider
from .web_scraper import WebScraperProvider
from .binance import BinanceProvider


DELAY_BETWEEN_PROVIDERS: float = 1.0
DELAY_BETWEEN_SYMBOLS: float = 2.0


class MultiSourceFetcher:
    """
    Orquestador que intenta múltiples fuentes de datos en secuencia.

    Cada provider se prueba en orden. El primer provider que retorna
    datos detiene la búsqueda para ese símbolo.
    """

    def __init__(self, logger: Optional[Callable[[str], None]] = None):
        self._logger = logger or print
        self._providers: List[DataProvider] = []
        self._symbol_provider_map: Dict[str, str] = {}
        self._init_providers()

    def _init_providers(self) -> None:
        """Inicializa todos los providers en orden de prioridad."""
        self._providers = [
            TiingoProvider(self._logger),
            YahooFinanceProvider(self._logger),
            AlphaVantageProvider(self._logger),
            StooqProvider(self._logger),
            WebScraperProvider(self._logger),
            BinanceProvider(self._logger),
        ]

    @property
    def providers(self) -> List[DataProvider]:
        """Retorna la lista de providers."""
        return self._providers

    @property
    def symbol_provider_map(self) -> Dict[str, str]:
        """Retorna el mapa de simbolo -> provider exitoso."""
        return dict(self._symbol_provider_map)

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """
        Intenta obtener datos de cada provider en secuencia.

        Args:
            symbol: Símbolo del activo
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            Lista de registros OHLCV del primer provider exitoso
        """
        self._logger(f"\n================================================")
        self._logger(f"Descargando {symbol.upper()}...")
        self._logger(f"================================================")

        for idx, provider in enumerate(self._providers):
            if not provider.is_available():
                self._logger(f"  [X] {provider.name}: No disponible")
                continue

            self._logger(f"\n-> Intentando con {provider.name}...")

            try:
                records = provider.fetch(symbol, start_date, end_date)

                if records:
                    self._logger(f"\n[OK] {provider.name} exito: {len(records)} registros")
                    self._symbol_provider_map[symbol.upper()] = provider.name
                    return records
                else:
                    self._logger(f"  [X] {provider.name}: Sin datos")

            except Exception as e:
                self._logger(f"  [ERR] {provider.name}: Excepcion: {e}")

            if idx < len(self._providers) - 1:
                time.sleep(DELAY_BETWEEN_PROVIDERS)

        self._logger(f"\n[FAIL] Ningun provider pudo obtener datos para {symbol}")
        return []

    def fetch_multiple(
        self,
        symbols: List[str],
        years: int = 5,
    ) -> List[Dict]:
        """
        Descarga datos para múltiples activos.

        Args:
            symbols: Lista de símbolos
            years: Años de historial

        Returns:
            Dataset combinado de todos los activos
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        all_records: List[Dict] = []
        total = len(symbols)
        self._symbol_provider_map = {}

        for idx, symbol in enumerate(symbols, 1):
            records = self.fetch(symbol, start_date, end_date)

            if records:
                all_records.extend(records)
                self._logger(f"  [OK] Total: {len(all_records)} registros")
            else:
                self._logger(f"  [ERR] Sin datos para {symbol}")

            if idx < total:
                time.sleep(DELAY_BETWEEN_SYMBOLS)

        # Report
        self._logger(f"\n{'=' * 50}")
        self._logger(f"DESCARGA COMPLETA: {len(all_records)} registros total")
        self._logger(f"{'=' * 50}")

        if self._symbol_provider_map:
            self._logger(f"\nFuentes por simbolo:")
            for sym, prov in sorted(self._symbol_provider_map.items()):
                self._logger(f"  [OK] {sym} -> {prov}")

        return all_records

    def close(self) -> None:
        """Cierra todos los providers."""
        for provider in self._providers:
            try:
                provider.close()
            except Exception:
                pass


def create_fetcher(logger: Optional[Callable[[str], None]] = None) -> MultiSourceFetcher:
    """
    Factory function para crear un MultiSourceFetcher.

    Args:
        logger: Función de logging opcional

    Returns:
        Instancia de MultiSourceFetcher
    """
    return MultiSourceFetcher(logger)
