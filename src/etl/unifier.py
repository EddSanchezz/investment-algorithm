"""
Unifier Module - Unificación de datasets financieros.
Este módulo implementa la capa de carga del proceso ETL.
Combina datos de múltiples fuentes manteniendo integridad temporal.
"""

from typing import List, Dict, Tuple
from datetime import datetime
import csv
import os


class DataUnifier:
    """
    Unificador de datos financieros de múltiples activos.

    Funcionalidades:
    - Combina datos de múltiples símbolos en un solo dataset
    - Ordena por fecha para mantener integridad temporal
    - Valida consistencia entre registros
    - Genera estadísticas del dataset unificado

    Complejidad temporal: O(n log n) dominada por el ordenamiento
    Complejidad espacial: O(n) para almacenar el dataset unificado
    """

    REQUIRED_FIELDS = ["date", "symbol", "open", "high", "low", "close", "volume"]

    def validate_record(self, record: Dict) -> bool:
        """
        Valida que un registro tenga todos los campos requeridos y valores válidos.

        Parámetros:
            record: Diccionario con datos del registro

        Retorna:
            True si el registro es válido, False en caso contrario

        Complejidad: O(f) donde f = número de campos requeridos (7)
        """
        for field in self.REQUIRED_FIELDS:
            if field not in record:
                return False
            if record[field] is None:
                return False

        if record["close"] <= 0 or record["volume"] < 0:
            return False

        return True

    def unify_datasets(self, datasets: List[List[Dict]]) -> List[Dict]:
        """
        Combina múltiples datasets en uno solo.

        Parámetros:
            datasets: Lista de listas de registros (cada lista es un activo)

        Retorna:
            Dataset unificado con todos los registros

        Complejidad: O(n) para concatenar + O(n log n) para ordenar
        El ordenamiento es necesario para mantener la integridad temporal
        """
        all_records = []

        for dataset in datasets:
            for record in dataset:
                if self.validate_record(record):
                    all_records.append(record)

        all_records.sort(key=lambda x: (x["date"], x["close"]))

        return all_records

    def load_from_csv(self, filepath: str) -> List[Dict]:
        """
        Carga registros desde un archivo CSV.

        Parámetros:
            filepath: Ruta del archivo CSV

        Retorna:
            Lista de diccionarios con los datos

        Complejidad: O(n) donde n = número de registros en el CSV
        """
        records = []

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = {
                    "date": row["date"],
                    "symbol": row["symbol"],
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": int(row["volume"]),
                }
                if self.validate_record(record):
                    records.append(record)

        return records

    def save_to_csv(self, records: List[Dict], filepath: str) -> None:
        """
        Guarda registros en un archivo CSV unificado.

        Parámetros:
            records: Lista de registros
            filepath: Ruta del archivo de salida

        Complejidad: O(n) para escritura de n registros
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.REQUIRED_FIELDS)
            writer.writeheader()
            writer.writerows(records)

        print(f"Dataset unificado guardado en {filepath} ({len(records)} registros)")

    def generate_statistics(self, records: List[Dict]) -> Dict:
        """
        Genera estadísticas descriptivas del dataset unificado.

        Parámetros:
            records: Lista de registros financieros

        Retorna:
            Diccionario con estadísticas (símbolos, registros, rango de fechas)

        Complejidad: O(n) para recorrer todos los registros
        """
        if not records:
            return {"total_records": 0}

        symbols = set(r["symbol"] for r in records)
        dates = [r["date"] for r in records]

        total_volume = sum(r["volume"] for r in records)
        avg_volume = total_volume / len(records)

        return {
            "total_records": len(records),
            "unique_symbols": len(symbols),
            "symbols": sorted(list(symbols)),
            "date_range": (min(dates), max(dates)),
            "total_volume": total_volume,
            "average_volume": avg_volume,
        }
