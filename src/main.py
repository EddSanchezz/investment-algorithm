"""Main entry point for the Investment Algorithm project

Ejecuta el pipeline completo: ETL, análisis de ordenamiento,
y genera visualizaciones.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.fetcher import DataFetcher
from src.etl.cleaner import DataCleaner
from src.etl.unifier import DataUnifier
from src.etl.validator import DataValidator
from src.sorting import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    heap_sort,
    shell_sort,
    counting_sort,
    radix_sort,
    cocktail_sort,
    comb_sort,
    tim_sort,
)
from src.analysis.time_analyzer import TimeAnalyzer
from src.analysis.performance_table import PerformanceTable
from src.visualization.bar_chart import BarChartGenerator
from src.utils.constants import DATE_COL, CLOSE_COL, VOLUME_COL, SYMBOL_COL


SORTING_ALGORITHMS = {
    "bubble_sort": bubble_sort,
    "selection_sort": selection_sort,
    "insertion_sort": insertion_sort,
    "merge_sort": merge_sort,
    "quick_sort": quick_sort,
    "heap_sort": heap_sort,
    "shell_sort": shell_sort,
    "counting_sort": counting_sort,
    "radix_sort": radix_sort,
    "cocktail_sort": cocktail_sort,
    "comb_sort": comb_sort,
    "tim_sort": tim_sort,
}


def run_etl_pipeline(years: int = 5, use_cache: bool = False) -> list[dict]:
    """Ejecuta el pipeline ETL completo"""
    print("=" * 60)
    print("ETL PIPELINE")
    print("=" * 60)

    raw_file = "data/raw_data.csv"
    processed_file = "data/processed_data.csv"

    if use_cache and os.path.exists(processed_file):
        print("Cargando datos desde cache...")
        return load_csv(processed_file)

    print("\n[1/4] Descargando datos...")
    fetcher = DataFetcher()
    records = fetcher.fetch_all_assets(years)
    print(f"Total de registros descargados: {len(records)}")

    print("\n[2/4] Limpiando datos...")
    cleaner = DataCleaner()
    records_dicts = [
        {
            DATE_COL: r.date,
            CLOSE_COL: r.close,
            VOLUME_COL: r.volume,
            SYMBOL_COL: r.symbol,
        }
        for r in records
    ]
    cleaned_records = cleaner.clean_dataset(records_dicts)
    report = cleaner.get_quality_report()
    print(f"Registros después de limpieza: {len(cleaned_records)}")

    print("\n[3/4] Unificando datos...")
    unifier = DataUnifier()
    unified_records = unifier.unify_records(cleaned_records)
    unification_report = unifier.get_report()
    total = unification_report.total_assets if unification_report else 0
    start = unification_report.date_range_start if unification_report else "N/A"
    end = unification_report.date_range_end if unification_report else "N/A"
    print(f"Total de activos: {total}")
    print(f"Rango de fechas: {start} - {end}")

    print("\n[4/4] Validando datos...")
    validator = DataValidator()
    validation = validator.validate(unified_records)
    if validation.is_valid:
        print("✓ Dataset válido")
    else:
        print("✗ Dataset con errores:")
        for error in validation.errors:
            print(f"  - {error}")

    return unified_records


def load_csv(filename: str) -> list[dict]:
    """Carga un archivo CSV"""
    import csv

    records = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def run_sorting_analysis(records: list[dict]) -> None:
    """Ejecuta el análisis de algoritmos de ordenamiento"""
    print("\n" + "=" * 60)
    print("SORTING ALGORITHM ANALYSIS")
    print("=" * 60)

    data_for_sorting = [
        (r[DATE_COL], float(r[CLOSE_COL]), r[SYMBOL_COL]) for r in records
    ]
    data_for_sorting.sort(key=lambda x: (x[0], x[1]))

    test_array = [int(r[VOLUME_COL]) for r in records[: min(1000, len(records))]]

    print(f"\nAnalizando {len(SORTING_ALGORITHMS)} algoritmos...")
    print(f"Tamaño del array de prueba: {len(test_array)} elementos")

    analyzer = TimeAnalyzer(runs=3)
    results = analyzer.analyze_all(SORTING_ALGORITHMS, test_array)

    print("\n" + analyzer.get_results_table())

    table_gen = PerformanceTable()
    table_gen.add_results(results)
    table_text = table_gen.generate_table()
    print("\n" + table_text)

    print("\nGenerando visualización...")
    chart = BarChartGenerator()
    chart.add_results(results)
    chart.set_title("Algoritmos de Ordenamiento - Comparación de Rendimiento")
    output_file = chart.generate("output/sorting_bar_chart.png")
    print(f"Gráfico guardado en: {output_file}")

    table_gen.export_to_csv("output/sorting_results.csv")
    print("Resultados CSV guardados en: output/sorting_results.csv")


def find_top_volume_days(records: list[dict], top_n: int = 15) -> None:
    """Encuentra los N días con mayor volumen de negociación"""
    print("\n" + "=" * 60)
    print(f"TOP {top_n} DÍAS CON MAYOR VOLUMEN")
    print("=" * 60)

    volume_by_date = {}
    for record in records:
        date = record[DATE_COL]
        volume = int(record.get(VOLUME_COL, 0))
        if date not in volume_by_date:
            volume_by_date[date] = 0
        volume_by_date[date] += volume

    sorted_days = sorted(volume_by_date.items(), key=lambda x: x[1], reverse=True)[
        :top_n
    ]

    print(f"\n{'Fecha':<15} {'Volumen Total':>20}")
    print("-" * 35)
    for date, volume in sorted_days:
        print(f"{date:<15} {volume:>20,}")


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Investment Algorithm Analysis")
    parser.add_argument("--years", type=int, default=5, help="Years of historical data")
    parser.add_argument(
        "--skip-etl", action="store_true", help="Skip ETL and use cached data"
    )
    parser.add_argument(
        "--sort-only", action="store_true", help="Run only sorting analysis"
    )
    args = parser.parse_args()

    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    if args.sort_only:
        records = load_csv("data/processed_data.csv")
        if not records:
            print("No hay datos cacheados. Ejecute sin --sort-only primero.")
            return
    else:
        records = run_etl_pipeline(years=args.years, use_cache=args.skip_etl)

    if records:
        run_sorting_analysis(records)
        find_top_volume_days(records)

    print("\n" + "=" * 60)
    print("ANÁLISIS COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
