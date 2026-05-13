"""
Alpha Vantage Provider - API REST para datos financieros.

Requiere ALPHA_VANTAGE_API_KEY en variable de entorno.
Rate limit: 5 calls/minute, 500 calls/day
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Optional

import requests

from .base import DataProvider


API_KEY: str = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
BASE_URL: str = "https://www.alphavantage.co/query"

REQUEST_TIMEOUT: int = 30
DELAY_BETWEEN_CALLS: float = 12.5
"""Delay entre llamadas (para respetar rate limit de 5/min)."""

MAX_RETRIES: int = 3
BACKOFF_BASE: float = 2.0


class AlphaVantageProvider(DataProvider):
    """
    Proveedor de datos vía Alpha Vantage REST API.

    Ventajas:
    - API oficial con formato JSON consistente
    - Rate limiting propio (respeta 5 calls/min)
    - Datos de alta calidad

    Desventajas:
    - Rate limit estricto
    - symbols con sufijos pueden no funcionar
    """

    def __init__(self, logger: Optional[callable] = None):
        self._logger = logger or print
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        self._last_call_time: float = 0.0

    @property
    def name(self) -> str:
        return "Alpha Vantage"

    def _wait_for_rate_limit(self) -> None:
        """Espera el tiempo necesario para respetar el rate limit."""
        elapsed = time.time() - self._last_call_time
        if elapsed < DELAY_BETWEEN_CALLS:
            wait_time = DELAY_BETWEEN_CALLS - elapsed
            self._logger(f"  ⏳ {self.name}: Esperando {wait_time:.1f}s (rate limit)")
            time.sleep(wait_time)
        self._last_call_time = time.time()

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """Descarga datos desde Alpha Vantage."""
        self._wait_for_rate_limit()

        clean_symbol = symbol.split(".")[0].upper()

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": clean_symbol,
            "apikey": API_KEY,
            "outputsize": "full",
        }

        for attempt in range(MAX_RETRIES):
            try:
                response = self._session.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()

                if "Error Message" in data:
                    self._logger(f"  [ERR] {self.name}: Error API para {symbol}: {data['Error Message']}")
                    return []

                if "Note" in data:
                    self._logger(f"  [WARN] {self.name}: Rate limit alcanzado: {data['Note']}")
                    return []

                time_series = data.get("Time Series (Daily)", {})
                if not time_series:
                    self._logger(f"  [ERR] {self.name}: Sin datos para {symbol}")
                    return []

                records = self._parse_time_series(time_series, clean_symbol, start_date, end_date)

                if records:
                    self._logger(f"  [OK] {self.name}: {symbol} ({len(records)} registros)")
                return records

            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    delay = BACKOFF_BASE ** attempt
                    self._logger(f"  [WARN] Reintento {attempt + 1}/{MAX_RETRIES} para {symbol}: {e}")
                    time.sleep(delay)
                else:
                    self._logger(f"  [ERR] {self.name}: Fallo definitivo para {symbol}: {e}")

            except (ValueError, KeyError) as e:
                self._logger(f"  [ERR] Error de parseo para {symbol}: {e}")
                return []

        return []

    def _parse_time_series(
        self,
        time_series: dict,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """Parsea el JSON de Time Series a registros OHLCV."""
        records: List[Dict] = []

        for date_str, values in time_series.items():
            try:
                record_date = datetime.strptime(date_str, "%Y-%m-%d")

                if not (start_date <= record_date <= end_date):
                    continue

                record = {
                    "date": date_str,
                    "symbol": symbol,
                    "open": self._safe_float(values.get("1. open")),
                    "high": self._safe_float(values.get("2. high")),
                    "low": self._safe_float(values.get("3. low")),
                    "close": self._safe_float(values.get("4. close")),
                    "volume": self._safe_int(values.get("5. volume")),
                }

                if record["close"] is not None:
                    records.append(record)

            except (ValueError, TypeError):
                continue

        records.sort(key=lambda x: x["date"])
        return records

    @staticmethod
    def _safe_float(value: Optional[str]) -> Optional[float]:
        """Convierte string a float de forma segura."""
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _safe_int(value: Optional[str]) -> Optional[int]:
        """Convierte string a int de forma segura."""
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def close(self) -> None:
        """Cierra la sesión HTTP."""
        self._session.close()