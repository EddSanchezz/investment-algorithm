"""
Generación de Reporte PDF — Documento técnico con análisis visual y numérico.
Usa ReportLab para la estructura del PDF y matplotlib para gráficos incrustados.
"""

import os
from datetime import datetime
from typing import List, Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak,
)


# Colores institucionales
UQ_COLOR = colors.HexColor("#003366")
ACCENT_COLOR = colors.HexColor("#6c63ff")
GRAY_LIGHT = colors.HexColor("#f3f4f6")
GRAY_MEDIUM = colors.HexColor("#d1d5db")

REPORT_TITLE = "Reporte de Análisis Algorítmico Financiero"
OUTPUT_DIR = "outputs"


def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "CoverTitle", fontName="Helvetica-Bold", fontSize=24,
        textColor=UQ_COLOR, alignment=TA_CENTER, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        "CoverSubtitle", fontName="Helvetica", fontSize=14,
        textColor=colors.HexColor("#4b5563"), alignment=TA_CENTER, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "SectionTitle", fontName="Helvetica-Bold", fontSize=16,
        textColor=UQ_COLOR, spaceBefore=16, spaceAfter=8,
        borderWidth=0, borderPadding=0,
    ))
    styles.add(ParagraphStyle(
        "SectionBody", fontName="Helvetica", fontSize=10,
        textColor=colors.HexColor("#374151"), spaceAfter=6,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        "TableCell", fontName="Helvetica", fontSize=8,
        textColor=colors.HexColor("#374151"),
    ))
    styles.add(ParagraphStyle(
        "TableHeader", fontName="Helvetica-Bold", fontSize=8,
        textColor=colors.white,
    ))
    return styles


def _add_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#9ca3af"))
    canvas.drawString(2 * cm, 1 * cm, REPORT_TITLE)
    canvas.drawRightString(A4[0] - 2 * cm, 1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def _generate_correlation_heatmap(corr_data: Dict) -> str:
    """Genera heatmap de correlación como imagen PNG temporal."""
    symbols = corr_data["symbols"]
    matrix = corr_data["matrix"]
    n = len(symbols)

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(symbols, rotation=45, ha="right", fontsize=7)
    ax.set_yticklabels(symbols, fontsize=7)

    for i in range(n):
        for j in range(n):
            val = matrix[i][j]
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=5, color=color, fontweight="bold")

    fig.colorbar(im, ax=ax, shrink=0.8, label="Correlación de Pearson")
    ax.set_title("Matriz de Correlación — Portafolio Completo", fontsize=12, fontweight="bold")

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "temp_heatmap.png")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _generate_candlestick_chart(
    dates: List[str], ohlc: List[Dict], sma20: List = None, sma50: List = None
) -> str:
    """Genera gráfico de velas con SMA como imagen PNG temporal."""
    fig, ax = plt.subplots(figsize=(10, 5))
    n = len(dates)

    if n == 0:
        plt.close(fig)
        return None

    idx = range(n)
    for i in range(n):
        o = ohlc[i].get("open")
        h = ohlc[i].get("high")
        l = ohlc[i].get("low")
        c = ohlc[i].get("close")
        if None in (o, h, l, c):
            continue
        color = "#22c55e" if c >= o else "#ef4444"
        ax.plot([i, i], [l, h], color=color, linewidth=1)
        ax.plot([i, i], [o, c], color=color, linewidth=4)

    if sma20:
        sma20_vals = [v if v is not None else None for v in sma20]
        valid = [(i, v) for i, v in enumerate(sma20_vals) if v is not None]
        if valid:
            xi, yi = zip(*valid)
            ax.plot(xi, yi, color="#6c63ff", linewidth=1.5, label="SMA-20", alpha=0.8)

    if sma50:
        sma50_vals = [v if v is not None else None for v in sma50]
        valid = [(i, v) for i, v in enumerate(sma50_vals) if v is not None]
        if valid:
            xi, yi = zip(*valid)
            ax.plot(xi, yi, color="#f59e0b", linewidth=1.5, label="SMA-50", alpha=0.8)

    tick_step = max(1, n // 10)
    ax.set_xticks(range(0, n, tick_step))
    ax.set_xticklabels([dates[i] for i in range(0, n, tick_step)], rotation=45, fontsize=8)
    ax.set_ylabel("Precio", fontsize=10)
    ax.set_title("Gráfico de Velas (Candlestick) con Medias Móviles", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "temp_candlestick.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _cleanup_temp_files():
    for f in ["temp_heatmap.png", "temp_candlestick.png"]:
        path = os.path.join(OUTPUT_DIR, f)
        if os.path.exists(path):
            os.remove(path)


class PDFReportGenerator:
    """
    Generador de reportes PDF con análisis algorítmico financiero.

    Uso:
        generator = PDFReportGenerator()
        generator.add_portfolio_summary(records)
        generator.add_correlation_matrix(corr_data)
        generator.add_risk_ranking(ranking_data)
        generator.add_candlestick_chart(candle_data)
        generator.save("outputs/reporte.pdf")
    """

    def __init__(self, title: str = REPORT_TITLE):
        """
        Inicializa el generador de PDF con estilos y elementos vacíos.

        Parámetros:
            title: Título del reporte (default: constante REPORT_TITLE)
        """
        self.title = title
        self.styles = _get_styles()
        self.elements = []
        self._page_width = A4[0] - 4 * cm

    def add_cover_page(self):
        """Agrega portada al reporte."""
        self.elements.append(Spacer(1, 80))
        self.elements.append(Paragraph(
            "Universidad del Quindío", self.styles["CoverSubtitle"]
        ))
        self.elements.append(Paragraph(
            "Programa de Ingeniería de Sistemas y Computación", self.styles["CoverSubtitle"]
        ))
        self.elements.append(Spacer(1, 30))
        self.elements.append(Paragraph(
            self.title, self.styles["CoverTitle"]
        ))
        self.elements.append(Spacer(1, 20))
        self.elements.append(Paragraph(
            "Análisis de Algoritmos — 2026-1", self.styles["CoverSubtitle"]
        ))
        self.elements.append(Spacer(1, 40))
        self.elements.append(Paragraph(
            f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            ParagraphStyle("DateLine", parent=self.styles["CoverSubtitle"], fontSize=10),
        ))
        self.elements.append(PageBreak())

    def add_portfolio_summary(self, records: List[Dict]):
        """Agrega tabla resumen del portafolio."""
        self.elements.append(Paragraph("1. Resumen del Portafolio", self.styles["SectionTitle"]))
        self.elements.append(Paragraph(
            "El análisis cubre los siguientes activos financieros, "
            "incluyendo acciones colombianas y ETFs internacionales.",
            self.styles["SectionBody"]
        ))

        if not records:
            return

        symbols = sorted(set(r["symbol"] for r in records))
        dates = sorted(set(r["date"] for r in records))

        data = [
            ["Total Activos", str(len(symbols))],
            ["Total Registros", str(len(records))],
            ["Rango de Fechas", f"{min(dates)} — {max(dates)}"],
            ["Símbolos", ", ".join(symbols[:8]) + ("..." if len(symbols) > 8 else "")],
        ]
        t = Table(data, colWidths=[4 * cm, self._page_width - 4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), GRAY_LIGHT),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, GRAY_MEDIUM),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        self.elements.append(t)
        self.elements.append(Spacer(1, 12))

    def add_correlation_matrix(self, corr_data: Dict):
        """Agrega matriz de correlación como imagen."""
        self.elements.append(Paragraph(
            "2. Matriz de Correlación", self.styles["SectionTitle"]
        ))
        self.elements.append(Paragraph(
            "La matriz muestra el coeficiente de correlación de Pearson "
            "entre todos los pares de activos. Valores cercanos a 1 indican "
            "alta correlación positiva; cercanos a -1, correlación negativa.",
            self.styles["SectionBody"]
        ))

        img_path = _generate_correlation_heatmap(corr_data)
        if img_path and os.path.exists(img_path):
            img = Image(img_path, width=16 * cm, height=14 * cm)
            self.elements.append(img)
            self.elements.append(Spacer(1, 8))

        if corr_data.get("symbols"):
            n = len(corr_data["symbols"])
            highest = -1
            lowest = 1
            hp = lp = None
            mat = corr_data["matrix"]
            syms = corr_data["symbols"]
            for i in range(n):
                for j in range(i + 1, n):
                    c = mat[i][j]
                    if c > highest:
                        highest = c
                        hp = (syms[i], syms[j], c)
                    if c < lowest:
                        lowest = c
                        lp = (syms[i], syms[j], c)

            details = []
            if hp:
                details.append(f"Mayor correlación: {hp[0]}-{hp[1]} = {hp[2]:.4f}")
            if lp:
                details.append(f"Menor correlación: {lp[0]}-{lp[1]} = {lp[2]:.4f}")
            if details:
                self.elements.append(Paragraph(
                    "<br/>".join(details), self.styles["SectionBody"]
                ))

        self.elements.append(PageBreak())

    def add_risk_ranking(self, ranking_data: Dict):
        """Agrega ranking de riesgo."""
        self.elements.append(Paragraph(
            "3. Ranking de Riesgo por Volatilidad", self.styles["SectionTitle"]
        ))
        self.elements.append(Paragraph(
            "Clasificación de cada activo según su volatilidad histórica anualizada. "
            "Categorías: Conservador (&lt;15%), Moderado (15-30%), Agresivo (&gt;30%).",
            self.styles["SectionBody"]
        ))

        ranking = ranking_data.get("ranking", [])
        if not ranking:
            self.elements.append(Paragraph("Sin datos de volatilidad.", self.styles["SectionBody"]))
            return

        table_data = [
            [Paragraph("Símbolo", self.styles["TableHeader"]),
             Paragraph("Vol. Anual", self.styles["TableHeader"]),
             Paragraph("σ Diaria", self.styles["TableHeader"]),
             Paragraph("Ret. Medio", self.styles["TableHeader"]),
             Paragraph("Categoría", self.styles["TableHeader"])]
        ]

        for r in ranking[:20]:
            category_colors = {
                "conservador": colors.HexColor("#d1fae5"),
                "moderado": colors.HexColor("#fef3c7"),
                "agresivo": colors.HexColor("#fee2e2"),
            }
            bg = category_colors.get(r["risk_category"], colors.white)
            table_data.append([
                Paragraph(r["symbol"], self.styles["TableCell"]),
                Paragraph(f"{r['annualized_volatility_pct']:.1f}%", self.styles["TableCell"]),
                Paragraph(f"{r['daily_std']*100:.3f}%", self.styles["TableCell"]),
                Paragraph(f"{r['mean_daily_return_pct']:.3f}%", self.styles["TableCell"]),
                Paragraph(r["risk_category"].capitalize(), self.styles["TableCell"]),
            ])

        col_w = self._page_width / 5
        t = Table(table_data, colWidths=[col_w] * 5, repeatRows=1)
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), UQ_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, GRAY_MEDIUM),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]
        for i, r in enumerate(ranking[:20], 1):
            cat = r["risk_category"]
            bg = {"conservador": colors.HexColor("#ecfdf5"),
                  "moderado": colors.HexColor("#fffbeb"),
                  "agresivo": colors.HexColor("#fef2f2")}.get(cat, colors.white)
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

        t.setStyle(TableStyle(style_cmds))
        self.elements.append(t)

        summary = ranking_data.get("summary", {})
        if summary.get("categories"):
            cats = summary["categories"]
            self.elements.append(Spacer(1, 8))
            self.elements.append(Paragraph(
                f"Distribución: 🟢 Conservadores: {cats.get('conservador', 0)} | "
                f"🟡 Moderados: {cats.get('moderado', 0)} | "
                f"🔴 Agresivos: {cats.get('agresivo', 0)}",
                self.styles["SectionBody"]
            ))
        self.elements.append(PageBreak())

    def add_candlestick_section(self, symbol: str, dates: List[str],
                                 ohlc: List[Dict], sma20: List = None,
                                 sma50: List = None):
        """Agrega gráfico de velas con SMA."""
        self.elements.append(Paragraph(
            f"4. Análisis Técnico — {symbol}", self.styles["SectionTitle"]
        ))
        self.elements.append(Paragraph(
            f"Gráfico de velas (candlestick) para {symbol} con medias móviles "
            f"simples de 20 y 50 períodos.",
            self.styles["SectionBody"]
        ))

        img_path = _generate_candlestick_chart(dates, ohlc, sma20, sma50)
        if img_path and os.path.exists(img_path):
            img = Image(img_path, width=16 * cm, height=8 * cm)
            self.elements.append(img)

        self.elements.append(PageBreak())

    def add_similarity_table(self, sim_data: Dict):
        """Agrega tabla de similitud."""
        self.elements.append(Paragraph(
            "5. Análisis de Similitud", self.styles["SectionTitle"]
        ))
        self.elements.append(Paragraph(
            "Métricas de similitud calculadas entre pares de activos "
            "usando los 4 algoritmos implementados.",
            self.styles["SectionBody"]
        ))

        if "error" in sim_data:
            self.elements.append(Paragraph(
                f"Datos no disponibles: {sim_data['error']}", self.styles["SectionBody"]
            ))
            return

        table_data = [
            [Paragraph("Métrica", self.styles["TableHeader"]),
             Paragraph("Valor", self.styles["TableHeader"]),
             Paragraph("Complejidad", self.styles["TableHeader"])]
        ]
        metrics = [
            ("Euclidiana", sim_data.get("euclidean", {}).get("distance"), "O(n)"),
            ("Pearson", sim_data.get("pearson", {}).get("correlation"), "O(n)"),
            ("DTW", sim_data.get("dtw", {}).get("distance"), "O(n×m)"),
            ("Coseno", sim_data.get("cosine", {}).get("similarity"), "O(n)"),
        ]
        for name, val, comp in metrics:
            display = f"{val:.6f}" if val is not None else "N/A"
            table_data.append([
                Paragraph(name, self.styles["TableCell"]),
                Paragraph(display, self.styles["TableCell"]),
                Paragraph(comp, self.styles["TableCell"]),
            ])

        col_w = self._page_width / 3
        t = Table(table_data, colWidths=[col_w] * 3, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), UQ_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, GRAY_MEDIUM),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 1), (-1, -1), GRAY_LIGHT),
        ]))
        self.elements.append(t)

    def save(self, filepath: str):
        """Genera y guarda el PDF."""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )
        doc.build(self.elements, onFirstPage=_add_header_footer,
                  onLaterPages=_add_header_footer)
        _cleanup_temp_files()
        return filepath
