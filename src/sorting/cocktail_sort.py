"""Cocktail Sort implementation with O(n²) time complexity

Complejidad:
- Mejor caso: O(n) cuando ya está ordenado
- Caso promedio: O(n²)
- Peor caso: O(n²)
- Espacio: O(1)

Variante bidireccional de Bubble Sort que alterna
entre mover elementos grandes al final y elementos pequeños al inicio.
"""


def cocktail_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Cocktail Shaker Sort

    Variante de Bubble Sort que procesa en ambas direcciones.
    """
    n = len(arr)
    start = 0
    end = n - 1
    swapped = True

    while swapped:
        swapped = False

        for i in range(start, end):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True

        if not swapped:
            break

        swapped = False
        end -= 1

        for i in range(end - 1, start - 1, -1):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True

        start += 1

    return arr


def cocktail_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta cocktail sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    cocktail_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
