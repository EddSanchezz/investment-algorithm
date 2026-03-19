"""Data unifier for combining multiple assets into a single dataset

Maneja diferencias entre calendarios bursátiles, días festivos
y desalineaciones temporales entre fuentes.
"""

from typing import Optional
from datetime import datetime
from dataclasses import dataclass

from ..utils.constants import (
    DATE_COL,
    OPEN_COL,
    HIGH_COL,
    LOW_COL,
    CLOSE_COL,
    VOLUME_COL,
    SYMBOL_COL,
)


@dataclass
class UnificationReport:
    """Reporte del proceso de unificación"""

    total_assets: int
    total_records: int
    date_range_start: Optional[str]
    date_range_end: Optional[str]
    records_per_asset: dict[str, int]


class DataUnifier:
    """Clase para unificar datasets de múltiples activos"""

    def __init__(self):
        self.report: Optional[UnificationReport] = None

    def unify_records(self, records: list[dict]) -> list[dict]:
        """Unifica registros de múltiples activos en un solo dataset"""
        if not records:
            return []

        records = self._sort_by_date_and_symbol(records)
        records = self._fill_missing_dates(records)

        self._generate_report(records)

        return records

    def _sort_by_date_and_symbol(self, records: list[dict]) -> list[dict]:
        """Ordena por fecha (ascendente), luego por símbolo"""
        return sorted(records, key=lambda x: (x[DATE_COL], x[SYMBOL_COL]))

    def _fill_missing_dates(self, records: list[dict]) -> list[dict]:
        """Rellena fechas faltantes usando interpolación"""
        if not records:
            return []

        all_dates = sorted(set(r[DATE_COL] for r in records))
        symbols = sorted(set(r[SYMBOL_COL] for r in records))

        complete_records = []
        records_by_symbol = self._group_by_symbol(records)

        for symbol in symbols:
            symbol_records = records_by_symbol.get(symbol, [])
            symbol_dates = set(r[DATE_COL] for r in symbol_records)

            for date in all_dates:
                if date in symbol_dates:
                    record = next(r for r in symbol_records if r[DATE_COL] == date)
                    complete_records.append(record)
                else:
                    complete_records.append(
                        {
                            DATE_COL: date,
                            SYMBOL_COL: symbol,
                            OPEN_COL: None,
                            HIGH_COL: None,
                            LOW_COL: None,
                            CLOSE_COL: None,
                            VOLUME_COL: 0,
                        }
                    )

        return sorted(complete_records, key=lambda x: (x[DATE_COL], x[SYMBOL_COL]))

    def _group_by_symbol(self, records: list[dict]) -> dict[str, list[dict]]:
        """Agrupa registros por símbolo"""
        grouped = {}
        for record in records:
            symbol = record[SYMBOL_COL]
            if symbol not in grouped:
                grouped[symbol] = []
            grouped[symbol].append(record)
        return grouped

    def _generate_report(self, records: list[dict]) -> None:
        """Genera reporte de unificación"""
        if not records:
            self.report = None
            return

        symbols = sorted(set(r[SYMBOL_COL] for r in records))
        records_per_asset = {}

        for symbol in symbols:
            records_per_asset[symbol] = sum(
                1 for r in records if r[SYMBOL_COL] == symbol
            )

        dates = sorted(set(r[DATE_COL] for r in records))

        self.report = UnificationReport(
            total_assets=len(symbols),
            total_records=len(records),
            date_range_start=dates[0] if dates else None,
            date_range_end=dates[-1] if dates else None,
            records_per_asset=records_per_asset,
        )

    def get_report(self) -> Optional[UnificationReport]:
        """Retorna el reporte de unificación"""
        return self.report
