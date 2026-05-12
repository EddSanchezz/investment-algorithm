"""
Distancia Euclidiana para Series Temporales Financieras.

Fórmula:
    d(x, y) = √( Σ(xᵢ - yᵢ)² / n )

Donde:
    x, y = series de precios normalizados de dos activos
    n = número de observaciones

Interpretación:
    - 0 ≤ d < ∞
    - 0 = series idénticas
    - Valores más altos indican mayor disimilitud
    - Sensible a la escala: se recomienda normalizar las series

Aplicación:
    - Comparación de precios normalizados (misma escala)
    - Comparación de retornos diarios
    - Línea base para otras métricas de similitud

Complejidad computacional:
    Temporal: O(n) — una sola pasada para calcular diferencias al cuadrado
    Espacial: O(1) — solo acumuladores
"""

from typing import List
import math


def _validate_series(series1: List[float], series2: List[float]) -> None:
    """Valida que dos series tengan la misma longitud. Lanza ValueError si no."""
    if len(series1) != len(series2):
        raise ValueError(
            f"Las series deben tener la misma longitud: "
            f"{len(series1)} vs {len(series2)}"
        )


def euclidean_distance(series1: List[float], series2: List[float]) -> dict:
    """
    Calcula la distancia euclidiana normalizada entre dos series.

    La distancia se normaliza dividiendo por n para hacerla independiente
    de la longitud de las series.

    Parámetros:
        series1: Primera serie de valores (precios o retornos)
        series2: Segunda serie de valores (precios o retornos)

    Retorna:
        Diccionario con:
            - distance: distancia euclidiana normalizada
            - raw_distance: distancia sin normalizar
            - n: número de observaciones
            - formula: representación de la fórmula
            - complexity: análisis de complejidad

    Complejidad: O(n) donde n = longitud de las series
    """
    _validate_series(series1, series2)
    if len(series1) == 0:
        return {
            "distance": None,
            "raw_distance": None,
            "n": 0,
            "formula": "$d(x,y) = \\sqrt{\\frac{1}{n}\\sum_{i=1}^{n}(x_i - y_i)^2}$",
            "complexity": "O(n)",
            "description": "Distancia Euclidiana Normalizada",
        }

    n = len(series1)
    sum_squared_diff = 0.0
    any_valid = False

    for i in range(n):
        a = series1[i]
        b = series2[i]
        if a is None or b is None or (isinstance(a, float) and math.isnan(a)) or (isinstance(b, float) and math.isnan(b)):
            continue
        diff = a - b
        sum_squared_diff += diff * diff
        any_valid = True

    if not any_valid:
        sum_squared_diff = 0.0

    raw_distance = sum_squared_diff ** 0.5
    normalized_distance = (sum_squared_diff / n) ** 0.5

    return {
        "distance": round(normalized_distance, 6),
        "raw_distance": round(raw_distance, 6),
        "n": n,
        "min_possible": 0.0,
        "max_possible": None,
        "interpretation": (
            "0 = series idénticas. "
            "Valores más altos indican mayor disimilitud."
        ),
        "formula": "$d(x,y) = \\sqrt{\\frac{1}{n}\\sum_{i=1}^{n}(x_i - y_i)^2}$",
        "complexity": "O(n)",
        "description": "Distancia Euclidiana Normalizada",
    }
