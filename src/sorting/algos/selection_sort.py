"""
Selection Sort — O(n²) siempre.

    [5, 3, 8, 1, 2]       ← original
     ↑min=1                ← encuentra mínimo en toda la lista
    [1, 3, 8, 5, 2]       ← intercambia con posición 0
        ↑min=2             ← busca en [1..n]
    [1, 2, 8, 5, 3]       ← intercambia con posición 1
           ↑min=3
    [1, 2, 3, 5, 8]       ← lista ordenada

Pasos:
  1. Dividir lista en parte ordenada (inicio) y no ordenada (resto)
  2. Encontrar el mínimo en la parte no ordenada
  3. Intercambiarlo con el primer elemento no ordenado
  4. Repetir hasta que toda la lista esté ordenada

Complejidad:
  Mejor:  O(n²) — siempre recorre toda la parte no ordenada
  Peor:   O(n²)
  Promedio: O(n²)
  Espacio: O(1) — in-place (copia defensiva al inicio)

Estabilidad: No estable (por los intercambios)
"""


def sort(arr, counters):
    """
    Selection Sort — O(n²). Mínimo número de escrituras (O(n) intercambios).

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    n = len(arr)
    result = arr.copy()

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            counters.comparison_count += 1
            if result[j]["sort_key"] < result[min_idx]["sort_key"]:
                min_idx = j
        if min_idx != i:
            result[i], result[min_idx] = result[min_idx], result[i]
            counters.swap_count += 1

    return result
