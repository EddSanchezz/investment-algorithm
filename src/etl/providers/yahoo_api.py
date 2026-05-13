"""
Yahoo Finance Provider - Implementación con rate limiting mejorado.

Este provider es más conservador con las peticiones para evitar
el bloqueo por 429 Too Many Requests.
"""

import random
import time
from datetime import datetime
from typing import List, Dict, Optional

import requests

from .base import DataProvider


DELAY_BETWEEN_REQUESTS: float = 3.0
"""Segundos entre peticiones a distintos símbolos (mayor que antes)."""

MAX_RETRIES: int = 3
"""Máximo de reintentos por símbolo."""

BACKOFF_BASE: float = 2.0
"""Base para backoff exponencial."""

JITTER_MAX: float = 1.0
"""Jitter máximo en segundos."""

CIRCUIT_BREAKER_THRESHOLD: int = 20
"""Umbral de fallos consecutivos para activar circuit breaker."""

CIRCUIT_BREAKER_RESET: float = 120.0
"""Segundos de espera cuando se activa el circuit breaker."""

REQUEST_TIMEOUT: int = 30
"""Timeout por petición HTTP."""

USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


def _exponential_backoff(attempt: int) -> float:
    """Calcula delay con backoff exponencial y jitter."""
    return BACKOFF_BASE ** attempt + random.uniform(0, JITTER_MAX)


def _parse_timestamp(ts: int) -> str:
    """Convierte timestamp Unix a string de fecha YYYY-MM-DD."""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


class YahooFinanceProvider(DataProvider):
    """
    Proveedor de Yahoo Finance con rate limiting mejorado.

    Cambios vs fetcher.py original:
    - Delay de 3s entre símbolos (antes 0.5s)
    - Circuit breaker con threshold 20 (antes 10)
    - Circuit breaker reset de 120s (antes 60s)
    - Solo 3 reintentos (antes 5)
    """

    BASE_URL: str = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    def __init__(self, logger: Optional[callable] = None):
        self._logger = logger or print
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0,
        )
        self._session.mount("https://", adapter)

        self._consecutive_failures: int = 0
        self._circuit_open_until: float = 0.0

    @property
    def name(self) -> str:
        return "Yahoo Finance API"

    def is_available(self) -> bool:
        """Verifica si el circuit breaker está abierto."""
        if self._circuit_open_until > time.time():
            self._logger(f"  [WARN] {self.name}: Circuit Breaker activo")
            return False
        return True

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """Descarga datos históricos desde Yahoo Finance."""
        if self._circuit_open():
            self._logger(f"  [WARN] {self.name}: Saltando {symbol} (Circuit Breaker activo)")
            return []

        url = self.BASE_URL.format(symbol=symbol.upper())
        params = {
            "period1": int(start_date.timestamp()),
            "period2": int(end_date.timestamp()),
            "interval": "1d",
            "events": "history",
        }

        for attempt in range(MAX_RETRIES):
            try:
                response = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                records = self._parse_response(response.json(), symbol)
                self._consecutive_failures = 0
                if records:
                    self._logger(f"  [OK] {self.name}: {symbol} ({len(records)} registros)")
                return records

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    self._consecutive_failures += 1
                    self._check_circuit_breaker()
                    self._logger(f"  [WARN] {self.name}: Rate limit para {symbol}")

                if attempt < MAX_RETRIES - 1:
                    delay = _exponential_backoff(attempt)
                    self._logger(f"  [WARN] Reintento {attempt + 1}/{MAX_RETRIES} para {symbol} en {delay:.1f}s")
                    time.sleep(delay)
                else:
                    self._logger(f"  [ERR] {self.name}: Fallo definitivo para {symbol}")

            except requests.exceptions.RequestException as e:
                self._consecutive_failures += 1
                self._check_circuit_breaker()

                if attempt < MAX_RETRIES - 1:
                    delay = _exponential_backoff(attempt)
                    self._logger(f"  [WARN] Reintento {attempt + 1}/{MAX_RETRIES} para {symbol}: {e}")
                    time.sleep(delay)

            except (ValueError, KeyError, TypeError, IndexError) as e:
                self._logger(f"  [ERR] Error de parseo para {symbol}: {e}")
                return []

        return []

    def _parse_response(self, data: dict, symbol: str) -> List[Dict]:
        """Parsea la respuesta JSON de Yahoo Finance."""
        result = data.get("chart", {}).get("result", [])
        if not result:
            return []

        result_data = result[0]
        timestamps = result_data.get("timestamp")
        if not timestamps:
            return []

        quote = result_data.get("indicators", {}).get("quote", [{}])[0]
        opens = quote.get("open", [])
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        closes = quote.get("close", [])
        volumes = quote.get("volume", [])

        records: List[Dict] = []
        clean_symbol = symbol.split(".")[0].upper()

        for i, ts in enumerate(timestamps):
            if i >= len(closes) or closes[i] is None:
                continue
            records.append({
                "date": _parse_timestamp(ts),
                "symbol": clean_symbol,
                "open": opens[i] if i < len(opens) else None,
                "high": highs[i] if i < len(highs) else None,
                "low": lows[i] if i < len(lows) else None,
                "close": closes[i],
                "volume": volumes[i] if i < len(volumes) else None,
            })

        return records

    def _circuit_open(self) -> bool:
        """Verifica si el Circuit Breaker está abierto."""
        return self._circuit_open_until > time.time()

    def _check_circuit_breaker(self) -> None:
        """Activa el Circuit Breaker si se superó el umbral."""
        if self._consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            self._circuit_open_until = time.time() + CIRCUIT_BREAKER_RESET
            self._logger(
                f"  [BREAKER] {self.name}: Circuit Breaker activado por {CIRCUIT_BREAKER_RESET}s "
                f"tras {self._consecutive_failures} fallos."
            )
            self._consecutive_failures = 0

    def close(self) -> None:
        """Cierra la sesión HTTP."""
        self._session.close()