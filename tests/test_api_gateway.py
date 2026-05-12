"""
Tests unitarios para la API Gateway (src.api.gateway).
Usa Flask test client para probar endpoints HTTP.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


@pytest.fixture
def client():
    from src.api.gateway import app
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "healthy"

    def test_health_has_message(self, client):
        resp = client.get("/api/health")
        data = resp.get_json()
        assert "message" in data


class TestRecordsEndpoint:
    def test_records_returns_json(self, client):
        resp = client.get("/api/records")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total" in data
        assert "records" in data

    def test_records_with_limit(self, client):
        resp = client.get("/api/records?limit=5")
        assert resp.status_code == 200


class TestStatisticsEndpoint:
    def test_statistics_returns_json(self, client):
        resp = client.get("/api/statistics")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "dataset" in data


class TestVolumeEndpoint:
    def test_volume_top_returns_json(self, client):
        resp = client.get("/api/volume/top")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "top_n" in data
        assert "days" in data


class TestBenchmarkEndpoint:
    def test_benchmark_returns_json(self, client):
        resp = client.get("/api/sorting/benchmark")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data


class TestSortedRecordsEndpoint:
    def test_sorted_records(self, client):
        resp = client.get("/api/records/sorted?key=date")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "sort_key" in data


class TestHTMLPages:
    def test_index_page(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"html" in resp.data.lower() or b"HTML" in resp.data

    def test_similarity_page(self, client):
        resp = client.get("/similarity")
        assert resp.status_code == 200

    def test_patterns_page(self, client):
        resp = client.get("/patterns")
        assert resp.status_code == 200

    def test_risk_page(self, client):
        resp = client.get("/risk")
        assert resp.status_code == 200

    def test_dashboard_page(self, client):
        resp = client.get("/dashboard")
        assert resp.status_code == 200


class TestBlueprintRoutes:
    def test_similarity_blueprint(self, client):
        resp = client.get("/api/similarity/symbols")
        assert resp.status_code == 200

    def test_patterns_blueprint_missing_param(self, client):
        resp = client.get("/api/patterns")
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_risk_blueprint_no_data(self, client):
        resp = client.get("/api/volatility/ranking")
        # 404 because no data file exists in test env
        assert resp.status_code == 404

    def test_dashboard_blueprint_missing_param(self, client):
        resp = client.get("/api/candlestick")
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data
