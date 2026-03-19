"""Heap Sort implementation with O(n log n) time complexity

Complejidad:
- Mejor caso: O(n log n)
- Caso promedio: O(n log n)
- Peor caso: O(n log n)
- Espacio: O(1)

Usa una estructura de Max Heap para ordenar el array.
"""


def heap_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Heap Sort

    Construye un Max Heap y extrae el máximo repetidamente.
    """
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)

    return arr


def heapify(arr: list, n: int, i: int) -> None:
    """Transforma un subarray en max heap

    n: tamaño del heap
    i: índice de la raíz del subarray
    """
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] > arr[largest]:
        largest = left

    if right < n and arr[right] > arr[largest]:
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)


def heap_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta heap sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    heap_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
