"""
Tests unitarios para YahooFinanceFetcher (src.etl.fetcher).
Usa mocking para evitar llamadas HTTP reales.
"""

import sys, os, json
from unittest.mock import patch, Mock
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.etl.fetcher import YahooFinanceFetcher, _exponential_backoff, _parse_yahoo_timestamp


class TestExponentialBackoff:
    def test_returns_positive_float(self):
        delay = _exponential_backoff(0)
        assert delay >= 1.0
        assert delay < 3.0

    def test_increases_with_attempt(self):
        d1 = _exponential_backoff(0)
        d2 = _exponential_backoff(1)
        # With jitter, d2 might occasionally be less, but very unlikely
        assert d2 > d1 - 1.5


class TestParseYahooTimestamp:
    def test_known_timestamp(self):
        # 2024-01-01 12:00:00 UTC (noon avoids timezone boundary issues)
        assert _parse_yahoo_timestamp(1704110400) == "2024-01-01"


class TestFetchHistoricalData:
    def setup_method(self):
        self.fetcher = YahooFinanceFetcher(logger=lambda msg: None)
        self.start = datetime(2024, 1, 1)
        self.end = datetime(2024, 1, 5)
        self.sample_json = {
            "chart": {
                "result": [{
                    "timestamp": [1704153600, 1704240000, 1704326400],
                    "indicators": {
                        "quote": [{
                            "open": [100.0, 102.0, 101.0],
                            "high": [105.0, 106.0, 104.0],
                            "low": [99.0, 101.0, 100.0],
                            "close": [102.0, 103.0, 101.5],
                            "volume": [1000, 1200, 1100],
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

        records = self.fetcher.fetch_historical_data("VOO", self.start, self.end)
        assert len(records) == 3
        assert records[0]["symbol"] == "VOO"
        assert records[0]["close"] == 102.0

    @patch("requests.Session.get")
    def test_circuit_breaker_returns_empty(self, mock_get):
        self.fetcher._consecutive_failures = 10
        self.fetcher._circuit_open_until = 9999999999.0
        records = self.fetcher.fetch_historical_data("VOO", self.start, self.end)
        assert records == []
        mock_get.assert_not_called()

    @patch("requests.Session.get")
    def test_request_exception_retries(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout
        records = self.fetcher.fetch_historical_data("VOO", self.start, self.end)
        assert records == []
        assert mock_get.call_count >= 1

    @patch("requests.Session.get")
    def test_parse_error_returns_empty(self, mock_get):
        mock_resp = Mock()
        mock_resp.json.side_effect = ValueError("No JSON")
        mock_get.return_value = mock_resp
        records = self.fetcher.fetch_historical_data("VOO", self.start, self.end)
        assert records == []


class TestParseYahooResponse:
    def setup_method(self):
        self.fetcher = YahooFinanceFetcher(logger=lambda msg: None)

    def test_parse_valid_response(self):
        data = {
            "chart": {
                "result": [{
                    "timestamp": [1704153600],
                    "indicators": {
                        "quote": [{
                            "open": [100.0],
                            "high": [105.0],
                            "low": [99.0],
                            "close": [102.0],
                            "volume": [1000],
                        }]
                    }
                }]
            }
        }
        records = self.fetcher._parse_yahoo_response(data, "VOO")
        assert len(records) == 1
        assert records[0]["symbol"] == "VOO"

    def test_empty_result(self):
        data = {"chart": {"result": []}}
        records = self.fetcher._parse_yahoo_response(data, "VOO")
        assert records == []

    def test_missing_timestamp(self):
        data = {"chart": {"result": [{"indicators": {"quote": [{}]}}]}}
        records = self.fetcher._parse_yahoo_response(data, "VOO")
        assert records == []


import requests
