"""
Rutas de Patrones y Volatilidad — API REST para detección de patrones
y análisis de riesgo.
"""

from flask import Blueprint, jsonify, request
from src.api.gateway import get_records
from src.services.patterns import PatternAnalyzer, VolatilityAnalyzer

patterns_bp = Blueprint("patterns", __name__)
pattern_analyzer = PatternAnalyzer()
volatility_analyzer = VolatilityAnalyzer()


@patterns_bp.route("/api/patterns", methods=["GET"])
def detect_pattern():
    """
    Detecta patrones en un activo usando ventana deslizante.

    Parámetros query:
        symbol (str): Símbolo del activo
        pattern (str): Tipo de patrón ("consecutive_up" o "gap_up")
        min_days (int): Días consecutivos (default: 3, solo consecutive_up)
        threshold (float): Umbral de gap (default: 0.02, solo gap_up)

    Ejemplo:
        GET /api/patterns?symbol=VOO&pattern=consecutive_up&min_days=3
        GET /api/patterns?symbol=ECOPETROL&pattern=gap_up&threshold=0.02
    """
    symbol = request.args.get("symbol", "").upper()
    pattern = request.args.get("pattern", "consecutive_up")
    min_days = request.args.get("min_days", 3, type=int)
    threshold = request.args.get("threshold", 0.02, type=float)

    if not symbol:
        return jsonify({"error": "Se requiere el parámetro symbol"}), 400

    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles. Ejecute el pipeline ETL primero."}), 404

    result = pattern_analyzer.analyze(records, symbol, pattern, min_days, threshold)
    return jsonify(result)


@patterns_bp.route("/api/volatility", methods=["GET"])
def get_volatility():
    """
    Calcula métricas de volatilidad para un activo.

    Parámetros query:
        symbol (str): Símbolo del activo

    Ejemplo:
        GET /api/volatility?symbol=VOO
    """
    symbol = request.args.get("symbol", "").upper()

    if not symbol:
        return jsonify({"error": "Se requiere el parámetro symbol"}), 400

    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    result = volatility_analyzer.analyze(records, symbol)
    return jsonify(result)


@patterns_bp.route("/api/volatility/ranking", methods=["GET"])
def get_volatility_ranking():
    """
    Ranking completo de todos los activos ordenados por volatilidad ascendente.

    Ejemplo:
        GET /api/volatility/ranking
    """
    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    symbols = request.args.getlist("symbols")
    if not symbols:
        symbols = None

    result = volatility_analyzer.ranking(records, symbols)
    return jsonify(result)
