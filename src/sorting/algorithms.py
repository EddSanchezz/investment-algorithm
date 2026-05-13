"""
Sorting Algorithms Module — 12 algoritmos de ordenamiento.

Cada algoritmo vive en su propio archivo bajo src/sorting/algos/.
Esta clase los envuelve para mantener la interfaz usada por SortingComparator.
"""

from src.sorting.algos import (
    selection_sort,
    comb_sort,
    gnome_sort,
    tim_sort,
    quicksort,
    heapsort,
    tree_sort,
    binary_insertion_sort,
    pigeonhole_sort,
    bucket_sort,
    bitonic_sort,
    radix_sort,
)


class SortingAlgorithms:
    """
    Colección de 12 algoritmos de ordenamiento con análisis de complejidad.

    Cada método delega en la función sort() del archivo correspondiente
    y pasa self como objeto contador (comparison_count, swap_count).
    """

    def __init__(self) -> None:
        self.comparison_count: int = 0
        self.swap_count: int = 0

    def reset_counters(self) -> None:
        """Reinicia los contadores de comparaciones e intercambios."""
        self.comparison_count = 0
        self.swap_count = 0

    def selection_sort(self, arr: list) -> list:
        self.reset_counters()
        return selection_sort(arr, self)

    def comb_sort(self, arr: list) -> list:
        self.reset_counters()
        return comb_sort(arr, self)

    def gnome_sort(self, arr: list) -> list:
        self.reset_counters()
        return gnome_sort(arr, self)

    def tim_sort(self, arr: list) -> list:
        self.reset_counters()
        return tim_sort(arr, self)

    def quicksort(self, arr: list) -> list:
        self.reset_counters()
        return quicksort(arr, self)

    def heapsort(self, arr: list) -> list:
        self.reset_counters()
        return heapsort(arr, self)

    def tree_sort(self, arr: list) -> list:
        self.reset_counters()
        return tree_sort(arr, self)

    def binary_insertion_sort(self, arr: list) -> list:
        self.reset_counters()
        return binary_insertion_sort(arr, self)

    def pigeonhole_sort(self, arr: list) -> list:
        self.reset_counters()
        return pigeonhole_sort(arr, self)

    def bucket_sort(self, arr: list, num_buckets: int = 10) -> list:
        self.reset_counters()
        return bucket_sort(arr, self, num_buckets)

    def bitonic_sort(self, arr: list, ascending: bool = True) -> list:
        self.reset_counters()
        return bitonic_sort(arr, self, ascending)

    def radix_sort(self, arr: list) -> list:
        self.reset_counters()
        return radix_sort(arr, self)
