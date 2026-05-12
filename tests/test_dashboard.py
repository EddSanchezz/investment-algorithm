"""
Tests unitarios para el dashboard (SMA, endpoints, PDF).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.reporting.technical import simple_moving_average


class TestSMA:
    def test_basic_sma(self):
        prices = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = simple_moving_average(prices, 3)
        assert len(result) == 5
        assert result[0] is None
        assert result[1] is None
        assert result[2] == 2.0
        assert result[3] == 3.0
        assert result[4] == 4.0

    def test_sma_single_window(self):
        prices = [10.0, 20.0, 30.0]
        result = simple_moving_average(prices, 1)
        assert result == [10.0, 20.0, 30.0]

    def test_sma_larger_than_data(self):
        prices = [1.0, 2.0]
        result = simple_moving_average(prices, 5)
        assert result == [None, None]

    def test_sma_empty(self):
        result = simple_moving_average([], 3)
        assert result == []

    def test_sma_with_none(self):
        prices = [1.0, None, 3.0, 4.0, 5.0]
        result = simple_moving_average(prices, 3)
        assert len(result) == 5
        assert result[0] is None
        assert result[1] is None
        assert result[2] is not None

    def test_sma_window_20(self):
        prices = [float(i) for i in range(1, 101)]
        result = simple_moving_average(prices, 20)
        assert len(result) == 100
        assert result[18] is None
        assert result[19] == sum(range(1, 21)) / 20
        assert result[99] == sum(range(81, 101)) / 20
