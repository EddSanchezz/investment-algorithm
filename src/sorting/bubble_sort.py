"""Bubble Sort implementation with O(n²) time complexity

Complejidad:
- Mejor caso: O(n) cuando ya está ordenado
- Caso promedio: O(n²)
- Peor caso: O(n²) cuando está ordenado inversamente
- Espacio: O(1)
"""


def bubble_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Bubble Sort

    Compara elementos adyacentes e intercambia si están en orden incorrecto.
    Después de cada pasada, el elemento más grande "burbujea" al final.
    """
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def bubble_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta bubble sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    bubble_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
