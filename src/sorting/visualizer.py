"""
Visualizer Module - Generación de gráficos para análisis de algoritmos.
Crea diagramas de barras comparativos de tiempos de ordenamiento.
"""

import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")
import os


class SortingVisualizer:
    """
    Generador de visualizaciones para resultados de benchmarking.

    Crea:
    - Diagramas de barras horizontales ordenados por complejidad teórica

    Complejidad de generación de gráficos: O(n) para preparar datos
    """

    def __init__(self):
        self.colors = [
            "#2E86AB",
            "#A23B72",
            "#F18F01",
            "#C73E1D",
            "#3B1F2B",
            "#95C623",
            "#7B2D26",
            "#4A7C59",
            "#D4A574",
            "#6B4226",
            "#4A154B",
            "#00A0B0",
        ]

    def plot_sorting_times(
        self, results: list, output_path: str = "data/processed/sorting_times.png"
    ) -> None:
        """
        Genera un diagrama de barras con los tiempos de ordenamiento.

        Parámetros:
            results: Lista de resultados con 'algorithm' y 'average_time'
            output_path: Ruta donde guardar la imagen

        Complejidad: O(n) para preparación de datos, dominated por matplotlib
        """
        algorithms = [r["algorithm"] for r in results]
        times = [r["average_time"] * 1000 for r in results]
        complexities = [r["complexity"] for r in results]

        fig, ax = plt.subplots(figsize=(14, 8))

        x_pos = range(len(algorithms))
        bars = ax.bar(x_pos, times, color=self.colors[: len(algorithms)])

        for i, (bar, complexity) in enumerate(zip(bars, complexities)):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{times[i]:.3f}ms\n({complexity})",
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=45,
            )

        ax.set_xlabel("Algoritmo", fontsize=12)
        ax.set_ylabel("Tiempo Promedio (milisegundos)", fontsize=12)
        ax.set_title(
            "Comparación de Tiempos de Algoritmos de Ordenamiento", fontsize=14
        )
        ax.set_xticks(x_pos)
        ax.set_xticklabels(algorithms, rotation=45, ha="right")

        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.3f}"))

        plt.tight_layout()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        print(f"Gráfico guardado en {output_path}")

    def plot_complexity_comparison(
        self,
        results: list,
        output_path: str = "data/processed/complexity_comparison.png",
    ) -> None:
        """
        Genera gráfico de barras horizontal ordenando algoritmos por complejidad teórica.
        Cada barra muestra el tiempo real, permitiendo comparar eficiencia real vs teórica.

        Parámetros:
            results: Lista de resultados de benchmarking
            output_path: Ruta donde guardar la imagen

        Complejidad: O(n log n) para ordenar por complejidad
        """
        complexity_order_map = {
            "O(n)": 0,
            "O(n log n)": 1,
            "O(log² n)": 2,
            "O(n + k)": 3,
            "O(nk)": 4,
            "O(n²)": 5,
        }

        sorted_results = sorted(
            results,
            key=lambda x: (
                complexity_order_map.get(x["complexity"], 99),
                x["average_time"],
            ),
        )

        algorithms = [f"{r['algorithm']} ({r['complexity']})" for r in sorted_results]
        times = [r["average_time"] * 1000 for r in sorted_results]
        n = len(algorithms)

        fig, ax = plt.subplots(figsize=(12, max(10, n * 0.6)))

        y_pos = range(n)
        bars = ax.barh(y_pos, times, color=self.colors[:n])

        ax.set_yticks(y_pos)
        ax.set_yticklabels(algorithms, fontsize=10)
        ax.invert_yaxis()

        for i, (bar, time_val) in enumerate(zip(bars, times)):
            ax.text(
                bar.get_width() + max(times) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{time_val:.3f} ms",
                va="center",
                fontsize=9,
            )

        ax.set_xlabel("Tiempo de Ejecución (milisegundos)", fontsize=12)
        ax.set_title(
            "Algoritmos de Ordenamiento - Ordenados por Complejidad Teórica",
            fontsize=12,
        )
        ax.set_xlim(0, max(times) * 1.25)
        ax.grid(axis="x", alpha=0.3)

        plt.tight_layout()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        print(f"Gráfico guardado en {output_path}")
