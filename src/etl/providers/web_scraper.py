"""
Web Scraper Provider - Scraping de 5 sitios financieros populares.

Sites en orden de prioridad:
1. Investing.com - Mejor para acciones colombianas
2. Google Finance - Simple y confiable
3. MarketWatch - ETFs y acciones US
4. CNBC - Cobertura global
5. Bloomberg - Último recurso (anti-scraping)

Cada sitio tiene su propio método que intenta scrapeo.
El primer sitio que retorna datos detiene la búsqueda.
"""

import time
import random
from datetime import datetime
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from .base import DataProvider


REQUEST_TIMEOUT: int = 30
DELAY_BETWEEN_ATTEMPTS: float = 2.0
"""Delay entre sitios para no saturar."""

USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


class WebScraperProvider(DataProvider):
    """
    Proveedor que intenta scraping de múltiples sitios financieros.

    Ventajas:
    - No requiere API key
    - Datos gratuitos

    Desventajas:
    - Estructura HTML puede cambiar
    - Rate limiting del sitio
    - Puede ser bloqueado
    """

    CRYPTO_SYMBOLS = {"BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "MATIC", "LTC"}

    def __init__(self, logger: Optional[callable] = None):
        self._logger = logger or print
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
        })
        self._adapter = requests.adapters.HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=1,
        )
        self._session.mount("https://", self._adapter)

    @property
    def name(self) -> str:
        return "Web Scraper (5 sitios)"

    def is_available(self) -> bool:
        """Siempre disponible, pero puede no retornar datos."""
        return True

    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict]:
        """
        Intenta scraping secuencial de sitios financieros.
        Retorna datos del primer sitio que tenga éxito.
        """
        clean_symbol = symbol.split(".")[0].upper()

        if clean_symbol in self.CRYPTO_SYMBOLS:
            self._logger(f"  [INFO] {self.name}: Simbolo crypto {symbol}, intentando Binance...")
            return self._try_binance(clean_symbol, start_date, end_date)

        sites = [
            ("StockAnalysis", self._try_stockanalysis),
            ("Investing.com", self._try_investing),
            ("Google Finance", self._try_google_finance),
            ("MarketWatch", self._try_marketwatch),
        ]

        for site_name, scraper_func in sites:
            self._logger(f"  -> {self.name}: Intentando {site_name}...")
            try:
                records = scraper_func(clean_symbol, start_date, end_date)
                if records:
                    self._logger(f"  [OK] {self.name}: {site_name} exito para {symbol} ({len(records)} registros)")
                    return records
            except Exception as e:
                self._logger(f"  [WARN] {self.name}: {site_name} fallo: {e}")

            time.sleep(DELAY_BETWEEN_ATTEMPTS)

        self._logger(f"  [ERR] {self.name}: Ningun sitio pudo obtener datos para {symbol}")
        return []

    def _try_stockanalysis(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Intenta scrapeo de StockAnalysis.com (buena cobertura internacional)."""
        url = f"https://stockanalysis.com/quote/bvc/{symbol.lower()}/history/"

        try:
            response = self._session.get(url, timeout=15)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")
            if not table:
                return []

            rows = table.find_all("tr")[1:]
            records: List[Dict] = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue
                try:
                    date_text = cols[0].get_text(strip=True)
                    record_date = datetime.strptime(date_text.replace(",", ""), "%b %d %Y")

                    if not (start_date <= record_date <= end_date):
                        continue

                    records.append({
                        "date": record_date.strftime("%Y-%m-%d"),
                        "symbol": symbol,
                        "open": self._safe_float(cols[1].get_text()),
                        "high": self._safe_float(cols[2].get_text()),
                        "low": self._safe_float(cols[3].get_text()),
                        "close": self._safe_float(cols[4].get_text()),
                        "volume": self._safe_int(cols[6].get_text(strip=True)),
                    })
                except (ValueError, IndexError):
                    continue

            return records

        except Exception:
            return []

    def _try_investing(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Intenta scrapeo de Investing.com."""
        url = f"https://www.investing.com/equities/{symbol.lower()}-historical-data"

        try:
            response = self._session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            table = soup.find("table", {"data-test": "historical-data-table"})
            if not table:
                return []

            rows = table.find_all("tr")[1:]
            records: List[Dict] = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue

                try:
                    date_str = cols[0].get_text(strip=True)
                    record_date = datetime.strptime(date_str, "%b %d, %Y")

                    if not (start_date <= record_date <= end_date):
                        continue

                    records.append({
                        "date": record_date.strftime("%Y-%m-%d"),
                        "symbol": symbol,
                        "open": self._safe_float(cols[1].get_text()),
                        "high": self._safe_float(cols[2].get_text()),
                        "low": self._safe_float(cols[3].get_text()),
                        "close": self._safe_float(cols[4].get_text()),
                        "volume": self._safe_int(cols[6].get_text()),
                    })
                except (ValueError, IndexError):
                    continue

            return records

        except Exception:
            return []

    def _try_google_finance(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Intenta scrapeo de Google Finance."""
        url = f"https://www.google.com/finance/quote/{symbol}:NASDAQ"

        if symbol.endswith("CL") or len(symbol) <= 4:
            url = f"https://www.google.com/finance/quote/{symbol}"

        try:
            response = self._session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "historicalPrices" in script.string:
                    import json
                    import re

                    match = re.search(r'historicalPrices":(\[.*?\])', script.string)
                    if match:
                        prices = json.loads(match.group(1))
                        records = []
                        for p in prices:
                            try:
                                date_str = p.get("date", "")
                                record_date = datetime.strptime(date_str, "%b %d, %Y")
                                if not (start_date <= record_date <= end_date):
                                    continue

                                records.append({
                                    "date": record_date.strftime("%Y-%m-%d"),
                                    "symbol": symbol,
                                    "open": p.get("open"),
                                    "high": p.get("high"),
                                    "low": p.get("low"),
                                    "close": p.get("close"),
                                    "volume": p.get("volume"),
                                })
                            except (ValueError, TypeError, KeyError):
                                continue

                        if records:
                            return records

            return []

        except Exception:
            return []

    def _try_marketwatch(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Intenta scrapeo de MarketWatch."""
        url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}/historical"

        try:
            response = self._session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            table = soup.find("table", {"class": "table"})
            if not table:
                return []

            rows = table.find_all("tr")[1:]
            records: List[Dict] = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 6:
                    continue

                try:
                    date_str = cols[0].get_text(strip=True)
                    record_date = datetime.strptime(date_str, "%b %d, %Y")

                    if not (start_date <= record_date <= end_date):
                        continue

                    records.append({
                        "date": record_date.strftime("%Y-%m-%d"),
                        "symbol": symbol,
                        "open": self._safe_float(cols[1].get_text()),
                        "high": self._safe_float(cols[2].get_text()),
                        "low": self._safe_float(cols[3].get_text()),
                        "close": self._safe_float(cols[4].get_text()),
                        "volume": self._safe_int(cols[5].get_text()),
                    })
                except (ValueError, IndexError):
                    continue

            return records

        except Exception:
            return []

    def _try_cnbc(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Intenta scrapeo de CNBC."""
        url = f"https://www.cnbc.com/quotes/{symbol}/historical.html"

        try:
            response = self._session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            table = soup.find("table", {"class": "historical-symbol-history"})
            if not table:
                return []

            rows = table.find_all("tr")[1:]
            records: List[Dict] = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 6:
                    continue

                try:
                    date_str = cols[0].get_text(strip=True)
                    record_date = datetime.strptime(date_str, "%m/%d/%Y")

                    if not (start_date <= record_date <= end_date):
                        continue

                    records.append({
                        "date": record_date.strftime("%Y-%m-%d"),
                        "symbol": symbol,
                        "open": self._safe_float(cols[1].get_text()),
                        "high": self._safe_float(cols[2].get_text()),
                        "low": self._safe_float(cols[3].get_text()),
                        "close": self._safe_float(cols[4].get_text()),
                        "volume": self._safe_int(cols[5].get_text()),
                    })
                except (ValueError, IndexError):
                    continue

            return records

        except Exception:
            return []

    def _try_bloomberg(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Intenta scrapeo de Bloomberg (último recurso, a menudo bloquea)."""
        url = f"https://www.bloomberg.com/quote/{symbol}:US"

        try:
            response = self._session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            script_tags = soup.find_all("script")
            for script in script_tags:
                if script.string and "historicalData" in script.string:
                    import json
                    import re

                    match = re.search(r'historicalData":(\{.*?\})', script.string)
                    if match:
                        data = json.loads(match.group(1))
                        if "data" in data:
                            records = []
                            for item in data["data"]:
                                try:
                                    date_str = item.get("date", "")
                                    record_date = datetime.strptime(date_str, "%Y-%m-%d")

                                    if not (start_date <= record_date <= end_date):
                                        continue

                                    records.append({
                                        "date": date_str,
                                        "symbol": symbol,
                                        "open": item.get("open"),
                                        "high": item.get("high"),
                                        "low": item.get("low"),
                                        "close": item.get("close"),
                                        "volume": item.get("volume"),
                                    })
                                except (ValueError, TypeError, KeyError):
                                    continue

                            if records:
                                return records

            return []

        except Exception:
            return []

    def _try_binance(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Intenta obtener datos de Binance para crypto."""
        url = f"https://api.binance.com/api/v3/klines"

        params = {
            "symbol": f"{symbol}USDT",
            "interval": "1d",
            "startTime": int(start_date.timestamp() * 1000),
            "endTime": int(end_date.timestamp() * 1000),
            "limit": 1000,
        }

        try:
            response = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            klines = response.json()
            if not isinstance(klines, list):
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
                        "symbol": symbol,
                        "open": float(k[1]),
                        "high": float(k[2]),
                        "low": float(k[3]),
                        "close": float(k[4]),
                        "volume": int(k[5]),
                    })
                except (ValueError, IndexError, TypeError):
                    continue

            if records:
                self._logger(f"  [OK] {self.name}: Binance datos para {symbol} ({len(records)} registros)")

            return records

        except Exception:
            return []

    @staticmethod
    def _safe_float(value: Optional[str]) -> Optional[float]:
        """Convierte string a float de forma segura."""
        if value is None:
            return None
        try:
            cleaned = value.replace(",", "").replace("$", "").strip()
            return float(cleaned) if cleaned and cleaned != "-" else None
        except ValueError:
            return None

    @staticmethod
    def _safe_int(value: Optional[str]) -> Optional[int]:
        """Convierte string a int de forma segura."""
        if value is None:
            return None
        try:
            cleaned = value.replace(",", "").strip()
            return int(cleaned) if cleaned and cleaned != "-" else None
        except ValueError:
            return None

    def close(self) -> None:
        """Cierra la sesión HTTP."""
        self._session.close()