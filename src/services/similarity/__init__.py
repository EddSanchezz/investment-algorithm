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

    def compare(
        self, records: List[Dict], symbol1: str, symbol2: str
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
        results_info = {}

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
