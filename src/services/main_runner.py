"""
Main Runner - Orquestador del pipeline ETL y análisis de ordenamiento.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.fetcher import FinancialDataFetcher
from src.etl.cleaner import DataCleaner
from src.etl.unifier import DataUnifier
from src.sorting.comparator import SortingComparator
from src.sorting.visualizer import SortingVisualizer
from src.services.volume_analyzer import VolumeAnalyzer


class InvestmentPipeline:
    COLOMBIAN_STOCKS = ["ecopetrol.cl", "isa.cl", "geb.cl", "nutresa.cl"]

    INTERNATIONAL_ETFS = [
        "voo",
        "vti",
        "qqq",
        "spy",
        "vea",
        "vwo",
        "bnd",
        "efa",
        "eem",
        "tlt",
        "ivv",
        "schd",
        "dia",
        "iwm",
        "xlf",
        "xlk",
    ]

    NYSE_STOCKS = ["ko", "pfe", "pep"]

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.raw_dir = os.path.join(data_dir, "raw")
        self.processed_dir = os.path.join(data_dir, "processed")

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

        self.fetcher = FinancialDataFetcher()
        self.cleaner = DataCleaner()
        self.unifier = DataUnifier()
        self.comparator = SortingComparator()
        self.visualizer = SortingVisualizer()
        self.volume_analyzer = VolumeAnalyzer()

    def run_etl(self, symbols: list = None, years: int = 5) -> list:
        """
        Ejecuta el proceso ETL completo.

        Parámetros:
            symbols: Lista de símbolos a descargar (default: predefined)
            years: Años de historial a descargar

        Retorna:
            Dataset unificado y limpiado

        Complejidad: O(n*d) para descarga + O(n) para limpieza + O(n log n) para unificación
        """
        if symbols is None:
            symbols = self.COLOMBIAN_STOCKS + self.INTERNATIONAL_ETFS + self.NYSE_STOCKS

        print(f"\n{'=' * 60}")
        print("ETAPA 1: Extracción de datos")
        print(f"{'=' * 60}")

        raw_file = os.path.join(self.raw_dir, "raw_data.csv")

        print("Usando sistema Multi-Source (Yahoo -> Alpha Vantage -> Web Scraper -> Binance)...")
        all_records = self.fetcher.fetch_multiple_assets(symbols, years)

        if not all_records:
            print("ERROR: No se pudieron obtener datos.")
            return []

        self.fetcher.save_to_csv(all_records, raw_file)

        print(f"\n{'=' * 60}")
        print("ETAPA 2: Limpieza de datos")
        print(f"{'=' * 60}")

        cleaned_records, report = self.cleaner.clean_records(all_records)

        print("Reporte de limpieza:")
        print(f"  - Valores faltantes detectados: {report['missing_values']}")
        print(f"  - Duplicados eliminados: {report['duplicates']}")
        print(f"  - Outliers Z-Score detectados: {report['outliers_zscore']}")
        print(f"  - Outliers IQR detectados: {report['outliers_iqr']}")
        print(f"  - Interpolaciones realizadas: {report['interpolations']}")
        print(f"  - Registros eliminados: {report['deletions']}")

        print(f"\n{'=' * 60}")
        print("ETAPA 3: Unificación de datos")
        print(f"{'=' * 60}")

        gaps = self.unifier.detect_calendar_gaps(cleaned_records)
        total_gaps = sum(len(v) for v in gaps.values())
        if total_gaps > 0:
            print(f"\nDesalineaciones de calendario detectadas: {total_gaps} días faltantes")
            for sym, missing in gaps.items():
                print(f"  - {sym}: {len(missing)} días faltantes")
            print("Alineando calendarios bursátiles...")
            aligned_records = self.unifier.align_calendars(cleaned_records)
            print(f"Registros después de alineación: {len(aligned_records)}")
        else:
            aligned_records = cleaned_records

        unified_file = os.path.join(self.processed_dir, "unified_data.csv")
        self.unifier.save_to_csv(aligned_records, unified_file)

        stats = self.unifier.generate_statistics(aligned_records)
        print("\nEstadísticas del dataset unificado:")
        print(f"  - Total de registros: {stats['total_records']}")
        print(f"  - Símbolos únicos: {stats['unique_symbols']}")
        print(
            f"  - Rango de fechas: {stats['date_range'][0]} a {stats['date_range'][1]}"
        )

        return aligned_records

    def run_sorting_analysis(
        self, records: list, sort_key: str = "date", output_dir: str = "data/processed"
    ) -> list:
        """
        Ejecuta el análisis de algoritmos de ordenamiento.

        Parámetros:
            records: Lista de registros a ordenar
            sort_key: Campo por el cual ordenar
            output_dir: Directorio para guardar resultados

        Retorna:
            Lista de resultados ordenados por tiempo promedio

        Complejidad: O(a * runs * T_max) donde a = 12 algoritmos
        """
        print(f"\n{'=' * 60}")
        print("ETAPA 4: Análisis de algoritmos de ordenamiento")
        print(f"{'=' * 60}")

        results = self.comparator.compare_all(records, sort_key)

        table = self.comparator.generate_table(results)
        print("\nTabla de resultados (orden ascendente por tiempo):")
        print(table)

        self.visualizer.plot_complexity_comparison(
            results, os.path.join(output_dir, "complexity_comparison.png")
        )

        sorting_csv = os.path.join(output_dir, "sorting_results.csv")
        self._save_sorting_csv(results, sorting_csv)

        return results

    def _save_sorting_csv(self, results: list, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write("Metodo de ordenamiento,Tamano,Tiempo (ms)\n")
            for r in results:
                time_ms = r["average_time"] * 1000
                f.write(
                    f"{r['algorithm']} {r['complexity']},{r['size']},{time_ms:.4f}\n"
                )
        print(f"Resultados de ordenamiento guardados en {filepath}")

    def run_volume_analysis(
        self, records: list, top_n: int = 15, output_dir: str = "data/processed"
    ) -> list:
        """
        Ejecuta el análisis de volumen de negociación.

        Parámetros:
            records: Lista de registros financieros
            top_n: Número de días con mayor volumen a retornar
            output_dir: Directorio para guardar resultados

        Retorna:
            Lista de los N días con mayor volumen (orden ascendente)

        Complejidad: O(n) para agregación + O(n log n) para ordenamiento
        """
        print(f"\n{'=' * 60}")
        print("ETAPA 5: Análisis de volumen de negociación")
        print(f"{'=' * 60}")

        top_days = self.volume_analyzer.top_volume_days_ascending(records, top_n)

        print(f"\nLos {top_n} días con mayor volumen (orden ascendente):")
        print(f"{'Fecha':<15} {'Volumen Total':>20}")
        print("-" * 40)
        for day in top_days:
            print(f"{day['date']:<15} {day['total_volume']:>20,}")

        volume_csv = os.path.join(output_dir, "top_volume_days.csv")
        self._save_volume_csv(top_days, volume_csv)

        return top_days

    def _save_volume_csv(self, top_days: list, filepath: str) -> None:
        """Guarda los días con mayor volumen en CSV."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write("Fecha,Volumen Total\n")
            for day in top_days:
                f.write(f"{day['date']},{day['total_volume']}\n")
        print(f"Resultados de volumen guardados en {filepath}")

    def run_full_pipeline(self) -> dict:
        """
        Ejecuta el pipeline completo del proyecto.

        Retorna:
            Diccionario con todos los resultados
        """
        print("\n" + "=" * 60)
        print("INICIO DEL PIPELINE COMPLETO")
        print("=" * 60)

        records = self.run_etl()

        sorting_results = self.run_sorting_analysis(records)

        volume_results = self.run_volume_analysis(records)

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETADO EXITOSAMENTE")
        print("=" * 60)

        return {
            "records": records,
            "sorting_results": sorting_results,
            "volume_results": volume_results,
        }


def main():
    """Función principal de ejecución."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pipeline de análisis de algoritmos para datos financieros"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Lista de símbolos a descargar (ej: --symbols VOO ECOPETROL)",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=5,
        help="Años de historial a descargar (default: 5)",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Forzar descarga aunque existan datos previos (garantiza reproducibilidad)",
    )

    args = parser.parse_args()

    pipeline = InvestmentPipeline()

    unified_file = os.path.join(pipeline.processed_dir, "unified_data.csv")
    if args.force_download or not os.path.exists(unified_file):
        if args.symbols:
            records = pipeline.run_etl(symbols=args.symbols, years=args.years)
        else:
            records = pipeline.run_etl()
    else:
        print(f"\nUsando datos existentes en {unified_file}")
        print("(usa --force-download para regenerar desde cero)")
        records = pipeline.unifier.load_from_csv(unified_file)

    pipeline.run_sorting_analysis(records)
    pipeline.run_volume_analysis(records)

    print("\n¡Análisis completado!")


if __name__ == "__main__":
    main()
