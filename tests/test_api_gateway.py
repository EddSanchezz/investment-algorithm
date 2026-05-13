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


def test_create_app_accepts_wsgi_call_signature():
    from werkzeug.test import EnvironBuilder
    from src.api.gateway import create_app

    environ = EnvironBuilder(path="/", method="HEAD").get_environ()
    status = []

    response = create_app(environ, lambda value, _headers, _exc_info=None: status.append(value))
    if hasattr(response, "close"):
        response.close()

    assert status[0].startswith("200")


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


class TestRefreshDataEndpoint:
    def test_refresh_data_starts_background_process(self, client, monkeypatch):
        import src.api.gateway as gateway

        started = {}

        class FakeProcess:
            def wait(self):
                return 0

        class FakeThread:
            def __init__(self, target, daemon):
                self.target = target
                self.daemon = daemon

            def start(self):
                self.target()

        def fake_popen(command, cwd):
            started["command"] = command
            started["cwd"] = cwd
            return FakeProcess()

        monkeypatch.setattr(gateway.shutil, "which", lambda _name: None)
        monkeypatch.setattr(gateway.subprocess, "Popen", fake_popen)
        monkeypatch.setattr(gateway.threading, "Thread", FakeThread)

        resp = client.post("/api/refresh-data")

        assert resp.status_code == 202
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["command"] == "python -m src.services.main_runner --force-download"
        assert started["command"][-3:] == ["-m", "src.services.main_runner", "--force-download"]


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

    def test_similarity_group_missing_symbols(self, client):
        resp = client.get("/api/similarity/group")
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_patterns_blueprint_missing_param(self, client):
        resp = client.get("/api/patterns")
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_patterns_blueprint_new_pattern(self, client):
        resp = client.get("/api/patterns?symbol=VOO&pattern=breakout_up&window=20")
        assert resp.status_code in (200, 404)

    def test_risk_blueprint_ranking(self, client):
        resp = client.get("/api/volatility/ranking")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "ranking" in data
        assert "summary" in data

    def test_dashboard_blueprint_missing_param(self, client):
        resp = client.get("/api/candlestick")
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data
