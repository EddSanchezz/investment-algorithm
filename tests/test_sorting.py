"""
Tests unitarios para los algoritmos de ordenamiento.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.sorting.algorithms import SortingAlgorithms


class TestSortingAlgorithms:
    def setup_method(self):
        self.sorter = SortingAlgorithms()
        self.data = [
            {"sort_key": 5, "name": "a"},
            {"sort_key": 3, "name": "b"},
            {"sort_key": 8, "name": "c"},
            {"sort_key": 1, "name": "d"},
            {"sort_key": 9, "name": "e"},
        ]
        self.expected = [1, 3, 5, 8, 9]

    def _verify_sorted(self, result):
        keys = [r["sort_key"] for r in result]
        assert keys == self.expected

    def test_tim_sort(self):
        self._verify_sorted(self.sorter.tim_sort(self.data))

    def test_quicksort(self):
        self._verify_sorted(self.sorter.quicksort(self.data))

    def test_quicksort(self):
        self._verify_sorted(self.sorter.quicksort(self.data))

    def test_tree_sort(self):
        self._verify_sorted(self.sorter.tree_sort(self.data))

    def test_heapsort(self):
        self._verify_sorted(self.sorter.heapsort(self.data))

    def test_binary_insertion_sort(self):
        self._verify_sorted(self.sorter.binary_insertion_sort(self.data))

    def test_comb_sort(self):
        self._verify_sorted(self.sorter.comb_sort(self.data))

    def test_selection_sort(self):
        self._verify_sorted(self.sorter.selection_sort(self.data))

    def test_bitonic_sort(self):
        self._verify_sorted(self.sorter.bitonic_sort(self.data))

    def test_single_element(self):
        result = self.sorter.tim_sort([{"sort_key": 42}])
        assert len(result) == 1
        assert result[0]["sort_key"] == 42

    def test_empty_list(self):
        result = self.sorter.tim_sort([])
        assert result == []
