"""
Fetcher Module - Extracción de datos financieros mediante HTTP directo.
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict
import csv
import os


class FinancialDataFetcher:
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    MAX_RETRIES = 3

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def fetch_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> "list[dict]":
        url = self.BASE_URL.format(symbol=symbol.upper())
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
                    print(f"  -> Advertencia: No hay datos disponibles para {symbol}")
                    return []

                result_data = result[0]

                if "timestamp" not in result_data or not result_data["timestamp"]:
                    print(f"  -> Advertencia: Sin fechas disponibles para {symbol}")
                    return []

                timestamps = result_data["timestamp"]
                quote = result_data.get("indicators", {}).get("quote", [{}])[0]

                # Validar que quote tenga datos
                if not quote.get("close"):
                    print(f"  -> Advertencia: Sin precios de cierre para {symbol}")
                    return []

                for i, ts in enumerate(timestamps):
                    if quote["open"][i] is None:
                        continue
                    record = {
                        "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                        "symbol": symbol.split(".")[0].upper(),
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
                    time.sleep(2 * (attempt + 1))
                else:
                    print(f"Error fetching {symbol}: {e}")
                    return records

    def fetch_multiple_assets(self, symbols: List[str], years: int = 5) -> List[Dict]:
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
                time.sleep(0.5)

        return all_records

    def save_to_csv(self, records: List[Dict], filepath: str) -> None:
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
