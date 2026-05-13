"""
QuickSort — O(n log n) promedio, O(n²) peor caso.

    [3, 7, 1, 9, 4]         ← arreglo original
          ↑pivote=4
    Partición de Lomuto:
    [3, 1, 4, 7, 9]         ← menores a izquierda, mayores a derecha
       ↑pivote=1    ↑pivote=7
    [1, 3] [4] [7, 9]       ← subarreglos ordenados recursivamente
    [1, 3, 4, 7, 9]         ← resultado final

Pasos:
  1. Elegir pivote (último elemento — partición de Lomuto)
  2. Particionar: menores al pivote a la izquierda, mayores a la derecha
  3. Procesar el subarreglo más pequeño primero (optimización de pila)
  4. Repetir hasta que todos los subarreglos tengan tamaño 1

Complejidad:
  Mejor:   O(n log n) — pivote equilibrado
  Peor:    O(n²)      — pivote siempre min/max
  Promedio: O(n log n)
  Espacio: O(log n) — pila iterativa
"""


def sort(arr, counters):
    """
    QuickSort — partición de Lomuto, versión iterativa con pila explícita.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    result = arr.copy()
    if len(result) <= 1:
        return result

    def partition(low, high):
        pivot = result[high]["sort_key"]
        i = low - 1
        for j in range(low, high):
            counters.comparison_count += 1
            if result[j]["sort_key"] <= pivot:
                i += 1
                result[i], result[j] = result[j], result[i]
                counters.swap_count += 1
        result[i + 1], result[high] = result[high], result[i + 1]
        counters.swap_count += 1
        return i + 1

    stack = [(0, len(result) - 1)]
    while stack:
        low, high = stack.pop()
        if low < high:
            pivot_idx = partition(low, high)
            if pivot_idx - 1 - low > high - pivot_idx - 1:
                stack.append((low, pivot_idx - 1))
                stack.append((pivot_idx + 1, high))
            else:
                stack.append((pivot_idx + 1, high))
                stack.append((low, pivot_idx - 1))

    return result
