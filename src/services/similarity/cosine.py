"""
Similitud por Coseno para Series Temporales Financieras.

Fórmula:
    cos(θ) = (x · y) / (||x|| · ||y||) = Σ(xᵢ · yᵢ) / √(Σxᵢ²) · √(Σyᵢ²)

Donde:
    x, y = vectores de retornos diarios de dos activos
    x · y = producto punto
    ||x|| = norma euclidiana (magnitud del vector)

Interpretación:
    - 1.0: Vectores en la misma dirección (misma proporción de retornos)
    - 0.0: Vectores ortogonales (sin relación direccional)
    - -1.0: Vectores en dirección opuesta (retornos inversamente proporcionales)
    - A diferencia de Pearson, la similitud por coseno NO centra los datos
      (no resta la media), por lo que mide similitud en magnitud y dirección.

Aplicación:
    - Comparar perfiles de retornos diarios
    - Identificar activos con patrones de retorno similares
    - Útil cuando la magnitud de los retornos importa (no solo la correlación)

Complejidad computacional:
    Temporal: O(n) — una sola pasada para producto punto y normas
    Espacial: O(1) — solo acumuladores
"""

from typing import List
import math


def cosine_similarity(series1: List[float], series2: List[float]) -> dict:
    """
    Calcula la similitud por coseno entre dos vectores de retornos.

    Parámetros:
        series1: Primera serie de retornos diarios
        series2: Segunda serie de retornos diarios

    Retorna:
        Diccionario con:
            - similarity: similitud por coseno
            - dot_product: producto punto
            - norm1, norm2: normas de cada vector
            - angle_degrees: ángulo entre vectores en grados
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
    if len(series1) == 0:
        return {
            "similarity": None,
            "dot_product": 0.0,
            "norm1": 0.0,
            "norm2": 0.0,
            "n": 0,
            "formula": "$cos(\\theta) = \\frac{x \\cdot y}{||x|| \\cdot ||y||}$",
            "complexity": "O(n)",
            "description": "Similitud por Coseno",
        }

    n = len(series1)
    dot_product = 0.0
    norm1 = 0.0
    norm2 = 0.0

    for i in range(n):
        dot_product += series1[i] * series2[i]
        norm1 += series1[i] * series1[i]
        norm2 += series2[i] * series2[i]

    norm1_sqrt = norm1 ** 0.5
    norm2_sqrt = norm2 ** 0.5

    if norm1_sqrt == 0 or norm2_sqrt == 0:
        clamped = 0.0
        angle_degrees = 90.0
    else:
        similarity = dot_product / (norm1_sqrt * norm2_sqrt)
        clamped = max(-1.0, min(1.0, similarity))
        angle_degrees = round(math.degrees(math.acos(clamped)), 4)

    return {
        "similarity": round(clamped, 6),
        "dot_product": round(dot_product, 6),
        "norm1": round(norm1_sqrt, 6),
        "norm2": round(norm2_sqrt, 6),
        "angle_degrees": angle_degrees,
        "n": n,
        "min_possible": -1.0,
        "max_possible": 1.0,
        "interpretation": _interpret_cosine(similarity, angle_degrees),
        "formula": "$cos(\\theta) = \\frac{x \\cdot y}{||x|| \\cdot ||y||}$",
        "complexity": "O(n)",
        "description": "Similitud por Coseno",
    }


def _interpret_cosine(sim: float, angle: float) -> str:
    """Interpreta el valor de similitud por coseno."""
    if sim >= 0.9:
        desc = "casi idéntica dirección"
    elif sim >= 0.7:
        desc = "dirección muy similar"
    elif sim >= 0.5:
        desc = "dirección moderadamente similar"
    elif sim >= 0.0:
        desc = "dirección ligeramente similar"
    elif sim >= -0.5:
        desc = "dirección ligeramente opuesta"
    else:
        desc = "dirección fuertemente opuesta"

    return (
        f"Similitud por coseno = {sim:.4f} (ángulo = {angle:.1f}°). "
        f"Los vectores de retornos tienen una {desc}."
    )
