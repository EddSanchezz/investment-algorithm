"""
Pigeonhole Sort — O(n + k) donde k = rango de valores.

    [5, 2, 7, 2, 5, 1]       ← k = 7-1+1 = 7

    Huecos (pigeonholes):
    [ ] [ ] [ ] [ ] [ ] [ ] [ ]
      1   2   3   4   5   6   7

    Distribuir:
    [1] [2,2] [ ] [ ] [5,5] [ ] [7]

    Recolectar:
    [1, 2, 2, 5, 5, 7]

Pasos:
  1. Encontrar min y max del arreglo
  2. Crear k = max-min+1 "huecos" (pigeonholes)
  3. Colocar cada elemento en su hueco según su valor
  4. Recolectar los huecos en orden

Complejidad:
  Mejor:   O(n + k) — k = rango de valores
  Peor:    O(n + k)
  Promedio: O(n + k)
  Espacio: O(k)

Nota: Para claves no numéricas usa diccionario como fallback.
"""


def sort(arr, counters):
    """
    Pigeonhole Sort — O(n+k). Distribuye en huecos indexados por valor.

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
        pigeon_holes = {}
        for item in arr:
            key = item["sort_key"]
            if key not in pigeon_holes:
                pigeon_holes[key] = []
            pigeon_holes[key].append(item)
            counters.comparison_count += 1
        result = []
        for key in sorted(pigeon_holes.keys()):
            result.extend(pigeon_holes[key])
        return result

    min_val = min(values)
    max_val = max(values)

    scale = 100
    min_val_scaled = int(min_val * scale)
    max_val_scaled = int(max_val * scale)
    scaled = [
        {
            "sort_key": int(x["sort_key"] * scale),
            **{k: v for k, v in x.items() if k != "sort_key"},
        }
        for x in arr
    ]

    range_size = max_val_scaled - min_val_scaled + 1
    holes = [[] for _ in range(range_size)]

    for item in scaled:
        holes[item["sort_key"] - min_val_scaled].append(item)
        counters.comparison_count += 1

    result = []
    for hole in holes:
        for item in hole:
            result.append(item)

    return result
