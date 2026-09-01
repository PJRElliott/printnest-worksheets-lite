#!/usr/bin/env python3
"""
PrintNest - Kindergarten Math Workbook 50ページPDFを一発生成。

問題は random で自動生成、PDFは reportlab で直接組版。画像生成AI不要。

Usage:
  python3 generate_math.py --book math_kg [--seed 42]
"""

import argparse
import json
import random
import sys
from pathlib import Path

try:
    from reportlab.lib.colors import HexColor, black, gray
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
except ImportError:
    sys.exit("Install reportlab: pip3 install reportlab")

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_BASE = Path.home() / "Desktop" / "PrintNest"

PAGE_W, PAGE_H = letter
MARGIN = 0.6 * inch

# カラーパレット（子供向けに優しい色）
PRIMARY = HexColor("#3B82F6")
ACCENT = HexColor("#F59E0B")
SOFT_PINK = HexColor("#FBCFE8")
SOFT_BLUE = HexColor("#BAE6FD")
LIGHT_GRAY = HexColor("#E5E7EB")
DARK = HexColor("#1F2937")


def load_meta(book: str) -> dict:
    return json.loads((SKILL_DIR / "references" / f"{book}_meta.json").read_text())


def draw_header(c: canvas.Canvas, title: str) -> None:
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - 5, title)
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(2)
    c.line(MARGIN, PAGE_H - MARGIN - 25, PAGE_W - MARGIN, PAGE_H - MARGIN - 25)


def draw_footer(c: canvas.Canvas, page_num: int) -> None:
    c.setFont("Helvetica", 9)
    c.setFillColor(gray)
    c.drawString(MARGIN, MARGIN / 2, "__YOUR_BRAND__")
    c.drawCentredString(PAGE_W / 2, MARGIN / 2, f"Page {page_num}")
    c.drawRightString(PAGE_W - MARGIN, MARGIN / 2, "Name: ____________________")


def page_cover(c: canvas.Canvas, meta: dict) -> None:
    # 上部 アクセント帯
    c.setFillColor(SOFT_PINK)
    c.rect(0, PAGE_H - 1.3 * inch, PAGE_W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(SOFT_BLUE)
    c.rect(0, 0, PAGE_W, 1.3 * inch, fill=1, stroke=0)

    # タイトル（2行に分割してマージン確保）
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 52)
    title_parts = meta["title"].split(" ", 1)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.5 * inch, title_parts[0])
    if len(title_parts) > 1:
        c.drawCentredString(PAGE_W / 2, PAGE_H - 3.3 * inch, title_parts[1])

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(PRIMARY)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.0 * inch, "50 Printable Worksheets")

    c.setFont("Helvetica", 15)
    c.setFillColor(DARK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.6 * inch, "Numbers 1-20  ·  Addition  ·  Subtraction  ·  Shapes")

    # AGES バッジ
    c.setFillColor(ACCENT)
    badge_w, badge_h = 2.4 * inch, 0.8 * inch
    bx = (PAGE_W - badge_w) / 2
    by = 2.5 * inch
    c.roundRect(bx, by, badge_w, badge_h, 0.15 * inch, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(PAGE_W / 2, by + 0.25 * inch, "AGES 4-6")

    # 著者
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(DARK)
    c.drawCentredString(PAGE_W / 2, 0.5 * inch, f"by {meta.get('author', '__YOUR_BRAND__')}")

    c.showPage()


def page_copyright(c: canvas.Canvas, meta: dict) -> None:
    c.setFont("Helvetica", 11)
    c.setFillColor(DARK)
    lines = [
        f"© 2026 {meta.get('author', '__YOUR_BRAND__')}. All rights reserved.",
        "",
        "This workbook is for personal and single-classroom use only.",
        "Please do not resell, redistribute, or share the file.",
        "",
        "Designs and worksheet content created by the author.",
        "Cover illustration created with the help of AI image",
        "generation tools. All worksheet problems and layouts are",
        "designed and generated programmatically.",
        "",
        "Thank you for supporting an independent creator.",
        "Find more printables at: etsy.com/shop/__YOUR_SHOP__",
    ]
    y = PAGE_H - 2.2 * inch
    for line in lines:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 0.3 * inch
    c.showPage()


def page_number_tracing(c: canvas.Canvas, page_num: int, number: int) -> None:
    draw_header(c, "Trace the Number")

    # 大きな数字（薄く）
    c.setFillColor(LIGHT_GRAY)
    c.setFont("Helvetica-Bold", 400)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 80, str(number))

    # ヒントテキスト
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(MARGIN, 2.7 * inch, f"Number: {number}")

    # ドット罫線（書き込み欄）
    c.setFillColor(DARK)
    c.setFont("Helvetica", 16)
    c.drawString(MARGIN, 2.3 * inch, "Practice writing:")
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(1)
    line_y = 1.9 * inch
    for _ in range(3):
        # 点線
        c.setDash(3, 4)
        c.line(MARGIN, line_y, PAGE_W - MARGIN, line_y)
        c.setDash(1, 0)  # reset
        line_y -= 0.35 * inch

    draw_footer(c, page_num)
    c.showPage()


def page_count_and_color(c: canvas.Canvas, page_num: int, target_count: int, total_count: int) -> None:
    draw_header(c, "Count and Color")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 18)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        f"Color {target_count} of the circles below.")

    # 円を配置（10個まで）
    positions = [
        (2.0, 6.5), (3.7, 6.7), (5.4, 6.4), (6.8, 6.6),
        (2.3, 5.3), (4.0, 5.5), (5.7, 5.2), (7.0, 5.4),
        (3.0, 4.0), (5.0, 4.2),
    ]
    c.setStrokeColor(DARK)
    c.setLineWidth(2.5)
    c.setFillColor(HexColor("#FFFFFF"))
    for i, (x, y) in enumerate(positions[:total_count]):
        c.circle(x * inch, y * inch, 0.4 * inch, stroke=1, fill=1)

    # 答え欄
    c.setFillColor(DARK)
    c.setFont("Helvetica", 16)
    c.drawString(MARGIN, 2.5 * inch,
                 f"How many circles in total? Total: ______")
    c.drawString(MARGIN, 2.0 * inch,
                 f"How many did you color? Colored: ______")

    draw_footer(c, page_num)
    c.showPage()


def page_addition(c: canvas.Canvas, page_num: int) -> list[tuple[int, int, int]]:
    draw_header(c, "Simple Addition")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        "Add the numbers and write the answer.")

    problems: list[tuple[int, int, int]] = []
    c.setFont("Helvetica-Bold", 30)
    y_start = PAGE_H - 2.3 * inch
    col1_x = MARGIN + 0.4 * inch
    col2_x = PAGE_W / 2 + 0.4 * inch
    for i in range(5):
        a = random.randint(0, 9)
        b = random.randint(0, 10 - a)
        problems.append((a, b, a + b))
        c.drawString(col1_x, y_start - i * 0.95 * inch, f"{a}  +  {b}  =  _____")

        a2 = random.randint(0, 9)
        b2 = random.randint(0, 10 - a2)
        problems.append((a2, b2, a2 + b2))
        c.drawString(col2_x, y_start - i * 0.95 * inch, f"{a2}  +  {b2}  =  _____")

    draw_footer(c, page_num)
    c.showPage()
    return problems


def page_subtraction(c: canvas.Canvas, page_num: int) -> list[tuple[int, int, int]]:
    draw_header(c, "Simple Subtraction")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        "Subtract the numbers and write the answer.")

    problems: list[tuple[int, int, int]] = []
    c.setFont("Helvetica-Bold", 30)
    y_start = PAGE_H - 2.3 * inch
    col1_x = MARGIN + 0.4 * inch
    col2_x = PAGE_W / 2 + 0.4 * inch
    for i in range(5):
        a = random.randint(2, 10)
        b = random.randint(0, a)
        problems.append((a, b, a - b))
        c.drawString(col1_x, y_start - i * 0.95 * inch, f"{a}  −  {b}  =  _____")

        a2 = random.randint(2, 10)
        b2 = random.randint(0, a2)
        problems.append((a2, b2, a2 - b2))
        c.drawString(col2_x, y_start - i * 0.95 * inch, f"{a2}  −  {b2}  =  _____")

    draw_footer(c, page_num)
    c.showPage()
    return problems


def draw_shape(c: canvas.Canvas, shape: str, cx: float, cy: float, size: float = 0.4 * inch) -> None:
    if shape == "circle":
        c.circle(cx, cy, size, stroke=1, fill=0)
    elif shape == "square":
        c.rect(cx - size, cy - size, 2 * size, 2 * size, stroke=1, fill=0)
    elif shape == "triangle":
        p = c.beginPath()
        p.moveTo(cx, cy + size)
        p.lineTo(cx - size, cy - size * 0.8)
        p.lineTo(cx + size, cy - size * 0.8)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
    elif shape == "star":
        # 5芒星近似
        import math
        pts = []
        for i in range(10):
            r = size if i % 2 == 0 else size * 0.4
            ang = math.radians(i * 36 - 90)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        p = c.beginPath()
        p.moveTo(*pts[0])
        for px, py in pts[1:]:
            p.lineTo(px, py)
        p.close()
        c.drawPath(p, stroke=1, fill=0)


def page_shapes(c: canvas.Canvas, page_num: int, target_shape: str, target_count: int, decoys: list[tuple[str, int]]) -> None:
    draw_header(c, f"Count the {target_shape.capitalize()}s")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        f"How many {target_shape}s do you see?")

    # 多種類の図形を混ぜて配置
    positions = [
        (1.8, 6.5), (3.2, 6.7), (4.6, 6.4), (6.0, 6.6), (7.2, 6.5),
        (2.0, 5.3), (3.5, 5.5), (5.0, 5.2), (6.5, 5.4), (7.5, 5.3),
        (2.4, 4.0), (4.0, 4.2), (5.6, 4.0), (6.8, 4.1),
        (3.0, 2.9), (4.5, 3.0), (6.0, 2.8),
    ]
    c.setStrokeColor(DARK)
    c.setLineWidth(2)

    shapes_to_place: list[str] = [target_shape] * target_count
    for shape, n in decoys:
        shapes_to_place.extend([shape] * n)
    random.shuffle(shapes_to_place)

    for i, (x, y) in enumerate(positions[:len(shapes_to_place)]):
        draw_shape(c, shapes_to_place[i], x * inch, y * inch)

    # 答え欄
    c.setFillColor(DARK)
    c.setFont("Helvetica", 16)
    c.drawString(MARGIN, 2.0 * inch, f"Answer: _______ {target_shape}s")

    draw_footer(c, page_num)
    c.showPage()


def page_answer_key(c: canvas.Canvas, page_num: int,
                    add_problems: list[list[tuple[int, int, int]]],
                    sub_problems: list[list[tuple[int, int, int]]]) -> None:
    draw_header(c, "Answer Key")

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, PAGE_H - 1.5 * inch, "Addition Pages")

    c.setFont("Helvetica", 10)
    y = PAGE_H - 1.85 * inch
    for i, page_set in enumerate(add_problems, start=1):
        line = " · ".join([f"{a}+{b}={s}" for a, b, s in page_set])
        c.drawString(MARGIN, y, f"P{i}: {line}")
        y -= 0.18 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, y - 0.1 * inch, "Subtraction Pages")
    y -= 0.45 * inch

    c.setFont("Helvetica", 10)
    for i, page_set in enumerate(sub_problems, start=1):
        line = " · ".join([f"{a}-{b}={d}" for a, b, d in page_set])
        c.drawString(MARGIN, y, f"P{i}: {line}")
        y -= 0.18 * inch

    draw_footer(c, page_num)
    c.showPage()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    meta = load_meta(args.book)
    out_dir = OUTPUT_BASE / args.book
    out_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = out_dir / f"{args.book}_workbook.pdf"

    c = canvas.Canvas(str(output_pdf), pagesize=letter)

    page_num = 0
    page_cover(c, meta)
    page_num += 1
    page_copyright(c, meta)
    page_num += 1

    # Number Tracing 1-10 (10 pages)
    for n in range(1, 11):
        page_num += 1
        page_number_tracing(c, page_num, n)

    # Number Tracing 11-20 (10 pages)
    for n in range(11, 21):
        page_num += 1
        page_number_tracing(c, page_num, n)

    # Count and Color (5 pages)
    for total, target in [(5, 3), (7, 4), (8, 5), (9, 6), (10, 7)]:
        page_num += 1
        page_count_and_color(c, page_num, target, total)

    # Addition (10 pages, 10問/ページ)
    addition_problems: list[list[tuple[int, int, int]]] = []
    for _ in range(10):
        page_num += 1
        addition_problems.append(page_addition(c, page_num))

    # Subtraction (8 pages)
    subtraction_problems: list[list[tuple[int, int, int]]] = []
    for _ in range(8):
        page_num += 1
        subtraction_problems.append(page_subtraction(c, page_num))

    # Shapes (5 pages)
    shape_configs = [
        ("circle", 5, [("square", 3), ("triangle", 2)]),
        ("square", 6, [("circle", 3), ("triangle", 2)]),
        ("triangle", 4, [("circle", 4), ("square", 3)]),
        ("star", 5, [("circle", 3), ("square", 3), ("triangle", 2)]),
        ("circle", 7, [("square", 2), ("triangle", 2), ("star", 2)]),
    ]
    for shape, count, decoys in shape_configs:
        page_num += 1
        page_shapes(c, page_num, shape, count, decoys)

    # Answer Key (2 pages: split addition / subtraction)
    page_num += 1
    page_answer_key(c, page_num, addition_problems[:5], subtraction_problems[:4])
    page_num += 1
    page_answer_key(c, page_num, addition_problems[5:], subtraction_problems[4:])

    c.save()
    print(f"Done. {page_num} pages total")
    print(f"Output: {output_pdf}")


if __name__ == "__main__":
    main()
