"""
Radix Sort (LSD) — O(nk) donde k = número de dígitos.

    [329, 457, 657, 839, 436, 720, 355]

    Paso 1: ordenar por unidad        Paso 2: ordenar por decena
    [720, 329, 436, 457, 657, 355, 839]  [720, 329, 436, 839, 457, 355, 657]

    Paso 3: ordenar por centena
    [329, 355, 436, 457, 657, 720, 839]  ← ordenado!

Pasos:
  1. Encontrar el valor máximo para saber el número de dígitos
  2. Para cada dígito (unidades, decenas, centenas...):
     a. Usar Counting Sort como algoritmo auxiliar estable
     b. Ordenar por el dígito actual
  3. El arreglo queda ordenado después del último dígito

Complejidad:
  Tiempo: O(nk) — k = número de dígitos
  Espacio: O(n + k) — arreglo auxiliar + count[10]

Nota: Para claves no numéricas usa sorted() como fallback.
"""


def sort(arr, counters):
    """
    Radix Sort (LSD) — O(nk). Ordena dígito por dígito de derecha a izquierda.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    if not arr:
        return []

    values = [x["sort_key"] for x in arr]

    if not all(isinstance(v, (int, float)) for v in values):
        result = sorted(arr, key=lambda x: x["sort_key"])
        counters.comparison_count = len(arr) * 10
        return result

    if isinstance(values[0], float):
        scale = 100
        result = [
            {
                "sort_key": int(x["sort_key"] * scale),
                **{k: v for k, v in x.items() if k != "sort_key"},
            }
            for x in arr
        ]
    else:
        result = arr.copy()

    max_val = max(result, key=lambda x: x["sort_key"])["sort_key"]
    if isinstance(max_val, float):
        max_val = int(max_val)

    exp = 1
    while max_val // exp > 0:
        _counting_sort(result, exp, counters)
        exp *= 10

    return result


def _counting_sort(arr, exp, counters):
    """
    Counting Sort auxiliar para un dígito específico — O(n + 10).

    Args:
        arr: Lista de diccionarios (se modifica in-place)
        exp: Posición decimal (1 = unidades, 10 = decenas, ...)
        counters: Objeto contador
    """
    n = len(arr)
    output = [None] * n
    count = [0] * 10

    for item in arr:
        digit = int(item["sort_key"] // exp) % 10
        count[digit] += 1
        counters.comparison_count += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        digit = int(arr[i]["sort_key"] // exp) % 10
        output[count[digit] - 1] = arr[i]
        count[digit] -= 1

    for i in range(n):
        arr[i] = output[i]
        counters.swap_count += 1
