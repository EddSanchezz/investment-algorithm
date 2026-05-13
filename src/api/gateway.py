"""
API Gateway — Punto de entrada de la aplicación web Flask.

Renderiza las páginas HTML y expone endpoints REST básicos.
Los endpoints de similitud, patrones, dashboard y reportes están
registrados como Blueprints en src/api/routes/.

Arquitectura:
    gateway.py (Flask + rutas propias)
        │
        ├── data.py (get_records, caché, instancias de servicios)
        │
        └── routes/
            ├── similarity.py  → /api/similarity, /api/correlation-matrix
            ├── patterns.py    → /api/patterns, /api/volatility
            ├── dashboard.py   → /api/candlestick, /api/dashboard/summary, /api/etl/cleaning-stats
            └── reports.py     → /api/report/generate

Complejidad: O(1) para enrutamiento; la carga de datos (O(n)) está en data.py.
"""

from flask import Flask, jsonify, request, render_template
import json
import os
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timezone

from src.api.data import get_records, invalidate_cache, comparator, volume_analyzer, unifier
from src.api.routes.similarity import similarity_bp
from src.api.routes.patterns import patterns_bp
from src.api.routes.dashboard import dashboard_bp
from src.api.routes.reports import reports_bp

app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))

app.register_blueprint(similarity_bp)
app.register_blueprint(patterns_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(reports_bp)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REFRESH_STATUS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "refresh_status.json")


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_refresh_status(status, message, command=None, exit_code=None):
    os.makedirs(os.path.dirname(REFRESH_STATUS_FILE), exist_ok=True)
    payload = {
        "status": status,
        "message": message,
        "command": command,
        "exit_code": exit_code,
        "updated_at": _utc_now_iso(),
    }
    with open(REFRESH_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    return payload


def _read_refresh_status():
    if not os.path.exists(REFRESH_STATUS_FILE):
        return {
            "status": "idle",
            "message": "No hay una actualización de datos en curso.",
            "command": None,
            "exit_code": None,
            "updated_at": None,
        }
    with open(REFRESH_STATUS_FILE, encoding="utf-8") as f:
        return json.load(f)


@app.route("/api/health", methods=["GET"])
def health_check():
    """Endpoint de verificación de estado. O(1)."""
    return jsonify({"status": "healthy", "message": "Investment Algorithm API"})


@app.route("/api/records", methods=["GET"])
def get_all_records():
    """Retorna todos los registros. O(n) con límite opcional."""
    records: list = get_records()
    limit: int | None = request.args.get("limit", type=int)
    if limit:
        records = records[:limit]
    return jsonify({"total": len(records), "records": records})


@app.route("/api/records/sorted", methods=["GET"])
def get_sorted_records():
    """Retorna registros ordenados por fecha. O(n log n) — TimSort."""
    records: list = get_records()
    sort_key: str = request.args.get("key", "date")

    prepared: list = comparator.prepare_data(records, sort_key)
    sorted_records: list = comparator.algorithms["TimSort"](prepared)

    return jsonify({"sort_key": sort_key, "total": len(sorted_records), "records": sorted_records[:100]})


@app.route("/api/volume/top", methods=["GET"])
def get_top_volume_days():
    """Retorna los días con mayor volumen. O(n log n) — ordenamiento."""
    records: list = get_records()
    n: int = request.args.get("n", 15, type=int)

    top_days: list = volume_analyzer.top_volume_days_ascending(records, n)

    return jsonify({"top_n": n, "days": top_days})


@app.route("/api/sorting/benchmark", methods=["GET"])
def run_benchmark():
    """Ejecuta benchmark de 12 algoritmos de ordenamiento. O(a × T(n))."""
    records: list = get_records()

    if len(records) > 1000:
        records = records[:1000]

    results: list = comparator.compare_all(records, runs=1)

    for r in results:
        r["average_time"] = r["average_time"] * 1000
        r["min_time"] = r["min_time"] * 1000
        r["max_time"] = r["max_time"] * 1000

    return jsonify({"dataset_size": len(records), "results": results})


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Retorna estadísticas del dataset. O(n)."""
    records: list = get_records()
    stats: dict = unifier.generate_statistics(records)
    volume_stats: dict = volume_analyzer.get_volume_statistics(records)

    return jsonify({"dataset": stats, "volume": volume_stats})


@app.route("/api/refresh-data", methods=["POST"])
def refresh_data():
    """
    Inicia el proceso ETL de descarga y limpieza de datos en segundo plano.
    Retorna inmediatamente sin esperar a que el ETL termine.
    """
    try:
        current_status = _read_refresh_status()
        if current_status["status"] == "running":
            return jsonify(current_status), 409

        task_executable = shutil.which("task")
        command = [task_executable, "run-full"] if task_executable else [
            sys.executable,
            "-m",
            "src.services.main_runner",
            "--force-download",
        ]
        command_label = "task run-full" if task_executable else "python -m src.services.main_runner --force-download"

        _write_refresh_status(
            "running",
            "Obteniendo y procesando datos financieros...",
            command_label,
        )
        process = subprocess.Popen(command, cwd=PROJECT_ROOT)

        def invalidate_when_done():
            exit_code = process.wait()
            if exit_code == 0:
                invalidate_cache()
                _write_refresh_status(
                    "success",
                    "Datos cargados correctamente.",
                    command_label,
                    exit_code,
                )
                print("[*] ETL: Datos actualizados y cache invalidada.")
            else:
                _write_refresh_status(
                    "error",
                    "No se pudieron actualizar los datos. Revisa los logs del servidor.",
                    command_label,
                    exit_code,
                )
                print(f"[!] ETL: Proceso finalizó con código {exit_code}.")

        threading.Thread(target=invalidate_when_done, daemon=True).start()
        print(f"[*] ETL: Proceso iniciado en segundo plano: {' '.join(command)}")
        return jsonify({
            "status": "success",
            "refresh_status": "running",
            "message": "Actualización de datos iniciada.",
            "command": command_label,
            "status_url": "/api/refresh-data/status",
        }), 202
    except Exception as e:
        _write_refresh_status(
            "error",
            f"No se pudo iniciar la actualización de datos: {e}",
        )
        print(f"[!] ETL: Error al iniciar proceso de actualización de datos: {e}")
        return jsonify({"status": "error", "message": f"Failed to initiate data refresh: {e}"}), 500


@app.route("/api/refresh-data/status", methods=["GET"])
def refresh_data_status():
    """Retorna el estado del proceso ETL iniciado desde la UI."""
    return jsonify(_read_refresh_status())


# ─── HTML Pages ──────────────────────────────────────────────

@app.route("/")
def index_page():
    """Renderiza la página principal con resumen y estadísticas."""
    return render_template("pages/index.html")


@app.route("/similarity")
def similarity_page():
    """Renderiza la página de comparación de similitud entre activos."""
    return render_template("pages/similarity.html")


@app.route("/patterns")
def patterns_page():
    """Renderiza la página de detección de patrones."""
    return render_template("pages/patterns.html", patterns_page=True)


@app.route("/risk")
def risk_page():
    """Renderiza la página de clasificación de riesgo por volatilidad."""
    return render_template("pages/risk.html")


@app.route("/dashboard")
def dashboard_page():
    """Renderiza el dashboard completo con heatmap, candlestick y exportación PDF."""
    return render_template("pages/dashboard.html")


def create_app(environ=None, start_response=None):
    """
    Retorna la instancia Flask o actúa como WSGI callable.

    Gunicorn permite cargar fábricas con ``module:create_app()``, pero si se
    configura como ``module:create_app`` llama a la función con la firma WSGI.
    Este puente conserva ambos modos para despliegues existentes.
    """
    if environ is not None and start_response is not None:
        return app(environ, start_response)
    return app


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
