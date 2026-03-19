"""Time analyzer for measuring sorting algorithm performance"""

from dataclasses import dataclass
from typing import Callable, Any
import time


@dataclass
class TimingResult:
    """Resultado del análisis de tiempo de un algoritmo"""

    algorithm_name: str
    execution_time_ms: float
    array_size: int
    is_correct: bool


class TimeAnalyzer:
    """Analizador de tiempo de ejecución para algoritmos de ordenamiento"""

    def __init__(self, runs: int = 5):
        self.runs = runs
        self.results: list[TimingResult] = []

    def analyze_sorting_algorithm(
        self, algorithm: Callable, test_data: list, algorithm_name: str
    ) -> TimingResult:
        """Analiza el tiempo de ejecución de un algoritmo de ordenamiento"""
        times = []

        for _ in range(self.runs):
            arr_copy = test_data.copy()
            start = time.perf_counter()
            sorted_arr = algorithm(arr_copy)
            end = time.perf_counter()
            times.append((end - start) * 1000)

        avg_time = sum(times) / len(times)

        sorted_expected = sorted(test_data)
        arr_copy = test_data.copy()
        result = algorithm(arr_copy)
        is_correct = result == sorted_expected

        result_obj = TimingResult(
            algorithm_name=algorithm_name,
            execution_time_ms=avg_time,
            array_size=len(test_data),
            is_correct=is_correct,
        )
        self.results.append(result_obj)

        return result_obj

    def analyze_all(
        self, algorithms: dict[str, Callable], test_data: list
    ) -> list[TimingResult]:
        """Analiza múltiples algoritmos de ordenamiento"""
        for name, algorithm in algorithms.items():
            self.analyze_sorting_algorithm(algorithm, test_data, name)
        return self.results

    def get_results_sorted(self) -> list[TimingResult]:
        """Retorna los resultados ordenados por tiempo de ejecución"""
        return sorted(self.results, key=lambda x: x.execution_time_ms)

    def get_results_table(self) -> str:
        """Genera una tabla de resultados formateada"""
        sorted_results = self.get_results_sorted()

        header = (
            f"{'Algoritmo':<20} {'Tiempo (ms)':<15} {'Tamaño':<10} {'Correcto':<10}"
        )
        separator = "-" * len(header)

        lines = [header, separator]
        for result in sorted_results:
            lines.append(
                f"{result.algorithm_name:<20} "
                f"{result.execution_time_ms:<15.4f} "
                f"{result.array_size:<10} "
                f"{'Sí' if result.is_correct else 'No':<10}"
            )

        return "\n".join(lines)
