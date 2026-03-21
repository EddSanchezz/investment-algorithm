"""
Comparator Module - Comparación de rendimiento de algoritmos de ordenamiento.
Ejecuta cada algoritmo y mide tiempo de ejecución.
"""

import time
from typing import List, Dict, Callable
from .algorithms import SortingAlgorithms


class SortingComparator:
    """
    Comparador de algoritmos de ordenamiento.

    Ejecuta cada algoritmo múltiples veces y calcula estadísticas
    de rendimiento (tiempo promedio, mínimo, máximo).

    Complejidad de benchmarking: O(m * n log n) donde m = número de algoritmos
    """

    def __init__(self):
        self.sorter = SortingAlgorithms()
        self.algorithms = {
            "TimSort": self.sorter.tim_sort,
            "Comb Sort": self.sorter.comb_sort,
            "Selection Sort": self.sorter.selection_sort,
            "Tree Sort": self.sorter.tree_sort,
            "Pigeonhole Sort": self.sorter.pigeonhole_sort,
            "Bucket Sort": self.sorter.bucket_sort,
            "QuickSort": self.sorter.quicksort,
            "HeapSort": self.sorter.heapsort,
            "Bitonic Sort": self.sorter.bitonic_sort,
            "Gnome Sort": self.sorter.gnome_sort,
            "Binary Insertion Sort": self.sorter.binary_insertion_sort,
            "Radix Sort": self.sorter.radix_sort,
        }
        self.complexities = {
            "TimSort": "O(n log n)",
            "Comb Sort": "O(n²)",
            "Selection Sort": "O(n²)",
            "Tree Sort": "O(n log n)",
            "Pigeonhole Sort": "O(n + k)",
            "Bucket Sort": "O(n + k)",
            "QuickSort": "O(n log n)",
            "HeapSort": "O(n log n)",
            "Bitonic Sort": "O(log² n)",
            "Gnome Sort": "O(n²)",
            "Binary Insertion Sort": "O(n²)",
            "Radix Sort": "O(nk)",
        }

    def prepare_data(self, records: List[Dict], sort_key: str = "date") -> List[Dict]:
        """
        Prepara los datos para ordenamiento agregando clave de ordenamiento.

        Parámetros:
            records: Lista de registros financieros
            sort_key: Campo por el cual ordenar

        Retorna:
            Lista de diccionarios con campo 'sort_key' adicional

        Complejidad: O(n) para recorrer y copiar registros
        """
        if sort_key == "date":

            def parse_key(r):
                parts = r["date"].split("-")
                return (int(parts[0]), int(parts[1]), int(parts[2]))

            return [{"sort_key": parse_key(r), **r} for r in records]
        else:
            return [{"sort_key": r[sort_key], **r} for r in records]

    def benchmark_algorithm(
        self, algorithm: Callable, data: List[Dict], runs: int = 3
    ) -> Dict:
        """
        Ejecuta un algoritmo múltiples veces y calcula estadísticas.

        Parámetros:
            algorithm: Función de ordenamiento a ejecutar
            data: Datos a ordenar
            runs: Número de ejecuciones para promediar

        Retorna:
            Diccionario con tiempo promedio, min, max y desviación

        Complejidad: O(runs * T(n)) donde T es la complejidad del algoritmo
        """
        times = []

        for _ in range(runs):
            start = time.perf_counter()
            algorithm(data.copy())
            end = time.perf_counter()
            times.append(end - start)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        return {
            "average_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "runs": runs,
        }

    def compare_all(
        self, records: List[Dict], sort_key: str = "date", runs: int = 3
    ) -> List[Dict]:
        """
        Compara todos los algoritmos de ordenamiento.

        Parámetros:
            records: Lista de registros financieros
            sort_key: Campo por el cual ordenar
            runs: Número de ejecuciones por algoritmo

        Retorna:
            Lista ordenada de resultados con tiempo promedio ascendente

        Complejidad: O(a * runs * T_max) donde a = 12 algoritmos
        """
        data = self.prepare_data(records, sort_key)
        n = len(data)

        results = []

        for name, algorithm in self.algorithms.items():
            print(f"Evaluando {name}...")
            stats = self.benchmark_algorithm(algorithm, data, runs)

            results.append(
                {
                    "algorithm": name,
                    "complexity": self.complexities[name],
                    "size": n,
                    "average_time": stats["average_time"],
                    "min_time": stats["min_time"],
                    "max_time": stats["max_time"],
                    "comparisons": self.sorter.comparison_count,
                    "swaps": self.sorter.swap_count,
                }
            )

        results.sort(key=lambda x: x["average_time"])

        return results

    def generate_table(self, results: List[Dict]) -> str:
        """
        Genera una tabla formateada con los resultados.

        Parámetros:
            results: Lista de resultados de comparación

        Retorna:
            String con tabla formateada
        """
        header = (
            f"{'Algoritmo':<25} {'Complejidad':<15} {'Tamaño':<10} {'Tiempo (s)':<15}"
        )
        separator = "-" * 75

        lines = [header, separator]

        for r in results:
            time_str = f"{r['average_time']:.6f}"
            line = f"{r['algorithm']:<25} {r['complexity']:<15} {r['size']:<10} {time_str:<15}"
            lines.append(line)

        return "\n".join(lines)
