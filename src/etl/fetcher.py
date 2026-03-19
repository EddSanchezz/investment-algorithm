"""Data fetcher for financial data from public APIs

Descarga datos históricos de Yahoo Finance mediante peticiones HTTP directas.
No utiliza librerías de alto nivel como yfinance.
"""

import csv
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from ..utils.constants import (
    YAHOO_BASE_URL,
    ASSETS,
    DATE_COL,
    OPEN_COL,
    HIGH_COL,
    LOW_COL,
    CLOSE_COL,
    VOLUME_COL,
    SYMBOL_COL,
)


@dataclass
class FinancialRecord:
    """Representa un registro de datos financieros"""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    symbol: str


class DataFetcher:
    """Clase para descargar datos financieros de Yahoo Finance API"""

    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = data_dir
        self.base_url = YAHOO_BASE_URL
        self.assets = ASSETS

    def build_url(self, symbol: str, start_date: datetime, end_date: datetime) -> str:
        """Construye la URL para descargar datos de Yahoo Finance"""
        params = urllib.parse.urlencode(
            {
                "period1": int(start_date.timestamp()),
                "period2": int(end_date.timestamp()),
                "interval": "1d",
                "events": "history",
            }
        )
        return f"{self.base_url}/{symbol}?{params}"

    def fetch_symbol_data(
        self, symbol: str, years: int = 5, retries: int = 3, delay: float = 1.0
    ) -> list[FinancialRecord]:
        """Descarga datos históricos para un símbolo específico"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        url = self.build_url(symbol, start_date, end_date)
        records = []

        for attempt in range(retries):
            try:
                request = urllib.request.Request(url)
                request.add_header("User-Agent", "Mozilla/5.0")

                with urllib.request.urlopen(request, timeout=30) as response:
                    csv_data = response.read().decode("utf-8")
                    reader = csv.DictReader(csv_data.splitlines())

                    for row in reader:
                        if self._is_valid_row(row):
                            records.append(
                                FinancialRecord(
                                    date=row["Date"],
                                    open=float(row["Open"]),
                                    high=float(row["High"]),
                                    low=float(row["Low"]),
                                    close=float(row["Close"]),
                                    volume=int(row["Volume"]),
                                    symbol=symbol,
                                )
                            )
                    return records

            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f"Símbolo {symbol} no encontrado")
                    return []
                time.sleep(delay * (attempt + 1))
            except Exception as e:
                print(f"Error descargando {symbol}: {e}")
                time.sleep(delay * (attempt + 1))

        return records

    def _is_valid_row(self, row: dict) -> bool:
        """Verifica si una fila tiene todos los campos necesarios"""
        required_fields = ["Date", "Open", "High", "Low", "Close", "Volume"]
        for field in required_fields:
            if field not in row or row[field] == "null" or row[field] == "":
                return False
        return True

    def fetch_all_assets(self, years: int = 5) -> list[FinancialRecord]:
        """Descarga datos para todos los activos configurados"""
        all_records = []

        for symbol in self.assets:
            print(f"Descargando {symbol}...")
            records = self.fetch_symbol_data(symbol, years)
            all_records.extend(records)
            print(f"  -> {len(records)} registros obtenidos")
            time.sleep(0.5)

        return all_records

    def save_to_csv(self, records: list[FinancialRecord], filename: str) -> None:
        """Guarda los registros en un archivo CSV"""
        if not records:
            return

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    DATE_COL,
                    OPEN_COL,
                    HIGH_COL,
                    LOW_COL,
                    CLOSE_COL,
                    VOLUME_COL,
                    SYMBOL_COL,
                ],
            )
            writer.writeheader()
            for record in records:
                writer.writerow(
                    {
                        DATE_COL: record.date,
                        OPEN_COL: record.open,
                        HIGH_COL: record.high,
                        LOW_COL: record.low,
                        CLOSE_COL: record.close,
                        VOLUME_COL: record.volume,
                        SYMBOL_COL: record.symbol,
                    }
                )
