"""Merge Sort implementation with O(n log n) time complexity

Complejidad:
- Mejor caso: O(n log n)
- Caso promedio: O(n log n)
- Peor caso: O(n log n)
- Espacio: O(n)

Recurrencia: T(n) = 2T(n/2) + Θ(n)
Por Master Theorem: Θ(n log n)
"""


def merge_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Merge Sort

    Divide el array en mitades recursivamente, ordena cada mitad
    y luego las fusiona.
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


def merge(left: list, right: list) -> list:
    """Fusiona dos arrays ordenados en uno solo ordenado"""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta merge sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    sorted_arr = merge_sort(arr_copy)
    end = time.perf_counter()
    return sorted_arr, (end - start) * 1000
