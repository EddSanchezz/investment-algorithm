"""Counting Sort implementation with O(n + k) time complexity

Complejidad:
- Mejor caso: O(n + k)
- Caso promedio: O(n + k)
- Peor caso: O(n + k)
- Espacio: O(k)

Donde k es el rango de los elementos de entrada.
No es un algoritmo basado en comparación.
"""


def counting_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Counting Sort

    Solo funciona para enteros no negativos.
    Cuenta las ocurrencias de cada valor.
    """
    if not arr:
        return []

    max_val = max(arr)
    min_val = min(arr)
    range_size = max_val - min_val + 1

    count = [0] * range_size
    output = [0] * len(arr)

    for num in arr:
        count[num - min_val] += 1

    for i in range(1, len(count)):
        count[i] += count[i - 1]

    for i in range(len(arr) - 1, -1, -1):
        output[count[arr[i] - min_val] - 1] = arr[i]
        count[arr[i] - min_val] -= 1

    return output


def counting_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta counting sort y retorna resultado junto con tiempo de ejecución"""
    import time

    start = time.perf_counter()
    sorted_arr = counting_sort(arr.copy())
    end = time.perf_counter()
    return sorted_arr, (end - start) * 1000
