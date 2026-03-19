"""Shell Sort implementation with O(n²) to O(n log² n) time complexity

Complejidad:
- Mejor caso: O(n log² n)
- Caso promedio: Depende de la secuencia de gaps (O(n^1.3) con Knuth)
- Peor caso: O(n²)
- Espacio: O(1)

Variante de Insertion Sort que usa gaps decrecientes.
"""


def shell_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Shell Sort

    Usa la secuencia de gaps de Knuth: gap = 3*gap + 1
    """
    n = len(arr)
    gap = 1

    while gap < n // 3:
        gap = 3 * gap + 1

    while gap >= 1:
        for i in range(gap, n):
            temp = arr[i]
            j = i

            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap

            arr[j] = temp

        gap //= 3

    return arr


def shell_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta shell sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    shell_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
