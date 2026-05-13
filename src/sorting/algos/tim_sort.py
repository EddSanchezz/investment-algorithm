"""
TimSort — O(n log n) promedio, híbrido Merge + Insertion Sort.

    [5, 1, 9, 3, 7, 2, 8, 4, 6]
     └─────┬─────┘  └──┬───┘
         run_0        run_1              ← detecta "runs" ordenados
     └─────────┬──────────┘
         insertion_sort(run_0)           ← ordena runs pequeños
     └──────────────┬──────────────┘
                    merge(run_0, run_1)  ← fusiona runs
     [1, 2, 3, 4, 5, 6, 7, 8, 9]

Pasos:
  1. Calcular min_run (normalmente 32-64) usando desplazamiento de bits
  2. Dividir arreglo en runs de tamaño min_run
  3. Ordenar cada run con Insertion Sort
  4. Fusionar runs con Merge Sort (doble cola)

Complejidad:
  Mejor:   O(n)       — datos ya ordenados
  Peor:    O(n log n)
  Promedio: O(n log n)
  Espacio: O(n) — arreglos auxiliares para merge

Estabilidad: Sí
"""

MIN_MERGE = 32


def sort(arr, counters):
    """
    TimSort — O(n log n). Óptimo para datos parcialmente ordenados.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    n = len(arr)
    if n <= 1:
        return arr.copy()

    result = arr.copy()

    def calc_min_run(n):
        r = 0
        while n >= MIN_MERGE:
            r |= n & 1
            n >>= 1
        return n + r

    def insertion_sort(left, right):
        for i in range(left + 1, right + 1):
            key = result[i]
            j = i - 1
            while j >= left:
                counters.comparison_count += 1
                if result[j]["sort_key"] > key["sort_key"]:
                    result[j + 1] = result[j]
                    counters.swap_count += 1
                    j -= 1
                else:
                    break
            result[j + 1] = key

    def merge(left, mid, right):
        left_arr = result[left: mid + 1]
        right_arr = result[mid + 1: right + 1]
        i = j = 0
        k = left
        while i < len(left_arr) and j < len(right_arr):
            counters.comparison_count += 1
            if left_arr[i]["sort_key"] <= right_arr[j]["sort_key"]:
                result[k] = left_arr[i]
                i += 1
            else:
                result[k] = right_arr[j]
                j += 1
            k += 1
        while i < len(left_arr):
            result[k] = left_arr[i]; i += 1; k += 1
        while j < len(right_arr):
            result[k] = right_arr[j]; j += 1; k += 1

    min_run = calc_min_run(n)
    for start in range(0, n, min_run):
        end = min(start + min_run - 1, n - 1)
        insertion_sort(start, end)

    size = min_run
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                merge(left, mid, right)
        size *= 2

    return result
