"""
Sliding Window — Detección de patrones en series temporales financieras.

Patrones implementados:
    1. Días consecutivos al alza (Consecutive Up)
       Define: secuencia de N días donde close > close anterior
       Algoritmo: ventana deslizante con contador acumulado O(n)

    2. Gap Up
       Define: día donde open > prev_close × (1 + umbral)
       Algoritmo: comparación día contra día anterior O(n)

Ambos patrones se detectan mediante una ventana deslizante que recorre
el historial de precios una sola vez (O(n)), manteniendo un contador
del estado actual de la secuencia.
"""

from typing import List, Dict
from collections import defaultdict


def detect_consecutive_up(
    records: List[Dict], min_days: int = 3
) -> Dict:
    """
    Detecta secuencias de días consecutivos al alza usando ventana deslizante.

    Algoritmo:
        1. Inicializar contador = 0
        2. Para cada día i en la serie:
           - Si close[i] > close[i-1]: contador++
           - Si no: contador = 0
           - Si contador >= min_days: patrón detectado (en día i)
        3. Retornar fechas de detección + frecuencia por año

    Complejidad: O(n) — una sola pasada con contador acumulado
    Espacial: O(k) donde k = número de ocurrencias

    Parámetros:
        records: Lista de registros financieros (de un solo símbolo,
                 ordenados por fecha ascendente)
        min_days: Número mínimo de días consecutivos al alza (default: 3)

    Retorna:
        Diccionario con:
            - pattern: nombre del patrón
            - min_days: días consecutivos requeridos
            - total_occurrences: número total de ocurrencias
            - by_year: {año: ocurrencias}
            - dates: lista de fechas de detección
            - last_occurrences: últimas 5 fechas de detección
            - algorithm: descripción del algoritmo
            - complexity: O(n)
    """
    if len(records) < min_days + 1:
        return {
            "pattern": "Consecutive Up",
            "min_days": min_days,
            "total_occurrences": 0,
            "by_year": {},
            "dates": [],
            "last_occurrences": [],
            "algorithm": "Ventana deslizante con contador acumulado",
            "complexity": "O(n)",
        }

    sorted_records = sorted(records, key=lambda x: x["date"])
    prices = []
    dates = []
    for r in sorted_records:
        c = r.get("close")
        if c is not None:
            prices.append(c)
            dates.append(r["date"])

    if len(prices) < min_days + 1:
        return {
            "pattern": "Consecutive Up",
            "min_days": min_days,
            "total_occurrences": 0,
            "by_year": {},
            "dates": [],
            "last_occurrences": [],
            "algorithm": "Ventana deslizante con contador acumulado",
            "complexity": "O(n)",
        }

    counter = 0
    detection_dates = []

    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            counter += 1
            if counter >= min_days:
                detection_dates.append(dates[i])
        else:
            counter = 0

    by_year: Dict[str, int] = defaultdict(int)
    for d in detection_dates:
        year = d[:4]
        by_year[year] += 1

    return {
        "pattern": "Consecutive Up",
        "min_days": min_days,
        "definition": f"Secuencia de {min_days} días donde el precio de cierre "
                       f"es superior al del día anterior",
        "total_occurrences": len(detection_dates),
        "by_year": dict(by_year),
        "dates": detection_dates,
        "last_occurrences": detection_dates[-5:] if detection_dates else [],
        "algorithm": (
            "Ventana deslizante con contador acumulado:\n"
            "1. Inicializar contador = 0\n"
            "2. Por cada día i: si close[i] > close[i-1], contador++\n"
            "3. Si contador alcanza min_days, registrar detección\n"
            "4. Si la secuencia se rompe, reiniciar contador = 0\n"
            "Complejidad: O(n) — una sola pasada"
        ),
        "complexity": "O(n)",
    }


def detect_gap_up(
    records: List[Dict], threshold: float = 0.02
) -> Dict:
    """
    Detecta patrones de Gap Up usando ventana deslizante.

    Un Gap Up ocurre cuando el precio de apertura es significativamente
    superior al precio de cierre del día anterior:
        open[i] > prev_close[i-1] × (1 + threshold)

    Algoritmo:
        1. Para cada día i (desde i=1):
           - Calcular ratio = open[i] / close[i-1]
           - Si ratio > 1 + threshold: Gap Up detectado
        2. Retornar fechas + estadísticas

    Complejidad: O(n) — una sola pasada
    Espacial: O(k) donde k = número de ocurrencias

    Parámetros:
        records: Lista de registros financieros (un solo símbolo, ordenados)
        threshold: Umbral de gap (default: 0.02 = 2%)

    Retorna:
        Diccionario con detecciones, estadísticas y análisis
    """
    if len(records) < 2:
        return {
            "pattern": "Gap Up",
            "threshold": threshold,
            "total_occurrences": 0,
            "by_year": {},
            "dates": [],
            "last_occurrences": [],
            "algorithm": "Comparación día contra día anterior",
            "complexity": "O(n)",
        }

    sorted_records = sorted(records, key=lambda x: x["date"])
    detection_dates = []
    gap_sizes = []

    for i in range(1, len(sorted_records)):
        curr = sorted_records[i]
        prev = sorted_records[i - 1]

        curr_open = curr.get("open")
        prev_close = prev.get("close")

        if curr_open is not None and prev_close is not None and prev_close > 0:
            ratio = curr_open / prev_close
            if ratio > 1 + threshold:
                detection_dates.append(curr["date"])
                gap_sizes.append(round((ratio - 1) * 100, 2))

    by_year: Dict[str, int] = defaultdict(int)
    for d in detection_dates:
        year = d[:4]
        by_year[year] += 1

    avg_gap = round(sum(gap_sizes) / len(gap_sizes), 2) if gap_sizes else 0.0
    max_gap = round(max(gap_sizes), 2) if gap_sizes else 0.0

    return {
        "pattern": "Gap Up",
        "threshold": threshold,
        "threshold_pct": threshold * 100,
        "definition": f"Día donde open > prev_close × (1 + {threshold}) "
                       f"= apertura superior al cierre anterior en al menos "
                       f"{threshold * 100:.0f}%",
        "total_occurrences": len(detection_dates),
        "by_year": dict(by_year),
        "dates": detection_dates,
        "last_occurrences": detection_dates[-5:] if detection_dates else [],
        "average_gap_pct": avg_gap,
        "max_gap_pct": max_gap,
        "algorithm": (
            "Comparación día contra día anterior:\n"
            "1. Por cada día i: calcular ratio = open[i] / close[i-1]\n"
            "2. Si ratio > 1 + threshold: Gap Up detectado\n"
            "3. Calcular tamaño del gap como porcentaje\n"
            "Complejidad: O(n) — una sola pasada"
        ),
        "complexity": "O(n)",
    }


class PatternAnalyzer:
    """
    Analizador de patrones en series temporales financieras.

    Une los métodos de detección de patrones en una interfaz unificada
    que trabaja con el formato de registros del pipeline ETL.

    Uso:
        analyzer = PatternAnalyzer()
        result = analyzer.analyze(records, "VOO", pattern="consecutive_up", min_days=3)
        result = analyzer.analyze(records, "VOO", pattern="gap_up", threshold=0.02)
    """

    @staticmethod
    def _filter_symbol(records: List[Dict], symbol: str) -> List[Dict]:
        """Filtra registros por símbolo. O(n)."""
        return [r for r in records if r["symbol"] == symbol.upper()]

    def analyze(
        self,
        records: List[Dict],
        symbol: str,
        pattern: str = "consecutive_up",
        min_days: int = 3,
        threshold: float = 0.02,
    ) -> Dict:
        """
        Analiza un patrón específico para un símbolo.

        Parámetros:
            records: Lista de registros financieros unificados
            symbol: Símbolo del activo
            pattern: Tipo de patrón ("consecutive_up" o "gap_up")
            min_days: Días mínimos (solo para consecutive_up)
            threshold: Umbral (solo para gap_up)

        Retorna:
            Resultado del análisis del patrón
        """
        sym_records = self._filter_symbol(records, symbol)
        if not sym_records:
            return {
                "symbol": symbol.upper(),
                "error": f"No hay datos para {symbol}",
                "pattern": pattern,
            }

        if pattern == "gap_up":
            result = detect_gap_up(sym_records, threshold)
        else:
            result = detect_consecutive_up(sym_records, min_days)

        result["symbol"] = symbol.upper()
        result["records_analyzed"] = len(sym_records)
        return result

    def analyze_all(
        self,
        records: List[Dict],
        symbols: List[str] = None,
        pattern: str = "consecutive_up",
        min_days: int = 3,
    ) -> Dict:
        """
        Analiza un patrón para todos los símbolos del portafolio.

        Parámetros:
            records: Lista de registros financieros unificados
            symbols: Lista de símbolos (default: todos)
            pattern: Tipo de patrón
            min_days: Días mínimos

        Retorna:
            Dict con resultados por símbolo y resumen general
        """
        if symbols is None:
            symbols = sorted(set(r["symbol"] for r in records))

        results = {}
        for sym in symbols:
            results[sym] = self.analyze(records, sym, pattern, min_days)

        total = sum(
            r["total_occurrences"]
            for r in results.values()
            if "total_occurrences" in r
        )

        return {
            "pattern": pattern,
            "results": results,
            "total_occurrences": total,
            "symbols_analyzed": len(symbols),
        }
