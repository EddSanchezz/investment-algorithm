"""
Gnome Sort — O(n²) promedio, similar a Insertion Sort.

    [3, 7, 1, 9, 4]
      ↑
    [3, 7, 1, 9, 4]      ← avanza si está ordenado
         ↑
    [3, 1, 7, 9, 4]      ← desordenado → intercambia y retrocede
         ↑
    [1, 3, 7, 9, 4]      ← retrocede comparando
      ↑
    [1, 3, 7, 9, 4]      ← ordenado → avanza
            ↑ ...

Pasos:
  1. Avanzar índice mientras pares adyacentes estén ordenados
  2. Al encontrar desorden, intercambiar y retroceder un paso
  3. Repetir hasta llegar al final del arreglo

Complejidad:
  Mejor:  O(n)   — lista ya ordenada
  Peor:   O(n²)
  Promedio: O(n²)
  Espacio: O(1) — in-place
"""


def sort(arr, counters):
    """
    Gnome Sort — O(n²). Camina y retrocede como un gnomo ordenando macetas.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    result = arr.copy()
    n = len(result)
    index = 0

    while index < n:
        if index == 0:
            index += 1
        counters.comparison_count += 1
        if result[index]["sort_key"] >= result[index - 1]["sort_key"]:
            index += 1
        else:
            result[index], result[index - 1] = result[index - 1], result[index]
            counters.swap_count += 1
            index -= 1

    return result
