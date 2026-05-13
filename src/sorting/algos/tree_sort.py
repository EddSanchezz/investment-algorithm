"""
Tree Sort — O(n log n) promedio, O(n²) peor caso.

    [5, 3, 7, 1, 9]

    Árbol BST:
        5
       / \
      3   7
     /     \
    1       9

    Recorrido in-order: [1, 3, 5, 7, 9]

Pasos:
  1. Insertar cada elemento en un BST (Binary Search Tree)
  2. Hacer recorrido in-order (izquierdo → nodo → derecho)
  3. Los elementos se obtienen en orden ascendente

Complejidad:
  Mejor:   O(n log n) — árbol balanceado
  Peor:    O(n²)      — árbol degenerado (datos ya ordenados)
  Promedio: O(n log n)
  Espacio:  O(n)      — nodos del árbol BST
"""


class _TreeNodeIter:
    """Nodo de BST para Tree Sort (iterativo, evita recursión profunda)."""
    __slots__ = ["value", "left", "right"]

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def sort(arr, counters):
    """
    Tree Sort — O(n log n) promedio. Inserta en BST y recorre in-order.

    Args:
        arr: Lista de diccionarios con clave 'sort_key'
        counters: Objeto con .comparison_count y .swap_count

    Returns:
        Lista ordenada
    """
    if not arr:
        return []

    root = None
    for item in arr:
        if root is None:
            root = _TreeNodeIter(item)
        else:
            current = root
            while True:
                counters.comparison_count += 1
                if item["sort_key"] < current.value["sort_key"]:
                    if current.left is None:
                        current.left = _TreeNodeIter(item)
                        break
                    current = current.left
                else:
                    if current.right is None:
                        current.right = _TreeNodeIter(item)
                        break
                    current = current.right

    result = []
    stack = []
    current = root
    while stack or current:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.value)
        current = current.right

    return result
