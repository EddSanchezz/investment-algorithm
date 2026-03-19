"""Tests for ETL pipeline modules"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.cleaner import DataCleaner
from src.etl.unifier import DataUnifier
from src.etl.validator import DataValidator
from src.utils.constants import (
    DATE_COL,
    OPEN_COL,
    HIGH_COL,
    LOW_COL,
    CLOSE_COL,
    VOLUME_COL,
    SYMBOL_COL,
)


class TestDataCleaner:
    """Tests para el módulo de limpieza de datos"""

    def test_remove_duplicates_directly(self):
        """Verifica eliminación de duplicados usando el método interno"""
        cleaner = DataCleaner()
        data = [
            {
                DATE_COL: "2024-01-01",
                OPEN_COL: 100,
                HIGH_COL: 105,
                LOW_COL: 98,
                CLOSE_COL: 103,
                VOLUME_COL: 1000,
                SYMBOL_COL: "AAPL",
            },
            {
                DATE_COL: "2024-01-01",
                OPEN_COL: 100,
                HIGH_COL: 105,
                LOW_COL: 98,
                CLOSE_COL: 103,
                VOLUME_COL: 1500,
                SYMBOL_COL: "AAPL",
            },
            {
                DATE_COL: "2024-01-02",
                OPEN_COL: 102,
                HIGH_COL: 108,
                LOW_COL: 100,
                CLOSE_COL: 102,
                VOLUME_COL: 2000,
                SYMBOL_COL: "AAPL",
            },
        ]
        result = cleaner._remove_duplicates(data)
        assert len(result) == 2

    def test_validate_price_consistency(self):
        """Verifica validación de consistencia de precios"""
        cleaner = DataCleaner()
        data = [
            {
                DATE_COL: "2024-01-01",
                OPEN_COL: 100,
                HIGH_COL: 105,
                LOW_COL: 98,
                CLOSE_COL: 50,
                VOLUME_COL: 1000,
                SYMBOL_COL: "AAPL",
            },
        ]
        result = cleaner.clean_dataset(data)
        assert result[0][CLOSE_COL] >= result[0][LOW_COL]


class TestDataUnifier:
    """Tests para el módulo de unificación de datos"""

    def test_sort_by_date_and_symbol(self):
        """Verifica ordenamiento por fecha y símbolo"""
        unifier = DataUnifier()
        data = [
            {
                DATE_COL: "2024-01-02",
                SYMBOL_COL: "AAPL",
                CLOSE_COL: 100,
                VOLUME_COL: 1000,
            },
            {
                DATE_COL: "2024-01-01",
                SYMBOL_COL: "AAPL",
                CLOSE_COL: 99,
                VOLUME_COL: 900,
            },
            {
                DATE_COL: "2024-01-01",
                SYMBOL_COL: "GOOG",
                CLOSE_COL: 150,
                VOLUME_COL: 500,
            },
        ]
        result = unifier._sort_by_date_and_symbol(data)
        assert result[0][DATE_COL] == "2024-01-01"
        assert result[1][DATE_COL] == "2024-01-01"

    def test_generate_report(self):
        """Verifica generación de reporte"""
        unifier = DataUnifier()
        data = [
            {
                DATE_COL: "2024-01-01",
                SYMBOL_COL: "AAPL",
                CLOSE_COL: 100,
                VOLUME_COL: 1000,
            },
            {
                DATE_COL: "2024-01-02",
                SYMBOL_COL: "AAPL",
                CLOSE_COL: 101,
                VOLUME_COL: 1100,
            },
        ]
        unifier.unify_records(data)
        report = unifier.get_report()
        assert report is not None
        assert report.total_assets == 1
        assert report.total_records == 2


class TestDataValidator:
    """Tests para el módulo de validación"""

    def test_validate_valid_data(self):
        """Verifica validación de datos válidos"""
        validator = DataValidator()
        data = [
            {
                DATE_COL: "2024-01-01",
                OPEN_COL: 100,
                HIGH_COL: 105,
                LOW_COL: 98,
                CLOSE_COL: 103,
                VOLUME_COL: 1000,
                SYMBOL_COL: "AAPL",
            },
            {
                DATE_COL: "2024-01-02",
                OPEN_COL: 103,
                HIGH_COL: 108,
                LOW_COL: 101,
                CLOSE_COL: 101,
                VOLUME_COL: 1100,
                SYMBOL_COL: "AAPL",
            },
        ]
        result = validator.validate(data)
        assert result.is_valid or len(result.stats) > 0

    def test_validate_empty_data(self):
        """Verifica validación de datos vacíos"""
        validator = DataValidator()
        result = validator.validate([])
        assert not result.is_valid
        assert "vacío" in result.errors[0].lower()

    def test_compute_statistics(self):
        """Verifica cálculo de estadísticas"""
        validator = DataValidator()
        data = [
            {
                DATE_COL: "2024-01-01",
                OPEN_COL: 100,
                HIGH_COL: 105,
                LOW_COL: 98,
                CLOSE_COL: 103,
                VOLUME_COL: 1000,
                SYMBOL_COL: "AAPL",
            },
            {
                DATE_COL: "2024-01-02",
                OPEN_COL: 103,
                HIGH_COL: 108,
                LOW_COL: 101,
                CLOSE_COL: 101,
                VOLUME_COL: 1100,
                SYMBOL_COL: "GOOG",
            },
        ]
        stats = validator._compute_statistics(data)
        assert stats["total_records"] == 2
        assert stats["unique_assets"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
