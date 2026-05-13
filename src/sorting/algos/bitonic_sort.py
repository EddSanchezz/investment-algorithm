"""
Bitonic Sort — O(log² n), paralelo, requiere n = 2^k.

    Secuencia bitónica: creciente + decreciente
    [3, 7, 9, 12, 8, 5, 2, 1]
      └── creciente ──┘└─ decreciente ─┘

    Fase 1: Construir secuencia bitónica
    [3, 7, 9, 12, 8, 5, 2, 1]   ← bitónica
          └── merge ──┘

    Fase 2: Bitonic Merge (comparar i con i+k/2)
    [3, 5, 2, 1, 8, 7, 9, 12]   ← primera mitad decreciente
    [1, 2, 3, 5, 7, 8, 9, 12]   ← ordenado

Pasos:
  1. Si n no es potencia de 2, rellenar con valores centinela
  2. Dividir recursivamente en mitades: primera creciente, segunda decreciente
  3. Fusionar usando compare-and-swap entre elementos separados por k/2
  4. Repetir hasta que toda la secuencia esté ordenada

Complejidad:
  Tiempo: O(log² n) para n = 2^k
  Espacio: O(1) — in-place (copia defensiva)

Ventaja: Altamente paralelizable (comparaciones independientes)
"""


def sort(arr, counters, ascending=True):
    """
    Bitonic Sort — O(log² n). Para arquitecturas paralelas.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count
        ascending: True = ascendente, False = descendente

    Returns:
        Lista ordenada
    """
    n = len(arr)
    if n == 0:
        return []

    result = arr.copy() if (n & (n - 1)) == 0 else None

    if (n & (n - 1)) != 0:
        next_pow2 = 1
        while next_pow2 < n:
            next_pow2 *= 2

        max_key = max(arr, key=lambda x: x["sort_key"])["sort_key"]
        if isinstance(max_key, tuple):
            padding = {"sort_key": (9999, 9999, 9999)}
        elif isinstance(max_key, (int, float)):
            padding = {"sort_key": float("inf")}
        else:
            padding = {"sort_key": max_key}

        result = arr + [padding] * (next_pow2 - n)

    def compare_and_swap(i, j, direction):
        try:
            should_swap = result[i]["sort_key"] > result[j]["sort_key"]
        except TypeError:
            should_swap = str(result[i]["sort_key"]) > str(result[j]["sort_key"])

        if direction == should_swap:
            result[i], result[j] = result[j], result[i]
            counters.swap_count += 1
        counters.comparison_count += 1

    def bitonic_merge(start, size, direction):
        if size > 1:
            k = size // 2
            for i in range(start, start + k):
                compare_and_swap(i, i + k, direction)
            bitonic_merge(start, k, direction)
            bitonic_merge(start + k, k, direction)

    def bitonic_sort_recursive(start, size, direction):
        if size > 1:
            k = size // 2
            bitonic_sort_recursive(start, k, True)
            bitonic_sort_recursive(start + k, k, False)
            bitonic_merge(start, size, direction)

    size = len(result)
    k = 1
    while k < size:
        k *= 2

    bitonic_sort_recursive(0, k, ascending)

    return result[:n]
