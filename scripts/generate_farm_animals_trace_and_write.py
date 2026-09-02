#!/usr/bin/env python3
"""Generate the branded Farm Animals trace-and-write workbook."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
GENERATOR_PATH = ROOT / "skills" / "trace-and-write" / "scripts" / "generate_trace_and_write.py"
ASSET_DIR = ROOT / "licensed-assets" / "farm-animals"
FARM_ANIMALS = ["cow", "pig", "hen", "duck", "sheep", "goat", "horse", "donkey"]


def load_generator():
    spec = importlib.util.spec_from_file_location("trace_and_write_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def draw_illustrated_strip(pdf: canvas.Canvas, generator, baseline: float, animal: str) -> None:
    image_path = ASSET_DIR / f"{animal}.png"
    if not image_path.exists():
        raise FileNotFoundError(f"Missing licensed farm-animal image: {image_path}")

    generator.draw_guide(pdf, baseline)
    image_size = 0.55 * inch
    pdf.drawImage(
        str(image_path),
        generator.CONTENT_LEFT + 0.03 * inch,
        baseline - 0.16 * inch,
        width=image_size,
        height=image_size,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )

    first_x = generator.CONTENT_LEFT + 0.72 * inch
    word_width = pdfmetrics.stringWidth(animal, "EduSABeginner-Regular", 34)
    second_x = first_x + word_width + 0.35 * inch
    pdf.setFillColor(generator.TRACE_GRAY)
    pdf.setFont("EduSABeginner-Regular", 34)
    pdf.drawString(first_x, baseline + 0.04 * inch, animal)
    pdf.drawString(second_x, baseline + 0.04 * inch, animal)


def draw_practice_page(pdf: canvas.Canvas, generator) -> None:
    pdf.drawImage(
        str(generator.PAGE_TEMPLATE), 0, 0,
        width=generator.PAGE_W, height=generator.PAGE_H, mask="auto",
    )
    baselines = generator.tracing_strip_baselines(generator.MAX_TRACE_STRIPS)
    generator.draw_heading(
        pdf,
        baselines[0] + generator.TRACE_TOP_EXTENT,
        title_override="Farm Animal Words",
        instruction_override="Trace each word twice, then continue writing on your own.",
    )
    for baseline, animal in zip(baselines, FARM_ANIMALS):
        draw_illustrated_strip(pdf, generator, baseline, animal)
    pdf.showPage()


def generate(output: Path) -> None:
    generator = load_generator()
    output.parent.mkdir(parents=True, exist_ok=True)
    generator.register_fonts()
    pdf = canvas.Canvas(str(output), pagesize=A4)
    generator.draw_instruction_page(pdf)
    draw_practice_page(pdf, generator)
    pdf.save()
    generator.insert_canonical_instruction_page(output)
    print(f"Created {output} (2 page(s))")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "farm-animals" / "farm_animals_trace_and_write.pdf",
    )
    generate(parser.parse_args().output)


if __name__ == "__main__":
    main()
