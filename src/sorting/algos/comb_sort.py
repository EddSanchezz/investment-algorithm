"""
Comb Sort — O(n²) promedio, mejora de Bubble Sort.

    gap = n = 9                          ← gap inicial
    gap = 9/1.3 ≈ 6     comparar [i] con [i+6]
    gap = 6/1.3 ≈ 4     comparar [i] con [i+4]
    gap = 4/1.3 ≈ 3     comparar [i] con [i+3]
    gap = 3/1.3 ≈ 2     comparar [i] con [i+2]
    gap = 2/1.3 ≈ 1     Bubble Sort final   ← gap=1 = bubble sort

Pasos:
  1. Inicializar gap = n
  2. Reducir gap ÷ 1.3 en cada iteración
  3. Comparar elementos separados por el gap; intercambiar si están desordenados
  4. Cuando gap = 1, hacer una pasada de Bubble Sort para finalizar

Complejidad:
  Mejor:  O(n)         — lista ya ordenada
  Peor:   O(n²)
  Promedio: O(n²/2^p)  — p = número de iteraciones
  Espacio: O(1) — in-place

SHRINK_FACTOR = 1.3  — determinado empíricamente como óptimo
"""

SHRINK_FACTOR = 1.3


def sort(arr, counters):
    """
    Comb Sort — O(n²) promedio, usa gap decreciente para eliminar turtles.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    n = len(arr)
    result = arr.copy()
    gap = n
    sorted_ = False

    while not sorted_:
        gap = int(gap / SHRINK_FACTOR)
        if gap <= 1:
            gap = 1
            sorted_ = True

        i = 0
        while i + gap < n:
            counters.comparison_count += 1
            if result[i]["sort_key"] > result[i + gap]["sort_key"]:
                result[i], result[i + gap] = result[i + gap], result[i]
                counters.swap_count += 1
                sorted_ = False
            i += 1

    return result
