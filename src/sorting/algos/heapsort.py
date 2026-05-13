"""
HeapSort — O(n log n) garantizado en todos los casos.

    [4, 3, 7, 1, 9, 2]        ← arreglo original

    Fase 1: Construir Max-Heap (O(n))
            9
          /   \\
         7     4
        / \\   /
       1   3  2

    Fase 2: Extraer máximo repetidamente (O(n log n))
    Extraer 9 → heapificar → [7, 3, 4, 1, 2, 9]
    Extraer 7 → heapificar → [4, 3, 2, 1, 7, 9]
    ...                        [1, 2, 3, 4, 7, 9]

Pasos:
  1. Construir max-heap desde el arreglo (heapify desde n/2 hasta 0)
  2. Intercambiar raíz (máximo) con última posición
  3. Reducir tamaño del heap y heapificar la raíz
  4. Repetir hasta que solo quede un elemento

Complejidad:
  Mejor:   O(n log n)
  Peor:    O(n log n) — garantizado
  Promedio: O(n log n)
  Espacio: O(1) — in-place

Estabilidad: No estable
"""


def sort(arr, counters):
    """
    HeapSort — O(n log n) garantizado. Max-heap in-place.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    n = len(arr)
    result = arr.copy()

    def heapify(size, root):
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2
        if left < size:
            counters.comparison_count += 1
            if result[left]["sort_key"] > result[largest]["sort_key"]:
                largest = left
        if right < size:
            counters.comparison_count += 1
            if result[right]["sort_key"] > result[largest]["sort_key"]:
                largest = right
        if largest != root:
            result[root], result[largest] = result[largest], result[root]
            counters.swap_count += 1
            heapify(size, largest)

    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    for i in range(n - 1, 0, -1):
        result[0], result[i] = result[i], result[0]
        counters.swap_count += 1
        heapify(i, 0)

    return result
