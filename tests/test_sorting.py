"""Unit tests for sorting algorithms"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sorting import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    heap_sort,
    shell_sort,
    counting_sort,
    radix_sort,
    cocktail_sort,
    comb_sort,
    tim_sort,
)


class TestSortingAlgorithms:
    """Tests for all sorting algorithms"""

    def test_bubble_sort_empty(self):
        assert bubble_sort([]) == []

    def test_bubble_sort_single(self):
        assert bubble_sort([1]) == [1]

    def test_bubble_sort_sorted(self):
        assert bubble_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_bubble_sort_reverse(self):
        assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_bubble_sort_duplicates(self):
        assert bubble_sort([3, 1, 4, 1, 5, 9, 2, 6, 5]) == [1, 1, 2, 3, 4, 5, 5, 6, 9]

    def test_selection_sort_empty(self):
        assert selection_sort([]) == []

    def test_selection_sort_single(self):
        assert selection_sort([1]) == [1]

    def test_selection_sort_sorted(self):
        assert selection_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_selection_sort_reverse(self):
        assert selection_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_selection_sort_duplicates(self):
        assert selection_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_insertion_sort_empty(self):
        assert insertion_sort([]) == []

    def test_insertion_sort_single(self):
        assert insertion_sort([1]) == [1]

    def test_insertion_sort_sorted(self):
        assert insertion_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_insertion_sort_reverse(self):
        assert insertion_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_merge_sort_empty(self):
        assert merge_sort([]) == []

    def test_merge_sort_single(self):
        assert merge_sort([1]) == [1]

    def test_merge_sort_sorted(self):
        assert merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_merge_sort_reverse(self):
        assert merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_merge_sort_duplicates(self):
        assert merge_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_quick_sort_empty(self):
        assert quick_sort([]) == []

    def test_quick_sort_single(self):
        assert quick_sort([1]) == [1]

    def test_quick_sort_sorted(self):
        assert quick_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_quick_sort_reverse(self):
        assert quick_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_quick_sort_duplicates(self):
        assert quick_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_heap_sort_empty(self):
        assert heap_sort([]) == []

    def test_heap_sort_single(self):
        assert heap_sort([1]) == [1]

    def test_heap_sort_sorted(self):
        assert heap_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_heap_sort_reverse(self):
        assert heap_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_heap_sort_duplicates(self):
        assert heap_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_shell_sort_empty(self):
        assert shell_sort([]) == []

    def test_shell_sort_single(self):
        assert shell_sort([1]) == [1]

    def test_shell_sort_sorted(self):
        assert shell_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_shell_sort_reverse(self):
        assert shell_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_counting_sort_empty(self):
        assert counting_sort([]) == []

    def test_counting_sort_single(self):
        assert counting_sort([1]) == [1]

    def test_counting_sort_sorted(self):
        assert counting_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_counting_sort_reverse(self):
        assert counting_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_counting_sort_duplicates(self):
        assert counting_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_radix_sort_empty(self):
        assert radix_sort([]) == []

    def test_radix_sort_single(self):
        assert radix_sort([1]) == [1]

    def test_radix_sort_sorted(self):
        assert radix_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_radix_sort_reverse(self):
        assert radix_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_radix_sort_duplicates(self):
        assert radix_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_cocktail_sort_empty(self):
        assert cocktail_sort([]) == []

    def test_cocktail_sort_single(self):
        assert cocktail_sort([1]) == [1]

    def test_cocktail_sort_sorted(self):
        assert cocktail_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_cocktail_sort_reverse(self):
        assert cocktail_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_cocktail_sort_duplicates(self):
        assert cocktail_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_comb_sort_empty(self):
        assert comb_sort([]) == []

    def test_comb_sort_single(self):
        assert comb_sort([1]) == [1]

    def test_comb_sort_sorted(self):
        assert comb_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_comb_sort_reverse(self):
        assert comb_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_comb_sort_duplicates(self):
        assert comb_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_tim_sort_empty(self):
        assert tim_sort([]) == []

    def test_tim_sort_single(self):
        assert tim_sort([1]) == [1]

    def test_tim_sort_sorted(self):
        assert tim_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_tim_sort_reverse(self):
        assert tim_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_tim_sort_duplicates(self):
        assert tim_sort([3, 1, 4, 1, 5]) == [1, 1, 3, 4, 5]

    def test_tim_sort_large_array(self):
        import random

        arr = [random.randint(0, 10000) for _ in range(1000)]
        assert tim_sort(arr.copy()) == sorted(arr)


class TestAlgorithmComplexity:
    """Tests para verificar la complejidad algorítmica"""

    def test_sorting_algorithms_correctness_on_large_input(self):
        """Verifica que los algoritmos funcionen correctamente con arrays grandes"""
        import random

        large_arr = [random.randint(0, 10000) for _ in range(1000)]
        expected = sorted(large_arr)

        assert bubble_sort(large_arr.copy()) == expected
        assert merge_sort(large_arr.copy()) == expected
        assert quick_sort(large_arr.copy()) == expected
        assert heap_sort(large_arr.copy()) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
