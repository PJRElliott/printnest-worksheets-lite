#!/usr/bin/env python3
"""Generate the branded Months of the Year trace-and-write workbook."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

from reportlab.lib.colors import black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
GENERATOR_PATH = (
    ROOT / "skills" / "trace-and-write" / "scripts" / "generate_trace_and_write.py"
)
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def load_generator():
    spec = importlib.util.spec_from_file_location("trace_and_write_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def draw_example_words(pdf: canvas.Canvas, generator, baseline: float, words: list[str], color) -> None:
    generator.draw_guide(pdf, baseline)
    pdf.setFillColor(color)
    pdf.setFont("EduSABeginner-Regular", 34)
    x = generator.CONTENT_LEFT + 0.2 * inch
    for word in words:
        pdf.drawString(x, baseline + 0.04 * inch, word)
        x += pdfmetrics.stringWidth(word, "EduSABeginner-Regular", 34) + 0.35 * inch


def draw_instruction_page(pdf: canvas.Canvas, generator) -> None:
    pdf.drawImage(
        str(generator.PAGE_TEMPLATE), 0, 0,
        width=generator.PAGE_W, height=generator.PAGE_H, mask="auto",
    )
    left = generator.CONTENT_LEFT
    top = generator.PAGE_H - 0.72 * inch
    pdf.setFillColor(black)
    pdf.setFont("LeagueSpartan-Bold", 28)
    pdf.drawString(left, top, "How to Use This Workbook")
    pdf.setFont("LeagueSpartan-Regular", 14)
    pdf.drawString(
        left, top - 0.34 * inch,
        "Trace each grey month twice, then continue writing with clear spaces.",
    )

    items = [
        ("1. Grey Words", "The two month-name models are grey.", ["January", "January"], generator.TRACE_GRAY),
        ("2. Traced Words", "The traced models are shown in black.", ["January", "January"], black),
        ("3. Continue Writing", "Repeat the word as many times as fit comfortably.", ["January"] * 3, black),
    ]
    baselines = [generator.PAGE_H - 3.8 * inch, generator.PAGE_H - 5.9 * inch, generator.PAGE_H - 8.0 * inch]
    for (title, note, words, color), baseline in zip(items, baselines):
        pdf.setFillColor(black)
        pdf.setFont("LeagueSpartan-Bold", 20)
        pdf.drawString(left, baseline + 0.82 * inch, title)
        pdf.setFont("LeagueSpartan-Regular", 10)
        pdf.drawString(left, baseline + 0.58 * inch, note)
        draw_example_words(pdf, generator, baseline, words, color)
    pdf.showPage()


def draw_months_page(pdf: canvas.Canvas, generator, months: list[str]) -> None:
    pdf.drawImage(
        str(generator.PAGE_TEMPLATE), 0, 0,
        width=generator.PAGE_W, height=generator.PAGE_H, mask="auto",
    )
    baselines = generator.tracing_strip_baselines(generator.MAX_TRACE_STRIPS)
    generator.draw_heading(
        pdf,
        baselines[0] + generator.TRACE_TOP_EXTENT,
        title_override="Months of the Year",
        instruction_override="Trace each month twice, then continue writing on your own.",
    )
    for baseline, month in zip(baselines, months):
        generator.draw_word_strip(pdf, baseline, month)
    pdf.showPage()


def generate(output: Path) -> None:
    generator = load_generator()
    output.parent.mkdir(parents=True, exist_ok=True)
    generator.register_fonts()
    pdf = canvas.Canvas(str(output), pagesize=A4)
    draw_instruction_page(pdf, generator)
    for start in range(0, len(MONTHS), generator.MAX_TRACE_STRIPS):
        draw_months_page(pdf, generator, MONTHS[start:start + generator.MAX_TRACE_STRIPS])
    pdf.save()
    print(f"Created {output} (3 page(s))")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "months-of-year" / "months_of_the_year_trace_and_write.pdf",
    )
    generate(parser.parse_args().output)


if __name__ == "__main__":
    main()
