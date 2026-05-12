"""
Tests unitarios para SortingComparator (src.sorting.comparator).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.sorting.comparator import SortingComparator


class TestPrepareData:
    def setup_method(self):
        self.comparator = SortingComparator()

    def test_date_sort_key(self):
        records = [
            {"date": "2024-01-02", "close": 103.0, "symbol": "VOO"},
            {"date": "2024-01-01", "close": 102.0, "symbol": "VOO"},
        ]
        prepared = self.comparator.prepare_data(records, "date")
        assert len(prepared) == 2
        assert "sort_key" in prepared[0]
        assert prepared[0]["sort_key"] == ((2024, 1, 2), 103.0)
        assert prepared[1]["sort_key"] == ((2024, 1, 1), 102.0)

    def test_field_sort_key(self):
        records = [{"volume": 5000}, {"volume": 1000}]
        prepared = self.comparator.prepare_data(records, "volume")
        assert prepared[0]["sort_key"] == 5000
        assert prepared[1]["sort_key"] == 1000

    def test_missing_key_fallsback_to_zero(self):
        records = [{"name": "a"}]
        prepared = self.comparator.prepare_data(records, "volume")
        assert prepared[0]["sort_key"] == 0


class TestBenchmarkAlgorithm:
    def setup_method(self):
        self.comparator = SortingComparator()
        self.data = [{"sort_key": i} for i in range(100)]

    def test_benchmark_returns_correct_keys(self):
        algo = self.comparator.algorithms["TimSort"]
        result = self.comparator.benchmark_algorithm(algo, self.data, runs=2)
        assert "average_time" in result
        assert "min_time" in result
        assert "max_time" in result
        assert result["runs"] == 2
        assert result["average_time"] > 0

    def test_counters_reset_per_run(self):
        algo = self.comparator.algorithms["Selection Sort"]
        self.comparator.sorter.comparison_count = 999
        self.comparator.sorter.swap_count = 999
        algo(self.data.copy())
        first_comparisons = self.comparator.sorter.comparison_count
        assert first_comparisons > 0
        self.comparator.sorter.comparison_count = 0
        self.comparator.sorter.swap_count = 0
        algo(self.data.copy())
        assert self.comparator.sorter.comparison_count > 0


class TestCompareAll:
    def setup_method(self):
        self.comparator = SortingComparator()
        self.records = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0,
             "open": 99.0, "high": 101.0, "low": 98.0, "volume": 1000},
            {"date": "2024-01-02", "symbol": "VOO", "close": 102.0,
             "open": 100.0, "high": 103.0, "low": 99.0, "volume": 1200},
            {"date": "2024-01-03", "symbol": "VOO", "close": 101.0,
             "open": 102.0, "high": 104.0, "low": 100.0, "volume": 1100},
        ]

    def test_compare_all_returns_results(self):
        results = self.comparator.compare_all(self.records, runs=1)
        assert len(results) > 0
        assert all("algorithm" in r for r in results)
        assert all("average_time" in r for r in results)
        assert all("comparisons" in r for r in results)
        assert all("swaps" in r for r in results)

    def test_results_sorted_by_time(self):
        results = self.comparator.compare_all(self.records, runs=1)
        times = [r["average_time"] for r in results]
        assert times == sorted(times)


class TestGenerateTable:
    def setup_method(self):
        self.comparator = SortingComparator()

    def test_generate_table_returns_string(self):
        results = [
            {"algorithm": "QuickSort", "complexity": "O(n log n)", "size": 100,
             "average_time": 0.001, "min_time": 0.0009, "max_time": 0.0011,
             "comparisons": 500, "swaps": 100},
        ]
        table = self.comparator.generate_table(results)
        assert "QuickSort" in table
        assert "O(n log n)" in table
