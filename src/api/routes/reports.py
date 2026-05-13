"""
Rutas de Reportes — API REST para generación y descarga de PDF.
"""

import os
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
from src.services.reporting.pdf_report import PDFReportGenerator
from src.services.similarity import SimilarityAnalyzer
from src.services.patterns import VolatilityAnalyzer
from src.services.reporting.technical import simple_moving_average

reports_bp = Blueprint("reports", __name__)
analyzer = SimilarityAnalyzer()
volatility_analyzer = VolatilityAnalyzer()
OUTPUT_DIR = "outputs"


@reports_bp.route("/api/report/generate", methods=["POST"])
def generate_report():
    """
    Genera un reporte PDF completo con todos los análisis.

    Cuerpo JSON (opcional):
        symbol (str): Activo principal para el candlestick

    Retorna:
        Archivo PDF para descarga
    """
    from src.api.gateway import get_records
    records = get_records()
    if not records:
        return jsonify({"error": "No hay datos disponibles. Ejecute el pipeline ETL primero."}), 404

    data = request.get_json(silent=True) or {}
    symbols = sorted(set(r["symbol"] for r in records))
    main_symbol = data.get("symbol", symbols[0] if symbols else "VOO").upper()
    if main_symbol not in symbols and symbols:
        main_symbol = symbols[0]

    corr_data = analyzer.compute_correlation_matrix(records, symbols)
    ranking = volatility_analyzer.ranking(records, symbols)

    sym_records = [r for r in records if r["symbol"] == main_symbol]
    sym_records.sort(key=lambda x: x["date"])
    dates = [r["date"] for r in sym_records]
    ohlc = [
        {"open": r.get("open"), "high": r.get("high"),
         "low": r.get("low"), "close": r.get("close"), "volume": r.get("volume")}
        for r in sym_records
    ]
    prices = [r.get("close") for r in sym_records]
    sma20 = simple_moving_average(prices, 20)
    sma50 = simple_moving_average(prices, 50)

    top_pair = None
    if len(symbols) >= 2:
        top_corr = -1
        best_pair = None
        mat = corr_data["matrix"]
        syms = corr_data["symbols"]
        for i in range(len(syms)):
            for j in range(i + 1, len(syms)):
                if mat[i][j] > top_corr:
                    top_corr = mat[i][j]
                    best_pair = (syms[i], syms[j])
        if best_pair:
            sim_data = analyzer.compare(records, best_pair[0], best_pair[1])
        else:
            sim_data = {"error": "No hay suficientes activos"}
    else:
        sim_data = {"error": "No hay suficientes activos"}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        pdf = PDFReportGenerator()
        pdf.add_cover_page()
        pdf.add_portfolio_summary(records)
        pdf.add_correlation_matrix(corr_data)
        pdf.add_risk_ranking(ranking)
        pdf.add_candlestick_section(main_symbol, dates, ohlc, sma20, sma50)
        pdf.add_similarity_table(sim_data)
        pdf.save(filepath)

        return send_file(
            filepath,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({"error": f"Error generando PDF: {str(e)}"}), 500
