"""
Indicadores Técnicos — Cálculos algorítmicos para análisis técnico.
Independiente de Flask para evitar importación circular.
"""


def simple_moving_average(prices: list, window: int) -> list:
    """
    Calcula la media móvil simple (SMA) para una ventana dada.

    Algoritmo: usa suma acumulativa para O(n).
    SMA[i] = (cumsum[i] - cumsum[i - window]) / window

    Parámetros:
        prices: Lista de precios ordenados por fecha
        window: Tamaño de la ventana

    Retorna:
        Lista del mismo largo con SMA en cada posición (None para primeros window-1)

    Complejidad: O(n) — una pasada con suma acumulativa
    """
    if not prices:
        return []

    if len(prices) < window:
        return [None] * len(prices)

    cumsum = [0.0] * (len(prices) + 1)
    valid_count = [0] * (len(prices) + 1)
    for i in range(len(prices)):
        val = prices[i]
        if val is not None:
            cumsum[i + 1] = cumsum[i] + val
            valid_count[i + 1] = valid_count[i] + 1
        else:
            cumsum[i + 1] = cumsum[i]
            valid_count[i + 1] = valid_count[i]

    result = [None] * (window - 1)
    for i in range(window - 1, len(prices)):
        actual = valid_count[i + 1] - valid_count[i + 1 - window]
        if actual == 0:
            result.append(None)
        else:
            sma = (cumsum[i + 1] - cumsum[i + 1 - window]) / actual
            result.append(round(sma, 4))

    return result
