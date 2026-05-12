"""
Rutas del Dashboard — API REST para candlestick, SMA y datos del dashboard.
"""

from flask import Blueprint, jsonify, request
from src.api.gateway import get_records
from src.services.similarity import SimilarityAnalyzer
from src.services.reporting.technical import simple_moving_average

dashboard_bp = Blueprint("dashboard", __name__)
analyzer = SimilarityAnalyzer()


@dashboard_bp.route("/api/candlestick", methods=["GET"])
def get_candlestick():
    """
    Retorna datos OHLC + SMA para un activo (para gráfico de velas).

    Parámetros query:
        symbol (str): Símbolo del activo
        smas (str): Ventanas SMA separadas por coma (ej: "20,50")
        limit (int): Máximo de registros a retornar

    Ejemplo:
        GET /api/candlestick?symbol=VOO&smas=20,50&limit=252
    """
    symbol = request.args.get("symbol", "").upper()
    smas_param = request.args.get("smas", "20,50")
    limit = request.args.get("limit", type=int)

    if not symbol:
        return jsonify({"error": "Se requiere el parámetro symbol"}), 400

    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    sym_records = [r for r in records if r["symbol"] == symbol]
    if not sym_records:
        return jsonify({"error": f"No hay datos para {symbol}"}), 404

    sym_records.sort(key=lambda x: x["date"])

    if limit and limit > 0:
        sym_records = sym_records[-limit:]

    dates = []
    ohlc = []
    for r in sym_records:
        dates.append(r["date"])
        ohlc.append({
            "open": r.get("open"),
            "high": r.get("high"),
            "low": r.get("low"),
            "close": r.get("close"),
            "volume": r.get("volume"),
        })

    prices = [r.get("close") for r in sym_records]
    sma_results = {}

    try:
        windows = [int(w.strip()) for w in smas_param.split(",")]
        for w in windows:
            if w > 0:
                sma_results[f"sma_{w}"] = simple_moving_average(prices, w)
    except ValueError:
        pass

    return jsonify({
        "symbol": symbol,
        "dates": dates,
        "ohlc": ohlc,
        "smas": sma_results,
        "total": len(dates),
    })


@dashboard_bp.route("/api/dashboard/summary", methods=["GET"])
def dashboard_summary():
    """
    Retorna un resumen del dashboard con estadísticas clave.

    Incluye: total activos, total registros, rango fechas,
    activo más y menos volátil, mejores correlaciones.
    """
    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    from src.services.patterns import VolatilityAnalyzer
    va = VolatilityAnalyzer()

    symbols = sorted(set(r["symbol"] for r in records))
    ranking = va.ranking(records, symbols)
    corr = analyzer.compute_correlation_matrix(records, symbols)

    highest_pair = None
    lowest_pair = None
    if len(symbols) >= 2:
        max_corr = -1
        min_corr = 1
        mat = corr["matrix"]
        syms = corr["symbols"]
        for i in range(len(syms)):
            for j in range(i + 1, len(syms)):
                c = mat[i][j]
                if c > max_corr:
                    max_corr = c
                    highest_pair = (syms[i], syms[j], c)
                if c < min_corr:
                    min_corr = c
                    lowest_pair = (syms[i], syms[j], c)

    return jsonify({
        "total_symbols": len(symbols),
        "total_records": len(records),
        "date_range": {
            "start": min(r["date"] for r in records),
            "end": max(r["date"] for r in records),
        },
        "volatility_summary": ranking["summary"],
        "correlation": {
            "highest": {
                "pair": f"{highest_pair[0]}-{highest_pair[1]}" if highest_pair else None,
                "value": round(highest_pair[2], 4) if highest_pair else None,
            } if highest_pair else None,
            "lowest": {
                "pair": f"{lowest_pair[0]}-{lowest_pair[1]}" if lowest_pair else None,
                "value": round(lowest_pair[2], 4) if lowest_pair else None,
            } if lowest_pair else None,
        },
    })
