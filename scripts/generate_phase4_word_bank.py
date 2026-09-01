#!/usr/bin/env python3
"""Generate separate branded Phase 4 set word-bank PDFs."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from reportlab.lib.colors import black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "references" / "phase_4_word_bank.json"
BASE_GENERATOR = ROOT / "scripts" / "generate_satpin_word_bank.py"
PAGE_W, PAGE_H = A4
LEFT = 0.5 * inch
CONTENT_BOTTOM = 0.72 * inch


def load_base_generator():
    spec = importlib.util.spec_from_file_location("word_bank_base", BASE_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {BASE_GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def section_height(word_count: int, columns: int = 5) -> float:
    rows = (word_count + columns - 1) // columns
    return 0.30 * inch + rows * 0.42 * inch + 0.20 * inch


def draw_header(pdf: canvas.Canvas, base, page_number: int, title: str) -> float:
    pdf.drawImage(str(base.TEMPLATE), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")
    top = PAGE_H - 0.72 * inch
    display = title if page_number == 1 else f"{title} Continued"
    font_size = 22
    pdf.setFillColor(black)
    pdf.setFont("LeagueSpartan-Bold", font_size)
    pdf.drawString(LEFT, top, display)
    pdf.setFont("LeagueSpartan-Regular", 10)
    pdf.drawString(
        LEFT, top - 0.28 * inch,
        "Blend each word using known graphemes and adjacent consonants.",
    )
    return top - 0.58 * inch


def generate(output: Path, title: str, sections: list[dict[str, object]]) -> None:
    base = load_base_generator()
    output.parent.mkdir(parents=True, exist_ok=True)
    base.register_fonts()
    pdf = canvas.Canvas(str(output), pagesize=A4)
    page_number = 1
    y = draw_header(pdf, base, page_number, title)
    for section in sections:
        if y - section_height(len(section["words"])) < CONTENT_BOTTOM:
            pdf.showPage()
            page_number += 1
            y = draw_header(pdf, base, page_number, title)
        y = base.draw_section(
            pdf,
            section["title"],
            f"Word structure: {section['structure']}",
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
    parser.add_argument("--set", choices=set_ids, help="Generate one Phase 4 set")
    parser.add_argument("--output", type=Path, help="Output path for one set")
    args = parser.parse_args()
    selected = [item for item in data["sets"] if not args.set or item["id"] == args.set]
    sections = {section["title"]: section for section in data["sections"]}
    for item in selected:
        output = args.output or (
            ROOT / "outputs" / "phonics" / "phase_4_sets" / f"{item['id']}_word_bank.pdf"
        )
        generate(output, f"{item['title']} Word Bank", [sections[x] for x in item["sections"]])


if __name__ == "__main__":
    main()
