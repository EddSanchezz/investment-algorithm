"""
Cleaner Module - Transformación y limpieza de datos financieros.
Este módulo implementa la capa de transformación del proceso ETL.
Incluye detección y manejo de valores faltantes, anomalías e inconsistencias.
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime
import statistics


class DataCleaner:
    """
    Limpiador de datos financieros con técnicas de detección y corrección.

    Detecta y maneja:
    - Valores faltantes (NaN, None)
    - Valores atípicos (anomalías)
    - Registros inconsistentes
    - Duplicados

    Complejidad temporal: O(n) para detección, O(n) para interpolación
    Complejidad espacial: O(n) para almacenamiento temporal
    """

    Z_SCORE_THRESHOLD = 3.0

    def __init__(self):
        self.cleaning_report = {
            "missing_values": 0,
            "duplicates": 0,
            "outliers": 0,
            "interpolations": 0,
            "deletions": 0,
        }

    def detect_missing_values(self, records: List[Dict]) -> List[int]:
        """
        Detecta registros con valores faltantes en campos numéricos.

        Parámetros:
            records: Lista de registros financieros

        Retorna:
            Índices de registros con valores faltantes

        Complejidad: O(n * f) donde n = registros, f = campos a verificar
        Se verifica cada campo numérico en cada registro
        """
        missing_indices = []
        numeric_fields = ["open", "high", "low", "close", "volume"]

        for idx, record in enumerate(records):
            for field in numeric_fields:
                value = record.get(field)
                if value is None or (isinstance(value, float) and value != value):
                    missing_indices.append(idx)
                    self.cleaning_report["missing_values"] += 1
                    break

        return missing_indices

    def detect_duplicates(self, records: List[Dict]) -> List[int]:
        """
        Detecta registros duplicados basándose en fecha y símbolo.

        Parámetros:
            records: Lista de registros financieros

        Retorna:
            Índices de registros duplicados (excepto el primero)

        Complejidad: O(n) usando tabla hash para deduplicación
        """
        seen = set()
        duplicate_indices = []

        for idx, record in enumerate(records):
            key = (record["date"], record["symbol"])
            if key in seen:
                duplicate_indices.append(idx)
                self.cleaning_report["duplicates"] += 1
            else:
                seen.add(key)

        return duplicate_indices

    def detect_outliers_zscore(
        self, records: List[Dict], field: str = "close"
    ) -> List[int]:
        """
        Detecta valores atípicos usando el método Z-Score.

        Un valor se considera atípico si |z| > threshold (default 3.0)

        Parámetros:
            records: Lista de registros financieros
            field: Campo numérico a analizar

        Retorna:
            Índices de registros con valores atípicos

        Complejidad: O(n) - dos pasadas: cálculo de media/desviación y detección
        """
        values = [r[field] for r in records if r.get(field) is not None]

        if len(values) < 3:
            return []

        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        if stdev == 0:
            return []

        outlier_indices = []
        for idx, record in enumerate(records):
            value = record.get(field)
            if value is not None:
                z_score = abs((value - mean) / stdev)
                if z_score > self.Z_SCORE_THRESHOLD:
                    outlier_indices.append(idx)
                    self.cleaning_report["outliers"] += 1

        return outlier_indices

    def interpolate_missing(
        self, records: List[Dict], field: str, indices: List[int]
    ) -> List[Dict]:
        """
        Interpola valores faltantes usando interpolación lineal.

        La interpolación lineal estima valores desconocidos usando la relación
        entre puntos vecinos: value = y1 + (y2 - y1) * ((x - x1) / (x2 - x1))

        Justificación algorítmica:
        - Preserva la longitud del dataset (importante para series temporales)
        - Mantiene tendencias sin introducir discontinuidades
        - O(n) para encontrar vecinos + O(1) para interpolar = O(n) total

        Parámetros:
            records: Lista de registros financieros
            field: Campo a interpolar
            indices: Índices con valores faltantes

        Retorna:
            Copia de registros con valores interpolados

        Complejidad: O(n) donde n = número de registros
        """
        if not indices:
            return records

        records_copy = [r.copy() for r in records]
        indices_set = set(indices)

        for idx in sorted(indices):
            prev_idx = None
            next_idx = None

            for i in range(idx - 1, -1, -1):
                if i not in indices_set and records_copy[i].get(field) is not None:
                    prev_idx = i
                    break

            for i in range(idx + 1, len(records_copy)):
                if i not in indices_set and records_copy[i].get(field) is not None:
                    next_idx = i
                    break

            if prev_idx is not None and next_idx is not None:
                prev_value = records_copy[prev_idx][field]
                next_value = records_copy[next_idx][field]
                records_copy[idx][field] = (prev_value + next_value) / 2
                self.cleaning_report["interpolations"] += 1
            elif prev_idx is not None:
                records_copy[idx][field] = records_copy[prev_idx][field]
                self.cleaning_report["interpolations"] += 1
            elif next_idx is not None:
                records_copy[idx][field] = records_copy[next_idx][field]
                self.cleaning_report["interpolations"] += 1

        return records_copy

    def remove_duplicates(self, records: List[Dict], indices: List[int]) -> List[Dict]:
        """
        Elimina registros duplicados.

        Justificación algorítmica:
        - Eliminamos duplicados porque cada registro debe ser único
        - La duplicación afecta el análisis (sobrestimación de volumen, etc.)
        - O(n) para filtrar usando comprensión de listas

        Parámetros:
            records: Lista de registros
            indices: Índices a eliminar

        Retorna:
            Lista sin duplicados

        Complejidad: O(n) donde n = número de registros
        """
        if not indices:
            return records

        indices_set = set(indices)
        cleaned = [r for i, r in enumerate(records) if i not in indices_set]
        self.cleaning_report["deletions"] += len(indices)

        return cleaned

    def clean_records(self, records: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Pipeline completo de limpieza de datos.

        Orden de operaciones:
        1. Detectar y eliminar duplicados (primero para no afectar estadísticas)
        2. Detectar y marcar outliers (para referencia)
        3. Interpolar valores faltantes (preserva longitud)

        Justificación del orden:
        - Duplicados primero: afectan cálculos estadísticos (media, varianza)
        - Outliers después: basados en estadísticas ya corregidas
        - Interpolación último: usa contexto temporal completo

        Parámetros:
            records: Lista de registros financieros

        Retorna:
            Tupla (registros limpiados, reporte de limpieza)

        Complejidad total: O(n) + O(n) + O(n) = O(n)
        Dominada por las operaciones lineales sobre los datos
        """
        self.cleaning_report = {
            "missing_values": 0,
            "duplicates": 0,
            "outliers": 0,
            "interpolations": 0,
            "deletions": 0,
        }

        duplicate_indices = self.detect_duplicates(records)
        cleaned = self.remove_duplicates(records, duplicate_indices)

        missing_indices = self.detect_missing_values(cleaned)

        outlier_indices = self.detect_outliers_zscore(cleaned, "close")

        if missing_indices:
            cleaned = self.interpolate_missing(cleaned, "close", missing_indices)
            cleaned = self.interpolate_missing(cleaned, "volume", missing_indices)
            cleaned = self.interpolate_missing(cleaned, "open", missing_indices)
            cleaned = self.interpolate_missing(cleaned, "high", missing_indices)
            cleaned = self.interpolate_missing(cleaned, "low", missing_indices)

        return cleaned, self.cleaning_report.copy()
