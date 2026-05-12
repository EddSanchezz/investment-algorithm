"""
Genera el PDF del Documento de Diseno (Diseno.md) usando ReportLab.
Convierte Markdown estructurado a PDF con formato profesional.
"""

import os
import re
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(ROOT, "docs", "Diseno.md")
OUTPUT_PATH = os.path.join(ROOT, "docs", "Diseno.pdf")


def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base["Title"],
            fontSize=24, leading=30, alignment=TA_CENTER,
            spaceAfter=6, textColor=HexColor("#003366"),
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle", parent=base["Normal"],
            fontSize=13, leading=18, alignment=TA_CENTER,
            spaceAfter=4, textColor=HexColor("#555555"),
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"],
            fontSize=18, leading=24, spaceBefore=20, spaceAfter=10,
            textColor=HexColor("#003366"),
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"],
            fontSize=14, leading=18, spaceBefore=14, spaceAfter=6,
            textColor=HexColor("#003366"),
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"],
            fontSize=12, leading=16, spaceBefore=10, spaceAfter=4,
            textColor=HexColor("#444444"),
        ),
        "body": ParagraphStyle(
            "Body", parent=base["Normal"],
            fontSize=9.5, leading=13, alignment=TA_JUSTIFY,
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "Code", parent=base["Code"],
            fontSize=8, leading=10, leftIndent=10,
            backColor=HexColor("#F5F5F5"),
            spaceAfter=4,
        ),
        "table_header": ParagraphStyle(
            "TableHeader", parent=base["Normal"],
            fontSize=8.5, leading=11, alignment=TA_CENTER,
            textColor=HexColor("#FFFFFF"),
        ),
        "table_cell": ParagraphStyle(
            "TableCell", parent=base["Normal"],
            fontSize=8, leading=11, alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["Normal"],
            fontSize=9.5, leading=13, leftIndent=15,
            spaceAfter=2,
        ),
    }
    return styles


def _is_heading(line: str):
    m = re.match(r"^(#{1,3})\s+(.*)", line)
    if m:
        return len(m.group(1)), m.group(2).strip()
    return None, None


def _is_table_row(line: str):
    return line.startswith("|")


def _is_code_block(line: str):
    return line.startswith("```")


def _is_horizontal_rule(line: str):
    return line.strip().startswith("---") and len(line.strip()) >= 3


def _is_list_item(line: str):
    return line.strip().startswith("- ") or line.strip().startswith("* ")


def _bold(text: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)


def _inline_code(text: str) -> str:
    return re.sub(r"`([^`]+)`", r"<font face='Courier'><i>\1</i></font>", text)


def _parse_markdown_line(line: str) -> str:
    text = _bold(line)
    text = _inline_code(text)
    return text


def _build_flowables(md_lines: list, styles: dict):
    elements = []
    in_code = False
    code_lines = []
    in_table = False
    table_rows = []
    list_items = []

    def flush_code():
        nonlocal code_lines
        if code_lines:
            code_text = "\n".join(code_lines)
            elements.append(Paragraph(
                code_text.replace(" ", "&nbsp;").replace("\n", "<br/>"),
                styles["code"]
            ))
            code_lines = []

    def flush_table():
        nonlocal table_rows
        if len(table_rows) > 1:
            col_count = max(len(r) for r in table_rows)
            header_style = styles["table_header"]
            cell_style = styles["table_cell"]

            styled_rows = []
            for ri, row in enumerate(table_rows):
                padded = row + [""] * (col_count - len(row))
                style = header_style if ri == 0 else cell_style
                styled_rows.append([Paragraph(c.strip(), style) for c in padded])

            avail = A4[0] - 4 * cm
            col_width = avail / col_count

            t = Table(styled_rows, colWidths=[col_width] * col_count)
            header_color = HexColor("#003366")
            alt_color = HexColor("#F0F4F8")
            cmds = [
                ("BACKGROUND", (0, 0), (-1, 0), header_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ]
            for ri in range(1, len(styled_rows)):
                if ri % 2 == 1:
                    cmds.append(("BACKGROUND", (0, ri), (-1, ri), alt_color))

            t.setStyle(TableStyle(cmds))
            elements.append(t)
            elements.append(Spacer(1, 6))
        table_rows = []

    def flush_list():
        nonlocal list_items
        if list_items:
            items = []
            for item in list_items:
                text = _parse_markdown_line(item)
                items.append(ListItem(Paragraph(text, styles["bullet"])))
            if items:
                elements.append(ListFlowable(items, bulletType="bullet",
                                             leftIndent=15, bulletFontSize=8))
            list_items = []

    for raw_line in md_lines:
        line = raw_line.rstrip()

        if _is_code_block(line):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_table()
            flush_list()
            elements.append(Spacer(1, 4))
            continue

        if _is_horizontal_rule(line):
            flush_table()
            flush_list()
            continue

        if _is_table_row(line):
            flush_list()
            in_table = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(c.startswith("---") for c in cells if c.strip()):
                table_rows.append(cells)
            continue

        if in_table:
            flush_table()
            in_table = False

        if _is_list_item(line):
            flush_table()
            list_items.append(re.sub(r"^[-*]\s+", "", line.strip()))
            continue

        flush_list()

        level, text = _is_heading(line)
        if level == 1:
            elements.append(Paragraph(text, styles["h1"]))
        elif level == 2:
            elements.append(Paragraph(text, styles["h2"]))
        elif level == 3:
            elements.append(Paragraph(text, styles["h3"]))
        else:
            parsed = _parse_markdown_line(line)
            elements.append(Paragraph(parsed, styles["body"]))

    flush_code()
    flush_table()
    flush_list()
    return elements


def generate():
    styles = _build_styles()

    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_lines = f.readlines()

    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    cover = [
        Spacer(1, 80),
        Paragraph("Documento de Diseño", styles["cover_title"]),
        Paragraph("Sistema de Análisis Algorítmico Financiero", styles["cover_subtitle"]),
        Spacer(1, 20),
        Paragraph("Universidad del Quindío", styles["cover_subtitle"]),
        Paragraph("Programa de Ingeniería de Sistemas y Computación", styles["cover_subtitle"]),
        Paragraph("Curso: Análisis de Algoritmos — 2026-1", styles["cover_subtitle"]),
        Spacer(1, 14),
        Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["cover_subtitle"]),
    ]

    body = _build_flowables(md_lines, styles)

    doc.build(cover + [PageBreak()] + body)
    print(f"PDF generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate()
