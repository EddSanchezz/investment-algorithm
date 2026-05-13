"""
API Gateway - API REST del proyecto.
Proporciona endpoints para el análisis algorítmico financiero.
Endpoints de similitud, patrones, volatilidad, dashboard y reportes.
"""

from flask import Flask, jsonify, request, render_template
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.unifier import DataUnifier
from src.sorting.comparator import SortingComparator
from src.services.volume_analyzer import VolumeAnalyzer

app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))

DATA_FILE = "data/processed/unified_data.csv"
unifier = DataUnifier()
comparator = SortingComparator()
volume_analyzer = VolumeAnalyzer()

records_cache = None


def get_records():
    """Carga y cachea los registros unificados."""
    global records_cache
    if records_cache is None:
        if os.path.exists(DATA_FILE):
            records_cache = unifier.load_from_csv(DATA_FILE)
        else:
            records_cache = []
    return records_cache


@app.route("/api/health", methods=["GET"])
def health_check():
    """Endpoint de verificación de estado."""
    return jsonify({"status": "healthy", "message": "Investment Algorithm API"})


@app.route("/api/records", methods=["GET"])
def get_all_records():
    """Retorna todos los registros."""
    records = get_records()
    limit = request.args.get("limit", type=int)
    if limit:
        records = records[:limit]
    return jsonify({"total": len(records), "records": records})


@app.route("/api/records/sorted", methods=["GET"])
def get_sorted_records():
    """Retorna registros ordenados por fecha y precio de cierre."""
    records = get_records()
    sort_key = request.args.get("key", "date")

    prepared = comparator.prepare_data(records, sort_key)
    sorted_records = comparator.algorithms["TimSort"](prepared)

    return jsonify(
        {
            "sort_key": sort_key,
            "total": len(sorted_records),
            "records": sorted_records[:100],
        }
    )


@app.route("/api/volume/top", methods=["GET"])
def get_top_volume_days():
    """Retorna los días con mayor volumen de negociación."""
    records = get_records()
    n = request.args.get("n", 15, type=int)

    top_days = volume_analyzer.top_volume_days_ascending(records, n)

    return jsonify({"top_n": n, "days": top_days})


@app.route("/api/sorting/benchmark", methods=["GET"])
def run_benchmark():
    """Ejecuta el benchmark de algoritmos de ordenamiento."""
    records = get_records()

    if len(records) > 1000:
        records = records[:1000]

    results = comparator.compare_all(records, runs=1)

    for r in results:
        r["average_time"] = r["average_time"] * 1000
        r["min_time"] = r["min_time"] * 1000
        r["max_time"] = r["max_time"] * 1000

    return jsonify({"dataset_size": len(records), "results": results})


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Retorna estadísticas del dataset."""
    records = get_records()
    stats = unifier.generate_statistics(records)
    volume_stats = volume_analyzer.get_volume_statistics(records)

    return jsonify({"dataset": stats, "volume": volume_stats})


from src.api.routes.similarity import similarity_bp
from src.api.routes.patterns import patterns_bp
from src.api.routes.dashboard import dashboard_bp
from src.api.routes.reports import reports_bp
app.register_blueprint(similarity_bp)
app.register_blueprint(patterns_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(reports_bp)

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
