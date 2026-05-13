"""
Bucket Sort — O(n + k) promedio, O(n²) peor caso.

    [0.42, 0.32, 0.73, 0.12, 0.91, 0.53]

    Buckets:
    [0-0.2)  [0.2-0.4)  [0.4-0.6)  [0.6-0.8)  [0.8-1.0]
    [0.12]   [0.32]     [0.42,0.53] [0.73]     [0.91]

    Ordenar cada bucket individualmente (con sorted() o similar)
    Concatenar buckets en orden:
    [0.12, 0.32, 0.42, 0.53, 0.73, 0.91]

Pasos:
  1. Crear k buckets que cubren el rango de valores
  2. Distribuir cada elemento en el bucket correspondiente
  3. Ordenar cada bucket individualmente
  4. Concatenar los buckets en orden

Complejidad:
  Mejor:   O(n + k) — distribución uniforme
  Peor:    O(n²)    — todos los elementos caen en un bucket
  Promedio: O(n + k) — con k ≈ n
  Espacio: O(n + k)

Nota: Para claves no numéricas usa distribución por hash.
"""


def sort(arr, counters, num_buckets=10):
    """
    Bucket Sort — O(n+k) promedio. Distribuye en buckets y ordena cada uno.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count
        num_buckets: Número de buckets (default 10)

    Returns:
        Lista ordenada
    """
    if not arr:
        return []

    values = [x["sort_key"] for x in arr]

    if not all(isinstance(v, (int, float)) for v in values):
        buckets_dict = {}
        for item in arr:
            key = item["sort_key"]
            bucket_idx = hash(key) % num_buckets
            if bucket_idx not in buckets_dict:
                buckets_dict[bucket_idx] = []
            buckets_dict[bucket_idx].append(item)
            counters.comparison_count += 1

        for bucket in buckets_dict.values():
            bucket.sort(key=lambda x: x["sort_key"])

        result = []
        for i in range(num_buckets):
            if i in buckets_dict:
                result.extend(buckets_dict[i])
        return result

    min_val = min(values)
    max_val = max(values)

    buckets = [[] for _ in range(num_buckets)]
    range_size = (max_val - min_val) / num_buckets if num_buckets > 0 else 1

    for item in arr:
        idx = (
            min(int((item["sort_key"] - min_val) / range_size), num_buckets - 1)
            if range_size > 0
            else 0
        )
        buckets[idx].append(item)
        counters.comparison_count += 1

    for bucket in buckets:
        bucket.sort(key=lambda x: x["sort_key"])

    result = []
    for bucket in buckets:
        result.extend(bucket)

    return result
