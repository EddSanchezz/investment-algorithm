"""
Volume Analyzer Module - Análisis de volumen de negociación.
Identifica los días con mayor volumen para todos los activos combinados.
"""

from typing import List, Dict
from collections import defaultdict


class VolumeAnalyzer:
    """
    Analizador de volumen de negociación.

    Funcionalidades:
    - Agrega volumen por fecha (todos los activos)
    - Encuentra los N días con mayor volumen
    - Genera rankings y estadísticas

    Complejidad temporal: O(n) para agregación, O(n log n) para ordenamiento
    """

    def __init__(self):
        pass

    def aggregate_volume_by_date(self, records: List[Dict]) -> List[Dict]:
        """
        Agrega el volumen de todos los activos por fecha.

        Parámetros:
            records: Lista de registros financieros

        Retorna:
            Lista de diccionarios con fecha y volumen total agregado

        Complejidad: O(n) donde n = número de registros
        Usa tabla hash (dict) para agregación eficiente
        """
        volume_by_date = defaultdict(int)

        for record in records:
            date = record["date"]
            volume = record.get("volume", 0)
            if volume is not None:
                volume_by_date[date] += volume

        aggregated = [
            {"date": date, "total_volume": volume}
            for date, volume in volume_by_date.items()
        ]

        return aggregated

    def top_volume_days(self, records: List[Dict], n: int = 15) -> List[Dict]:
        """
        Encuentra los N días con mayor volumen de negociación.

        Parámetros:
            records: Lista de registros financieros
            n: Número de días a retornar (default: 15)

        Retorna:
            Lista de los N días con mayor volumen, ordenados descendentemente

        Complejidad: O(n) para agregar + O(n log n) para ordenar
        """
        aggregated = self.aggregate_volume_by_date(records)

        sorted_by_volume = sorted(
            aggregated, key=lambda x: x["total_volume"], reverse=True
        )

        return sorted_by_volume[:n]

    def top_volume_days_ascending(self, records: List[Dict], n: int = 15) -> List[Dict]:
        """
        Retorna los N días con mayor volumen, ordenados ascendentemente.

        Parámetros:
            records: Lista de registros financieros
            n: Número de días a retornar

        Retorna:
            Lista de los N días con mayor volumen, ordenados ascendentemente

        Complejidad: O(n) + O(n log n) = O(n log n)
        """
        top_days = self.top_volume_days(records, n)
        return sorted(top_days, key=lambda x: x["total_volume"])

    def get_volume_statistics(self, records: List[Dict]) -> Dict:
        """
        Calcula estadísticas de volumen agregadas.

        Parámetros:
            records: Lista de registros financieros

        Retorna:
            Diccionario con estadísticas (total, promedio, máximo, mínimo)

        Complejidad: O(n) para recorrer todos los registros
        """
        if not records:
            return {}

        volumes = [r["volume"] for r in records if r.get("volume") is not None]

        if not volumes:
            return {}

        return {
            "total_volume": sum(volumes),
            "average_volume": sum(volumes) / len(volumes),
            "max_volume": max(volumes),
            "min_volume": min(volumes),
            "unique_dates": len(set(r["date"] for r in records)),
        }
