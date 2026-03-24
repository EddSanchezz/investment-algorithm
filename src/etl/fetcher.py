"""
Fetcher Module - Extracción de datos financieros mediante HTTP directo.
Este módulo implementa la capa de extracción del proceso ETL.
No utiliza librerías de alto nivel como yfinance, solo requests para HTTP directo.
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict
import csv
import os


class FinancialDataFetcher:
    """
    Obtenedor de datos financieros mediante peticiones HTTP directas.

    Utiliza Yahoo Finance API (no oficial) para obtener datos históricos.
    Implementa manejo de errores y rate limiting para cumplir buenas prácticas.

    Complejidad temporal de descarga por activo: O(d) donde d = días solicitados
    Complejidad espacial: O(d) para almacenar los datos descargados
    """

    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    MAX_RETRIES = 3
    RETRY_DELAY = 2

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

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _normalize_symbol(self, symbol: str) -> str:
        """
        Normaliza el símbolo según el mercado.
        Las acciones colombianas necesitan el sufijo .CO
        Los ETFs estadounidenses no necesitan sufijo.
        """
        symbol = symbol.upper().strip()

        if symbol in self.US_ETFS:
            return symbol

        colombian_stocks = ["ECOPETROL", "ISA", "GEB", "NUTRESA"]
        if symbol in colombian_stocks:
            return symbol + self.COLOMBIAN_SUFFIX

        return symbol

    def fetch_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> "list[dict]":
        """
        Descarga datos históricos para un símbolo financiero.

        Parámetros:
            symbol: Símbolo del activo (ej: 'ECOPETROL', 'VOO')
            start_date: Fecha inicial del período
            end_date: Fecha final del período

        Retorna:
            Lista de diccionarios con OHLCV (Open, High, Low, Close, Volume)

        Complejidad: O(d) donde d es el número de días en el período
        """
        normalized_symbol = self._normalize_symbol(symbol)
        url = self.BASE_URL.format(symbol=normalized_symbol)
        params = {
            "period1": int(start_date.timestamp()),
            "period2": int(end_date.timestamp()),
            "interval": "1d",
            "events": "history",
        }

        records: List[Dict] = []

        for attempt in range(self.MAX_RETRIES):
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

                for i, ts in enumerate(timestamps):
                    if quote["open"][i] is None:
                        continue
                    record = {
                        "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                        "symbol": symbol,
                        "open": quote["open"][i],
                        "high": quote["high"][i],
                        "low": quote["low"][i],
                        "close": quote["close"][i],
                        "volume": quote["volume"][i],
                    }
                    records.append(record)

                return records

            except (
                requests.exceptions.RequestException,
                KeyError,
                TypeError,
                IndexError,
            ) as e:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    print(
                        f"Error fetching {symbol} after {self.MAX_RETRIES} attempts: {e}"
                    )
                    return records

    def fetch_multiple_assets(self, symbols: List[str], years: int = 5) -> List[Dict]:
        """
        Descarga datos para múltiples activos.

        Parámetros:
            symbols: Lista de símbolos a descargar
            years: Número de años de historial (default: 5)

        Retorna:
            Lista combinada de todos los registros

        Complejidad: O(n * d) donde n = número de activos, d = días por activo
        Se aplica rate limiting entre peticiones para evitar bloqueos
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        all_records = []
        total = len(symbols)

        for idx, symbol in enumerate(symbols, 1):
            print(f"Descargando {symbol} ({idx}/{total})...")
            records = self.fetch_historical_data(symbol, start_date, end_date)

            if records:
                all_records.extend(records)
                print(f"  -> {len(records)} registros obtenidos")
            else:
                print("  -> Sin datos disponibles")

            if idx < total:
                time.sleep(0.5)

        return all_records

    def save_to_csv(self, records: List[Dict], filepath: str) -> None:
        """
        Guarda los registros en un archivo CSV.

        Parámetros:
            records: Lista de diccionarios con datos financieros
            filepath: Ruta del archivo de salida

        Complejidad: O(n) donde n = número de registros
        """
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
