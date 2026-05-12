"""
Correlación de Pearson para Series Temporales Financieras.

Fórmula:
    r = Σ((xᵢ - x̄)(yᵢ - ȳ)) / √(Σ(xᵢ - x̄)² · Σ(yᵢ - ȳ)²)

Donde:
    x, y = retornos diarios de dos activos
    x̄, ȳ = medias de cada serie

Interpretación:
    - 1.0: Correlación perfecta positiva (se mueven juntos)
    - 0.0: Sin correlación lineal
    - -1.0: Correlación perfecta negativa (se mueven en direcciones opuestas)
    - En finanzas, r > 0.7 se considera alta correlación
    - r < 0.3 se considera baja correlación

Aplicación:
    - Medir relación lineal entre retornos de activos
    - Construcción de portafolios diversificados (buscar baja correlación)
    - Identificar activos redundantes (alta correlación)

Complejidad computacional:
    Temporal: O(n) — filtro NaN + media + covarianza/varianzas = 3 pasadas O(n)
    Espacial: O(n) — listas filtradas temporales
"""

from typing import List
import math


def pearson_correlation(series1: List[float], series2: List[float]) -> dict:
    """
    Calcula el coeficiente de correlación de Pearson entre dos series de retornos.

    Parámetros:
        series1: Primera serie de retornos diarios
        series2: Segunda serie de retornos diarios

    Retorna:
        Diccionario con:
            - correlation: coeficiente r de Pearson
            - covariance: covarianza entre las series
            - variance1, variance2: varianzas individuales
            - n: número de observaciones
            - formula: representación de la fórmula
            - complexity: análisis de complejidad

    Complejidad: O(n) donde n = longitud de las series
    """
    if len(series1) != len(series2):
        raise ValueError(
            f"Las series deben tener la misma longitud: "
            f"{len(series1)} vs {len(series2)}"
        )
    if len(series1) < 3:
        return {
            "correlation": None,
            "n": len(series1),
            "formula": "$r = \\frac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}"
                       "{\\sqrt{\\sum(x_i - \\bar{x})^2 \\cdot \\sum(y_i - \\bar{y})^2}}$",
            "complexity": "O(n)",
            "description": "Correlación de Pearson",
            "error": "Se necesitan al menos 3 observaciones",
        }

    n = len(series1)

    filtered_s1 = []
    filtered_s2 = []
    for i in range(n):
        a = series1[i]
        b = series2[i]
        invalid = (a is None or b is None or
                   (isinstance(a, float) and math.isnan(a)) or
                   (isinstance(b, float) and math.isnan(b)))
        if not invalid:
            filtered_s1.append(a)
            filtered_s2.append(b)

    if len(filtered_s1) < 3:
        return {
            "correlation": None,
            "n": len(filtered_s1),
            "formula": "$r = \\frac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}"
                       "{\\sqrt{\\sum(x_i - \\bar{x})^2 \\cdot \\sum(y_i - \\bar{y})^2}}$",
            "complexity": "O(n)",
            "description": "Correlación de Pearson",
            "error": "Se necesitan al menos 3 observaciones válidas (sin NaN)",
        }

    n = len(filtered_s1)

    mean1 = sum(filtered_s1) / n
    mean2 = sum(filtered_s2) / n

    cov = 0.0
    var1 = 0.0
    var2 = 0.0

    for i in range(n):
        d1 = filtered_s1[i] - mean1
        d2 = filtered_s2[i] - mean2
        cov += d1 * d2
        var1 += d1 * d1
        var2 += d2 * d2

    if var1 == 0 or var2 == 0:
        return {
            "correlation": 0.0,
            "covariance": 0.0,
            "variance1": round(var1 / (n - 1), 6),
            "variance2": round(var2 / (n - 1), 6),
            "n": n,
            "formula": "$r = \\frac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}"
                       "{\\sqrt{\\sum(x_i - \\bar{x})^2 \\cdot \\sum(y_i - \\bar{y})^2}}$",
            "complexity": "O(n)",
            "description": "Correlación de Pearson",
            "interpretation": "Varianza cero en una o ambas series. No es posible calcular correlación.",
        }

    r = cov / ((var1 * var2) ** 0.5)
    r = max(-1.0, min(1.0, r))

    return {
        "correlation": round(r, 6),
        "covariance": round(cov / (n - 1), 6),
        "variance1": round(var1 / (n - 1), 6),
        "variance2": round(var2 / (n - 1), 6),
        "n": n,
        "min_possible": -1.0,
        "max_possible": 1.0,
        "interpretation": _interpret_correlation(r),
        "formula": "$r = \\frac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}"
                   "{\\sqrt{\\sum(x_i - \\bar{x})^2 \\cdot \\sum(y_i - \\bar{y})^2}}$",
        "complexity": "O(n)",
        "description": "Correlación de Pearson",
    }


def _interpret_correlation(r: float) -> str:
    """Interpreta el valor de correlación."""
    abs_r = abs(r)
    if abs_r >= 0.9:
        strength = "muy fuerte"
    elif abs_r >= 0.7:
        strength = "fuerte"
    elif abs_r >= 0.5:
        strength = "moderada"
    elif abs_r >= 0.3:
        strength = "débil"
    else:
        strength = "muy débil o nula"

    direction = "positiva" if r >= 0 else "negativa"
    return (
        f"Correlación {direction} {strength} (r = {r:.4f}). "
        f"Los activos {'se mueven en la misma dirección' if r >= 0 else 'se mueven en direcciones opuestas'}."
    )
