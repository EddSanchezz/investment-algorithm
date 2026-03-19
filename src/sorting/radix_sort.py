"""Radix Sort implementation with O(nk) time complexity

Complejidad:
- Mejor caso: O(nk)
- Caso promedio: O(nk)
- Peor caso: O(nk)
- Espacio: O(n + k)

Donde k es el número de dígitos del máximo elemento.
Usa Counting Sort como algoritmo estable para cada dígito.
"""


def radix_sort(arr: list) -> list:
    """Ordena una lista usando el algoritmo Radix Sort (LSD)

    Procesa los dígitos de menor a mayor significancia.
    """
    if not arr:
        return []

    max_val = max(arr)

    exp = 1
    while max_val // exp > 0:
        counting_sort_by_digit(arr, exp)
        exp *= 10

    return arr


def counting_sort_by_digit(arr: list, exp: int) -> None:
    """Counting Sort modificado para un dígito específico"""
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for num in arr:
        digit = (num // exp) % 10
        count[digit] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        digit = (arr[i] // exp) % 10
        output[count[digit] - 1] = arr[i]
        count[digit] -= 1

    for i in range(n):
        arr[i] = output[i]


def radix_sort_time_analysis(arr: list) -> tuple[list, float]:
    """Ejecuta radix sort y retorna resultado junto con tiempo de ejecución"""
    import time

    arr_copy = arr.copy()
    start = time.perf_counter()
    radix_sort(arr_copy)
    end = time.perf_counter()
    return arr_copy, (end - start) * 1000
