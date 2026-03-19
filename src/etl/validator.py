"""Data validator for ensuring data integrity

Valida que el dataset cumpla con los requisitos mínimos del proyecto.
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
    MIN_YEARS,
    MIN_ASSETS,
)


@dataclass
class ValidationResult:
    """Resultado de la validación del dataset"""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    stats: dict


class DataValidator:
    """Validador para verificar integridad y requisitos del dataset"""

    def __init__(self, min_years: int = MIN_YEARS, min_assets: int = MIN_ASSETS):
        self.min_years = min_years
        self.min_assets = min_assets
        self.required_columns = [
            DATE_COL,
            OPEN_COL,
            HIGH_COL,
            LOW_COL,
            CLOSE_COL,
            VOLUME_COL,
            SYMBOL_COL,
        ]

    def validate(self, records: list[dict]) -> ValidationResult:
        """Valida el dataset completo"""
        errors = []
        warnings = []
        stats = {}

        if not records:
            errors.append("Dataset vacío")
            return ValidationResult(False, errors, warnings, stats)

        errors.extend(self._validate_columns(records))
        errors.extend(self._validate_data_types(records))
        warnings.extend(self._validate_completeness(records))

        stats = self._compute_statistics(records)

        if stats["unique_assets"] < self.min_assets:
            errors.append(
                f"Activos insuficientes: {stats['unique_assets']} < {self.min_assets}"
            )

        is_valid = len(errors) == 0

        return ValidationResult(is_valid, errors, warnings, stats)

    def _validate_columns(self, records: list[dict]) -> list[str]:
        """Verifica que existan todas las columnas requeridas"""
        errors = []
        if not records:
            return errors

        missing_columns = []
        for col in self.required_columns:
            if col not in records[0]:
                missing_columns.append(col)

        if missing_columns:
            errors.append(f"Columnas faltantes: {missing_columns}")

        return errors

    def _validate_data_types(self, records: list[dict]) -> list[str]:
        """Valida tipos de datos en campos numéricos"""
        errors = []

        for i, record in enumerate(records[:100]):
            for col in [OPEN_COL, HIGH_COL, LOW_COL, CLOSE_COL]:
                try:
                    float(record.get(col, 0))
                except (ValueError, TypeError):
                    errors.append(
                        f"Valor inválido en {col} fila {i}: {record.get(col)}"
                    )

            try:
                int(record.get(VOLUME_COL, 0))
            except (ValueError, TypeError):
                errors.append(f"Volumen inválido en fila {i}: {record.get(VOLUME_COL)}")

        return errors

    def _validate_completeness(self, records: list[dict]) -> list[str]:
        """Verifica completitud del dataset"""
        warnings = []

        null_counts = {col: 0 for col in self.required_columns}
        for record in records:
            for col in self.required_columns:
                if record.get(col) is None or record.get(col) == "":
                    null_counts[col] += 1

        for col, count in null_counts.items():
            if count > 0:
                pct = (count / len(records)) * 100
                warnings.append(f"{col}: {count} valores nulos ({pct:.1f}%)")

        return warnings

    def _compute_statistics(self, records: list[dict]) -> dict:
        """Calcula estadísticas del dataset"""
        if not records:
            return {}

        symbols = sorted(set(r[SYMBOL_COL] for r in records))
        dates = sorted(set(r[DATE_COL] for r in records))

        volumes = [
            r[VOLUME_COL] for r in records if r.get(VOLUME_COL) not in [None, ""]
        ]

        return {
            "total_records": len(records),
            "unique_assets": len(symbols),
            "unique_dates": len(dates),
            "date_range": (dates[0], dates[-1]) if dates else (None, None),
            "total_volume": sum(volumes) if volumes else 0,
            "avg_volume": sum(volumes) // len(volumes) if volumes else 0,
            "assets": symbols[:5],
        }
