"""
Binary Insertion Sort — O(n²) con O(n log n) comparaciones.

    [5, 1, 9, 3, 7]

    i=1: key=1, búsqueda binaria en [0..0] → pos=0
         [1, 5, 9, 3, 7]   ← shift [5] a derecha
    i=2: key=9, búsqueda binaria en [0..1] → pos=2
         [1, 5, 9, 3, 7]   ← sin shift
    i=3: key=3, búsqueda binaria en [0..2] → pos=1
         [1, 3, 5, 9, 7]   ← shift [5,9] a derecha

Pasos:
  1. Para cada elemento desde i=1 hasta n-1:
     a. Buscar posición de inserción con búsqueda binaria (O(log n))
     b. Hacer shift de elementos a la derecha (O(n))
     c. Insertar elemento en posición encontrada

Complejidad:
  Mejor:   O(n)       — datos ya ordenados
  Peor:    O(n²)      — shift sigue siendo O(n) por elemento
  Promedio: O(n²)     — pero con menos comparaciones que Insertion Sort
  Espacio: O(1) — in-place
"""


def sort(arr, counters):
    """
    Binary Insertion Sort — O(n²) pero solo O(n log n) comparaciones.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    result = arr.copy()
    n = len(result)

    def binary_search(arr, item, low, high):
        while low < high:
            mid = (low + high) // 2
            counters.comparison_count += 1
            if arr[mid]["sort_key"] < item["sort_key"]:
                low = mid + 1
            else:
                high = mid
        return low

    for i in range(1, n):
        key = result[i]
        pos = binary_search(result, key, 0, i)
        j = i - 1
        while j >= pos:
            result[j + 1] = result[j]
            counters.swap_count += 1
            j -= 1
        result[pos] = key

    return result
