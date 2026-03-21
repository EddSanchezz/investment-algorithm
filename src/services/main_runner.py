"""
Main Runner - Orquestador principal del proyecto.
Coordina la ejecución del pipeline ETL y análisis de ordenamiento.
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
    """
    Pipeline principal que orquesta todas las etapas del proyecto.

    Etapas:
    1. Extracción de datos (HTTP directo)
    2. Limpieza y transformación
    3. Unificación de datasets
    4. Análisis de ordenamiento
    5. Análisis de volumen
    6. Generación de visualizaciones

    Complejidad total del pipeline: Dominada por ETL O(n*d) y ordenamiento O(a*n*log*n)
    """

    COLOMBIAN_STOCKS = ["ISA", "GEB"]

    INTERNATIONAL_ETFS = [
        "VOO",
        "VTI",
        "QQQ",
        "SPY",
        "VEA",
        "VWO",
        "BND",
        "EFA",
        "EEM",
        "TLT",
    ]

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
            symbols = self.COLOMBIAN_STOCKS[:10] + self.INTERNATIONAL_ETFS[:10]

        print(f"\n{'=' * 60}")
        print("ETAPA 1: Extracción de datos")
        print(f"{'=' * 60}")

        raw_file = os.path.join(self.raw_dir, "raw_data.csv")
        all_records = self.fetcher.fetch_multiple_assets(symbols, years)

        if not all_records:
            print("No se pudieron obtener datos. Usando datos de ejemplo...")
            all_records = self._generate_sample_data(symbols)

        self.fetcher.save_to_csv(all_records, raw_file)

        print(f"\n{'=' * 60}")
        print("ETAPA 2: Limpieza de datos")
        print(f"{'=' * 60}")

        cleaned_records, report = self.cleaner.clean_records(all_records)

        print(f"Reporte de limpieza:")
        print(f"  - Valores faltantes detectados: {report['missing_values']}")
        print(f"  - Duplicados eliminados: {report['duplicates']}")
        print(f"  - Outliers detectados: {report['outliers']}")
        print(f"  - Interpolaciones realizadas: {report['interpolations']}")
        print(f"  - Registros eliminados: {report['deletions']}")

        print(f"\n{'=' * 60}")
        print("ETAPA 3: Unificación de datos")
        print(f"{'=' * 60}")

        unified_file = os.path.join(self.processed_dir, "unified_data.csv")
        self.unifier.save_to_csv(cleaned_records, unified_file)

        stats = self.unifier.generate_statistics(cleaned_records)
        print(f"\nEstadísticas del dataset unificado:")
        print(f"  - Total de registros: {stats['total_records']}")
        print(f"  - Símbolos únicos: {stats['unique_symbols']}")
        print(
            f"  - Rango de fechas: {stats['date_range'][0]} a {stats['date_range'][1]}"
        )

        return cleaned_records

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
        print(f"\nTabla de resultados (orden ascendente por tiempo):")
        print(table)

        self.visualizer.plot_sorting_times(
            results, os.path.join(output_dir, "sorting_times.png")
        )
        self.visualizer.plot_complexity_comparison(
            results, os.path.join(output_dir, "complexity_comparison.png")
        )

        return results

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

        return top_days

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

    def _generate_sample_data(self, symbols: list) -> list:
        """
        Genera datos de ejemplo para pruebas.

        Parámetros:
            symbols: Lista de símbolos

        Retorna:
            Lista de registros de ejemplo
        """
        from datetime import datetime, timedelta
        import random

        records = []
        base_date = datetime(2021, 1, 1)

        for symbol in symbols:
            price = random.uniform(10, 100)
            for day in range(365 * 5):
                date = base_date + timedelta(days=day)
                if date.weekday() < 5:
                    change = random.uniform(-0.05, 0.05)
                    price = max(1, price * (1 + change))

                    record = {
                        "date": date.strftime("%Y-%m-%d"),
                        "symbol": symbol,
                        "open": price * random.uniform(0.98, 1.0),
                        "high": price * random.uniform(1.0, 1.05),
                        "low": price * random.uniform(0.95, 1.0),
                        "close": price,
                        "volume": random.randint(100000, 10000000),
                    }
                    records.append(record)

        return records


def main():
    """Función principal de ejecución."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pipeline de análisis de algoritmos para datos financieros"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Usar datos de ejemplo en lugar de descargar datos reales",
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

    args = parser.parse_args()

    pipeline = InvestmentPipeline()

    if args.symbols:
        records = pipeline.run_etl(symbols=args.symbols, years=args.years)
    elif args.sample:
        records = pipeline.run_etl()
    else:
        records = pipeline.run_etl()

    pipeline.run_sorting_analysis(records)
    pipeline.run_volume_analysis(records)

    print("\n¡Análisis completado!")


if __name__ == "__main__":
    main()
