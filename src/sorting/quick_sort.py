"""Quick Sort implementation with O(n log n) average time complexity

Complejidad:
- Mejor caso: O(n log n)
- Caso promedio: O(n log n)
- Peor caso: O(n²) cuando el pivote es siempre el mínimo o máximo
- Espacio: O(log n) para el stack de recursión

Estrategia: Selecciona un pivote y particiona el array alrededor de él.
"""


def quick_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Quick Sort

    Implementación in-place con último elemento como pivote.
    """
    _quick_sort_helper(arr, 0, len(arr) - 1)
    return arr


def _quick_sort_helper(arr: list, low: int, high: int) -> None:
    """Función auxiliar recursiva para Quick Sort"""
    if low < high:
        pivot_index = partition(arr, low, high)
        _quick_sort_helper(arr, low, pivot_index - 1)
        _quick_sort_helper(arr, pivot_index + 1, high)


def partition(arr: list, low: int, high: int) -> int:
    """Particiona el array usando el último elemento como pivote

    Retorna el índice final del pivote después de la partición.
    """
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quick_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta quick sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    quick_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
