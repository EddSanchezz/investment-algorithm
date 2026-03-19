"""Integration tests for the complete pipeline"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.time_analyzer import TimeAnalyzer
from src.analysis.performance_table import PerformanceTable
from src.sorting import bubble_sort, merge_sort, quick_sort


class TestTimeAnalyzer:
    """Tests para el analizador de tiempo"""

    def test_analyze_single_algorithm(self):
        """Verifica análisis de un solo algoritmo"""
        analyzer = TimeAnalyzer(runs=2)
        test_data = [5, 3, 8, 1, 9, 2, 7]

        result = analyzer.analyze_sorting_algorithm(
            bubble_sort, test_data, "bubble_sort"
        )

        assert result.algorithm_name == "bubble_sort"
        assert result.array_size == 7
        assert result.is_correct
        assert result.execution_time_ms >= 0

    def test_analyze_all_algorithms(self):
        """Verifica análisis de múltiples algoritmos"""
        analyzer = TimeAnalyzer(runs=2)
        test_data = [5, 3, 8, 1, 9, 2, 7]

        algorithms = {
            "bubble_sort": bubble_sort,
            "merge_sort": merge_sort,
            "quick_sort": quick_sort,
        }

        results = analyzer.analyze_all(algorithms, test_data)

        assert len(results) == 3
        assert all(r.is_correct for r in results)

    def test_sorted_results(self):
        """Verifica que los resultados se ordenen correctamente"""
        analyzer = TimeAnalyzer(runs=2)
        test_data = [5, 3, 8, 1, 9, 2, 7]

        analyzer.analyze_sorting_algorithm(bubble_sort, test_data, "bubble_sort")
        analyzer.analyze_sorting_algorithm(merge_sort, test_data, "merge_sort")

        sorted_results = analyzer.get_results_sorted()
        times = [r.execution_time_ms for r in sorted_results]

        assert times == sorted(times)


class TestPerformanceTable:
    """Tests para la tabla de rendimiento"""

    def test_add_single_result(self):
        """Verifica agregar un resultado"""
        from src.analysis.time_analyzer import TimingResult

        table = PerformanceTable()
        result = TimingResult(
            algorithm_name="bubble_sort",
            execution_time_ms=1.5,
            array_size=100,
            is_correct=True,
        )

        table.add_result(result)
        assert len(table.results) == 1

    def test_generate_table(self):
        """Verifica generación de tabla"""
        from src.analysis.time_analyzer import TimingResult

        table = PerformanceTable()

        results = [
            TimingResult("Bubble Sort", 2.0, 100, True),
            TimingResult("Merge Sort", 0.5, 100, True),
        ]

        table.add_results(results)
        table_text = table.generate_table()

        assert "Bubble Sort" in table_text
        assert "Merge Sort" in table_text
        assert "2.0000" in table_text or "0.5000" in table_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
