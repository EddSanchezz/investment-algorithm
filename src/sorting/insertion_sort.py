"""Insertion Sort implementation with O(n²) time complexity

Complejidad:
- Mejor caso: O(n) cuando ya está ordenado
- Caso promedio: O(n²)
- Peor caso: O(n²) cuando está ordenado inversamente
- Espacio: O(1)

Inserción: Inserta cada elemento en su posición correcta dentro de la parte ordenada.
"""


def insertion_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Insertion Sort

    Construye el array ordenado uno a la vez insertando
    cada elemento en su posición correcta.
    """
    n = len(arr)
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def insertion_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta insertion sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    insertion_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
