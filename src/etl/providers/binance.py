"""
Binance Provider - API de Binance para datos de crypto.

Solo para símbolos cryptocurrency. Usa el endpoint público de klines.
"""

import time
from datetime import datetime
from typing import List, Dict, Optional

import requests

from .base import DataProvider


BASE_URL: str = "https://api.binance.com/api/v3/klines"
REQUEST_TIMEOUT: int = 30

CRYPTO_SYMBOLS = {
    "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT",
    "MATIC", "LTC", "AVAX", "LINK", "ATOM", "UNI", "XLM",
}


class BinanceProvider(DataProvider):
    """
    Proveedor de datos de Binance Spot API.

    Solo funciona para símbolos crypto. Intenta buscar el símbolo
    en formato {SYMBOL}USDT.
    """

    def __init__(self, logger: Optional[callable] = None):
        self._logger = logger or print
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
        })

    @property
    def name(self) -> str:
        return "Binance"

    def is_available(self) -> bool:
        return True

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """Descarga datos de Binance para símbolos crypto."""
        clean_symbol = symbol.split(".")[0].upper()

        if clean_symbol not in CRYPTO_SYMBOLS:
            self._logger(f"  [INFO] {self.name}: {symbol} no es crypto, saltando")
            return []

        params = {
            "symbol": f"{clean_symbol}USDT",
            "interval": "1d",
            "startTime": int(start_date.timestamp() * 1000),
            "endTime": int(end_date.timestamp() * 1000),
            "limit": 1000,
        }

        try:
            response = self._session.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            klines = response.json()

            if not isinstance(klines, list) or not klines:
                self._logger(f"  [ERR] {self.name}: Sin datos para {symbol}")
                return []

            records: List[Dict] = []

            for k in klines:
                try:
                    ts = k[0] / 1000
                    record_date = datetime.fromtimestamp(ts)

                    if not (start_date <= record_date <= end_date):
                        continue

                    records.append({
                        "date": record_date.strftime("%Y-%m-%d"),
                        "symbol": clean_symbol,
                        "open": float(k[1]),
                        "high": float(k[2]),
                        "low": float(k[3]),
                        "close": float(k[4]),
                        "volume": int(k[5]),
                    })
                except (ValueError, IndexError, TypeError):
                    continue

            if records:
                self._logger(f"  [OK] {self.name}: {symbol} ({len(records)} registros)")

            return records

        except requests.exceptions.HTTPError as e:
            self._logger(f"  [ERR] {self.name}: HTTP error para {symbol}: {e}")
        except requests.exceptions.RequestException as e:
            self._logger(f"  [ERR] {self.name}: Error de red para {symbol}: {e}")
        except (ValueError, KeyError) as e:
            self._logger(f"  [ERR] {self.name}: Error de parseo para {symbol}: {e}")

        return []

    def close(self) -> None:
        """Cierra la sesión HTTP."""
        self._session.close()