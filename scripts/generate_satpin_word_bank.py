#!/usr/bin/env python3
"""Generate the branded Phase 2 SATPIN word-bank PDF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib.colors import Color, black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "trace-and-write"
DATA_PATH = ROOT / "references" / "phase_2_satpin_word_bank.json"
FONT_DIR = SKILL / "assets" / "fonts"
TEMPLATE = SKILL / "assets" / "images" / "portrait-page-template.png"
PAGE_W, PAGE_H = A4
LEFT = 0.5 * inch
RIGHT = PAGE_W - 0.5 * inch
BLUE = Color(28 / 255, 57 / 255, 86 / 255)
GOLD = Color(214 / 255, 180 / 255, 105 / 255)
LIGHT_GRAY = Color(0.94, 0.94, 0.94)


def register_fonts() -> None:
    for weight in ("Regular", "Bold"):
        name = f"LeagueSpartan-{weight}"
        pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / f"{name}.ttf")))


def draw_word_grid(
    pdf: canvas.Canvas,
    words: list[str],
    top: float,
    columns: int = 5,
    font_size: int = 18,
) -> float:
    cell_gap = 0.10 * inch
    cell_h = 0.42 * inch
    cell_w = (RIGHT - LEFT - (columns - 1) * cell_gap) / columns
    for index, word in enumerate(words):
        row, column = divmod(index, columns)
        x = LEFT + column * (cell_w + cell_gap)
        y = top - (row + 1) * cell_h
        pdf.setFillColor(LIGHT_GRAY if row % 2 == 0 else white)
        pdf.setStrokeColor(Color(0.75, 0.75, 0.75))
        pdf.setLineWidth(0.7)
        pdf.rect(x, y, cell_w, cell_h - 0.05 * inch, fill=1, stroke=1)
        pdf.setFillColor(black)
        pdf.setFont("LeagueSpartan-Bold", font_size)
        pdf.drawCentredString(x + cell_w / 2, y + 0.11 * inch, word)
    rows = (len(words) + columns - 1) // columns
    return top - rows * cell_h


def draw_section(
    pdf: canvas.Canvas,
    title: str,
    note: str,
    words: list[str],
    top: float,
    columns: int = 5,
) -> float:
    pdf.setFillColor(BLUE)
    pdf.setFont("LeagueSpartan-Bold", 15)
    pdf.drawString(LEFT, top, title)
    pdf.setFillColor(black)
    pdf.setFont("LeagueSpartan-Regular", 9)
    pdf.drawString(LEFT, top - 0.22 * inch, note)
    return draw_word_grid(pdf, words, top - 0.30 * inch, columns) - 0.22 * inch


def generate(output: Path) -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    register_fonts()
    pdf = canvas.Canvas(str(output), pagesize=A4)
    pdf.drawImage(str(TEMPLATE), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")

    top = PAGE_H - 0.72 * inch
    pdf.setFillColor(black)
    pdf.setFont("LeagueSpartan-Bold", 28)
    pdf.drawString(LEFT, top, "Phase 2 SATPIN Word Bank")
    pdf.setFont("LeagueSpartan-Regular", 11)
    pdf.drawString(LEFT, top - 0.30 * inch, "Blend from left to right using only taught sounds.")

    letters_y = top - 1.08 * inch
    letter_w = 0.62 * inch
    for index, letter in enumerate(data["graphemes"]):
        x = LEFT + index * (letter_w + 0.10 * inch)
        pdf.setFillColor(BLUE if index < 3 else GOLD)
        pdf.rect(x, letters_y, letter_w, letter_w, fill=1, stroke=0)
        pdf.setFillColor(white if index < 3 else black)
        pdf.setFont("LeagueSpartan-Bold", 25)
        pdf.drawCentredString(x + letter_w / 2, letters_y + 0.16 * inch, letter)

    y = letters_y - 0.38 * inch
    y = draw_section(
        pdf,
        "Core Set 1-2 Words",
        "Official Letters and Sounds practice bank: regular VC and CVC words.",
        data["official_regular"],
        y,
    )
    y = draw_section(
        pdf,
        "Teach With Pronunciation Support",
        "In normal speech, a may reduce to a schwa; s in as and is represents /z/.",
        data["pronunciation_attention"],
        y,
        columns=3,
    )
    y = draw_section(
        pdf,
        "Additional CVC Words",
        "Regular real words made only from SATPIN graphemes.",
        data["additional_cvc"],
        y,
        columns=3,
    )
    y = draw_section(
        pdf,
        "Adjacent-Consonant Extension",
        "Use after children are ready to blend consonants next to each other.",
        data["adjacent_consonant_extension"],
        y,
        columns=5,
    )
    draw_section(
        pdf,
        "Longer Extension",
        "A two-syllable word made only from SATPIN graphemes.",
        data["longer_extension"],
        y,
        columns=3,
    )

    pdf.showPage()
    pdf.save()
    print(f"Created {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "phonics" / "phase_2_satpin_word_bank.pdf",
    )
    generate(parser.parse_args().output)


if __name__ == "__main__":
    main()
