"""
Rutas de Similitud — API REST para algoritmos de comparación de activos.

Endpoints:
    GET /api/similarity?s1=VOO&s2=SPY                 4 métricas de similitud
    GET /api/similarity/group?symbols=VOO&symbols=SPY comparación multi-activo
    GET /api/similarity/symbols                       lista de símbolos disponibles
    GET /api/correlation-matrix                       matriz de correlación n×n

Complejidad:
    /api/similarity           O(n) — dominado por la comparación de series
    /api/similarity/group     O(p × n + s²) — p = pares comparados, s = símbolos
    /api/similarity/symbols   O(n) — para listar símbolos únicos
    /api/correlation-matrix   O(s² × n) — s = símbolos, n = registros
"""

from typing import Any, Dict

from flask import Blueprint, jsonify, request

from src.api.data import get_records
from src.services.similarity import SimilarityAnalyzer

similarity_bp = Blueprint("similarity", __name__)
analyzer: SimilarityAnalyzer = SimilarityAnalyzer()


def _parse_symbol_list() -> list[str]:
    symbols = request.args.getlist("symbols")
    if not symbols:
        csv_symbols = request.args.get("symbols", "")
        if csv_symbols:
            symbols = [symbol.strip() for symbol in csv_symbols.split(",") if symbol.strip()]
    return symbols


@similarity_bp.route("/api/similarity", methods=["GET"])
def compare_symbols():
    """
    Calcula las 4 métricas de similitud entre dos activos o procesa un grupo.

    Parámetros query:
        s1 (str): Primer símbolo (ej: VOO)
        s2 (str): Segundo símbolo (ej: SPY)
        symbols (list[str]): Lista opcional para comparación multi-activo
        window (int): Cantidad de puntos recientes a considerar
    """
    symbols = _parse_symbol_list()
    window = request.args.get("window", type=int)

    records: list = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles. Ejecute el pipeline ETL primero."}), 404

    if symbols:
        result: Dict[str, Any] = analyzer.compare_many(records, symbols, max_points=window or 252)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)

    s1: str = request.args.get("s1", "").upper()
    s2: str = request.args.get("s2", "").upper()
    if not s1 or not s2:
        return jsonify({"error": "Se requieren los parámetros s1 y s2"}), 400

    result: Dict[str, Any] = analyzer.compare(records, s1, s2, max_points=window)
    if "error" in result:
        return jsonify(result), 404

    return jsonify(result)


@similarity_bp.route("/api/similarity/group", methods=["GET"])
def compare_group():
    symbols = _parse_symbol_list()
    if len(symbols) < 2:
        return jsonify({"error": "Se requieren al menos 2 símbolos en el parámetro symbols"}), 400

    records: list = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles. Ejecute el pipeline ETL primero."}), 404

    window = request.args.get("window", 252, type=int)
    result: Dict[str, Any] = analyzer.compare_many(records, symbols, max_points=window)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@similarity_bp.route("/api/similarity/symbols", methods=["GET"])
def list_symbols():
    """Retorna la lista de símbolos disponibles con mercado de origen. O(n)."""
    from src.etl.unifier import DataUnifier

    records: list = get_records()
    if not records:
        return jsonify({"symbols": [], "market_map": {}})

    symbols: list = sorted(set(record["symbol"] for record in records))
    unifier: DataUnifier = DataUnifier()
    market_map: dict = {
        symbol: "bvc" if unifier._is_colombian(symbol) else "nyse"
        for symbol in symbols
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
    records: list = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    symbols: list = sorted(set(record["symbol"] for record in records))
    result: dict = analyzer.compute_correlation_matrix(records, symbols)
    return jsonify(result)
