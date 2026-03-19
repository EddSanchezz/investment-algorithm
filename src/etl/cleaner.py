"""Data cleaner for handling missing values and anomalies

Implementa técnicas de limpieza: interpolación, eliminación de registros
y corrección de valores inconsistentes.
"""

from typing import Optional
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
class DataQualityReport:
    """Reporte de calidad de datos después de la limpieza"""

    original_count: int
    final_count: int
    missing_values_filled: int
    outliers_removed: int
    duplicates_removed: int


class DataCleaner:
    """Clase para limpiar y validar datos financieros"""

    def __init__(self):
        self.quality_report: Optional[DataQualityReport] = None

    def clean_dataset(self, records: list[dict]) -> list[dict]:
        """Pipeline completo de limpieza de datos"""
        original_count = len(records)

        records = self._remove_duplicates(records)
        records = self._interpolate_missing_values(records)
        records = self._remove_outliers(records)
        records = self._validate_price_consistency(records)

        duplicates_removed = original_count - len(records)

        self.quality_report = DataQualityReport(
            original_count=original_count,
            final_count=len(records),
            missing_values_filled=0,
            outliers_removed=0,
            duplicates_removed=duplicates_removed,
        )

        return records

    def _remove_duplicates(self, records: list[dict]) -> list[dict]:
        """Elimina registros duplicados basados en fecha y símbolo"""
        seen = set()
        unique_records = []

        for record in records:
            key = (record[DATE_COL], record[SYMBOL_COL])
            if key not in seen:
                seen.add(key)
                unique_records.append(record)

        return unique_records

    def _interpolate_missing_values(self, records: list[dict]) -> list[dict]:
        """Interpolación lineal para valores faltantes en series de tiempo"""
        cleaned = []
        missing_filled = 0

        grouped = self._group_by_symbol(records)

        for symbol, symbol_records in grouped.items():
            sorted_records = sorted(symbol_records, key=lambda x: x[DATE_COL])

            for i, record in enumerate(sorted_records):
                new_record = record.copy()

                for col in [OPEN_COL, HIGH_COL, LOW_COL, CLOSE_COL]:
                    if record.get(col) is None or record[col] == "":
                        value = self._interpolate_value(sorted_records, i, col)
                        if value is not None:
                            new_record[col] = value
                            missing_filled += 1

                if record.get(VOLUME_COL) is None or record[VOLUME_COL] == "":
                    value = self._interpolate_value(sorted_records, i, VOLUME_COL)
                    if value is not None:
                        new_record[VOLUME_COL] = int(value)
                        missing_filled += 1

                cleaned.append(new_record)

        if self.quality_report:
            self.quality_report.missing_values_filled = missing_filled

        return cleaned

    def _interpolate_value(
        self, records: list[dict], index: int, column: str
    ) -> Optional[float]:
        """Interpolación lineal: busca valores válidos antes y después"""
        prev_value = None
        next_value = None

        for i in range(index - 1, -1, -1):
            if records[i].get(column) not in [None, ""]:
                prev_value = float(records[i][column])
                break

        for i in range(index + 1, len(records)):
            if records[i].get(column) not in [None, ""]:
                next_value = float(records[i][column])
                break

        if prev_value is not None and next_value is not None:
            return (prev_value + next_value) / 2
        elif prev_value is not None:
            return prev_value
        elif next_value is not None:
            return next_value

        return None

    def _remove_outliers(self, records: list[dict]) -> list[dict]:
        """Elimina outliers usando el método IQR (Interquartile Range)"""
        grouped = self._group_by_symbol(records)
        cleaned = []
        outliers_removed = 0

        for symbol, symbol_records in grouped.items():
            for col in [CLOSE_COL, VOLUME_COL]:
                values = [
                    r[col] for r in symbol_records if r.get(col) not in [None, ""]
                ]
                if not values:
                    continue

                sorted_values = sorted(values)
                q1_idx = len(sorted_values) // 4
                q3_idx = 3 * len(sorted_values) // 4
                q1 = sorted_values[q1_idx]
                q3 = sorted_values[q3_idx]
                iqr = q3 - q1

                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                for record in symbol_records:
                    if lower_bound <= record[col] <= upper_bound:
                        cleaned.append(record)
                    else:
                        outliers_removed += 1

        if self.quality_report:
            self.quality_report.outliers_removed = outliers_removed

        return cleaned

    def _validate_price_consistency(self, records: list[dict]) -> list[dict]:
        """Verifica que High >= Low y que Open/Close estén en el rango [Low, High]"""
        valid_records = []

        for record in records:
            high = record[HIGH_COL]
            low = record[LOW_COL]
            open_price = record[OPEN_COL]
            close = record[CLOSE_COL]

            if high < low:
                continue

            if not (low <= open_price <= high):
                record[OPEN_COL] = max(low, min(high, open_price))

            if not (low <= close <= high):
                record[CLOSE_COL] = max(low, min(high, close))

            valid_records.append(record)

        return valid_records

    def _group_by_symbol(self, records: list[dict]) -> dict[str, list[dict]]:
        """Agrupa registros por símbolo"""
        grouped = {}
        for record in records:
            symbol = record[SYMBOL_COL]
            if symbol not in grouped:
                grouped[symbol] = []
            grouped[symbol].append(record)
        return grouped

    def get_quality_report(self) -> Optional[DataQualityReport]:
        """Retorna el reporte de calidad de datos"""
        return self.quality_report
