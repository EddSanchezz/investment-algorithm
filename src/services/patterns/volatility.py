"""
Volatility Analyzer — Cálculo de volatilidad y clasificación de riesgo.

Métricas:
    1. Retorno diario: r_i = (close_i - close_{i-1}) / close_{i-1}
    2. Desviación estándar de retornos: σ = √(Σ(r_i - r̄)² / (n-1))
    3. Volatilidad anualizada: σ_anual = σ_diaria × √252

Clasificación de riesgo:
    - Conservador: volatilidad anualizada < 15%
    - Moderado: 15% ≤ volatilidad < 30%
    - Agresivo: volatilidad ≥ 30%

Complejidad: O(n) para todas las operaciones
"""

from typing import List, Dict


def daily_returns(prices: List[float]) -> List[float]:
    """
    Calcula retornos diarios a partir de precios de cierre.

    Fórmula: r_i = (p_i - p_{i-1}) / p_{i-1}

    Parámetros:
        prices: Lista de precios de cierre

    Retorna:
        Lista de retornos diarios (longitud n-1)

    Complejidad: O(n)
    """
    if len(prices) < 2:
        return []
    return [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]


def standard_deviation(values: List[float]) -> float:
    """
    Calcula la desviación estándar muestral.

    Fórmula: s = √(Σ(x_i - x̄)² / (n-1))

    Parámetros:
        values: Lista de valores numéricos

    Retorna:
        Desviación estándar (0 si n < 2)

    Complejidad: O(n)
    """
    n = len(values)
    if n < 2:
        return 0.0

    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / (n - 1)
    return variance ** 0.5


def annualized_volatility(daily_std: float, trading_days: int = 252) -> float:
    """
    Anualiza la volatilidad diaria.

    Fórmula: σ_anual = σ_diaria × √(días_de_negociación)

    Se usan 252 días de negociación como estándar para mercados bursátiles.

    Parámetros:
        daily_std: Desviación estándar de retornos diarios
        trading_days: Días de negociación por año (default: 252)

    Retorna:
        Volatilidad anualizada como decimal (ej: 0.18 = 18%)

    Complejidad: O(1)
    """
    return daily_std * (trading_days ** 0.5)


def classify_risk(annual_vol: float) -> str:
    """
    Clasifica el nivel de riesgo según la volatilidad anualizada.

    Categorías:
        - Conservador: vol < 15% (0.15)
        - Moderado: 15% ≤ vol < 30% (0.15 a 0.30)
        - Agresivo: vol ≥ 30% (0.30)

    Parámetros:
        annual_vol: Volatilidad anualizada (decimal)

    Retorna:
        "conservador", "moderado", o "agresivo"
    """
    if annual_vol < 0.15:
        return "conservador"
    elif annual_vol < 0.30:
        return "moderado"
    else:
        return "agresivo"


class VolatilityAnalyzer:
    """
    Analizador de volatilidad y riesgo para activos financieros.

    Calcula métricas de volatilidad y clasifica cada activo según
    su nivel de riesgo basado exclusivamente en criterios algorítmicos.

    Uso:
        analyzer = VolatilityAnalyzer()
        result = analyzer.analyze(records, "VOO")
        ranking = analyzer.ranking(records)
    """

    TRADING_DAYS = 252

    @staticmethod
    def _filter_symbol(records: List[Dict], symbol: str) -> List[float]:
        """Extrae precios de cierre para un símbolo, ordenados por fecha. O(n)."""
        sym_records = [r for r in records if r["symbol"] == symbol.upper()]
        sym_records.sort(key=lambda x: x["date"])
        return [r["close"] for r in sym_records if r.get("close") is not None]

    def analyze(self, records: List[Dict], symbol: str) -> Dict:
        """
        Calcula métricas de volatilidad para un símbolo.

        Parámetros:
            records: Lista de registros financieros unificados
            symbol: Símbolo del activo

        Retorna:
            Diccionario con métricas de volatilidad y clasificación de riesgo

        Complejidad: O(n) para filtrado + O(n) para retornos + O(n) para std = O(n)
        """
        prices = self._filter_symbol(records, symbol)

        if len(prices) < 5:
            return {
                "symbol": symbol.upper(),
                "error": f"Datos insuficientes para {symbol} ({len(prices)} precios)",
            }

        returns = daily_returns(prices)
        std_daily = standard_deviation(returns)
        vol_annual = annualized_volatility(std_daily, self.TRADING_DAYS)
        risk_category = classify_risk(vol_annual)

        mean_return = sum(returns) / len(returns) if returns else 0.0

        return {
            "symbol": symbol.upper(),
            "daily_std": round(std_daily, 6),
            "annualized_volatility": round(vol_annual, 6),
            "annualized_volatility_pct": round(vol_annual * 100, 2),
            "mean_daily_return": round(mean_return, 6),
            "mean_daily_return_pct": round(mean_return * 100, 4),
            "n_returns": len(returns),
            "n_prices": len(prices),
            "risk_category": risk_category,
            "trading_days": self.TRADING_DAYS,
            "formula": (
                "σ_anual = σ_diaria × √252\n"
                "donde σ_diaria = √(Σ(r_i - r̄)² / (n-1))"
            ),
            "complexity": "O(n)",
        }

    def ranking(self, records: List[Dict], symbols: List[str] = None) -> Dict:
        """
        Genera un ranking completo de todos los activos ordenados por volatilidad.

        Parámetros:
            records: Lista de registros financieros unificados
            symbols: Lista de símbolos (default: todos disponibles)

        Retorna:
            Diccionario con ranking ordenado y estadísticas del portafolio

        Complejidad: O(s × n + s log s) donde s = número de símbolos
        """
        if symbols is None:
            symbols = sorted(set(r["symbol"] for r in records))

        results = []
        for sym in symbols:
            analysis = self.analyze(records, sym)
            if "error" not in analysis:
                results.append(analysis)

        results.sort(key=lambda x: x["annualized_volatility"])

        categories = {"conservador": 0, "moderado": 0, "agresivo": 0}
        for r in results:
            cat = r["risk_category"]
            if cat in categories:
                categories[cat] += 1

        vols = [r["annualized_volatility"] for r in results]
        avg_vol = sum(vols) / len(vols) if vols else 0.0
        min_vol = min(vols) if vols else 0.0
        max_vol = max(vols) if vols else 0.0

        return {
            "ranking": results,
            "summary": {
                "total_symbols": len(results),
                "average_volatility_pct": round(avg_vol * 100, 2),
                "min_volatility": {"symbol": results[0]["symbol"], "vol_pct": results[0]["annualized_volatility_pct"]} if results else None,
                "max_volatility": {"symbol": results[-1]["symbol"], "vol_pct": results[-1]["annualized_volatility_pct"]} if results else None,
                "categories": categories,
            },
            "complexity": "O(s × n + s log s)",
        }
