"""
Tests unitarios para DataUnifier y funciones auxiliares (src.etl.unifier).
"""

import sys, os, csv, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.etl.unifier import DataUnifier, _is_weekend, _is_bvc_trading_day, _is_nyse_trading_day


class TestTradingDayHelpers:
    def test_is_weekend_saturday(self):
        assert _is_weekend("2024-01-06")

    def test_is_weekend_sunday(self):
        assert _is_weekend("2024-01-07")

    def test_is_weekend_weekday(self):
        assert not _is_weekend("2024-01-05")

    def test_bvc_trading_day_holiday(self):
        assert not _is_bvc_trading_day("2024-01-01")

    def test_bvc_trading_day_normal(self):
        assert _is_bvc_trading_day("2024-01-08")

    def test_nyse_trading_day_holiday(self):
        assert not _is_nyse_trading_day("2024-01-01")

    def test_nyse_trading_day_normal(self):
        assert _is_nyse_trading_day("2024-01-08")


class TestValidateRecord:
    def setup_method(self):
        self.unifier = DataUnifier()

    def test_valid_record(self):
        r = {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
             "low": 99.0, "close": 102.0, "volume": 1000}
        assert self.unifier.validate_record(r)

    def test_missing_field(self):
        r = {"date": "2024-01-01", "symbol": "VOO"}
        assert not self.unifier.validate_record(r)

    def test_none_field(self):
        r = {"date": "2024-01-01", "symbol": "VOO", "open": None, "high": 105.0,
             "low": 99.0, "close": 102.0, "volume": 1000}
        assert not self.unifier.validate_record(r)

    def test_zero_close(self):
        r = {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
             "low": 99.0, "close": 0.0, "volume": 1000}
        assert not self.unifier.validate_record(r)

    def test_negative_volume(self):
        r = {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
             "low": 99.0, "close": 102.0, "volume": -1}
        assert not self.unifier.validate_record(r)


class TestUnifyDatasets:
    def setup_method(self):
        self.unifier = DataUnifier()

    def test_unify_multiple_datasets(self):
        d1 = [{"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
               "low": 99.0, "close": 102.0, "volume": 1000}]
        d2 = [{"date": "2024-01-02", "symbol": "VOO", "open": 102.0, "high": 106.0,
               "low": 101.0, "close": 103.0, "volume": 1200}]
        result = self.unifier.unify_datasets([d1, d2])
        assert len(result) == 2

    def test_unify_filters_invalid(self):
        d1 = [{"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
               "low": 99.0, "close": 0.0, "volume": 1000}]
        result = self.unifier.unify_datasets([d1])
        assert len(result) == 0

    def test_unify_sorts_by_date_symbol(self):
        d1 = [{"date": "2024-01-02", "symbol": "VOO", "open": 102.0, "high": 106.0,
               "low": 101.0, "close": 103.0, "volume": 1200}]
        d2 = [{"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
               "low": 99.0, "close": 102.0, "volume": 1000}]
        result = self.unifier.unify_datasets([d1, d2])
        assert result[0]["date"] == "2024-01-01"


class TestGenerateStatistics:
    def setup_method(self):
        self.unifier = DataUnifier()

    def test_statistics(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
             "low": 99.0, "close": 102.0, "volume": 1000},
            {"date": "2024-01-02", "symbol": "VOO", "open": 102.0, "high": 106.0,
             "low": 101.0, "close": 103.0, "volume": 1200},
        ]
        stats = self.unifier.generate_statistics(records)
        assert stats["total_records"] == 2
        assert stats["unique_symbols"] == 1
        assert stats["date_range"] == ("2024-01-01", "2024-01-02")

    def test_empty(self):
        assert self.unifier.generate_statistics([]) == {"total_records": 0}


class TestLoadSaveCSV:
    def setup_method(self):
        self.unifier = DataUnifier()
        self.tmpdir = tempfile.mkdtemp()

    def test_save_and_load(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
             "low": 99.0, "close": 102.0, "volume": 1000},
        ]
        path = os.path.join(self.tmpdir, "test.csv")
        self.unifier.save_to_csv(records, path)
        loaded = self.unifier.load_from_csv(path)
        assert len(loaded) == 1
        assert loaded[0]["symbol"] == "VOO"
        assert loaded[0]["close"] == 102.0


class TestIsColombian:
    def setup_method(self):
        self.unifier = DataUnifier()

    def test_colombian_symbol(self):
        assert self.unifier._is_colombian("ECOPETROL")

    def test_international_symbol(self):
        assert not self.unifier._is_colombian("VOO")
