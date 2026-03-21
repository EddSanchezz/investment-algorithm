"""
API Gateway - API REST simple para el proyecto.
Proporciona endpoints para acceder a los resultados del análisis.
"""

from flask import Flask, jsonify, request
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.unifier import DataUnifier
from src.sorting.comparator import SortingComparator
from src.services.volume_analyzer import VolumeAnalyzer

app = Flask(__name__)

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

    return jsonify({"dataset_size": len(records), "results": results})


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Retorna estadísticas del dataset."""
    records = get_records()
    stats = unifier.generate_statistics(records)
    volume_stats = volume_analyzer.get_volume_statistics(records)

    return jsonify({"dataset": stats, "volume": volume_stats})


def create_app():
    """Factory function para crear la aplicación Flask."""
    return app


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
