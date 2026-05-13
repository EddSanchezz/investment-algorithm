"""
Tests unitarios para los algoritmos de similitud.
Usa datos sintéticos conocidos para verificar cada implementación.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.similarity.euclidean import euclidean_distance
from src.services.similarity.pearson import pearson_correlation
from src.services.similarity.dtw import dtw_distance
from src.services.similarity.cosine import cosine_similarity
from src.services.similarity import SimilarityAnalyzer


class TestEuclidean:
    def test_identical_series(self):
        s = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = euclidean_distance(s, s)
        assert result["distance"] == 0.0
        assert result["n"] == 5

    def test_different_series(self):
        a = [1.0, 2.0, 3.0]
        b = [4.0, 5.0, 6.0]
        result = euclidean_distance(a, b)
        assert result["distance"] > 0.0
        assert round(result["distance"], 6) == 3.0

    def test_empty_series(self):
        result = euclidean_distance([], [])
        assert result["distance"] is None

    def test_with_nan(self):
        result = euclidean_distance([1.0, float("nan"), 3.0], [4.0, 5.0, 6.0])
        assert result["n"] == 3
        assert result["distance"] > 0.0

    def test_different_lengths(self):
        try:
            euclidean_distance([1.0], [1.0, 2.0])
            assert False
        except ValueError:
            pass


class TestPearson:
    def test_perfect_positive(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0]
        b = [2.0, 4.0, 6.0, 8.0, 10.0]
        result = pearson_correlation(a, b)
        assert result["correlation"] == 1.0

    def test_perfect_negative(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0]
        b = [5.0, 4.0, 3.0, 2.0, 1.0]
        result = pearson_correlation(a, b)
        assert round(result["correlation"], 4) == -1.0

    def test_no_correlation(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0]
        b = [3.0, 3.0, 3.0, 3.0, 3.0]
        result = pearson_correlation(a, b)
        assert result["correlation"] == 0.0

    def test_insufficient_data(self):
        result = pearson_correlation([1.0], [2.0])
        assert result["correlation"] is None


class TestDTW:
    def test_identical_series(self):
        s = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = dtw_distance(s, s)
        assert result["distance"] == 0.0

    def test_different_series(self):
        a = [1.0, 2.0, 3.0]
        b = [1.0, 2.0, 2.0, 3.0]
        result = dtw_distance(a, b)
        assert result["distance"] >= 0.0
        assert result["path_length"] > 0

    def test_empty_series(self):
        result = dtw_distance([], [1.0])
        assert result["distance"] is None

    def test_with_window(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0]
        b = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = dtw_distance(a, b, window=2)
        assert result["distance"] == 0.0

    def test_full_matrix_false(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0]
        b = [2.0, 3.0, 4.0, 5.0, 6.0]
        result = dtw_distance(a, b, full_matrix=False)
        assert result["distance"] >= 0.0
        assert result["full_matrix"] is False
        assert result["path_length"] > 0


class TestCosine:
    def test_identical_vectors(self):
        v = [1.0, 2.0, 3.0]
        result = cosine_similarity(v, v)
        assert result["similarity"] == 1.0

    def test_orthogonal_vectors(self):
        result = cosine_similarity([1.0, 0.0], [0.0, 1.0])
        assert result["similarity"] == 0.0

    def test_opposite_vectors(self):
        result = cosine_similarity([1.0, 2.0], [-1.0, -2.0])
        assert round(result["similarity"], 4) == -1.0

    def test_empty_vectors(self):
        result = cosine_similarity([], [])
        assert result["similarity"] is None

    def test_different_lengths(self):
        try:
            cosine_similarity([1.0], [1.0, 2.0])
            assert False
        except ValueError:
            pass

    def test_zero_norm_vector(self):
        result = cosine_similarity([0.0, 0.0], [1.0, -1.0])
        assert result["similarity"] == 0.0
        assert result["angle_degrees"] == 90.0


class TestSimilarityAnalyzer:
    def setup_method(self):
        self.records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 400.0, "open": 398.0, "high": 402.0, "low": 397.0, "volume": 1000},
            {"date": "2024-01-02", "symbol": "VOO", "close": 402.0, "open": 400.0, "high": 403.0, "low": 399.0, "volume": 1100},
            {"date": "2024-01-03", "symbol": "VOO", "close": 401.0, "open": 402.0, "high": 404.0, "low": 400.0, "volume": 900},
            {"date": "2024-01-01", "symbol": "SPY", "close": 500.0, "open": 498.0, "high": 502.0, "low": 497.0, "volume": 2000},
            {"date": "2024-01-02", "symbol": "SPY", "close": 503.0, "open": 500.0, "high": 504.0, "low": 499.0, "volume": 2100},
            {"date": "2024-01-03", "symbol": "SPY", "close": 502.0, "open": 503.0, "high": 505.0, "low": 501.0, "volume": 1900},
        ]
        self.analyzer = SimilarityAnalyzer()

    def test_extract_series(self):
        result = self.analyzer._extract_series(self.records, "VOO", "SPY")
        assert result is not None
        s1, s2, dates = result
        assert len(s1) == 3
        assert len(s2) == 3
        assert s1 == [400.0, 402.0, 401.0]
        assert s2 == [500.0, 503.0, 502.0]

    def test_returns(self):
        prices = [100.0, 105.0, 103.0]
        r = self.analyzer._returns(prices)
        assert len(r) == 2
        assert round(r[0], 4) == 0.05
        assert round(r[1], 4) == -0.0190

    def test_compare(self):
        result = self.analyzer.compare(self.records, "VOO", "SPY")
        assert result["symbol1"] == "VOO"
        assert result["symbol2"] == "SPY"
        assert result["common_dates"] == 3
        assert "euclidean" in result
        assert "pearson" in result
        assert "dtw" in result
        assert "cosine" in result
        assert "series" in result

    def test_compare_no_data(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 400.0, "open": 398.0, "high": 402.0, "low": 397.0, "volume": 1000},
        ]
        result = self.analyzer.compare(records, "VOO", "FAKE")
        assert "error" in result

    def test_correlation_matrix(self):
        result = self.analyzer.compute_correlation_matrix(self.records, ["VOO", "SPY"])
        assert "matrix" in result
        assert "symbols" in result
        assert len(result["symbols"]) == 2
        assert len(result["matrix"]) == 2
        assert result["matrix"][0][0] == 1.0
        assert result["matrix"][1][1] == 1.0

    def test_compare_many(self):
        records = self.records + [
            {"date": "2024-01-01", "symbol": "QQQ", "close": 300.0, "open": 299.0, "high": 301.0, "low": 298.0, "volume": 1500},
            {"date": "2024-01-02", "symbol": "QQQ", "close": 303.0, "open": 300.0, "high": 304.0, "low": 299.0, "volume": 1520},
            {"date": "2024-01-03", "symbol": "QQQ", "close": 302.0, "open": 303.0, "high": 305.0, "low": 301.0, "volume": 1490},
        ]
        result = self.analyzer.compare_many(records, ["VOO", "SPY", "QQQ"], max_points=10)
        assert result["mode"] == "group"
        assert result["symbols"] == ["VOO", "SPY", "QQQ"]
        assert len(result["pairwise"]) == 3
        assert result["correlation_matrix"]["matrix"][0][0] == 1.0
        assert "normalized_series" in result
