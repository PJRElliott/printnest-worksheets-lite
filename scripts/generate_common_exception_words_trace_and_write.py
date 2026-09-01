#!/usr/bin/env python3
"""Generate England KS1 common-exception-word trace-and-write workbooks."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from reportlab.lib.colors import black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "references" / "common_exception_words_england_ks1.json"
GENERATOR_PATH = ROOT / "skills" / "trace-and-write" / "scripts" / "generate_trace_and_write.py"
OUTPUT_DIR = ROOT / "outputs" / "common-exception-words"


def load_generator():
    spec = importlib.util.spec_from_file_location("trace_and_write_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_sets() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))["sets"]


def draw_examples(pdf: canvas.Canvas, generator, baseline: float, words: list[str], color) -> None:
    generator.draw_guide(pdf, baseline)
    pdf.setFillColor(color)
    pdf.setFont("EduSABeginner-Regular", 34)
    x = generator.CONTENT_LEFT + 0.2 * inch
    for word in words:
        pdf.drawString(x, baseline + 0.04 * inch, word)
        x += pdfmetrics.stringWidth(word, "EduSABeginner-Regular", 34) + 0.35 * inch


def draw_instruction_page(pdf: canvas.Canvas, generator, example: str) -> None:
    pdf.drawImage(str(generator.PAGE_TEMPLATE), 0, 0, width=generator.PAGE_W, height=generator.PAGE_H, mask="auto")
    left = generator.CONTENT_LEFT
    top = generator.PAGE_H - 0.72 * inch
    pdf.setFillColor(black)
    pdf.setFont("LeagueSpartan-Bold", 28)
    pdf.drawString(left, top, "How to Use This Workbook")
    pdf.setFont("LeagueSpartan-Regular", 14)
    pdf.drawString(left, top - 0.34 * inch, "Trace each grey word twice, then continue writing with clear spaces.")
    items = [
        ("1. Grey Words", "The two spelling models are grey.", [example, example], generator.TRACE_GRAY),
        ("2. Traced Words", "The traced models are shown in black.", [example, example], black),
        ("3. Continue Writing", "Repeat the word as many times as fit comfortably.", [example] * 5, black),
    ]
    baselines = [generator.PAGE_H - 3.8 * inch, generator.PAGE_H - 5.9 * inch, generator.PAGE_H - 8.0 * inch]
    for (title, note, words, color), baseline in zip(items, baselines):
        pdf.setFillColor(black)
        pdf.setFont("LeagueSpartan-Bold", 20)
        pdf.drawString(left, baseline + 0.82 * inch, title)
        pdf.setFont("LeagueSpartan-Regular", 10)
        pdf.drawString(left, baseline + 0.58 * inch, note)
        draw_examples(pdf, generator, baseline, words, color)
    pdf.showPage()


def draw_word_page(pdf: canvas.Canvas, generator, title: str, words: list[str]) -> None:
    pdf.drawImage(str(generator.PAGE_TEMPLATE), 0, 0, width=generator.PAGE_W, height=generator.PAGE_H, mask="auto")
    baselines = generator.tracing_strip_baselines(generator.MAX_TRACE_STRIPS)
    generator.draw_heading(
        pdf,
        baselines[0] + generator.TRACE_TOP_EXTENT,
        title_override=title,
        instruction_override="Trace each word twice, then continue writing on your own.",
    )
    for baseline, word in zip(baselines, words):
        generator.draw_word_strip(pdf, baseline, word)
    pdf.showPage()


def generate_set(generator, item: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=A4)
    words = item["words"]
    draw_instruction_page(pdf, generator, words[0])
    for start in range(0, len(words), generator.MAX_TRACE_STRIPS):
        draw_word_page(pdf, generator, item["title"], words[start:start + generator.MAX_TRACE_STRIPS])
    pdf.save()
    print(f"Created {output}")


def main() -> None:
    sets = load_sets()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", choices=[item["id"] for item in sets])
    args = parser.parse_args()
    generator = load_generator()
    generator.register_fonts()
    selected = [item for item in sets if args.set in (None, item["id"])]
    for item in selected:
        generate_set(generator, item, OUTPUT_DIR / f"{item['id']}_common_exception_words_trace_and_write.pdf")


if __name__ == "__main__":
    main()
