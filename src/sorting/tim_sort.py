"""Tim Sort implementation with O(n log n) time complexity

Complejidad:
- Mejor caso: O(n) para secuencias ya ordenadas
- Caso promedio: O(n log n)
- Peor caso: O(n log n)
- Espacio: O(n)

Algoritmo híbrido que combina Merge Sort e Insertion Sort.
Optimizado para datos del mundo real con subsequencias ordenadas.
"""


def tim_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Tim Sort

    Usa runs (subsecuencias ordenadas) y Merge Sort para combinarlas.
    MIN_RUN típicamente es 32 o 64.
    """
    MIN_RUN = 32
    n = len(arr)

    for start in range(0, n, MIN_RUN):
        end = min(start + MIN_RUN - 1, n - 1)
        insertion_sort_min(arr, start, end)

    size = MIN_RUN
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                merge_min(arr, left, mid, right)
        size *= 2

    return arr


def insertion_sort_min(arr: list, left: int, right: int) -> None:
    """Insertion Sort para un rango específico [left, right]"""
    for i in range(left + 1, right + 1):
        temp = arr[i]
        j = i - 1
        while j >= left and arr[j] > temp:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = temp


def merge_min(arr: list, left: int, mid: int, right: int) -> None:
    """Fusiona dos subarrays ordenados"""
    left_part = arr[left : mid + 1]
    right_part = arr[mid + 1 : right + 1]

    i = j = 0
    k = left

    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1

    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1

    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1


def tim_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta tim sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    tim_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
