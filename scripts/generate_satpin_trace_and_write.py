#!/usr/bin/env python3
"""Generate the Phase 2 SATPIN Trace and Write workbook."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
GENERATOR_PATH = (
    ROOT
    / "skills"
    / "trace-and-write"
    / "scripts"
    / "generate_trace_and_write.py"
)
DATA_PATH = ROOT / "references" / "phase_2_satpin_word_bank.json"


def load_generator():
    spec = importlib.util.spec_from_file_location("trace_and_write_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_sections(data: dict[str, object]) -> list[tuple[str, list[str]]]:
    groups = [
        ("Core SATPIN Words", data["official_regular"]),
        ("Pronunciation Support", data["pronunciation_attention"]),
        ("Additional CVC Words", data["additional_cvc"]),
        ("Longer SATPIN Words", data["longer_extension"]),
        ("Adjacent-Consonant Words", data["adjacent_consonant_extension"]),
    ]
    return [
        (title, words[start:start + 10])
        for title, words in groups
        for start in range(0, len(words), 10)
    ]


def pack_sections(
    sections: list[tuple[str, list[str]]], capacity: int
) -> list[list[tuple[str, list[str]]]]:
    pages: list[list[tuple[str, list[str]]]] = []
    used = 0
    for section in sections:
        cost = len(section[1]) + (1 if used else 0)
        if used and used + cost > capacity:
            used = 0
        if not pages or used == 0:
            pages.append([])
        pages[-1].append(section)
        used += len(section[1]) + (1 if len(pages[-1]) > 1 else 0)
    return pages


def generate(output: Path) -> None:
    generator = load_generator()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    sections = build_sections(data)
    pages = pack_sections(sections, generator.MAX_TRACE_STRIPS)

    output.parent.mkdir(parents=True, exist_ok=True)
    generator.register_fonts()
    pdf = canvas.Canvas(str(output), pagesize=A4)
    generator.draw_instruction_page(pdf)
    for page_sections in pages:
        generator.draw_packed_page(pdf, page_sections, title_builder=lambda title: title)
    pdf.save()
    print(f"Created {output} ({len(pages) + 1} page(s))")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "phonics" / "phase_2_satpin_trace_and_write.pdf",
    )
    generate(parser.parse_args().output)


if __name__ == "__main__":
    main()
