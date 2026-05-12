"""
Dynamic Time Warping (DTW) para Series Temporales Financieras.

DTW permite comparar secuencias que pueden diferir en velocidad o fase,
"warping" (estiramiento/compresión) no lineal del eje temporal.

Algoritmo:
    1. Construir matriz de distancia acumulada D de tamaño (n+1) × (m+1)
    2. Inicializar D[0][*] = ∞, D[*][0] = ∞, D[0][0] = 0
    3. Para cada celda (i, j):
        D[i][j] = d(xᵢ, yⱼ) + min(D[i-1][j], D[i][j-1], D[i-1][j-1])
       donde d(xᵢ, yⱼ) = |xᵢ - yⱼ|
    4. DTW(x, y) = D[n][m]

Optimización (Sakoe-Chiba):
    Restringe el warping a una banda de ancho w alrededor de la diagonal,
    reduciendo la complejidad de O(n×m) a O(n×w).

    Esto es útil cuando se sabe que las series no tienen diferencias
    temporales extremas (común en datos financieros diarios).

Donde:
    x, y = series de precios o retornos de dos activos
    n, m = longitudes de cada serie

Interpretación:
    - 0 ≤ DTW < ∞
    - 0 = series idénticas (con posible warping temporal)
    - Valores más bajos indican mayor similitud (considerando warping)
    - DTW puede encontrar similitudes que la Euclidiana no detecta

Aplicación:
    - Comparar activos con diferentes calendarios o desfases
    - Detectar patrones similares que ocurren en diferentes momentos
    - Útil cuando los ciclos económicos afectan activos con rezago temporal

Complejidad computacional:
    Temporal: O(n × m) sin optimización
             O(n × w) con restricción Sakoe-Chiba (w = ancho de banda)
    Espacial: O(n × m) para matriz completa
             O(n) si se optimiza con ventana
"""

from typing import List, Optional


def dtw_distance(series1: List[float], series2: List[float], window: Optional[int] = None, full_matrix: bool = True) -> dict:
    """
    Calcula la distancia DTW entre dos series temporales.

    Implementa Dynamic Time Warping con optimización opcional de Sakoe-Chiba
    y modo de memoria reducida (solo distancia, sin path de warping).

    Parámetros:
        series1: Primera serie de valores
        series2: Segunda serie de valores
        window: Ancho de banda de Sakoe-Chiba (None = sin restricción)
        full_matrix: Si es True, almacena matriz completa (permite path).
                     Si es False, usa solo dos filas (solo distancia, O(n) memoria).

    Retorna:
        Diccionario con:
            - distance: distancia DTW
            - normalized_distance: distancia normalizada por longitud del camino
            - path_length: longitud del camino de warping (solo si full_matrix=True)
            - n, m: dimensiones de las series
            - window: ancho de banda usado
            - formula: representación de la fórmula
            - complexity: análisis de complejidad

    Complejidad: O(n × m) u O(n × w) con restricción
    """
    if len(series1) == 0 or len(series2) == 0:
        return {
            "distance": None,
            "normalized_distance": None,
            "path_length": 0,
            "n": len(series1),
            "m": len(series2),
            "window": window,
            "formula": "$DTW(x,y) = \\min_{\\pi} \\sum_{(i,j)\\in\\pi} |x_i - y_j|$",
            "complexity": f"O({len(series1)}×{len(series2)})" if window is None else f"O(n×{window})",
            "description": "Dynamic Time Warping",
        }

    n, m = len(series1), len(series2)

    INF = float("inf")

    if window is not None:
        window = max(window, abs(n - m) + 1)

    if full_matrix:
        dtw_matrix = [[INF] * (m + 1) for _ in range(n + 1)]
        dtw_matrix[0][0] = 0.0

        for i in range(1, n + 1):
            if window is not None:
                j_start = max(1, i - window)
                j_end = min(m, i + window)
                for j in range(j_start, j_end + 1):
                    cost = abs(series1[i - 1] - series2[j - 1])
                    dtw_matrix[i][j] = cost + min(
                        dtw_matrix[i - 1][j],
                        dtw_matrix[i][j - 1],
                        dtw_matrix[i - 1][j - 1],
                    )
            else:
                for j in range(1, m + 1):
                    cost = abs(series1[i - 1] - series2[j - 1])
                    dtw_matrix[i][j] = cost + min(
                        dtw_matrix[i - 1][j],
                        dtw_matrix[i][j - 1],
                        dtw_matrix[i - 1][j - 1],
                    )

        distance = dtw_matrix[n][m]

        i, j = n, m
        path_length = 1
        while i > 0 or j > 0:
            if i > 0 and j > 0:
                min_prev = min(
                    dtw_matrix[i - 1][j],
                    dtw_matrix[i][j - 1],
                    dtw_matrix[i - 1][j - 1],
                )
                if min_prev == dtw_matrix[i - 1][j - 1]:
                    i -= 1
                    j -= 1
                elif min_prev == dtw_matrix[i - 1][j]:
                    i -= 1
                else:
                    j -= 1
            elif i > 0:
                i -= 1
            else:
                j -= 1
            path_length += 1

        normalized = distance / path_length if path_length > 0 else distance
    else:
        prev_row = [INF] * (m + 1)
        curr_row = [INF] * (m + 1)
        prev_row[0] = 0.0

        for i in range(1, n + 1):
            curr_row[0] = INF
            if window is not None:
                j_start = max(1, i - window)
                j_end = min(m, i + window)
                for j in range(1, m + 1):
                    if j < j_start or j > j_end:
                        continue
                    cost = abs(series1[i - 1] - series2[j - 1])
                    curr_row[j] = cost + min(
                        prev_row[j],
                        curr_row[j - 1],
                        prev_row[j - 1],
                    )
            else:
                for j in range(1, m + 1):
                    cost = abs(series1[i - 1] - series2[j - 1])
                    curr_row[j] = cost + min(
                        prev_row[j],
                        curr_row[j - 1],
                        prev_row[j - 1],
                    )
            prev_row, curr_row = curr_row, prev_row

        distance = prev_row[m]
        path_length = n + m
        normalized = distance / path_length if path_length > 0 else distance

    complexity = f"O(n×m) = O({n}×{m})"
    if window is not None:
        complexity = f"O(n×w) = O({n}×{window}) [Sakoe-Chiba]"

    return {
        "distance": round(distance, 6),
        "normalized_distance": round(normalized, 6),
        "path_length": path_length,
        "n": n,
        "m": m,
        "window": window,
        "full_matrix": full_matrix,
        "formula": "$DTW(x,y) = \\min_{\\pi} \\sum_{(i,j)\\in\\pi} |x_i - y_j|$",
        "complexity": complexity,
        "description": "Dynamic Time Warping",
        "interpretation": (
            f"DTW = {distance:.4f} (normalizado = {normalized:.4f}). "
            f"Camino de warping de {path_length} pasos. "
            "Valores más bajos indican mayor similitud temporal."
        ),
    }
