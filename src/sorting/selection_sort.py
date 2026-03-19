"""Selection Sort implementation with O(n²) time complexity

Complejidad:
- Mejor caso: O(n²)
- Caso promedio: O(n²)
- Peor caso: O(n²)
- Espacio: O(1)

Selección: Busca el mínimo en cada pasada y lo intercambia con la posición actual.
"""


def selection_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Selection Sort

    Encuentra el elemento mínimo en cada iteración y lo coloca
    en su posición correcta.
    """
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def selection_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta selection sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    selection_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
