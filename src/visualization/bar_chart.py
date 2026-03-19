"""Bar chart generator for sorting algorithm performance visualization"""

import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.use("Agg")
except ImportError:
    plt = None


class BarChartGenerator:
    """Generador de diagramas de barras para tiempos de ordenamiento"""

    def __init__(self):
        self.data: list[tuple[str, float]] = []
        self.title = "Sorting Algorithm Performance Comparison"

    def add_algorithm(self, name: str, time_ms: float) -> None:
        """Agrega datos de un algoritmo"""
        self.data.append((name, time_ms))

    def add_results(self, results: list) -> None:
        """Agrega múltiples resultados"""
        for result in results:
            if hasattr(result, "algorithm_name") and hasattr(
                result, "execution_time_ms"
            ):
                self.add_algorithm(result.algorithm_name, result.execution_time_ms)

    def generate(
        self,
        output_file: str = "output/bar_chart.png",
        figsize: tuple[int, int] = (14, 8),
    ) -> str:
        """Genera el diagrama de barras"""
        if not self.data:
            return "No hay datos para graficar"

        if plt is None:
            return "matplotlib no está instalado. Ejecute: pip install matplotlib"

        sorted_data = sorted(self.data, key=lambda x: x[1])

        names = [d[0] for d in sorted_data]
        times = [d[1] for d in sorted_data]

        fig, ax = plt.subplots(figsize=figsize)

        colors = plt.cm.viridis([i / len(names) for i in range(len(names))])

        bars = ax.barh(names, times, color=colors)

        for bar, time_val in zip(bars, times):
            width = bar.get_width()
            ax.text(
                width + max(times) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{time_val:.2f} ms",
                va="center",
                fontsize=9,
            )

        ax.set_xlabel("Execution Time (milliseconds)", fontsize=12)
        ax.set_ylabel("Algorithm", fontsize=12)
        ax.set_title(self.title, fontsize=14, fontweight="bold")

        ax.set_xlim(0, max(times) * 1.15)

        ax.grid(axis="x", linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        plt.close()

        return output_file

    def set_title(self, title: str) -> None:
        """Establece el título del gráfico"""
        self.title = title

    def generate_comparison_chart(
        self,
        theoretical_complexities: dict[str, str],
        output_file: str = "output/comparison_chart.png",
    ) -> str:
        """Genera un gráfico comparativo con complejidades teóricas"""
        if not self.data or plt is None:
            return "No hay datos para graficar"

        sorted_data = sorted(self.data, key=lambda x: x[1])

        names = [d[0] for d in sorted_data]
        times = [d[1] for d in sorted_data]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        colors = plt.cm.coolwarm([i / len(names) for i in range(len(names))])
        bars1 = ax1.barh(names, times, color=colors)
        ax1.set_xlabel("Execution Time (ms)")
        ax1.set_title("Actual Execution Time")
        ax1.grid(axis="x", linestyle="--", alpha=0.7)

        complexity_values = []
        complexity_colors = []

        o_values = {
            "O(1)": 0,
            "O(log n)": 1,
            "O(n)": 2,
            "O(n log n)": 3,
            "O(n²)": 4,
            "O(n³)": 5,
            "O(2^n)": 6,
        }
        color_scale = plt.cm.RdYlGn_r

        for name in names:
            complexity = theoretical_complexities.get(name, "O(n²)")
            val = o_values.get(complexity, 3)
            complexity_values.append(val)
            complexity_colors.append(color_scale(val / 6))

        bars2 = ax2.barh(names, complexity_values, color=complexity_colors)
        ax2.set_xlabel("Theoretical Complexity Level")
        ax2.set_title("Theoretical Complexity")
        ax2.set_xlim(0, 6)
        ax2.set_xticks(range(len(o_values)))
        ax2.set_xticklabels(list(o_values.keys()), rotation=45, ha="right")
        ax2.grid(axis="x", linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        plt.close()

        return output_file
