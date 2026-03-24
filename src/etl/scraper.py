"""
Scraper Module - Fallback scraper para datos financieros.
Utiliza Yahoo Finance API mediante requests directos como alternativa.
"""

import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import requests


class InvestingScraper:
    """
    Scraper para obtener datos financieros (usa Yahoo Finance API).

    Dado que Investing.com bloquea solicitudes directas, este módulo
    utiliza la API de Yahoo Finance mediante requests HTTP directos,
    que cumple con los requisitos del documento de seguimiento.

    Complejidad de extracción por activo: O(d) donde d = días solicitados
    """

    COLOMBIAN_SUFFIX = ".CL"
    US_ETFS = [
        "VOO",
        "VTI",
        "QQQ",
        "SPY",
        "VEA",
        "VWO",
        "BND",
        "EFA",
        "EEM",
        "TLT",
        "IVV",
        "SCHD",
        "DIA",
        "IWM",
        "XLF",
        "XLK",
    ]

    COLOMBIAN_STOCKS = {
        "ecopetrol": "Ecopetrol S.A.",
        "isa": "ISA",
        "geb": "Grupo Energía de Bogotá",
        "nutresa": "Nutresa",
    }

    INTERNATIONAL_ETFS = {
        "voo": "Vanguard S&P 500 ETF",
        "vti": "Vanguard Total Stock Market",
        "qqq": "Invesco QQQ Trust",
        "spy": "SPDR S&P 500 ETF",
        "vea": "Vanguard FTSE Developed Markets",
        "vwo": "Vanguard FTSE Emerging Markets",
        "bnd": "Vanguard Total Bond Market",
        "efa": "iShares MSCI EAFE",
        "eem": "iShares MSCI Emerging Markets",
        "tlt": "iShares 20+ Year Treasury Bond",
        "ivv": "iShares Core S&P 500 ETF",
        "schd": "Schwab U.S. Dividend Equity ETF",
        "dia": "SPDR Dow Jones Industrial Average",
        "iwm": "iShares Russell 2000 ETF",
        "xlf": "Financial Select Sector SPDR",
        "xlk": "Technology Select Sector SPDR",
    }

    def __init__(self, headless: bool = True):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        self.wait_time = random.uniform(0.5, 1.5)

    def _normalize_symbol(self, symbol: str) -> str:
        """Normaliza el símbolo según el mercado."""
        symbol = symbol.upper().strip()

        if symbol in self.US_ETFS:
            return symbol

        if symbol in ["ECOPETROL", "ISA", "GEB", "NUTRESA"]:
            return symbol + self.COLOMBIAN_SUFFIX

        return symbol

    def fetch_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime = None
    ) -> List[Dict]:
        """
        Descarga datos históricos para un símbolo.

        Parámetros:
            symbol: Símbolo del activo
            start_date: Fecha inicial
            end_date: Fecha final

        Retorna:
            Lista de diccionarios con OHLCV
        """
        if end_date is None:
            end_date = datetime.now()

        normalized_symbol = self._normalize_symbol(symbol)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{normalized_symbol}"

        params = {
            "period1": int(start_date.timestamp()),
            "period2": int(end_date.timestamp()),
            "interval": "1d",
            "events": "history",
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            result = data.get("chart", {}).get("result", [])
            if not result:
                return []

            result_data = result[0]
            if "timestamp" not in result_data:
                return []

            timestamps = result_data["timestamp"]
            quote = result_data.get("indicators", {}).get("quote", [{}])[0]

            records = []
            for i, ts in enumerate(timestamps):
                if quote["open"][i] is None:
                    continue
                record = {
                    "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                    "symbol": symbol.upper(),
                    "open": quote["open"][i],
                    "high": quote["high"][i],
                    "low": quote["low"][i],
                    "close": quote["close"][i],
                    "volume": quote["volume"][i],
                }
                records.append(record)

            return records

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return []

    def fetch_multiple_assets(self, symbols: List[str], years: int = 5) -> List[Dict]:
        """
        Descarga datos para múltiples activos.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        all_records = []
        total = len(symbols)

        for idx, symbol in enumerate(symbols, 1):
            print(f"Descargando {symbol.upper()} ({idx}/{total})...")

            records = self.fetch_historical_data(symbol, start_date, end_date)

            if records:
                all_records.extend(records)
                print(f"  -> {len(records)} registros obtenidos")
            else:
                print("  -> Sin datos disponibles")

            if idx < total:
                delay = random.uniform(1, 2)
                time.sleep(delay)

        return all_records

    def close(self):
        """Cierra la sesión."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
