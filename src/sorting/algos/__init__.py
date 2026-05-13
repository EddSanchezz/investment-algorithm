"""Módulo con un archivo por algoritmo de ordenamiento.

Cada archivo exporta una función `sort(arr, counters)` que recibe:
  - arr:      Lista de diccionarios con clave 'sort_key'
  - counters: Objeto con atributos .comparison_count y .swap_count

Retorna la lista ordenada.
"""

from .selection_sort import sort as selection_sort
from .comb_sort import sort as comb_sort
from .gnome_sort import sort as gnome_sort
from .tim_sort import sort as tim_sort
from .quicksort import sort as quicksort
from .heapsort import sort as heapsort
from .tree_sort import sort as tree_sort
from .binary_insertion_sort import sort as binary_insertion_sort
from .pigeonhole_sort import sort as pigeonhole_sort
from .bucket_sort import sort as bucket_sort
from .bitonic_sort import sort as bitonic_sort
from .radix_sort import sort as radix_sort

__all__ = [
    "selection_sort",
    "comb_sort",
    "gnome_sort",
    "tim_sort",
    "quicksort",
    "heapsort",
    "tree_sort",
    "binary_insertion_sort",
    "pigeonhole_sort",
    "bucket_sort",
    "bitonic_sort",
    "radix_sort",
]
