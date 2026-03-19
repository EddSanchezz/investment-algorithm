"""Performance table generator for sorting results"""

from typing import Optional
from dataclasses import dataclass

from .time_analyzer import TimingResult


@dataclass
class AlgorithmComplexity:
    """Información de complejidad algorítmica"""

    name: str
    best_case: str
    average_case: str
    worst_case: str
    space_complexity: str
    algorithm_type: str


COMPLEXITY_TABLE = {
    "bubble_sort": AlgorithmComplexity(
        name="Bubble Sort",
        best_case="O(n)",
        average_case="O(n²)",
        worst_case="O(n²)",
        space_complexity="O(1)",
        algorithm_type="Comparison",
    ),
    "selection_sort": AlgorithmComplexity(
        name="Selection Sort",
        best_case="O(n²)",
        average_case="O(n²)",
        worst_case="O(n²)",
        space_complexity="O(1)",
        algorithm_type="Comparison",
    ),
    "insertion_sort": AlgorithmComplexity(
        name="Insertion Sort",
        best_case="O(n)",
        average_case="O(n²)",
        worst_case="O(n²)",
        space_complexity="O(1)",
        algorithm_type="Comparison",
    ),
    "merge_sort": AlgorithmComplexity(
        name="Merge Sort",
        best_case="O(n log n)",
        average_case="O(n log n)",
        worst_case="O(n log n)",
        space_complexity="O(n)",
        algorithm_type="Comparison",
    ),
    "quick_sort": AlgorithmComplexity(
        name="Quick Sort",
        best_case="O(n log n)",
        average_case="O(n log n)",
        worst_case="O(n²)",
        space_complexity="O(log n)",
        algorithm_type="Comparison",
    ),
    "heap_sort": AlgorithmComplexity(
        name="Heap Sort",
        best_case="O(n log n)",
        average_case="O(n log n)",
        worst_case="O(n log n)",
        space_complexity="O(1)",
        algorithm_type="Comparison",
    ),
    "shell_sort": AlgorithmComplexity(
        name="Shell Sort",
        best_case="O(n log² n)",
        average_case="O(n^1.3)",
        worst_case="O(n²)",
        space_complexity="O(1)",
        algorithm_type="Comparison",
    ),
    "counting_sort": AlgorithmComplexity(
        name="Counting Sort",
        best_case="O(n + k)",
        average_case="O(n + k)",
        worst_case="O(n + k)",
        space_complexity="O(k)",
        algorithm_type="Non-comparison",
    ),
    "radix_sort": AlgorithmComplexity(
        name="Radix Sort",
        best_case="O(nk)",
        average_case="O(nk)",
        worst_case="O(nk)",
        space_complexity="O(n + k)",
        algorithm_type="Non-comparison",
    ),
    "cocktail_sort": AlgorithmComplexity(
        name="Cocktail Sort",
        best_case="O(n)",
        average_case="O(n²)",
        worst_case="O(n²)",
        space_complexity="O(1)",
        algorithm_type="Comparison",
    ),
    "comb_sort": AlgorithmComplexity(
        name="Comb Sort",
        best_case="O(n log n)",
        average_case="O(n²)",
        worst_case="O(n²)",
        space_complexity="O(1)",
        algorithm_type="Comparison",
    ),
    "tim_sort": AlgorithmComplexity(
        name="Tim Sort",
        best_case="O(n)",
        average_case="O(n log n)",
        worst_case="O(n log n)",
        space_complexity="O(n)",
        algorithm_type="Hybrid",
    ),
}


class PerformanceTable:
    """Generador de tablas de rendimiento con análisis de complejidad"""

    def __init__(self):
        self.results: list[TimingResult] = []

    def add_result(self, result: TimingResult) -> None:
        """Agrega un resultado de análisis"""
        self.results.append(result)

    def add_results(self, results: list[TimingResult]) -> None:
        """Agrega múltiples resultados"""
        self.results.extend(results)

    def generate_table(self) -> str:
        """Genera tabla completa de rendimiento con complejidades"""
        if not self.results:
            return "No hay resultados disponibles"

        sorted_results = sorted(self.results, key=lambda x: x.execution_time_ms)

        lines = []
        lines.append("=" * 120)
        lines.append(f"{'TABLA DE ANÁLISIS DE ALGORITMOS DE ORDENAMIENTO':^120}")
        lines.append("=" * 120)
        lines.append("")

        lines.append(
            f"{'#':<4} {'Algoritmo':<18} {'Complejidad Promedio':<18} {'Espacio':<12} {'Tipo':<15} {'Tiempo (ms)':<12} {'Estado':<10}"
        )
        lines.append("-" * 120)

        for i, result in enumerate(sorted_results, 1):
            complexity = COMPLEXITY_TABLE.get(
                result.algorithm_name,
                COMPLEXITY_TABLE.get(result.algorithm_name.replace(" ", "_").lower()),
            )

            if complexity:
                lines.append(
                    f"{i:<4} "
                    f"{complexity.name:<18} "
                    f"{complexity.average_case:<18} "
                    f"{complexity.space_complexity:<12} "
                    f"{complexity.algorithm_type:<15} "
                    f"{result.execution_time_ms:<12.4f} "
                    f"{'✓ Correcto' if result.is_correct else '✗ Error':<10}"
                )

        lines.append("-" * 120)
        lines.append("")

        lines.append("Leyenda de Complejidades:")
        lines.append("  O(1)  - Constante")
        lines.append("  O(log n) - Logarítmica")
        lines.append("  O(n)  - Lineal")
        lines.append("  O(n log n) - Linearítmica")
        lines.append("  O(n²) - Cuadrática")
        lines.append("")

        return "\n".join(lines)

    def export_to_csv(self, filename: str) -> None:
        """Exporta los resultados a un archivo CSV"""
        import csv

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Posición",
                    "Algoritmo",
                    "Tiempo (ms)",
                    "Tamaño Array",
                    "Correcto",
                    "Complejidad Promedio",
                    "Complejidad Peor Caso",
                    "Espacio",
                ]
            )

            sorted_results = sorted(self.results, key=lambda x: x.execution_time_ms)

            for i, result in enumerate(sorted_results, 1):
                complexity = COMPLEXITY_TABLE.get(result.algorithm_name)
                writer.writerow(
                    [
                        i,
                        result.algorithm_name,
                        f"{result.execution_time_ms:.4f}",
                        result.array_size,
                        "Sí" if result.is_correct else "No",
                        complexity.average_case if complexity else "N/A",
                        complexity.worst_case if complexity else "N/A",
                        complexity.space_complexity if complexity else "N/A",
                    ]
                )
