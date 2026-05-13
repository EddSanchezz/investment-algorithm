"""
Scraper Module - Fallback scraper usando Yahoo Finance API.
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict

import requests


class YahooFallbackFetcher:
    """
    Scraper alternativo de datos financieros usando Yahoo Finance API.

    Sirve como Plan B cuando el fetcher principal falla. Usa requests HTTP
    directos para obtener datos históricos OHLCV.

    Complejidad: O(n) por activo donde n = días obtenidos.
    """

    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def __init__(self):
        """
        Inicializa la sesión HTTP compartida con headers por defecto.

        Complejidad: O(1)
        """
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def fetch_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime = None
    ) -> List[Dict]:
        """
        Obtiene datos históricos OHLCV para un símbolo.

        Parámetros:
            symbol: Símbolo del activo (ej. "VOO")
            start_date: Fecha de inicio del período
            end_date: Fecha de fin (default: hoy)

        Retorna:
            Lista de registros con date, symbol, open, high, low, close, volume

        Complejidad: O(n) donde n = días obtenidos
        """
        if end_date is None:
            end_date = datetime.now()

        url = self.BASE_URL.format(symbol=symbol.upper())
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
                ohlcv = {
                    "open": quote["open"][i],
                    "high": quote["high"][i],
                    "low": quote["low"][i],
                    "close": quote["close"][i],
                    "volume": quote["volume"][i],
                }
                if any(v is None for v in ohlcv.values()):
                    continue
                record = {
                    "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                    "symbol": symbol.split(".")[0].upper(),
                    **ohlcv,
                }
                records.append(record)

            return records

        except (KeyError, TypeError, IndexError) as e:
            print(f"Error fetching {symbol}: {e}")
            return []

    def fetch_multiple_assets(self, symbols: List[str], years: int = 5) -> List[Dict]:
        """
        Obtiene datos históricos para múltiples activos.

        Parámetros:
            symbols: Lista de símbolos a descargar
            years: Años de historia (default: 5)

        Retorna:
            Lista combinada de registros de todos los activos

        Complejidad: O(a × n) donde a = activos, n = registros por activo
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
                time.sleep(1)

        return all_records

    def close(self):
        """Cierra la sesión HTTP liberando conexiones."""
        self.session.close()

    def __enter__(self):
        """Soporte para context manager (with)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la sesión al salir del context manager."""
        self.close()
