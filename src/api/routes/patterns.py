"""
Rutas de Patrones y Volatilidad — API REST para detección de patrones
y análisis de riesgo.

Endpoints:
    GET /api/patterns?symbol=VOO&pattern=consecutive_up    detección de patrones
    GET /api/volatility?symbol=VOO                         métricas de volatilidad
    GET /api/volatility/ranking                            ranking completo de riesgo

Complejidad:
    /api/patterns              O(n) — ventana deslizante
    /api/volatility            O(n) — desviación estándar
    /api/volatility/ranking    O(s × n + s log s) — s = símbolos, n = registros
"""

from typing import List, Dict
from flask import Blueprint, jsonify, request
from src.services.patterns import PatternAnalyzer, VolatilityAnalyzer
from src.api.data import get_records

patterns_bp = Blueprint("patterns", __name__)
pattern_analyzer: PatternAnalyzer = PatternAnalyzer()
volatility_analyzer: VolatilityAnalyzer = VolatilityAnalyzer()


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
    symbol: str = request.args.get("symbol", "").upper()
    pattern: str = request.args.get("pattern", "consecutive_up")
    min_days: int = request.args.get("min_days", 3, type=int)
    threshold: float = request.args.get("threshold", 0.02, type=float)

    if not symbol:
        return jsonify({"error": "Se requiere el parámetro symbol"}), 400

    records: list = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles. Ejecute el pipeline ETL primero."}), 404

    result: dict = pattern_analyzer.analyze(records, symbol, pattern, min_days, threshold)
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
    symbol: str = request.args.get("symbol", "").upper()

    if not symbol:
        return jsonify({"error": "Se requiere el parámetro symbol"}), 400

    records: list = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    result: dict = volatility_analyzer.analyze(records, symbol)
    return jsonify(result)


@patterns_bp.route("/api/volatility/ranking", methods=["GET"])
def get_volatility_ranking():
    """
    Ranking completo de todos los activos ordenados por volatilidad ascendente.

    Ejemplo:
        GET /api/volatility/ranking
    """
    records: list = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    symbols: list = request.args.getlist("symbols") or None
    result: dict = volatility_analyzer.ranking(records, symbols)
    return jsonify(result)
