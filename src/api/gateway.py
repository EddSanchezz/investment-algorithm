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
import os

from src.api.data import get_records, comparator, volume_analyzer, unifier
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


def create_app():
    """Retorna la instancia de la aplicación Flask para uso externo (ej. gunicorn)."""
    return app


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
