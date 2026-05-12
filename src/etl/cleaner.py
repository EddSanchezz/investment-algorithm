"""
Cleaner Module - Transformación y limpieza de datos financieros.
Este módulo implementa la capa de transformación del proceso ETL.
Incluye detección y manejo de valores faltantes, anomalías e inconsistencias.
"""

from typing import List, Dict, Tuple
import statistics
import math


class DataCleaner:
    """
    Limpiador de datos financieros con técnicas de detección y corrección.

    Detecta y maneja:
    - Valores faltantes (NaN, None)
    - Valores atípicos (anomalías) mediante Z-Score e IQR
    - Registros inconsistentes
    - Duplicados

    Técnicas de interpolación disponibles:
    1. Interpolación lineal: Estima valores desconocidos usando promedio de vecinos
       más cercanos. Preserva tendencias lineales. O(n) por campo.
    2. Forward-fill: Propaga el último valor conocido hacia adelante.
       Apropiado cuando el valor se mantiene constante hasta nuevo registro.
    3. Backward-fill: Propaga el siguiente valor conocido hacia atrás.
       Útil para valores faltantes al inicio de la serie.

    Complejidad temporal: O(n) para detección, O(n) para interpolación
    Complejidad espacial: O(n) para almacenamiento temporal
    """

    Z_SCORE_THRESHOLD = 3.0
    IQR_MULTIPLIER = 1.5

    def __init__(self):
        self.cleaning_report = {
            "missing_values": 0,
            "duplicates": 0,
            "outliers_zscore": 0,
            "outliers_iqr": 0,
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
                if value is None or (isinstance(value, float) and math.isnan(value)):
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
                    self.cleaning_report["outliers_zscore"] += 1

        return outlier_indices

    def detect_outliers_iqr(
        self, records: List[Dict], field: str = "close"
    ) -> List[int]:
        """
        Detecta valores atípicos usando el método Rango Intercuartil (IQR).

        Un valor se considera atípico si está fuera del rango:
        [Q1 - 1.5*IQR, Q3 + 1.5*IQR]

        Justificación algorítmica:
        - IQR es más robusto que Z-Score para datos no normales
        - No asume distribución específica de los datos
        - Los valores financieros típicamente no siguen distribución normal
        - O(n log n) por el ordenamiento necesario para encontrar cuartiles

        Parámetros:
            records: Lista de registros financieros
            field: Campo numérico a analizar (default: "close")

        Retorna:
            Índices de registros con valores atípicos

        Complejidad: O(n log n) - dominada por el ordenamiento para cuartiles
        """
        values = [(idx, r[field]) for idx, r in enumerate(records)
                  if r.get(field) is not None]

        if len(values) < 4:
            return []

        sorted_vals = sorted(v[1] for v in values)
        n = len(sorted_vals)

        def median(arr: List[float]) -> float:
            m = len(arr)
            if m % 2 == 0:
                return (arr[m // 2 - 1] + arr[m // 2]) / 2
            return arr[m // 2]

        mid = n // 2
        if n % 2 == 0:
            q1 = median(sorted_vals[:mid])
            q3 = median(sorted_vals[mid:])
        else:
            q1 = median(sorted_vals[:mid])
            q3 = median(sorted_vals[mid + 1:])

        iqr = q3 - q1
        lower_bound = q1 - self.IQR_MULTIPLIER * iqr
        upper_bound = q3 + self.IQR_MULTIPLIER * iqr

        outlier_indices = []
        for idx, val in values:
            if val < lower_bound or val > upper_bound:
                outlier_indices.append(idx)
                self.cleaning_report["outliers_iqr"] += 1

        return outlier_indices

    def interpolate_forward_fill(
        self, records: List[Dict], field: str, indices: List[int]
    ) -> List[Dict]:
        """
        Interpola valores faltantes usando forward-fill (propagación hacia adelante).

        Reemplaza el valor faltante con el último valor conocido anterior.
        Si no hay valor anterior, deja el valor como está.

        Justificación algorítmica:
        - Útil cuando se espera que el valor se mantenga constante
        - Apropiado para datos financieros en días sin cambios significativos
        - O(n) - una sola pasada hacia adelante

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
        last_valid = None

        for i, r in enumerate(records_copy):
            if i in indices_set:
                if last_valid is not None:
                    r[field] = last_valid
                    self.cleaning_report["interpolations"] += 1
            else:
                val = r.get(field)
                if val is not None:
                    last_valid = val

        return records_copy

    def interpolate_backward_fill(
        self, records: List[Dict], field: str, indices: List[int]
    ) -> List[Dict]:
        """
        Interpola valores faltantes usando backward-fill (propagación hacia atrás).

        Reemplaza el valor faltante con el siguiente valor conocido.
        Si no hay valor siguiente, deja el valor como está.

        Justificación algorítmica:
        - Útil para valores faltantes al inicio de la serie
        - Complementario a forward-fill para casos extremos
        - O(n) - una sola pasada hacia atrás

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
        next_valid = None

        for i in range(len(records_copy) - 1, -1, -1):
            if i in indices_set:
                if next_valid is not None:
                    records_copy[i][field] = next_valid
                    self.cleaning_report["interpolations"] += 1
            else:
                val = records_copy[i].get(field)
                if val is not None:
                    next_valid = val

        return records_copy

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
        - O(n) con precomputación de vecinos, evitando el cuello de botella O(n²)

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
        n = len(records_copy)

        if len(indices) == n:
            return records_copy

        prev_valid = [None] * n
        next_valid = [None] * n

        last_valid = None
        for i in range(n):
            if i not in indices_set and records_copy[i].get(field) is not None:
                last_valid = i
            prev_valid[i] = last_valid

        next_seen = None
        for i in range(n - 1, -1, -1):
            if i not in indices_set and records_copy[i].get(field) is not None:
                next_seen = i
            next_valid[i] = next_seen

        for idx in sorted(indices):
            p_idx = prev_valid[idx]
            n_idx = next_valid[idx]

            if p_idx is not None and n_idx is not None:
                prev_value = records_copy[p_idx][field]
                next_value = records_copy[n_idx][field]
                records_copy[idx][field] = (prev_value + next_value) / 2
                self.cleaning_report["interpolations"] += 1
            elif p_idx is not None:
                records_copy[idx][field] = records_copy[p_idx][field]
                self.cleaning_report["interpolations"] += 1
            elif n_idx is not None:
                records_copy[idx][field] = records_copy[n_idx][field]
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
        2. Detectar outliers con Z-Score e IQR (para referencia)
        3. Interpolar valores faltantes (preserva longitud)
           - Usa interpolación lineal como método principal
           - Forward-fill como fallback si no hay vecino anterior
           - Backward-fill como fallback si no hay vecino siguiente

        Justificación del orden:
        - Duplicados primero: afectan cálculos estadísticos (media, varianza)
        - Outliers después: basados en estadísticas ya corregidas
        - Interpolación último: usa contexto temporal completo
        - Lineal primero: mejor estimación cuando hay vecinos en ambos lados
        - Forward-fill segundo: razonable si el valor persiste
        - Backward-fill último: solo cuando no hay dato anterior

        Parámetros:
            records: Lista de registros financieros

        Retorna:
            Tupla (registros limpiados, reporte de limpieza)

        Complejidad total: O(n) + O(n) + O(n) + O(n log n) = O(n log n)
        El IQR introduce la complejidad logarítmica por el ordenamiento
        """
        self.cleaning_report = {
            "missing_values": 0,
            "duplicates": 0,
            "outliers_zscore": 0,
            "outliers_iqr": 0,
            "interpolations": 0,
            "deletions": 0,
        }

        duplicate_indices = self.detect_duplicates(records)
        cleaned = self.remove_duplicates(records, duplicate_indices)

        missing_indices = self.detect_missing_values(cleaned)

        self.detect_outliers_zscore(cleaned, "close")
        self.detect_outliers_iqr(cleaned, "close")

        if missing_indices:
            cleaned = self.interpolate_missing(cleaned, "close", missing_indices)
            cleaned = self.interpolate_forward_fill(cleaned, "close", missing_indices)
            cleaned = self.interpolate_backward_fill(cleaned, "close", missing_indices)

            cleaned = self.interpolate_missing(cleaned, "volume", missing_indices)
            cleaned = self.interpolate_forward_fill(cleaned, "volume", missing_indices)
            cleaned = self.interpolate_backward_fill(cleaned, "volume", missing_indices)

            cleaned = self.interpolate_missing(cleaned, "open", missing_indices)
            cleaned = self.interpolate_forward_fill(cleaned, "open", missing_indices)
            cleaned = self.interpolate_backward_fill(cleaned, "open", missing_indices)

            cleaned = self.interpolate_missing(cleaned, "high", missing_indices)
            cleaned = self.interpolate_forward_fill(cleaned, "high", missing_indices)
            cleaned = self.interpolate_backward_fill(cleaned, "high", missing_indices)

            cleaned = self.interpolate_missing(cleaned, "low", missing_indices)
            cleaned = self.interpolate_forward_fill(cleaned, "low", missing_indices)
            cleaned = self.interpolate_backward_fill(cleaned, "low", missing_indices)

        return cleaned, self.cleaning_report.copy()
