#!/usr/bin/env python3
"""
PrintNest - Alphabet Tracing Workbook (Pre-K) 68ページPDFを一発生成。

Uppercase A-Z + Lowercase a-z + 認識/マッチング/Beginning Sound。
すべて reportlab で直接描画、画像生成AI不要。

Usage:
  python3 generate_alphabet.py --book alphabet_prek [--seed 42]
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

PRIMARY = HexColor("#0EA5E9")
ACCENT = HexColor("#F59E0B")
SOFT_PINK = HexColor("#FCE7F3")
SOFT_BLUE = HexColor("#DBEAFE")
SOFT_YELLOW = HexColor("#FEF3C7")
LIGHT_GRAY = HexColor("#E5E7EB")
MID_GRAY = HexColor("#D1D5DB")
DARK = HexColor("#1F2937")

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

BEGINNING_WORDS = {
    "A": "Apple", "B": "Ball", "C": "Cat", "D": "Dog", "E": "Egg",
    "F": "Fish", "G": "Goat", "H": "Hat", "I": "Ice", "J": "Jam",
    "K": "Kite", "L": "Lion", "M": "Moon", "N": "Nest", "O": "Owl",
    "P": "Pig", "Q": "Queen", "R": "Rabbit", "S": "Sun", "T": "Tree",
    "U": "Umbrella", "V": "Van", "W": "Whale", "X": "X-ray", "Y": "Yarn", "Z": "Zebra",
}


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
    c.setFillColor(SOFT_PINK)
    c.rect(0, PAGE_H - 1.3 * inch, PAGE_W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(SOFT_BLUE)
    c.rect(0, 0, PAGE_W, 1.3 * inch, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 56)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.5 * inch, "Alphabet")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 3.3 * inch, "Tracing")

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(PRIMARY)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.0 * inch, "A-Z Letter Practice Workbook")

    c.setFont("Helvetica", 15)
    c.setFillColor(DARK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.7 * inch, "Uppercase · Lowercase · Recognition · Beginning Sounds")

    # ABCバッジ風（大きなA B C 装飾・中央寄せ・3色とも視認可）
    deco = ["A", "B", "C"]
    deco_colors = [PRIMARY, ACCENT, HexColor("#EC4899")]
    c.setFont("Helvetica-Bold", 100)
    spacing = 1.2 * inch
    for i, ch in enumerate(deco):
        c.setFillColor(deco_colors[i])
        cx = PAGE_W / 2 + (i - 1) * spacing
        c.drawCentredString(cx, 3.4 * inch, ch)

    # AGES バッジ
    c.setFillColor(ACCENT)
    badge_w, badge_h = 2.4 * inch, 0.8 * inch
    bx = (PAGE_W - badge_w) / 2
    by = 2.0 * inch
    c.roundRect(bx, by, badge_w, badge_h, 0.15 * inch, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_W / 2, by + 0.25 * inch, "AGES 3-5")

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
        "All worksheet content (letters, layouts, activities) was",
        "designed and generated programmatically by the author.",
        "Cover illustration created with the help of AI image",
        "generation tools.",
        "",
        "Thank you for supporting an independent creator.",
        "Find more printables at: etsy.com/shop/__YOUR_SHOP__",
    ]
    y = PAGE_H - 2.2 * inch
    for line in lines:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 0.3 * inch
    c.showPage()


def draw_4line_guide(c: canvas.Canvas, x_left: float, x_right: float, baseline_y: float, scale: float = 1.0) -> None:
    """4本罫線（手書き練習用 top / midline / baseline / descender）。"""
    gap = 0.32 * inch * scale
    top = baseline_y + 2 * gap
    mid_high = baseline_y + gap  # midline
    base = baseline_y
    descender = baseline_y - gap
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(1)
    # top solid
    c.setDash(1, 0)
    c.line(x_left, top, x_right, top)
    # midline dashed
    c.setDash(3, 3)
    c.line(x_left, mid_high, x_right, mid_high)
    # baseline solid (heaviest)
    c.setDash(1, 0)
    c.setStrokeColor(DARK)
    c.setLineWidth(1.4)
    c.line(x_left, base, x_right, base)
    # descender dashed
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(1)
    c.setDash(3, 3)
    c.line(x_left, descender, x_right, descender)
    c.setDash(1, 0)


def page_letter_tracing(c: canvas.Canvas, page_num: int, letter_char: str, is_upper: bool) -> None:
    title = "Trace the Uppercase Letter" if is_upper else "Trace the Lowercase Letter"
    draw_header(c, title)

    # Letter shown big + word
    word = BEGINNING_WORDS[letter_char.upper()]
    display_letter = letter_char if is_upper else letter_char.lower()

    # 巨大シルエット（ヘッダーと被らないよう下に）
    c.setFillColor(SOFT_YELLOW if is_upper else SOFT_BLUE)
    c.setFont("Helvetica-Bold", 280)
    c.drawCentredString(PAGE_W / 2 + 1.8 * inch, PAGE_H - 5.0 * inch, display_letter)

    # ラベル
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 60)
    c.drawString(MARGIN, PAGE_H - 2.1 * inch, f"{letter_char}  {letter_char.lower()}")

    c.setFont("Helvetica", 18)
    c.drawString(MARGIN, PAGE_H - 2.6 * inch, f"{letter_char} is for {word}")

    # トレース練習（4本罫線×2行、各行に薄い文字6個）
    practice_letter = display_letter
    for row in range(2):
        baseline_y = 3.0 * inch - row * 1.4 * inch
        draw_4line_guide(c, MARGIN, PAGE_W - MARGIN, baseline_y)
        # 薄い文字を等間隔に配置（最初の2個はガイド付き、残り4個は薄文字、最後2個は空欄）
        usable_w = PAGE_W - 2 * MARGIN
        slot_w = usable_w / 6
        font_size = 60
        c.setFont("Helvetica-Bold", font_size)
        c.setFillColor(LIGHT_GRAY)
        for i in range(4):  # 6スロット中4個に薄文字（最後2スロットは空欄=自分で書く）
            x_center = MARGIN + slot_w * (i + 0.5)
            c.drawCentredString(x_center, baseline_y + 0.02 * inch, practice_letter)

    # ヒント
    c.setFillColor(DARK)
    c.setFont("Helvetica", 13)
    c.drawString(MARGIN, 0.8 * inch, "Trace the gray letters first, then write your own in the empty spaces.")

    draw_footer(c, page_num)
    c.showPage()


def page_letter_recognition(c: canvas.Canvas, page_num: int, target: str, decoys: list[str]) -> None:
    draw_header(c, f"Find and Circle the Letter {target}")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        f"Circle every '{target}' you can find. How many did you find?")

    # 6x7 グリッドで文字混在
    grid_cols = 7
    grid_rows = 6
    cell_w = (PAGE_W - 2 * MARGIN) / grid_cols
    cell_h = 0.95 * inch
    top_y = PAGE_H - 2.3 * inch

    letters_pool: list[str] = []
    target_count = random.randint(10, 14)
    letters_pool.extend([target] * target_count)
    while len(letters_pool) < grid_cols * grid_rows:
        letters_pool.append(random.choice(decoys))
    random.shuffle(letters_pool)

    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(DARK)
    for row in range(grid_rows):
        for col in range(grid_cols):
            i = row * grid_cols + col
            x = MARGIN + cell_w * (col + 0.5)
            y = top_y - cell_h * row
            c.drawCentredString(x, y, letters_pool[i])

    c.setFont("Helvetica", 16)
    c.drawString(MARGIN, 1.5 * inch, f"How many '{target}' did you find?  Answer: ______")
    c.drawString(MARGIN, 1.1 * inch, f"(Correct answer: {target_count})")

    draw_footer(c, page_num)
    c.showPage()


def page_matching(c: canvas.Canvas, page_num: int, pairs: list[str]) -> None:
    draw_header(c, "Match Uppercase to Lowercase")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        "Draw a line from each uppercase letter to its lowercase pair.")

    # 左列大文字、右列小文字（シャッフル）
    upper = pairs.copy()
    lower = [p.lower() for p in pairs]
    random.shuffle(lower)

    c.setFont("Helvetica-Bold", 56)
    left_x = MARGIN + 0.8 * inch
    right_x = PAGE_W - MARGIN - 0.8 * inch
    n = len(pairs)
    spacing = (PAGE_H - 4 * inch) / max(n - 1, 1)
    top_y = PAGE_H - 2.5 * inch

    for i in range(n):
        y = top_y - i * spacing
        c.setFillColor(DARK)
        c.drawCentredString(left_x, y, upper[i])
        c.drawCentredString(right_x, y, lower[i])
        # ガイド点（マッチング用）
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica-Bold", 18)
        c.circle(left_x + 0.6 * inch, y + 0.18 * inch, 0.07 * inch, stroke=1, fill=0)
        c.circle(right_x - 0.6 * inch, y + 0.18 * inch, 0.07 * inch, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 56)

    draw_footer(c, page_num)
    c.showPage()


def page_beginning_sound(c: canvas.Canvas, page_num: int, letters_block: list[str]) -> None:
    draw_header(c, "Beginning Sounds")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        "Say the word out loud. Trace the letter that the word starts with.")

    # 各letter について大文字＋単語を表示
    n = len(letters_block)
    spacing_y = (PAGE_H - 3 * inch) / n
    top_y = PAGE_H - 2.3 * inch

    for i, L in enumerate(letters_block):
        word = BEGINNING_WORDS[L]
        y = top_y - i * spacing_y

        # 大文字（薄い灰色でなぞる用）
        c.setFillColor(LIGHT_GRAY)
        c.setFont("Helvetica-Bold", 72)
        c.drawString(MARGIN + 0.2 * inch, y - 0.15 * inch, L)

        # 単語
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 32)
        c.drawString(MARGIN + 1.6 * inch, y + 0.15 * inch, word)

        # 罫線
        c.setStrokeColor(MID_GRAY)
        c.setLineWidth(1.5)
        c.setDash(1, 0)
        line_y = y - 0.05 * inch
        c.line(MARGIN + 1.6 * inch, line_y, PAGE_W - MARGIN, line_y)

        # ヒント
        c.setFillColor(gray)
        c.setFont("Helvetica-Oblique", 11)
        c.drawString(MARGIN + 1.6 * inch, line_y - 0.18 * inch,
                     f"\"{word}\" starts with the letter {L}.")

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

    # Uppercase A-Z (26 pages)
    for L in LETTERS:
        page_num += 1
        page_letter_tracing(c, page_num, L, is_upper=True)

    # Lowercase a-z (26 pages)
    for L in LETTERS:
        page_num += 1
        page_letter_tracing(c, page_num, L, is_upper=False)

    # Letter Recognition (6 pages)
    recognition_targets = ["A", "E", "M", "S", "B", "T"]
    for target in recognition_targets:
        decoys = [c2 for c2 in LETTERS if c2 != target]
        page_num += 1
        page_letter_recognition(c, page_num, target, decoys)

    # Matching Uppercase to Lowercase (4 pages, 7 pairs each)
    matching_letters = list(LETTERS)
    random.shuffle(matching_letters)
    for i in range(4):
        block = matching_letters[i * 7 : i * 7 + 7]
        if len(block) < 7:
            block += random.sample([x for x in LETTERS if x not in block], 7 - len(block))
        page_num += 1
        page_matching(c, page_num, block)

    # Beginning Sounds (4 pages, 6 letters each)
    beginning_letters = list(LETTERS)
    random.shuffle(beginning_letters)
    for i in range(4):
        block = beginning_letters[i * 6 : i * 6 + 6]
        if len(block) < 6:
            block += random.sample([x for x in LETTERS if x not in block], 6 - len(block))
        page_num += 1
        page_beginning_sound(c, page_num, block)

    c.save()
    print(f"Done. {page_num} pages total")
    print(f"Output: {output_pdf}")


if __name__ == "__main__":
    main()
