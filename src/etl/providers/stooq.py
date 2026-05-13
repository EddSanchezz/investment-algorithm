"""
Stooq Provider - Descarga CSV diaria para acciones y ETFs de EE.UU.

Stooq ofrece un endpoint CSV simple que no requiere API key. Se usa como
fallback para activos NYSE/NASDAQ cuando Yahoo responde rate limit.
"""

import csv
import os
from datetime import datetime
from io import StringIO
from typing import Dict, List, Optional

import requests

from .base import DataProvider


BASE_URL = "https://stooq.com/q/d/l/"
REQUEST_TIMEOUT = 30
COLOMBIAN_SUFFIX = ".CL"
API_KEY = os.environ.get("STOOQ_API_KEY", "")


class StooqProvider(DataProvider):
    """Proveedor CSV sin API key para símbolos estadounidenses."""

    def __init__(self, logger: Optional[callable] = None):
        self._logger = logger or print
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/csv,*/*",
        })

    @property
    def name(self) -> str:
        return "Stooq CSV"

    def is_available(self) -> bool:
        """Stooq pide API key para descargas CSV automatizadas."""
        if not API_KEY:
            self._logger(f"  [X] {self.name}: falta STOOQ_API_KEY")
            return False
        return True

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        clean_symbol = symbol.split(".")[0].lower()
        if symbol.upper().endswith(COLOMBIAN_SUFFIX):
            self._logger(f"  [INFO] {self.name}: {symbol} es BVC, saltando")
            return []

        params = {
            "s": f"{clean_symbol}.us",
            "d1": start_date.strftime("%Y%m%d"),
            "d2": end_date.strftime("%Y%m%d"),
            "i": "d",
            "apikey": API_KEY,
        }

        try:
            response = self._session.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self._logger(f"  [ERR] {self.name}: error de red para {symbol}: {e}")
            return []

        records = self._parse_csv(response.text, clean_symbol.upper(), start_date, end_date)
        if records:
            self._logger(f"  [OK] {self.name}: {symbol} ({len(records)} registros)")
        else:
            self._logger(f"  [X] {self.name}: sin datos para {symbol}")
        return records

    def _parse_csv(
        self,
        content: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        if not content or "No data" in content:
            return []

        records: List[Dict] = []
        reader = csv.DictReader(StringIO(content))
        for row in reader:
            try:
                record_date = datetime.strptime(row["Date"], "%Y-%m-%d")
                if not (start_date <= record_date <= end_date):
                    continue

                records.append({
                    "date": row["Date"],
                    "symbol": symbol,
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(float(row["Volume"])),
                })
            except (KeyError, TypeError, ValueError):
                continue

        return records

    def close(self) -> None:
        self._session.close()
