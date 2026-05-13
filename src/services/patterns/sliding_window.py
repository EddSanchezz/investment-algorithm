"""
Sliding Window — Detección de patrones en series temporales financieras.

Patrones implementados:
    1. Días consecutivos al alza
    2. Días consecutivos a la baja
    3. Gap Up
    4. Gap Down
    5. Breakout alcista
    6. Breakout bajista
"""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List


def _history_years(records: List[Dict]) -> float:
    dated_records = [r for r in sorted(records, key=lambda x: x["date"]) if r.get("date")]
    if len(dated_records) < 2:
        return 0.0

    start = datetime.strptime(dated_records[0]["date"], "%Y-%m-%d")
    end = datetime.strptime(dated_records[-1]["date"], "%Y-%m-%d")
    return round((end - start).days / 365.25, 1)


def _empty_pattern_result(
    pattern_name: str,
    formula: str,
    algorithm: str,
    definition: str,
    **extra,
) -> Dict:
    result = {
        "pattern": pattern_name,
        "definition": definition,
        "formula": formula,
        "total_occurrences": 0,
        "by_year": {},
        "dates": [],
        "occurrences": [],
        "last_occurrences": [],
        "algorithm": algorithm,
        "complexity": "O(n)",
        "years": 0.0,
    }
    result.update(extra)
    return result


def _finalize_pattern_result(
    pattern_name: str,
    records: List[Dict],
    occurrences: List[Dict],
    definition: str,
    formula: str,
    algorithm: str,
    **extra,
) -> Dict:
    by_year: Dict[str, int] = defaultdict(int)
    for occurrence in occurrences:
        year = occurrence["date"][:4]
        by_year[year] += 1

    return {
        "pattern": pattern_name,
        "definition": definition,
        "formula": formula,
        "total_occurrences": len(occurrences),
        "by_year": dict(by_year),
        "dates": [occurrence["date"] for occurrence in occurrences],
        "occurrences": occurrences,
        "last_occurrences": occurrences[-5:],
        "algorithm": algorithm,
        "complexity": "O(n)",
        "years": _history_years(records),
        **extra,
    }


def _valid_close_records(records: List[Dict]) -> List[Dict]:
    return [
        record
        for record in sorted(records, key=lambda x: x["date"])
        if record.get("close") is not None
    ]


def detect_consecutive_up(records: List[Dict], min_days: int = 3) -> Dict:
    formula = "$close_i > close_{i-1}$ durante $k$ sesiones consecutivas"
    definition = (
        f"Secuencia de {min_days} incrementos consecutivos donde cada precio de cierre "
        "es superior al del día hábil anterior."
    )
    algorithm = (
        "Ventana deslizante con contador acumulado:\n"
        "1. Recorrer la serie una sola vez\n"
        "2. Incrementar contador si close[i] > close[i-1]\n"
        "3. Registrar una ocurrencia cuando el contador alcanza el mínimo\n"
        "4. Reiniciar el contador cuando la racha se rompe"
    )
    if len(records) < min_days + 1:
        return _empty_pattern_result(
            "Consecutive Up",
            formula,
            algorithm,
            definition,
            min_days=min_days,
        )

    sorted_records = _valid_close_records(records)
    if len(sorted_records) < min_days + 1:
        return _empty_pattern_result(
            "Consecutive Up",
            formula,
            algorithm,
            definition,
            min_days=min_days,
        )

    occurrences = []
    counter = 0

    for index in range(1, len(sorted_records)):
        current_close = sorted_records[index]["close"]
        previous_close = sorted_records[index - 1]["close"]
        if current_close > previous_close:
            counter += 1
            if counter >= min_days:
                start_index = index - counter
                start_close = sorted_records[start_index]["close"]
                change_pct = round(((current_close / start_close) - 1) * 100, 2)
                occurrences.append(
                    {
                        "date": sorted_records[index]["date"],
                        "start_date": sorted_records[start_index]["date"],
                        "end_date": sorted_records[index]["date"],
                        "duration": counter + 1,
                        "change_pct": change_pct,
                    }
                )
        else:
            counter = 0

    return _finalize_pattern_result(
        "Consecutive Up",
        sorted_records,
        occurrences,
        definition,
        formula,
        algorithm,
        min_days=min_days,
    )


def detect_consecutive_down(records: List[Dict], min_days: int = 3) -> Dict:
    formula = "$close_i < close_{i-1}$ durante $k$ sesiones consecutivas"
    definition = (
        f"Secuencia de {min_days} caídas consecutivas donde cada precio de cierre "
        "es inferior al del día hábil anterior."
    )
    algorithm = (
        "Ventana deslizante con contador acumulado sobre cierres decrecientes."
    )
    if len(records) < min_days + 1:
        return _empty_pattern_result(
            "Consecutive Down",
            formula,
            algorithm,
            definition,
            min_days=min_days,
        )

    sorted_records = _valid_close_records(records)
    if len(sorted_records) < min_days + 1:
        return _empty_pattern_result(
            "Consecutive Down",
            formula,
            algorithm,
            definition,
            min_days=min_days,
        )

    occurrences = []
    counter = 0

    for index in range(1, len(sorted_records)):
        current_close = sorted_records[index]["close"]
        previous_close = sorted_records[index - 1]["close"]
        if current_close < previous_close:
            counter += 1
            if counter >= min_days:
                start_index = index - counter
                start_close = sorted_records[start_index]["close"]
                change_pct = round(((current_close / start_close) - 1) * 100, 2)
                occurrences.append(
                    {
                        "date": sorted_records[index]["date"],
                        "start_date": sorted_records[start_index]["date"],
                        "end_date": sorted_records[index]["date"],
                        "duration": counter + 1,
                        "change_pct": change_pct,
                    }
                )
        else:
            counter = 0

    return _finalize_pattern_result(
        "Consecutive Down",
        sorted_records,
        occurrences,
        definition,
        formula,
        algorithm,
        min_days=min_days,
    )


def detect_gap_up(records: List[Dict], threshold: float = 0.02) -> Dict:
    formula = "$open_i > close_{i-1} \\cdot (1 + \\theta)$"
    definition = (
        f"Día donde la apertura supera el cierre previo en al menos {threshold * 100:.1f}%"
    )
    algorithm = "Comparación día contra día anterior con cálculo directo del tamaño del gap."
    if len(records) < 2:
        return _empty_pattern_result(
            "Gap Up",
            formula,
            algorithm,
            definition,
            threshold=threshold,
            threshold_pct=threshold * 100,
            average_gap_pct=0.0,
            max_gap_pct=0.0,
        )

    sorted_records = sorted(records, key=lambda x: x["date"])
    occurrences = []
    gap_sizes = []

    for index in range(1, len(sorted_records)):
        current = sorted_records[index]
        previous = sorted_records[index - 1]
        current_open = current.get("open")
        previous_close = previous.get("close")
        if current_open is None or previous_close is None or previous_close <= 0:
            continue

        gap_ratio = (current_open / previous_close) - 1
        if gap_ratio > threshold:
            gap_pct = round(gap_ratio * 100, 2)
            gap_sizes.append(gap_pct)
            occurrences.append(
                {
                    "date": current["date"],
                    "start_date": previous["date"],
                    "end_date": current["date"],
                    "duration": 1,
                    "gap_pct": gap_pct,
                    "change_pct": gap_pct,
                    "reference_close": round(previous_close, 4),
                    "open_price": round(current_open, 4),
                }
            )

    return _finalize_pattern_result(
        "Gap Up",
        sorted_records,
        occurrences,
        definition,
        formula,
        algorithm,
        threshold=threshold,
        threshold_pct=threshold * 100,
        average_gap_pct=round(sum(gap_sizes) / len(gap_sizes), 2) if gap_sizes else 0.0,
        max_gap_pct=round(max(gap_sizes), 2) if gap_sizes else 0.0,
    )


def detect_gap_down(records: List[Dict], threshold: float = 0.02) -> Dict:
    formula = "$open_i < close_{i-1} \\cdot (1 - \\theta)$"
    definition = (
        f"Día donde la apertura queda por debajo del cierre previo en al menos {threshold * 100:.1f}%"
    )
    algorithm = "Comparación día contra día anterior con cálculo directo del gap bajista."
    if len(records) < 2:
        return _empty_pattern_result(
            "Gap Down",
            formula,
            algorithm,
            definition,
            threshold=threshold,
            threshold_pct=threshold * 100,
            average_gap_pct=0.0,
            max_gap_pct=0.0,
        )

    sorted_records = sorted(records, key=lambda x: x["date"])
    occurrences = []
    gap_sizes = []

    for index in range(1, len(sorted_records)):
        current = sorted_records[index]
        previous = sorted_records[index - 1]
        current_open = current.get("open")
        previous_close = previous.get("close")
        if current_open is None or previous_close is None or previous_close <= 0:
            continue

        gap_ratio = 1 - (current_open / previous_close)
        if gap_ratio > threshold:
            gap_pct = round(gap_ratio * 100, 2)
            gap_sizes.append(gap_pct)
            occurrences.append(
                {
                    "date": current["date"],
                    "start_date": previous["date"],
                    "end_date": current["date"],
                    "duration": 1,
                    "gap_pct": gap_pct,
                    "change_pct": -gap_pct,
                    "reference_close": round(previous_close, 4),
                    "open_price": round(current_open, 4),
                }
            )

    return _finalize_pattern_result(
        "Gap Down",
        sorted_records,
        occurrences,
        definition,
        formula,
        algorithm,
        threshold=threshold,
        threshold_pct=threshold * 100,
        average_gap_pct=round(sum(gap_sizes) / len(gap_sizes), 2) if gap_sizes else 0.0,
        max_gap_pct=round(max(gap_sizes), 2) if gap_sizes else 0.0,
    )


def detect_breakout_up(records: List[Dict], window: int = 20) -> Dict:
    formula = "$close_i > \\max(close_{i-w}, \\ldots, close_{i-1})$"
    definition = (
        f"Cierre que supera el máximo de las {window} sesiones anteriores."
    )
    algorithm = "Ventana deslizante con comparación del cierre actual contra el máximo reciente."
    if len(records) < window + 1:
        return _empty_pattern_result(
            "Breakout Up",
            formula,
            algorithm,
            definition,
            window=window,
        )

    sorted_records = _valid_close_records(records)
    if len(sorted_records) < window + 1:
        return _empty_pattern_result(
            "Breakout Up",
            formula,
            algorithm,
            definition,
            window=window,
        )

    occurrences = []
    for index in range(window, len(sorted_records)):
        history = [record["close"] for record in sorted_records[index - window:index]]
        reference = max(history)
        current_close = sorted_records[index]["close"]
        if current_close > reference:
            change_pct = round(((current_close / reference) - 1) * 100, 2)
            occurrences.append(
                {
                    "date": sorted_records[index]["date"],
                    "start_date": sorted_records[index - window]["date"],
                    "end_date": sorted_records[index]["date"],
                    "duration": window,
                    "change_pct": change_pct,
                    "reference_price": round(reference, 4),
                    "close_price": round(current_close, 4),
                    "window": window,
                }
            )

    return _finalize_pattern_result(
        "Breakout Up",
        sorted_records,
        occurrences,
        definition,
        formula,
        algorithm,
        window=window,
    )


def detect_breakout_down(records: List[Dict], window: int = 20) -> Dict:
    formula = "$close_i < \\min(close_{i-w}, \\ldots, close_{i-1})$"
    definition = (
        f"Cierre que perfora el mínimo de las {window} sesiones anteriores."
    )
    algorithm = "Ventana deslizante con comparación del cierre actual contra el mínimo reciente."
    if len(records) < window + 1:
        return _empty_pattern_result(
            "Breakout Down",
            formula,
            algorithm,
            definition,
            window=window,
        )

    sorted_records = _valid_close_records(records)
    if len(sorted_records) < window + 1:
        return _empty_pattern_result(
            "Breakout Down",
            formula,
            algorithm,
            definition,
            window=window,
        )

    occurrences = []
    for index in range(window, len(sorted_records)):
        history = [record["close"] for record in sorted_records[index - window:index]]
        reference = min(history)
        current_close = sorted_records[index]["close"]
        if current_close < reference:
            change_pct = round(((current_close / reference) - 1) * 100, 2)
            occurrences.append(
                {
                    "date": sorted_records[index]["date"],
                    "start_date": sorted_records[index - window]["date"],
                    "end_date": sorted_records[index]["date"],
                    "duration": window,
                    "change_pct": change_pct,
                    "reference_price": round(reference, 4),
                    "close_price": round(current_close, 4),
                    "window": window,
                }
            )

    return _finalize_pattern_result(
        "Breakout Down",
        sorted_records,
        occurrences,
        definition,
        formula,
        algorithm,
        window=window,
    )


class PatternAnalyzer:
    """Analizador de patrones en series temporales financieras."""

    @staticmethod
    def _filter_symbol(records: List[Dict], symbol: str) -> List[Dict]:
        return [record for record in records if record["symbol"] == symbol.upper()]

    def analyze(
        self,
        records: List[Dict],
        symbol: str,
        pattern: str = "consecutive_up",
        min_days: int = 3,
        threshold: float = 0.02,
        window: int = 20,
    ) -> Dict:
        sym_records = self._filter_symbol(records, symbol)
        if not sym_records:
            return {
                "symbol": symbol.upper(),
                "error": f"No hay datos para {symbol}",
                "pattern": pattern,
            }

        if pattern == "gap_up":
            result = detect_gap_up(sym_records, threshold)
        elif pattern == "gap_down":
            result = detect_gap_down(sym_records, threshold)
        elif pattern == "consecutive_down":
            result = detect_consecutive_down(sym_records, min_days)
        elif pattern == "breakout_up":
            result = detect_breakout_up(sym_records, window)
        elif pattern == "breakout_down":
            result = detect_breakout_down(sym_records, window)
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
        threshold: float = 0.02,
        window: int = 20,
    ) -> Dict:
        if isinstance(symbols, str):
            pattern = symbols
            symbols = None

        if symbols is None:
            symbols = sorted(set(record["symbol"] for record in records))

        results = {}
        for symbol in symbols:
            results[symbol] = self.analyze(
                records,
                symbol,
                pattern,
                min_days,
                threshold,
                window,
            )

        total = sum(
            result.get("total_occurrences", 0)
            for result in results.values()
        )

        return {
            "pattern": pattern,
            "results": results,
            "total_occurrences": total,
            "symbols_analyzed": len(symbols),
        }
