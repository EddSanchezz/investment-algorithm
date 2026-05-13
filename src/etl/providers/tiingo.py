"""
Tiingo Provider - API REST de Tiingo para datos financieros.

API Token: 7ef477f89420fd2e44ed2f9020653ac672a2ddc8
Rate limit: 500 requests/hour, 20,000 requests/day
"""

import time
from datetime import datetime
from typing import List, Dict, Optional

import requests

from .base import DataProvider


API_TOKEN: str = "7ef477f89420fd2e44ed2f9020653ac672a2ddc8"
BASE_URL: str = "https://api.tiingo.com/tiingo/daily/{symbol}/prices"

REQUEST_TIMEOUT: int = 30
DELAY_BETWEEN_CALLS: float = 1.0
"""Delay entre llamadas (muy por debajo del rate limit de 500/h)."""

MAX_RETRIES: int = 3
BACKOFF_BASE: float = 2.0


class TiingoProvider(DataProvider):
    """
    Proveedor de datos via Tiingo REST API.

    Ventajas:
    - API oficial con formato JSON consistente
    - 500 requests/hour gratis
    - 50+ anos de historial
    - Datos ajustados por dividendos y splits
    - Cobertura: US stocks, ETFs, algunos internacionales (ADR)
    """

    def __init__(self, logger: Optional[callable] = None):
        self._logger = logger or print
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
        })
        self._last_call_time: float = 0.0

    @property
    def name(self) -> str:
        return "Tiingo API"

    def _wait_for_rate_limit(self) -> None:
        """Espera lo necesario para no exceder rate limit."""
        elapsed = time.time() - self._last_call_time
        if elapsed < DELAY_BETWEEN_CALLS:
            time.sleep(DELAY_BETWEEN_CALLS - elapsed)
        self._last_call_time = time.time()

    def _tiingo_symbol(self, symbol: str) -> str:
        """Convierte simbolo al formato que entiende Tiingo."""
        clean = symbol.split(".")[0].upper()
        # Mapeo de tickers colombianos
        mapping = {
            "ECOPETROL": "EC",
            "GEB": "GEB",
        }
        return mapping.get(clean, clean)

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """Descarga datos historicos desde Tiingo API."""
        self._wait_for_rate_limit()

        tiingo_sym = self._tiingo_symbol(symbol)
        url = BASE_URL.format(symbol=tiingo_sym)

        params = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "token": API_TOKEN,
        }

        for attempt in range(MAX_RETRIES):
            try:
                response = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                if response.status_code == 404:
                    self._logger(f"  [ERR] {self.name}: Simbolo '{tiingo_sym}' no encontrado en Tiingo")
                    return []

                response.raise_for_status()
                data = response.json()

                if not isinstance(data, list) or not data:
                    self._logger(f"  [ERR] {self.name}: Sin datos para {symbol} -> {tiingo_sym}")
                    return []

                records = self._parse_response(data, symbol)
                if records:
                    self._logger(f"  [OK] {self.name}: {symbol} ({len(records)} registros)")
                return records

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    self._logger(f"  [WARN] {self.name}: Rate limit, esperando...")
                    time.sleep(10)
                    continue

                if attempt < MAX_RETRIES - 1:
                    delay = BACKOFF_BASE ** attempt
                    self._logger(f"  [WARN] Reintento {attempt + 1}/{MAX_RETRIES}: {e}")
                    time.sleep(delay)
                else:
                    self._logger(f"  [ERR] {self.name}: Fallo para {symbol}: {e}")

            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    delay = BACKOFF_BASE ** attempt
                    self._logger(f"  [WARN] Reintento {attempt + 1}/{MAX_RETRIES}: {e}")
                    time.sleep(delay)
                else:
                    self._logger(f"  [ERR] {self.name}: Error de red para {symbol}: {e}")

            except (ValueError, KeyError, TypeError) as e:
                self._logger(f"  [ERR] {self.name}: Error de parseo para {symbol}: {e}")
                return []

        return []

    def _parse_response(self, data: list, original_symbol: str) -> List[Dict]:
        """Parsea la respuesta JSON de Tiingo a formato OHLCV."""
        clean_symbol = original_symbol.split(".")[0].upper()

        records: List[Dict] = []
        for item in data:
            try:
                date_str = item.get("date", "")
                record_date = datetime.strptime(date_str[:10], "%Y-%m-%d")

                record = {
                    "date": date_str[:10],
                    "symbol": clean_symbol,
                    "open": item.get("adjOpen") or item.get("open"),
                    "high": item.get("adjHigh") or item.get("high"),
                    "low": item.get("adjLow") or item.get("low"),
                    "close": item.get("adjClose") or item.get("close"),
                    "volume": item.get("adjVolume") or item.get("volume"),
                }

                if record["close"] is not None:
                    records.append(record)

            except (ValueError, TypeError):
                continue

        return records

    def close(self) -> None:
        """Cierra la sesion HTTP."""
        self._session.close()
