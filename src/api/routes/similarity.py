"""
Rutas de Similitud — API REST para algoritmos de comparación de activos.
"""

from flask import Blueprint, jsonify, request
from src.services.similarity import SimilarityAnalyzer
from src.etl.unifier import DataUnifier

similarity_bp = Blueprint("similarity", __name__)
analyzer = SimilarityAnalyzer()
_unifier = DataUnifier()


@similarity_bp.route("/api/similarity", methods=["GET"])
def compare_symbols():
    """
    Calcula las 4 métricas de similitud entre dos activos.

    Parámetros query:
        s1 (str): Primer símbolo (ej: VOO)
        s2 (str): Segundo símbolo (ej: SPY)

    Retorna:
        JSON con resultados de los 4 algoritmos y datos para gráfica

    Ejemplo:
        GET /api/similarity?s1=VOO&s2=SPY
    """
    s1 = request.args.get("s1", "").upper()
    s2 = request.args.get("s2", "").upper()

    if not s1 or not s2:
        return jsonify({"error": "Se requieren los parámetros s1 y s2"}), 400

    from src.api.gateway import get_records
    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles. Ejecute el pipeline ETL primero."}), 404

    result = analyzer.compare(records, s1, s2)

    if "error" in result:
        return jsonify(result), 404

    return jsonify(result)


@similarity_bp.route("/api/similarity/symbols", methods=["GET"])
def list_symbols():
    """Retorna la lista de símbolos disponibles con mercado de origen."""
    from src.api.gateway import get_records
    records = get_records()
    if not records:
        return jsonify({"symbols": [], "market_map": {}})

    symbols = sorted(set(r["symbol"] for r in records))
    market_map = {
        sym: "bvc" if _unifier._is_colombian(sym) else "nyse"
        for sym in symbols
    }
    return jsonify({"symbols": symbols, "market_map": market_map})


@similarity_bp.route("/api/correlation-matrix", methods=["GET"])
def correlation_matrix():
    """
    Calcula la matriz de correlación de Pearson para todos los activos.

    Retorna:
        JSON con matriz de correlación n×n y lista de símbolos

    Ejemplo:
        GET /api/correlation-matrix
    """
    from src.api.gateway import get_records
    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    symbols = sorted(set(r["symbol"] for r in records))
    result = analyzer.compute_correlation_matrix(records, symbols)

    return jsonify(result)
