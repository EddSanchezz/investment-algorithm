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
    - Diagramas de barras de tiempos de algoritmos
    - Comparativas de complejidad vs tiempo real

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
        Genera gráfico comparativo mostrando complejidad teórica vs tiempo real.
        Los nombres se alternan izquierda/derecha para evitar solapamiento.

        Parámetros:
            results: Lista de resultados de benchmarking
            output_path: Ruta donde guardar la imagen

        Complejidad: O(n) para preparación de datos
        """
        algorithms = [r["algorithm"] for r in results]
        times = [r["average_time"] * 1000 for r in results]

        complexity_map = {
            "O(n)": 1,
            "O(n log n)": 2,
            "O(log² n)": 3,
            "O(n + k)": 4,
            "O(nk)": 5,
            "O(n²)": 6,
        }

        complexity_order = [complexity_map.get(r["complexity"], 0) for r in results]

        fig, ax = plt.subplots(figsize=(14, 8))

        scatter_colors = [
            self.colors[i % len(self.colors)] for i in range(len(results))
        ]

        for i, (alg, time_val, order) in enumerate(
            zip(algorithms, times, complexity_order)
        ):
            ax.scatter(order, time_val, c=scatter_colors[i], s=200, zorder=5)

            if i % 2 == 0:
                ha = "right"
                x_offset = -15
            else:
                ha = "left"
                x_offset = 15

            ax.annotate(
                alg,
                (order, time_val),
                textcoords="offset points",
                xytext=(x_offset, 10),
                ha=ha,
                fontsize=9,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
            )

        ax.set_xlabel("Complejidad Teórica (orden)", fontsize=12)
        ax.set_ylabel("Tiempo Real (milisegundos)", fontsize=12)
        ax.set_title("Complejidad Teórica vs Tiempo Real", fontsize=14)
        ax.set_xticks([1, 2, 3, 4, 5, 6])
        ax.set_xticklabels(
            ["O(n)", "O(n log n)", "O(log² n)", "O(n+k)", "O(nk)", "O(n²)"]
        )
        ax.grid(True, alpha=0.3)

        ax.set_xlim(0.5, 6.5)

        plt.tight_layout()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        print(f"Gráfico de complejidad guardado en {output_path}")
