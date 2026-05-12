"""
Tests unitarios para DataCleaner (src.etl.cleaner).
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.etl.cleaner import DataCleaner


class TestDetectMissingValues:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_no_missing(self):
        records = [
            {"open": 100.0, "high": 105.0, "low": 99.0, "close": 102.0, "volume": 1000},
            {"open": 102.0, "high": 106.0, "low": 101.0, "close": 103.0, "volume": 1200},
        ]
        assert self.cleaner.detect_missing_values(records) == []

    def test_none_value(self):
        records = [
            {"open": 100.0, "high": 105.0, "low": 99.0, "close": 102.0, "volume": 1000},
            {"open": None, "high": 106.0, "low": 101.0, "close": 103.0, "volume": 1200},
        ]
        assert self.cleaner.detect_missing_values(records) == [1]

    def test_nan_value(self):
        records = [
            {"open": 100.0, "high": 105.0, "low": 99.0, "close": float("nan"), "volume": 1000},
        ]
        result = self.cleaner.detect_missing_values(records)
        assert result == [0]

    def test_missing_field(self):
        records = [{"open": 100.0, "high": 105.0, "low": 99.0, "volume": 1000}]
        assert self.cleaner.detect_missing_values(records) == [0]


class TestDetectDuplicates:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_no_duplicates(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO"},
            {"date": "2024-01-02", "symbol": "VOO"},
        ]
        assert self.cleaner.detect_duplicates(records) == []

    def test_with_duplicates(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO"},
            {"date": "2024-01-01", "symbol": "VOO"},
            {"date": "2024-01-02", "symbol": "VOO"},
        ]
        assert self.cleaner.detect_duplicates(records) == [1]

    def test_same_date_different_symbol(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO"},
            {"date": "2024-01-01", "symbol": "ECOPETROL"},
        ]
        assert self.cleaner.detect_duplicates(records) == []


class TestDetectOutliersZScore:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_no_outliers(self):
        records = [{"close": 100.0 + i} for i in range(20)]
        assert self.cleaner.detect_outliers_zscore(records) == []

    def test_with_outlier(self):
        values = [100.0] * 19 + [1000.0]
        records = [{"close": v} for v in values]
        result = self.cleaner.detect_outliers_zscore(records)
        assert len(result) == 1
        assert result[0] == 19

    def test_insufficient_data(self):
        records = [{"close": 100.0}, {"close": 101.0}]
        assert self.cleaner.detect_outliers_zscore(records) == []

    def test_zero_stdev(self):
        records = [{"close": 100.0} for _ in range(10)]
        assert self.cleaner.detect_outliers_zscore(records) == []


class TestDetectOutliersIQR:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_no_outliers(self):
        records = [{"close": float(i)} for i in range(10, 30)]
        assert self.cleaner.detect_outliers_iqr(records) == []

    def test_with_outlier(self):
        values = list(range(10, 30)) + [1000]
        records = [{"close": float(v)} for v in values]
        result = self.cleaner.detect_outliers_iqr(records)
        assert 1000.0 in [records[i]["close"] for i in result]

    def test_insufficient_data(self):
        records = [{"close": 1.0}, {"close": 2.0}, {"close": 3.0}]
        assert self.cleaner.detect_outliers_iqr(records) == []


class TestInterpolateForwardFill:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_forward_fill(self):
        records = [{"close": 100.0}, {"close": None}, {"close": 102.0}]
        result = self.cleaner.interpolate_forward_fill(records, "close", [1])
        assert result[1]["close"] == 100.0

    def test_no_previous_value(self):
        records = [{"close": None}, {"close": 102.0}]
        result = self.cleaner.interpolate_forward_fill(records, "close", [0])
        assert result[0]["close"] is None

    def test_empty_indices(self):
        records = [{"close": 100.0}]
        result = self.cleaner.interpolate_forward_fill(records, "close", [])
        assert result == records


class TestInterpolateBackwardFill:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_backward_fill(self):
        records = [{"close": 100.0}, {"close": None}, {"close": 102.0}]
        result = self.cleaner.interpolate_backward_fill(records, "close", [1])
        assert result[1]["close"] == 102.0

    def test_no_next_value(self):
        records = [{"close": 100.0}, {"close": None}]
        result = self.cleaner.interpolate_backward_fill(records, "close", [1])
        assert result[1]["close"] is None


class TestInterpolateMissing:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_linear_interpolation(self):
        records = [{"close": 100.0}, {"close": None}, {"close": 102.0}]
        result = self.cleaner.interpolate_missing(records, "close", [1])
        assert result[1]["close"] == 101.0

    def test_all_missing(self):
        records = [{"close": None}, {"close": None}]
        result = self.cleaner.interpolate_missing(records, "close", [0, 1])
        for r in result:
            assert r["close"] is None

    def test_consecutive_missing(self):
        records = [{"close": 100.0}, {"close": None}, {"close": None}, {"close": 106.0}]
        result = self.cleaner.interpolate_missing(records, "close", [1, 2])
        assert result[1]["close"] == 103.0
        assert result[2]["close"] == 103.0


class TestRemoveDuplicates:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_remove_some(self):
        records = [{"a": 1}, {"a": 2}, {"a": 1}]
        result = self.cleaner.remove_duplicates(records, [2])
        assert len(result) == 2
        assert result == [{"a": 1}, {"a": 2}]

    def test_no_indices(self):
        records = [{"a": 1}]
        assert self.cleaner.remove_duplicates(records, []) == records


class TestCleanRecords:
    def setup_method(self):
        self.cleaner = DataCleaner()

    def test_clean_pipeline(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0, "low": 99.0, "close": 102.0, "volume": 1000},
            {"date": "2024-01-02", "symbol": "VOO", "open": 102.0, "high": 106.0, "low": 101.0, "close": None, "volume": 1200},
            {"date": "2024-01-03", "symbol": "VOO", "open": 103.0, "high": 107.0, "low": 102.0, "close": 104.0, "volume": 1100},
        ]
        cleaned, report = self.cleaner.clean_records(records)
        assert len(cleaned) == 3
        assert report["missing_values"] == 1
        assert cleaned[1]["close"] is not None

    def test_duplicates_removed(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0, "low": 99.0, "close": 102.0, "volume": 1000},
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0, "low": 99.0, "close": 102.0, "volume": 1000},
            {"date": "2024-01-02", "symbol": "VOO", "open": 102.0, "high": 106.0, "low": 101.0, "close": 103.0, "volume": 1200},
        ]
        cleaned, report = self.cleaner.clean_records(records)
        assert len(cleaned) == 2
        assert report["duplicates"] == 1
        assert report["deletions"] == 1
