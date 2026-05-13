"""
Rutas del Dashboard — API REST para candlestick, SMA, cleaning stats y datos del dashboard.
"""

from flask import Blueprint, jsonify, request
from src.services.similarity import SimilarityAnalyzer
from src.services.reporting.technical import simple_moving_average
import os

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

    from src.api.gateway import get_records
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
    from src.api.gateway import get_records
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


@dashboard_bp.route("/api/etl/cleaning-stats", methods=["GET"])
def cleaning_stats():
    """
    Retorna estadísticas de limpieza ETL y calidad de datos.

    Incluye:
    - Proveedores de datos disponibles
    - Calidad: nulos por campo, registros por símbolo
    - Cobertura temporal por mercado
    """
    from src.api.gateway import get_records
    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles"}), 404

    total = len(records)
    symbols = sorted(set(r["symbol"] for r in records))
    dates = sorted(set(r["date"] for r in records))

    nulls = {"open": 0, "high": 0, "low": 0, "close": 0, "volume": 0}
    for r in records:
        for f in nulls:
            if r.get(f) is None:
                nulls[f] += 1

    per_symbol = {}
    for s in symbols:
        sym_recs = [r for r in records if r["symbol"] == s]
        sym_dates = sorted(set(r["date"] for r in sym_recs))
        sym_nulls = sum(1 for r in sym_recs if r.get("close") is None)
        per_symbol[s] = {
            "records": len(sym_recs),
            "trading_days": len(sym_dates),
            "null_closes": sym_nulls,
            "date_from": sym_dates[0] if sym_dates else None,
            "date_to": sym_dates[-1] if sym_dates else None,
        }

    raw_path = "data/raw/raw_data.csv"
    raw_exists = os.path.exists(raw_path)
    raw_records = 0
    if raw_exists:
        import csv
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_records = sum(1 for _ in csv.DictReader(f))

    records_diff = raw_records - total if raw_records > 0 else None

    bvc_symbols = [s for s in symbols if s in {"ECOPETROL", "ISA", "GEB", "NUTRESA"}]
    nyse_symbols = [s for s in symbols if s not in bvc_symbols]

    return jsonify({
        "providers": {
            "available": ["Tiingo API", "Yahoo Finance API", "Alpha Vantage", "Web Scraper (5 sitios)", "Binance"],
            "active": "Multi-Source con fallback automático",
        },
        "quality": {
            "total_records": total,
            "raw_records": raw_records,
            "records_removed": records_diff if records_diff else "N/A",
            "unique_symbols": len(symbols),
            "trading_days": len(dates),
            "date_range": {"start": dates[0], "end": dates[-1]},
            "nulls_by_field": nulls,
            "nulls_percentage": {k: round(v / total * 100, 2) for k, v in nulls.items()},
            "symbols_bvc": len(bvc_symbols),
            "symbols_nyse": len(nyse_symbols),
        },
        "per_symbol": per_symbol,
    })
