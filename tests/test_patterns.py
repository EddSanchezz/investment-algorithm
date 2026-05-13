"""
Tests unitarios para detección de patrones y análisis de volatilidad.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.patterns.sliding_window import (
    detect_breakout_down,
    detect_breakout_up,
    detect_consecutive_down,
    detect_consecutive_up,
    detect_gap_down,
    detect_gap_up,
    PatternAnalyzer,
)
from src.services.patterns.volatility import (
    daily_returns,
    standard_deviation,
    annualized_volatility,
    classify_risk,
    VolatilityAnalyzer,
)


class TestConsecutiveUp:
    def test_basic_detection(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 103.0},
        ]
        result = detect_consecutive_up(records, min_days=3)
        assert result["total_occurrences"] == 1
        assert result["dates"] == ["2024-01-04"]

    def test_no_pattern(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 99.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 98.0},
        ]
        result = detect_consecutive_up(records, min_days=3)
        assert result["total_occurrences"] == 0

    def test_multiple_occurrences(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 103.0},
            {"date": "2024-01-05", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-06", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-07", "symbol": "VOO", "close": 103.0},
            {"date": "2024-01-08", "symbol": "VOO", "close": 104.0},
        ]
        result = detect_consecutive_up(records, min_days=3)
        assert result["total_occurrences"] == 2

    def test_by_year_grouping(self):
        records = [
            {"date": "2023-12-28", "symbol": "VOO", "close": 99.0},
            {"date": "2023-12-29", "symbol": "VOO", "close": 100.0},
            {"date": "2023-12-30", "symbol": "VOO", "close": 101.0},
            {"date": "2023-12-31", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 103.0},
        ]
        result = detect_consecutive_up(records, min_days=3)
        by_year = result["by_year"]
        assert "2023" in by_year
        assert "2024" in by_year

    def test_insufficient_data(self):
        result = detect_consecutive_up([{"date": "2024-01-01", "close": 100.0}], min_days=3)
        assert result["total_occurrences"] == 0


class TestGapUp:
    def test_basic_detection(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "open": 110.0, "close": 112.0},
        ]
        result = detect_gap_up(records, threshold=0.05)
        assert result["total_occurrences"] == 1
        assert result["average_gap_pct"] >= 9.0

    def test_no_gap(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "close": 101.0},
            {"date": "2024-01-02", "symbol": "VOO", "open": 101.5, "close": 102.0},
        ]
        result = detect_gap_up(records, threshold=0.05)
        assert result["total_occurrences"] == 0

    def test_insufficient_data(self):
        result = detect_gap_up([{"date": "2024-01-01", "open": 100.0, "close": 100.0}])
        assert result["total_occurrences"] == 0


class TestConsecutiveDown:
    def test_basic_detection(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 103.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 100.0},
        ]
        result = detect_consecutive_down(records, min_days=3)
        assert result["total_occurrences"] == 1
        assert result["dates"] == ["2024-01-04"]


class TestGapDown:
    def test_basic_detection(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "open": 90.0, "close": 92.0},
        ]
        result = detect_gap_down(records, threshold=0.05)
        assert result["total_occurrences"] == 1
        assert result["average_gap_pct"] >= 9.0


class TestBreakouts:
    def test_breakout_up(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 105.0},
        ]
        result = detect_breakout_up(records, window=3)
        assert result["total_occurrences"] == 1
        assert result["dates"] == ["2024-01-04"]

    def test_breakout_down(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 105.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 104.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 103.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 100.0},
        ]
        result = detect_breakout_down(records, window=3)
        assert result["total_occurrences"] == 1
        assert result["dates"] == ["2024-01-04"]


class TestPatternAnalyzer:
    def setup_method(self):
        self.records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-05", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-06", "symbol": "VOO", "close": 103.0},
            {"date": "2024-01-07", "symbol": "VOO", "close": 104.0},
        ]
        self.analyzer = PatternAnalyzer()

    def test_analyze_consecutive_up(self):
        result = self.analyzer.analyze(self.records, "VOO", "consecutive_up", 3)
        assert result["symbol"] == "VOO"
        assert result["total_occurrences"] == 1

    def test_analyze_gap_up(self):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "open": 110.0, "close": 112.0},
        ]
        result = self.analyzer.analyze(records, "VOO", "gap_up", threshold=0.05)
        assert result["total_occurrences"] == 1

    def test_unknown_symbol(self):
        result = self.analyzer.analyze(self.records, "FAKE", "consecutive_up")
        assert "error" in result

    def test_analyze_consecutive_down(self):
        descending_records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 104.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 103.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 101.0},
        ]
        result = self.analyzer.analyze(descending_records, "VOO", "consecutive_down", 3)
        assert result["total_occurrences"] == 1

    def test_analyze_breakout(self):
        breakout_records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 105.0},
        ]
        result = self.analyzer.analyze(breakout_records, "VOO", "breakout_up", window=3)
        assert result["total_occurrences"] == 1
        assert result["window"] == 3

    def test_analyze_all(self):
        result = self.analyzer.analyze_all(self.records, "consecutive_up", min_days=3)
        assert "results" in result
        assert len(result["results"]) > 0

class TestVolatilityMetrics:
    def test_daily_returns(self):
        prices = [100.0, 105.0, 103.0, 106.0]
        r = daily_returns(prices)
        assert len(r) == 3
        assert round(r[0], 4) == 0.05
        assert round(r[1], 4) == -0.0190
        assert round(r[2], 4) == 0.0291

    def test_daily_returns_insufficient(self):
        assert daily_returns([100.0]) == []

    def test_standard_deviation(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        std = standard_deviation(values)
        assert round(std, 4) == 1.5811

    def test_standard_deviation_single(self):
        assert standard_deviation([1.0]) == 0.0

    def test_annualized_volatility(self):
        daily_std = 0.01
        ann = annualized_volatility(daily_std, 252)
        assert round(ann, 4) == 0.1587

    def test_classify_risk(self):
        assert classify_risk(0.10) == "conservador"
        assert classify_risk(0.20) == "moderado"
        assert classify_risk(0.35) == "agresivo"
        assert classify_risk(0.15) == "moderado"
        assert classify_risk(0.30) == "agresivo"


class TestVolatilityAnalyzer:
    def setup_method(self):
        self.records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0},
            {"date": "2024-01-02", "symbol": "VOO", "close": 102.0},
            {"date": "2024-01-03", "symbol": "VOO", "close": 101.0},
            {"date": "2024-01-04", "symbol": "VOO", "close": 103.0},
            {"date": "2024-01-05", "symbol": "VOO", "close": 105.0},
            {"date": "2024-01-01", "symbol": "SPY", "close": 200.0},
            {"date": "2024-01-02", "symbol": "SPY", "close": 201.0},
            {"date": "2024-01-03", "symbol": "SPY", "close": 202.0},
            {"date": "2024-01-04", "symbol": "SPY", "close": 203.0},
            {"date": "2024-01-05", "symbol": "SPY", "close": 204.0},
        ]
        self.analyzer = VolatilityAnalyzer()

    def test_analyze(self):
        result = self.analyzer.analyze(self.records, "VOO")
        assert result["symbol"] == "VOO"
        assert result["n_prices"] == 5
        assert result["risk_category"] in ("conservador", "moderado", "agresivo")
        assert result["annualized_volatility"] > 0

    def test_insufficient_data(self):
        result = self.analyzer.analyze(self.records, "FAKE")
        assert "error" in result

    def test_ranking(self):
        ranking = self.analyzer.ranking(self.records)
        assert ranking["summary"]["total_symbols"] == 2
        assert len(ranking["ranking"]) == 2
        assert ranking["ranking"][0]["annualized_volatility"] <= ranking["ranking"][1]["annualized_volatility"]

    def test_ranking_summary(self):
        ranking = self.analyzer.ranking(self.records)
        s = ranking["summary"]
        assert s["min_volatility"] is not None
        assert s["max_volatility"] is not None
        assert "categories" in s
