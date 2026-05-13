"""
Tests unitarios para FinancialDataFetcher con Multi-Source.
Usa mocking para evitar llamadas HTTP reales.
"""

import sys, os, json
from unittest.mock import patch, Mock
from datetime import datetime
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.etl.fetcher import FinancialDataFetcher
from src.etl.providers.multi_source import MultiSourceFetcher


class TestFinancialDataFetcher:
    def setup_method(self):
        self.fetcher = FinancialDataFetcher(logger=lambda msg: None)
        self.start = datetime(2024, 1, 1)
        self.end = datetime(2024, 1, 5)

    def test_initialization(self):
        assert self.fetcher._fetcher is not None

    def test_fetch_historical_data_returns_list(self):
        with patch.object(self.fetcher._fetcher, 'fetch', return_value=[]):
            records = self.fetcher.fetch_historical_data("VOO", self.start, self.end)
            assert isinstance(records, list)

    def test_fetch_multiple_assets_returns_list(self):
        with patch.object(self.fetcher._fetcher, 'fetch_multiple', return_value=[]):
            records = self.fetcher.fetch_multiple_assets(["VOO", "SPY"], 5)
            assert isinstance(records, list)

    def test_save_to_csv_creates_file(self, tmp_path):
        records = [
            {"date": "2024-01-01", "symbol": "VOO", "open": 100.0, "high": 105.0,
             "low": 99.0, "close": 102.0, "volume": 1000}
        ]
        csv_path = tmp_path / "test.csv"
        self.fetcher.save_to_csv(records, str(csv_path))
        assert csv_path.exists()

    def test_save_to_csv_empty_records(self, capsys):
        self.fetcher.save_to_csv([], "data/test.csv")
        captured = capsys.readouterr()
        assert "No hay datos" in captured.out


class TestMultiSourceFetcher:
    def setup_method(self):
        self.fetcher = MultiSourceFetcher(logger=lambda msg: None)

    def test_providers_initialized(self):
        assert len(self.fetcher.providers) == 5

    def test_provider_names(self):
        names = [p.name for p in self.fetcher.providers]
        assert "Tiingo API" in names
        assert "Yahoo Finance API" in names
        assert "Alpha Vantage" in names
        assert "Web Scraper (5 sitios)" in names
        assert "Binance" in names

    def test_fetch_returns_list(self):
        with patch.object(self.fetcher.providers[0], 'fetch', return_value=[]):
            records = self.fetcher.fetch("VOO", datetime(2024, 1, 1), datetime(2024, 1, 5))
            assert isinstance(records, list)

    def test_close_calls_provider_close(self):
        for provider in self.fetcher.providers:
            with patch.object(provider, 'close') as mock_close:
                self.fetcher.close()
                mock_close.assert_called_once()