#!/usr/bin/env python3
"""Generate A4 CVC trace-and-write worksheet pages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from reportlab.lib.colors import Color, black
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
except ImportError:
    sys.exit("Install reportlab and Pillow: pip install reportlab Pillow")


SKILL_DIR = Path(__file__).resolve().parent.parent
PAGE_W, PAGE_H = A4
CONTENT_TOP = PAGE_H - 1.0 * inch
CONTENT_BOTTOM = 0.5 * inch
CONTENT_LEFT = 0.5 * inch
CONTENT_RIGHT = PAGE_W - 0.5 * inch
TRACE_TOP_EXTENT = 0.44 * inch
TRACE_BOTTOM_EXTENT = 0.22 * inch
TRACE_GAP = 0.35 * inch
BANNER_BOTTOM = PAGE_H - PAGE_H * 115 / 5999
TITLE_SIZE = 22
INSTRUCTION_SIZE = 10
TITLE_INSTRUCTION_GAP = 0.08 * inch
TRACE_WORD_GAP_SCALE = 0.60

MID_GRAY = Color(0.55, 0.55, 0.55)
TRACE_GRAY = Color(0.72, 0.72, 0.72)
FONT_DIR = SKILL_DIR / "assets" / "fonts"
PAGE_TEMPLATE = SKILL_DIR / "assets" / "images" / "portrait-page-template.png"
WORD_FAMILIES_PATH = SKILL_DIR / "references" / "cvc_word_families.json"
FAMILIES: dict[str, list[str]] = json.loads(
    WORD_FAMILIES_PATH.read_text(encoding="utf-8")
)


def register_fonts() -> None:
    for name in ("Regular", "Bold"):
        font_name = f"LeagueSpartan-{name}"
        pdfmetrics.registerFont(TTFont(font_name, str(FONT_DIR / f"{font_name}.ttf")))
    pdfmetrics.registerFont(
        TTFont(
            "EduSABeginner-Regular",
            str(FONT_DIR / "EduSABeginner-Regular.ttf"),
        )
    )


def tracing_strip_baselines(count: int = 10) -> list[float]:
    strip_height = TRACE_TOP_EXTENT + TRACE_BOTTOM_EXTENT
    step = strip_height + TRACE_GAP
    group_height = strip_height + (count - 1) * step
    top_inset = max(0, (CONTENT_TOP - CONTENT_BOTTOM - group_height) / 2)
    first = CONTENT_TOP - top_inset - TRACE_TOP_EXTENT
    return [first - index * step for index in range(count)]


def draw_heading(pdf: canvas.Canvas, first_strip_top: float) -> None:
    title_font = "LeagueSpartan-Bold"
    instruction_font = "LeagueSpartan-Regular"
    title_ascent, title_descent = pdfmetrics.getAscentDescent(title_font, TITLE_SIZE)
    instruction_ascent, instruction_descent = pdfmetrics.getAscentDescent(
        instruction_font, INSTRUCTION_SIZE
    )
    available = BANNER_BOTTOM - first_strip_top
    outer_gap = (
        available
        - (title_ascent - title_descent)
        - (instruction_ascent - instruction_descent)
        - TITLE_INSTRUCTION_GAP
    ) / 2
    title_y = BANNER_BOTTOM - outer_gap - title_ascent
    instruction_y = (
        title_y + title_descent - TITLE_INSTRUCTION_GAP - instruction_ascent
    )

    pdf.setFillColor(black)
    pdf.setFont(title_font, TITLE_SIZE)
    pdf.drawCentredString(PAGE_W / 2, title_y, "Trace and Write Words")
    pdf.setFont(instruction_font, INSTRUCTION_SIZE)
    pdf.drawCentredString(
        PAGE_W / 2,
        instruction_y,
        "Trace each word twice, then write it on your own.",
    )


def draw_guide(pdf: canvas.Canvas, baseline: float) -> None:
    gap = 0.22 * inch
    pdf.setStrokeColor(MID_GRAY)
    pdf.setLineWidth(1)
    pdf.setDash(1, 0)
    pdf.line(CONTENT_LEFT, baseline + 2 * gap, CONTENT_RIGHT, baseline + 2 * gap)
    pdf.setDash(3, 3)
    pdf.line(CONTENT_LEFT, baseline + gap, CONTENT_RIGHT, baseline + gap)
    pdf.setStrokeColor(black)
    pdf.setLineWidth(1.4)
    pdf.setDash(1, 0)
    pdf.line(CONTENT_LEFT, baseline, CONTENT_RIGHT, baseline)
    pdf.setStrokeColor(MID_GRAY)
    pdf.setLineWidth(1)
    pdf.setDash(3, 3)
    pdf.line(CONTENT_LEFT, baseline - gap, CONTENT_RIGHT, baseline - gap)
    pdf.setDash(1, 0)


def draw_page(pdf: canvas.Canvas, words: list[str]) -> None:
    pdf.drawImage(str(PAGE_TEMPLATE), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")
    baselines = tracing_strip_baselines()
    draw_heading(pdf, baselines[0] + TRACE_TOP_EXTENT)

    for index, baseline in enumerate(baselines):
        draw_guide(pdf, baseline)
        word = words[index % len(words)]
        first_x = CONTENT_LEFT + 0.2 * inch
        old_second_x = CONTENT_LEFT + 2.0 * inch
        width = pdfmetrics.stringWidth(word, "EduSABeginner-Regular", 34)
        old_gap = old_second_x - first_x - width
        second_x = first_x + width + old_gap * TRACE_WORD_GAP_SCALE
        pdf.setFillColor(TRACE_GRAY)
        pdf.setFont("EduSABeginner-Regular", 34)
        pdf.drawString(first_x, baseline + 0.04 * inch, word)
        pdf.drawString(second_x, baseline + 0.04 * inch, word)
    pdf.showPage()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--family", choices=FAMILIES, help="Generate one family page")
    selection.add_argument(
        "--vowel",
        choices=("a", "e", "i", "o", "u"),
        help="Generate every family for one short vowel",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.home()
        / "Desktop"
        / "PrintNest"
        / "trace_and_write"
        / "trace_and_write_cvc.pdf",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    register_fonts()
    pdf = canvas.Canvas(str(args.output), pagesize=A4)
    if args.family:
        selected = [args.family]
    elif args.vowel:
        selected = [family for family in FAMILIES if family.startswith(args.vowel)]
    else:
        selected = list(FAMILIES)
    for family in selected:
        draw_page(pdf, FAMILIES[family])
    pdf.save()
    print(f"Created {args.output} ({len(selected)} page(s))")


if __name__ == "__main__":
    main()
