"""
Fetcher Module — Extracción de datos financieros mediante HTTP directo.

Ahora usa el sistema Multi-Source con fallback automático:
- Yahoo Finance API (rate limiting mejorado)
- Alpha Vantage API
- Web Scraper (5 sitios)
- Binance (solo crypto)

El sistema intenta providers en secuencia hasta obtener datos.

Restricciones del proyecto:
- ✅ NO usa yfinance / pandas_datareader (peticiones HTTP explícitas)
- ✅ Parseo manual del JSON de respuesta
- ✅ Reintentos automáticos documentados
"""

import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from .providers import MultiSourceFetcher


def _default_logger(msg: str) -> None:
    """Logger por defecto."""
    print(msg)


class FinancialDataFetcher:
    """
    Wrapper que usa MultiSourceFetcher para descarga de datos.

    Este wrapper mantiene la interfaz existente pero internamente
    usa el sistema de providers con fallback automático.

    Providers en orden de prioridad:
    1. Yahoo Finance API (rate limiting mejorado)
    2. Alpha Vantage API
    3. Web Scraper (5 sitios)
    4. Binance (solo crypto)
    """

    def __init__(self, logger: Optional[callable] = None):
        self._logger = logger or _default_logger
        self._fetcher = MultiSourceFetcher(self._logger)

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """
        Descarga datos para un símbolo usando el sistema Multi-Source.

        Args:
            symbol: Símbolo del activo (ej: "VOO", "ECOPETROL.CL")
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            Lista de registros OHLCV
        """
        return self._fetcher.fetch(symbol, start_date, end_date)

    def fetch_with_fallback(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """Alias para fetch_historical_data (compatibilidad hacia atrás)."""
        return self.fetch_historical_data(symbol, start_date, end_date)

    def fetch_multiple_assets(
        self,
        symbols: List[str],
        years: int = 5,
        use_fallback: bool = False,
    ) -> List[Dict]:
        """
        Descarga datos para múltiples activos.

        Args:
            symbols: Lista de símbolos
            years: Años de historial
            use_fallback: Ignorado (el sistema ya usa fallback automático)

        Returns:
            Dataset combinado de todos los activos
        """
        return self._fetcher.fetch_multiple(symbols, years)

    @staticmethod
    def save_to_csv(records: List[Dict], filepath: str) -> None:
        """Guarda registros en CSV."""
        if not records:
            print("No hay datos para guardar")
            return

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        fieldnames = ["date", "symbol", "open", "high", "low", "close", "volume"]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        print(f"Datos guardados en {filepath} ({len(records)} registros)")

    def close(self) -> None:
        """Cierra recursos del fetcher."""
        self._fetcher.close()

