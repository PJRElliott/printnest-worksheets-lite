#!/usr/bin/env python3
"""Generate an A4 sheet of circular CVC family stickers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
except ImportError:
    sys.exit("Install reportlab: pip install reportlab")


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "skills" / "trace-and-write" / "references" / "cvc_word_families.json"
FONT_DIR = ROOT / "assets" / "fonts"
OUTPUT_DIR = Path.home() / "Desktop" / "PrintNest" / "cvc_family_stickers"
OUTPUT_PATH = OUTPUT_DIR / "cvc_family_stickers.pdf"

PAGE_W, PAGE_H = A4
NAVY = HexColor("#193754")
GOLD = HexColor("#D9B76E")


def register_fonts() -> None:
    pdfmetrics.registerFont(
        TTFont("LeagueSpartan-Regular", str(FONT_DIR / "LeagueSpartan-Regular.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("LeagueSpartan-Bold", str(FONT_DIR / "LeagueSpartan-Bold.ttf"))
    )


def draw_sticker(pdf: canvas.Canvas, x: float, y: float, radius: float,
                 family: str, words: list[str]) -> None:
    pdf.setFillColor(NAVY)
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(5)
    pdf.circle(x, y, radius, fill=1, stroke=1)

    pdf.setFillColor(GOLD)
    pdf.setFont("LeagueSpartan-Bold", 8)
    pdf.drawCentredString(x, y + 0.36 * radius, "CVC FAMILY")

    pdf.setFillColor(white)
    pdf.setFont("LeagueSpartan-Bold", 25)
    pdf.drawCentredString(x, y - 0.05 * radius, f"-{family}")

    examples = "  ".join(words[:3])
    pdf.setFillColor(GOLD)
    pdf.setFont("LeagueSpartan-Regular", 7.5)
    pdf.drawCentredString(x, y - 0.46 * radius, examples)


def main() -> None:
    families: dict[str, list[str]] = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if len(families) != 35:
        raise ValueError(f"Expected 35 CVC families, found {len(families)}")

    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT_PATH), pagesize=A4)
    pdf.setTitle("CVC Family Circle Stickers")

    columns, rows = 5, 7
    margin_x = 0.34 * inch
    margin_y = 0.37 * inch
    cell_w = (PAGE_W - 2 * margin_x) / columns
    cell_h = (PAGE_H - 2 * margin_y) / rows
    radius = min(cell_w, cell_h) * 0.43

    for index, (family, words) in enumerate(families.items()):
        row, column = divmod(index, columns)
        x = margin_x + (column + 0.5) * cell_w
        y = PAGE_H - margin_y - (row + 0.5) * cell_h
        draw_sticker(pdf, x, y, radius, family, words)

    pdf.showPage()
    pdf.save()
    print(f"Created {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
