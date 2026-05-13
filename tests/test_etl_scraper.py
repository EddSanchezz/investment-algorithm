"""
Tests unitarios para YahooFallbackFetcher (src.etl.scraper).
Usa mocking para evitar llamadas HTTP reales.
"""

import sys, os
from unittest.mock import patch, Mock
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.etl.scraper import YahooFallbackFetcher


class TestFetchHistoricalData:
    def setup_method(self):
        self.scraper = YahooFallbackFetcher()
        self.start = datetime(2024, 1, 1)
        self.end = datetime(2024, 1, 5)
        self.sample_json = {
            "chart": {
                "result": [{
                    "timestamp": [1704153600, 1704240000],
                    "indicators": {
                        "quote": [{
                            "open": [100.0, 102.0],
                            "high": [105.0, 106.0],
                            "low": [99.0, 101.0],
                            "close": [102.0, 103.0],
                            "volume": [1000, 1200],
                        }]
                    }
                }]
            }
        }

    @patch("requests.Session.get")
    def test_successful_fetch(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = self.sample_json
        mock_get.return_value = mock_resp

        records = self.scraper.fetch_historical_data("VOO", self.start, self.end)
        assert len(records) == 2
        assert records[0]["symbol"] == "VOO"
        assert records[0]["close"] == 102.0

    @patch("requests.Session.get")
    def test_empty_result(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"chart": {"result": []}}
        mock_get.return_value = mock_resp

        records = self.scraper.fetch_historical_data("VOO", self.start, self.end)
        assert records == []

    @patch("requests.Session.get")
    def test_malformed_response(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"chart": {"result": [{"bad": "data"}]}}
        mock_get.return_value = mock_resp

        records = self.scraper.fetch_historical_data("VOO", self.start, self.end)
        assert records == []

    @patch("requests.Session.get")
    def test_filters_none_values(self, mock_get):
        data = {
            "chart": {
                "result": [{
                    "timestamp": [1704153600, 1704240000],
                    "indicators": {
                        "quote": [{
                            "open": [100.0, None],
                            "high": [105.0, None],
                            "low": [99.0, None],
                            "close": [102.0, None],
                            "volume": [1000, None],
                        }]
                    }
                }]
            }
        }
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = data
        mock_get.return_value = mock_resp

        records = self.scraper.fetch_historical_data("VOO", self.start, self.end)
        assert len(records) == 1

    def test_default_end_date(self):
        scraper = YahooFallbackFetcher()
        records = scraper.fetch_historical_data("VOO", self.start)
        assert isinstance(records, list)

    def test_close_session(self):
        self.scraper.close()
        # Should not raise
        assert True


class TestFetchMultipleAssets:
    def setup_method(self):
        self.scraper = YahooFallbackFetcher()

    @patch("src.etl.scraper.YahooFallbackFetcher.fetch_historical_data")
    def test_multiple_symbols(self, mock_fetch):
        mock_fetch.return_value = [
            {"date": "2024-01-01", "symbol": "VOO", "close": 100.0}
        ]
        records = self.scraper.fetch_multiple_assets(["VOO", "IVV"])
        assert len(records) == 2
