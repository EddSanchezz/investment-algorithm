"""
Módulo de Algoritmos de Similitud para Series Temporales Financieras.

Implementa 4 algoritmos de similitud entre series de tiempo:
- Distancia Euclidiana
- Correlación de Pearson
- Dynamic Time Warping (DTW)
- Similitud por Coseno

Cada algoritmo incluye:
- Fórmula matemática completa
- Descripción algorítmica detallada
- Análisis de complejidad computacional (Big-O)
"""

from itertools import combinations
from typing import List, Dict, Tuple, Optional
from src.services.similarity.euclidean import euclidean_distance
from src.services.similarity.pearson import pearson_correlation
from src.services.similarity.dtw import dtw_distance
from src.services.similarity.cosine import cosine_similarity


class SimilarityAnalyzer:
    """
    Analizador de similitud entre pares de activos financieros.

    Calcula las 4 métricas de similitud para un par de símbolos,
    alineando automáticamente las series temporales por fecha.

    Uso:
        analyzer = SimilarityAnalyzer()
        result = analyzer.compare(records, "VOO", "SPY")
        # result = {
        #     "symbol1": "VOO",
        #     "symbol2": "SPY",
        #     "euclidean": {...},
        #     "pearson": {...},
        #     "dtw": {...},
        #     "cosine": {...},
        #     "common_dates": n,
        #     "series": {...}
        # }
    """

    @staticmethod
    def _extract_series(
        records: List[Dict], symbol1: str, symbol2: str
    ) -> Optional[Tuple[List[float], List[float], List[str]]]:
        """
        Extrae y alinea dos series de precios de cierre por fecha común.

        Parámetros:
            records: Lista de registros financieros
            symbol1: Primer símbolo
            symbol2: Segundo símbolo

        Retorna:
            Tupla (series1, series2, fechas_comunes) o None si no hay datos suficientes

        Complejidad: O(n) donde n = total de registros
        """
        prices1: Dict[str, float] = {}
        prices2: Dict[str, float] = {}

        for r in records:
            sym = r["symbol"]
            close = r.get("close")
            if close is None:
                continue
            date = r["date"]
            if sym == symbol1:
                prices1[date] = close
            elif sym == symbol2:
                prices2[date] = close

        common_dates = sorted(set(prices1.keys()) & set(prices2.keys()))
        if len(common_dates) < 2:
            return None

        series1 = [prices1[d] for d in common_dates]
        series2 = [prices2[d] for d in common_dates]
        return series1, series2, common_dates

    @staticmethod
    def _returns(prices: List[float]) -> List[float]:
        """
        Calcula retornos diarios a partir de precios.
        r_i = (p_i - p_{i-1}) / p_{i-1}

        Complejidad: O(n)
        """
        if len(prices) < 2:
            return []
        return [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]

    @staticmethod
    def _unique_symbols(symbols: List[str]) -> List[str]:
        unique = []
        seen = set()
        for symbol in symbols:
            upper = symbol.upper()
            if upper not in seen:
                seen.add(upper)
                unique.append(upper)
        return unique

    @staticmethod
    def _slice_tail(*series: List, max_points: Optional[int] = None) -> Tuple[List, ...]:
        if max_points is None or max_points <= 0:
            return tuple(series)
        return tuple(s[-max_points:] if len(s) > max_points else s for s in series)

    @staticmethod
    def _build_symbol_price_maps(records: List[Dict], symbols: List[str]) -> Dict[str, Dict[str, float]]:
        symbol_maps = {symbol: {} for symbol in symbols}
        valid_symbols = set(symbols)

        for record in records:
            symbol = record["symbol"].upper()
            close = record.get("close")
            if symbol not in valid_symbols or close is None:
                continue
            symbol_maps[symbol][record["date"]] = close

        return symbol_maps

    @staticmethod
    def _normalize_series(prices: List[Optional[float]]) -> List[Optional[float]]:
        base = next((price for price in prices if price not in (None, 0)), None)
        if base is None:
            return [None for _ in prices]
        return [round((price / base) * 100, 4) if price is not None else None for price in prices]

    def _build_group_series(
        self,
        records: List[Dict],
        symbols: List[str],
        max_points: Optional[int] = None,
    ) -> Dict:
        symbol_maps = self._build_symbol_price_maps(records, symbols)
        all_dates = sorted({date for prices in symbol_maps.values() for date in prices})
        if max_points is not None and max_points > 0 and len(all_dates) > max_points:
            all_dates = all_dates[-max_points:]

        series = {"dates": all_dates}
        normalized = {"dates": all_dates}
        coverage = {}

        for symbol in symbols:
            values = [symbol_maps[symbol].get(date) for date in all_dates]
            series[symbol] = values
            normalized[symbol] = self._normalize_series(values)
            coverage[symbol] = sum(value is not None for value in values)

        return {
            "series": series,
            "normalized_series": normalized,
            "coverage": coverage,
        }

    def compare(
        self,
        records: List[Dict],
        symbol1: str,
        symbol2: str,
        max_points: Optional[int] = None,
    ) -> Dict:
        """
        Calcula las 4 métricas de similitud entre dos activos.

        Parámetros:
            records: Lista de registros financieros unificados
            symbol1: Primer símbolo (ej: "VOO")
            symbol2: Segundo símbolo (ej: "SPY")

        Retorna:
            Diccionario con resultados de cada algoritmo + datos para gráfica

        Complejidad total: O(n + n*m) donde n = longitud de serie, m = warp en DTW
        """
        result = self._extract_series(records, symbol1.upper(), symbol2.upper())
        if result is None:
            return {
                "error": f"No hay suficientes datos comunes para {symbol1} y {symbol2}",
                "symbol1": symbol1.upper(),
                "symbol2": symbol2.upper(),
                "common_dates": 0,
            }

        prices1, prices2, dates = result
        prices1, prices2, dates = self._slice_tail(
            prices1, prices2, dates, max_points=max_points
        )
        returns1 = self._returns(prices1)
        returns2 = self._returns(prices2)

        results = {
            "symbol1": symbol1.upper(),
            "symbol2": symbol2.upper(),
            "common_dates": len(dates),
            "series": {
                "dates": dates,
                symbol1.upper(): prices1,
                symbol2.upper(): prices2,
            },
        }

        results["euclidean"] = euclidean_distance(prices1, prices2)
        results["pearson"] = pearson_correlation(returns1, returns2)
        results["dtw"] = dtw_distance(prices1, prices2)
        results["cosine"] = cosine_similarity(returns1, returns2)

        return results

    def compare_many(
        self,
        records: List[Dict],
        symbols: List[str],
        max_points: int = 252,
    ) -> Dict:
        symbols = self._unique_symbols(symbols)
        if len(symbols) < 2:
            return {
                "error": "Seleccione al menos 2 activos para comparar.",
                "symbols": symbols,
            }

        group_series = self._build_group_series(records, symbols, max_points=max_points)
        dates = group_series["series"].get("dates", [])
        if len(dates) < 2:
            return {
                "error": "No hay suficientes fechas para construir una comparación multi-activo.",
                "symbols": symbols,
            }

        pairwise = []
        matrix_index = {symbol: index for index, symbol in enumerate(symbols)}
        matrix = [[1.0 if i == j else 0.0 for j in range(len(symbols))] for i in range(len(symbols))]

        for symbol1, symbol2 in combinations(symbols, 2):
            comparison = self.compare(
                records,
                symbol1,
                symbol2,
                max_points=max_points,
            )
            if "error" in comparison:
                continue

            pair = {
                "pair": f"{symbol1}-{symbol2}",
                "symbol1": symbol1,
                "symbol2": symbol2,
                "common_dates": comparison["common_dates"],
                "euclidean_distance": comparison["euclidean"].get("distance"),
                "pearson_correlation": comparison["pearson"].get("correlation"),
                "dtw_normalized_distance": comparison["dtw"].get("normalized_distance"),
                "cosine_similarity": comparison["cosine"].get("similarity"),
            }
            pairwise.append(pair)

            correlation = pair["pearson_correlation"]
            if correlation is not None:
                i = matrix_index[symbol1]
                j = matrix_index[symbol2]
                matrix[i][j] = round(correlation, 4)
                matrix[j][i] = matrix[i][j]

        return {
            "mode": "group",
            "symbols": symbols,
            "window_points": max_points,
            "series": group_series["series"],
            "normalized_series": group_series["normalized_series"],
            "coverage": group_series["coverage"],
            "pairwise": pairwise,
            "correlation_matrix": {
                "symbols": symbols,
                "matrix": matrix,
            },
        }

    def compute_correlation_matrix(
        self, records: List[Dict], symbols: List[str]
    ) -> Dict:
        """
        Calcula la matriz de correlación de Pearson para un conjunto de símbolos.

        Parámetros:
            records: Lista de registros financieros unificados
            symbols: Lista de símbolos a incluir

        Retorna:
            Dict con matriz de correlación y lista de símbolos

        Complejidad: O(s² × n) donde s = número de símbolos, n = longitud de series
        """
        n = len(symbols)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    cmp = self.compare(records, symbols[i], symbols[j])
                    r = cmp.get("pearson", {})
                    val = r.get("correlation") if isinstance(r, dict) else None
                    if val is not None:
                        matrix[i][j] = round(val, 4)
                        matrix[j][i] = matrix[i][j]

        return {
            "symbols": symbols,
            "matrix": matrix,
        }
