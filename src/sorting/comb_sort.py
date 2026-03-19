"""Comb Sort implementation with O(n²) to O(n log n) time complexity

Complejidad:
- Mejor caso: O(n log n) cuando ya está ordenado
- Caso promedio: O(n²)
- Peor caso: O(n²)
- Espacio: O(1)

Mejora de Bubble Sort que elimina "tortugas" (pequeños valores
al final) usando un gap que se reduce por un factor de 1.3.
"""


def comb_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Comb Sort

    Usa un gap inicial igual al tamaño del array que se reduce
    por un factor de 1.3 (best shrink factor) en cada pasada.
    """
    n = len(arr)
    gap = n
    shrink = 1.3
    sorted_ = False

    while not sorted_:
        gap = int(gap / shrink)
        if gap <= 1:
            gap = 1
            sorted_ = True

        i = 0
        while i + gap < n:
            if arr[i] > arr[i + gap]:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                sorted_ = False
            i += 1

    return arr


def comb_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta comb sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    comb_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
