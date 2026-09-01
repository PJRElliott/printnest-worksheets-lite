#!/usr/bin/env python3
"""Generate separate Phase 4 set Trace and Write PDFs."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "references" / "phase_4_word_bank.json"
GENERATOR_PATH = ROOT / "skills" / "trace-and-write" / "scripts" / "generate_trace_and_write.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("trace_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def chunk_sections(sections: list[dict[str, object]]) -> list[tuple[str, list[str]]]:
    return [
        (section["title"], section["words"][start:start + 10])
        for section in sections
        for start in range(0, len(section["words"]), 10)
    ]


def pack_sections(sections, capacity: int):
    pages = []
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


def generate(output: Path, sections: list[dict[str, object]]) -> None:
    generator = load_generator()
    pages = pack_sections(chunk_sections(sections), generator.MAX_TRACE_STRIPS)
    output.parent.mkdir(parents=True, exist_ok=True)
    generator.register_fonts()
    pdf = canvas.Canvas(str(output), pagesize=A4)
    generator.draw_instruction_page(pdf)
    for page_sections in pages:
        generator.draw_packed_page(pdf, page_sections, title_builder=lambda title: title)
    pdf.save()
    generator.insert_canonical_instruction_page(output)
    print(f"Created {output} ({len(pages) + 1} page(s))")


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
            ROOT / "outputs" / "phonics" / "phase_4_sets" / f"{item['id']}_trace_and_write.pdf"
        )
        generate(output, [sections[x] for x in item["sections"]])


if __name__ == "__main__":
    main()
