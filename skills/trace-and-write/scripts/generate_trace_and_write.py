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
MAX_TRACE_STRIPS = 10

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


def tracing_strip_baselines(count: int = MAX_TRACE_STRIPS) -> list[float]:
    if not 1 <= count <= MAX_TRACE_STRIPS:
        raise ValueError(f"Strip count must be between 1 and {MAX_TRACE_STRIPS}")
    strip_height = TRACE_TOP_EXTENT + TRACE_BOTTOM_EXTENT
    step = strip_height + TRACE_GAP
    group_height = strip_height + (MAX_TRACE_STRIPS - 1) * step
    top_inset = max(0, (CONTENT_TOP - CONTENT_BOTTOM - group_height) / 2)
    first = CONTENT_TOP - top_inset - TRACE_TOP_EXTENT
    return [first - index * step for index in range(count)]


def draw_heading(
    pdf: canvas.Canvas,
    first_strip_top: float,
    family: str | None = None,
    title_override: str | None = None,
) -> None:
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
    title = title_override or (
        f"-{family} Family Words"
        if family
        else "Short Vowel Words"
    )
    pdf.drawString(CONTENT_LEFT, title_y, title)
    pdf.setFont(instruction_font, INSTRUCTION_SIZE)
    pdf.drawString(
        CONTENT_LEFT,
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


def draw_page(pdf: canvas.Canvas, family: str, words: list[str]) -> None:
    pdf.drawImage(str(PAGE_TEMPLATE), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")
    baselines = tracing_strip_baselines(len(words))
    draw_heading(pdf, baselines[0] + TRACE_TOP_EXTENT, family)

    for index, baseline in enumerate(baselines):
        draw_guide(pdf, baseline)
        word = words[index]
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


def draw_singleton_page(
    pdf: canvas.Canvas, families: list[tuple[str, str]], vowel: str
) -> None:
    pdf.drawImage(str(PAGE_TEMPLATE), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")
    baselines = tracing_strip_baselines(len(families))
    draw_heading(
        pdf,
        baselines[0] + TRACE_TOP_EXTENT,
        title_override=f"Short {vowel.upper()} Words",
    )

    for baseline, (family, word) in zip(baselines, families):
        draw_guide(pdf, baseline)
        pdf.setFillColor(black)
        pdf.setFont("LeagueSpartan-Bold", 12)
        pdf.drawRightString(
            CONTENT_RIGHT,
            baseline + TRACE_TOP_EXTENT + 0.08 * inch,
            f"-{family} Family",
        )
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


def draw_section_heading(
    pdf: canvas.Canvas,
    previous_baseline: float,
    family: str,
) -> float:
    title_font = "LeagueSpartan-Bold"
    instruction_font = "LeagueSpartan-Regular"
    title_ascent, title_descent = pdfmetrics.getAscentDescent(title_font, TITLE_SIZE)
    instruction_ascent, instruction_descent = pdfmetrics.getAscentDescent(
        instruction_font, INSTRUCTION_SIZE
    )
    first_strip_top = tracing_strip_baselines(MAX_TRACE_STRIPS)[0] + TRACE_TOP_EXTENT
    heading_available = BANNER_BOTTOM - first_strip_top
    outer_gap = (
        heading_available
        - (title_ascent - title_descent)
        - (instruction_ascent - instruction_descent)
        - TITLE_INSTRUCTION_GAP
    ) / 2
    title_y = previous_baseline - TRACE_BOTTOM_EXTENT - outer_gap - title_ascent
    instruction_y = (
        title_y + title_descent - TITLE_INSTRUCTION_GAP - instruction_ascent
    )
    instruction_bottom = instruction_y + instruction_descent
    next_baseline = instruction_bottom - outer_gap - TRACE_TOP_EXTENT

    pdf.setFillColor(black)
    pdf.setFont(title_font, TITLE_SIZE)
    pdf.drawString(
        CONTENT_LEFT, title_y, f"-{family} Family Words"
    )
    pdf.setFont(instruction_font, INSTRUCTION_SIZE)
    pdf.drawString(
        CONTENT_LEFT,
        instruction_y,
        "Trace each word twice, then write it on your own.",
    )
    return next_baseline


def draw_word_strip(pdf: canvas.Canvas, baseline: float, word: str) -> None:
    draw_guide(pdf, baseline)
    first_x = CONTENT_LEFT + 0.2 * inch
    old_second_x = CONTENT_LEFT + 2.0 * inch
    width = pdfmetrics.stringWidth(word, "EduSABeginner-Regular", 34)
    old_gap = old_second_x - first_x - width
    second_x = first_x + width + old_gap * TRACE_WORD_GAP_SCALE
    pdf.setFillColor(TRACE_GRAY)
    pdf.setFont("EduSABeginner-Regular", 34)
    pdf.drawString(first_x, baseline + 0.04 * inch, word)
    pdf.drawString(second_x, baseline + 0.04 * inch, word)


def draw_instruction_page(pdf: canvas.Canvas) -> None:
    pdf.drawImage(str(PAGE_TEMPLATE), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")
    title_font = "LeagueSpartan-Bold"
    body_font = "LeagueSpartan-Regular"
    instruction_title_size = 28
    title_ascent, _ = pdfmetrics.getAscentDescent(
        title_font, instruction_title_size
    )
    title_y = BANNER_BOTTOM - 0.254 * inch - title_ascent

    pdf.setFillColor(black)
    pdf.setFont(title_font, instruction_title_size)
    pdf.drawString(CONTENT_LEFT, title_y, "How to Use This Worksheet")
    pdf.setFont(body_font, 14)
    pdf.drawString(
        CONTENT_LEFT,
        title_y - 0.32 * inch,
        "Trace each grey word twice, then continue writing to the end using finger spaces.",
    )

    steps_y = title_y - 0.78 * inch
    step_gap = 0.34 * inch
    pdf.setFont(title_font, 17)
    pdf.drawString(CONTENT_LEFT, steps_y, "1. Trace")
    pdf.setFont(body_font, 13)
    pdf.drawString(CONTENT_LEFT + 1.08 * inch, steps_y, "Follow the grey letters carefully.")
    pdf.setFont(title_font, 17)
    pdf.drawString(CONTENT_LEFT, steps_y - step_gap, "2. Write")
    pdf.setFont(body_font, 13)
    pdf.drawString(
        CONTENT_LEFT + 1.08 * inch,
        steps_y - step_gap,
        "Continue the word to the end using finger spaces.",
    )
    pdf.setFont(title_font, 17)
    pdf.drawString(CONTENT_LEFT, steps_y - 2 * step_gap, "3. Read")
    pdf.setFont(body_font, 13)
    pdf.drawString(
        CONTENT_LEFT + 1.08 * inch,
        steps_y - 2 * step_gap,
        "Say each sound, then read the whole word.",
    )

    grey_baseline = PAGE_H - 4.15 * inch
    pdf.setFont(title_font, 20)
    pdf.drawString(CONTENT_LEFT, grey_baseline + 0.82 * inch, "1. Grey Words")
    pdf.setFont(body_font, 10)
    pdf.drawString(
        CONTENT_LEFT,
        grey_baseline + 0.58 * inch,
        "The two words begin as grey tracing models.",
    )
    draw_guide(pdf, grey_baseline)
    pdf.setFillColor(TRACE_GRAY)
    pdf.setFont("EduSABeginner-Regular", 34)
    example_first_x = CONTENT_LEFT + 0.2 * inch
    example_second_x = CONTENT_LEFT + 1.62 * inch
    pdf.drawString(example_first_x, grey_baseline + 0.04 * inch, "cat")
    pdf.drawString(example_second_x, grey_baseline + 0.04 * inch, "cat")

    black_baseline = PAGE_H - 6.15 * inch
    pdf.setFillColor(black)
    pdf.setFont(title_font, 20)
    pdf.drawString(CONTENT_LEFT, black_baseline + 0.82 * inch, "2. Traced Words")
    pdf.setFont(body_font, 10)
    pdf.drawString(
        CONTENT_LEFT,
        black_baseline + 0.58 * inch,
        "The two traced words are now shown in black.",
    )
    draw_guide(pdf, black_baseline)
    pdf.setFillColor(black)
    pdf.setFont("EduSABeginner-Regular", 34)
    pdf.drawString(example_first_x, black_baseline + 0.04 * inch, "cat")
    pdf.drawString(example_second_x, black_baseline + 0.04 * inch, "cat")

    complete_baseline = PAGE_H - 8.15 * inch
    pdf.setFillColor(black)
    pdf.setFont(title_font, 20)
    pdf.drawString(CONTENT_LEFT, complete_baseline + 0.82 * inch, "3. Complete Row")
    pdf.setFont(body_font, 10)
    pdf.drawString(
        CONTENT_LEFT,
        complete_baseline + 0.58 * inch,
        "Six independently written words complete the row.",
    )
    draw_guide(pdf, complete_baseline)
    pdf.setFillColor(black)
    pdf.setFont("EduSABeginner-Regular", 34)
    word_width = pdfmetrics.stringWidth("cat", "EduSABeginner-Regular", 34)
    usable_width = CONTENT_RIGHT - CONTENT_LEFT - 0.4 * inch
    word_gap = (usable_width - 6 * word_width) / 5
    for index in range(6):
        word_x = CONTENT_LEFT + 0.2 * inch + index * (word_width + word_gap)
        pdf.drawString(word_x, complete_baseline + 0.04 * inch, "cat")
    pdf.showPage()


def draw_packed_page(
    pdf: canvas.Canvas, sections: list[tuple[str, list[str]]]
) -> None:
    pdf.drawImage(str(PAGE_TEMPLATE), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")
    step = TRACE_TOP_EXTENT + TRACE_BOTTOM_EXTENT + TRACE_GAP
    baseline = tracing_strip_baselines(MAX_TRACE_STRIPS)[0]
    draw_heading(pdf, baseline + TRACE_TOP_EXTENT, sections[0][0])
    for section_index, (family, words) in enumerate(sections):
        if section_index:
            baseline = draw_section_heading(pdf, baseline, family)
        for word_index, word in enumerate(words):
            if word_index:
                baseline -= step
            draw_word_strip(pdf, baseline, word)
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
    parser.add_argument(
        "--merge-singletons",
        action="store_true",
        help="Combine one-word families on a shared labeled page",
    )
    parser.add_argument(
        "--pack-families",
        action="store_true",
        help="Move following family sections into unused page space",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    register_fonts()
    pdf = canvas.Canvas(str(args.output), pagesize=A4)
    draw_instruction_page(pdf)
    if args.family:
        selected = [args.family]
    elif args.vowel:
        selected = [family for family in FAMILIES if family.startswith(args.vowel)]
    else:
        selected = list(FAMILIES)
    page_count = 1
    if args.pack_families or (not args.family and not args.merge_singletons):
        sections = [
            (family, FAMILIES[family][start:start + MAX_TRACE_STRIPS])
            for family in selected
            for start in range(0, len(FAMILIES[family]), MAX_TRACE_STRIPS)
        ]
        pages: list[list[tuple[str, list[str]]]] = []
        used = 0
        for section in sections:
            cost = len(section[1]) + (1 if used else 0)
            if used and used + cost > MAX_TRACE_STRIPS:
                pages.append([])
                used = 0
                cost = len(section[1])
            if not pages or not pages[-1]:
                if not pages or pages[-1]:
                    pages.append([])
            pages[-1].append(section)
            used += cost
        for page_sections in pages:
            draw_packed_page(pdf, page_sections)
            page_count += 1
        pdf.save()
        print(f"Created {args.output} ({page_count} page(s))")
        return
    singletons: list[tuple[str, str]] = []
    for family in selected:
        words = FAMILIES[family]
        if args.merge_singletons and len(words) == 1:
            singletons.append((family, words[0]))
            continue
        for start in range(0, len(words), 10):
            draw_page(pdf, family, words[start:start + 10])
            page_count += 1
    for start in range(0, len(singletons), MAX_TRACE_STRIPS):
        draw_singleton_page(
            pdf,
            singletons[start:start + MAX_TRACE_STRIPS],
            args.vowel or singletons[start][0][0],
        )
        page_count += 1
    pdf.save()
    print(f"Created {args.output} ({page_count} page(s))")


if __name__ == "__main__":
    main()
