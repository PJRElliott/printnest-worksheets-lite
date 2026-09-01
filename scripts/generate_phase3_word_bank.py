#!/usr/bin/env python3
"""Generate the branded Phase 3 phonics word-bank PDF."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from reportlab.lib.colors import Color, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "references" / "phase_3_word_bank.json"
SATPIN_GENERATOR = ROOT / "scripts" / "generate_satpin_word_bank.py"
LEFT = 0.5 * inch
PAGE_W, PAGE_H = A4
CONTENT_BOTTOM = 0.72 * inch
BLUE = Color(28 / 255, 57 / 255, 86 / 255)


def load_satpin_generator():
    spec = importlib.util.spec_from_file_location("satpin_word_bank", SATPIN_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SATPIN_GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def section_height(word_count: int, columns: int = 5) -> float:
    rows = (word_count + columns - 1) // columns
    title_and_note = 0.30 * inch
    return title_and_note + rows * 0.42 * inch + 0.20 * inch


def draw_page_header(
    pdf: canvas.Canvas, base, page_number: int, product_title: str
) -> float:
    pdf.drawImage(
        str(base.TEMPLATE), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto"
    )
    top = PAGE_H - 0.72 * inch
    pdf.setFillColor(black)
    pdf.setFont("LeagueSpartan-Bold", 28 if page_number == 1 else 22)
    title = product_title if page_number == 1 else f"{product_title} Continued"
    pdf.drawString(LEFT, top, title)
    pdf.setFont("LeagueSpartan-Regular", 10)
    pdf.drawString(
        LEFT,
        top - 0.28 * inch,
        "Read and blend each word using the highlighted Phase 3 progression.",
    )
    return top - 0.58 * inch


def generate(output: Path, product_title: str, sections: list[dict[str, object]]) -> None:
    base = load_satpin_generator()
    output.parent.mkdir(parents=True, exist_ok=True)
    base.register_fonts()
    pdf = canvas.Canvas(str(output), pagesize=A4)

    page_number = 1
    y = draw_page_header(pdf, base, page_number, product_title)
    for section in sections:
        needed = section_height(len(section["words"]))
        if y - needed < CONTENT_BOTTOM:
            pdf.showPage()
            page_number += 1
            y = draw_page_header(pdf, base, page_number, product_title)
        y = base.draw_section(
            pdf,
            section["title"],
            f"Target grapheme: {section['grapheme']}",
            section["words"],
            y,
        )

    pdf.showPage()
    pdf.save()
    print(f"Created {output} ({page_number} page(s))")


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    set_ids = [item["id"] for item in data["sets"]]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", choices=set_ids, help="Generate one Phase 3 set")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path when generating one set",
    )
    args = parser.parse_args()
    selected = [item for item in data["sets"] if not args.set or item["id"] == args.set]
    sections_by_title = {section["title"]: section for section in data["sections"]}
    for item in selected:
        output = args.output or (
            ROOT / "outputs" / "phonics" / "phase_3_sets" / f"{item['id']}_word_bank.pdf"
        )
        sections = [sections_by_title[title] for title in item["sections"]]
        generate(output, f"{item['title']} Word Bank", sections)


if __name__ == "__main__":
    main()
