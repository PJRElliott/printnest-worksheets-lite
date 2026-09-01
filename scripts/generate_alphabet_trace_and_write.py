#!/usr/bin/env python3
"""Generate the branded A-Z Alphabet Trace and Write workbook."""

from __future__ import annotations

import argparse
import importlib.util
import string
from pathlib import Path

from reportlab.lib.colors import black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
GENERATOR_PATH = (
    ROOT
    / "skills"
    / "trace-and-write"
    / "scripts"
    / "generate_trace_and_write.py"
)


def load_generator():
    spec = importlib.util.spec_from_file_location("trace_and_write_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def draw_letter_examples(pdf: canvas.Canvas, generator, baseline: float, text: str, color) -> None:
    generator.draw_guide(pdf, baseline)
    pdf.setFillColor(color)
    pdf.setFont("EduSABeginner-Regular", 34)
    x = generator.CONTENT_LEFT + 0.2 * inch
    gap = 0.72 * inch
    for character in text:
        pdf.drawString(x, baseline + 0.04 * inch, character)
        x += pdfmetrics.stringWidth(character, "EduSABeginner-Regular", 34) + gap


def draw_instruction_page(pdf: canvas.Canvas, generator) -> None:
    pdf.drawImage(
        str(generator.PAGE_TEMPLATE),
        0,
        0,
        width=generator.PAGE_W,
        height=generator.PAGE_H,
        mask="auto",
    )
    left = generator.CONTENT_LEFT
    top = generator.PAGE_H - 0.72 * inch
    pdf.setFillColor(black)
    pdf.setFont("LeagueSpartan-Bold", 28)
    pdf.drawString(left, top, "How to Use This Workbook")
    pdf.setFont("LeagueSpartan-Regular", 14)
    pdf.drawString(
        left,
        top - 0.34 * inch,
        "Trace each grey letter, then continue writing with clear spaces.",
    )

    items = [
        ("1. Grey Letters", "The uppercase and lowercase models are grey.", "AAaa", generator.TRACE_GRAY),
        ("2. Traced Letters", "The traced models are shown in black.", "AAaa", black),
        ("3. Continue Writing", "Repeat each letter as many times as fit comfortably.", "AaAaAa", black),
    ]
    baselines = [generator.PAGE_H - 3.8 * inch, generator.PAGE_H - 5.9 * inch, generator.PAGE_H - 8.0 * inch]
    for (title, note, text, color), baseline in zip(items, baselines):
        pdf.setFillColor(black)
        pdf.setFont("LeagueSpartan-Bold", 20)
        pdf.drawString(left, baseline + 0.82 * inch, title)
        pdf.setFont("LeagueSpartan-Regular", 10)
        pdf.drawString(left, baseline + 0.58 * inch, note)
        draw_letter_examples(pdf, generator, baseline, text, color)
    pdf.showPage()


def draw_letter_page(pdf: canvas.Canvas, generator, uppercase: str) -> None:
    lowercase = uppercase.lower()
    pdf.drawImage(
        str(generator.PAGE_TEMPLATE),
        0,
        0,
        width=generator.PAGE_W,
        height=generator.PAGE_H,
        mask="auto",
    )
    baselines = generator.tracing_strip_baselines(generator.MAX_TRACE_STRIPS)
    generator.draw_heading(
        pdf,
        baselines[0] + generator.TRACE_TOP_EXTENT,
        title_override=f"Letter {uppercase} {lowercase}",
        instruction_override="Trace each grey letter twice, then continue writing on your own.",
    )
    for index, baseline in enumerate(baselines):
        letter = uppercase if index < 5 else lowercase
        draw_letter_examples(pdf, generator, baseline, letter * 2, generator.TRACE_GRAY)
    pdf.showPage()


def generate(output: Path) -> None:
    generator = load_generator()
    output.parent.mkdir(parents=True, exist_ok=True)
    generator.register_fonts()
    pdf = canvas.Canvas(str(output), pagesize=A4)
    draw_instruction_page(pdf, generator)
    for uppercase in string.ascii_uppercase:
        draw_letter_page(pdf, generator, uppercase)
    pdf.save()
    print(f"Created {output} (27 page(s))")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "alphabet" / "alphabet_trace_and_write.pdf",
    )
    generate(parser.parse_args().output)


if __name__ == "__main__":
    main()
