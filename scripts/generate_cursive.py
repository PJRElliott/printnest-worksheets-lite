#!/usr/bin/env python3
"""
PrintNest - Cursive Handwriting Workbook を一発生成。

Apple Chancery を筆記体フォントとして登録 → A-Z, a-z 各1ページ + 単語/文ページ。
4本罫線ガイド・薄字トレース・自由書き欄を提供。

Usage:
  python3 generate_cursive.py --book cursive_handwriting
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from reportlab.lib.colors import HexColor, black, gray, white
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
except ImportError:
    sys.exit("Install reportlab: pip3 install reportlab")

# 筆記体フォントを登録
CURSIVE_TTF = Path("/System/Library/Fonts/Supplemental/Apple Chancery.ttf")
if not CURSIVE_TTF.exists():
    sys.exit(f"Cursive font not found: {CURSIVE_TTF}")
pdfmetrics.registerFont(TTFont("Cursive", str(CURSIVE_TTF)))

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_BASE = Path.home() / "Desktop" / "PrintNest"
PAGE_W, PAGE_H = letter
MARGIN = 0.6 * inch

PRIMARY = HexColor("#0EA5E9")
ACCENT = HexColor("#F59E0B")
SOFT_BLUE = HexColor("#DBEAFE")
SOFT_PINK = HexColor("#FCE7F3")
SOFT_YELLOW = HexColor("#FEF3C7")
LIGHT_GRAY = HexColor("#E5E7EB")
MID_GRAY = HexColor("#9CA3AF")
TRACE_GRAY = HexColor("#D1D5DB")
DARK = HexColor("#1F2937")

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
WORDS = ["cat", "dog", "sun", "moon", "tree", "fish", "bird", "star",
         "love", "hope", "kind", "play", "read", "smile", "happy", "friend"]
SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Practice makes perfect.",
    "Every day is a fresh start.",
    "Read every day.",
]


def load_meta(book: str) -> dict:
    return json.loads((SKILL_DIR / "references" / f"{book}_meta.json").read_text())


def draw_header(c, title: str, subtitle: str = "") -> None:
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - 5, title)
    if subtitle:
        c.setFillColor(DARK)
        c.setFont("Helvetica", 11)
        c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - 22, subtitle)
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(2)
    c.line(MARGIN, PAGE_H - MARGIN - 32, PAGE_W - MARGIN, PAGE_H - MARGIN - 32)


def draw_footer(c, page_num: int) -> None:
    c.setFont("Helvetica", 9)
    c.setFillColor(gray)
    c.drawString(MARGIN, MARGIN / 2, "__YOUR_BRAND__")
    c.drawCentredString(PAGE_W / 2, MARGIN / 2, f"Page {page_num}")
    c.drawRightString(PAGE_W - MARGIN, MARGIN / 2, "Name: ______________")


def draw_4line(c, x_left, x_right, baseline_y, gap=0.32 * inch) -> None:
    """4本罫線：top / mid（点線）/ baseline / descender（点線）"""
    top = baseline_y + 2 * gap
    mid = baseline_y + gap
    desc = baseline_y - gap
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(1)
    c.setDash(1, 0)
    c.line(x_left, top, x_right, top)
    c.setDash(3, 3)
    c.line(x_left, mid, x_right, mid)
    c.setDash(1, 0)
    c.setStrokeColor(DARK)
    c.setLineWidth(1.4)
    c.line(x_left, baseline_y, x_right, baseline_y)
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(1)
    c.setDash(3, 3)
    c.line(x_left, desc, x_right, desc)
    c.setDash(1, 0)


def page_cover(c, meta: dict) -> None:
    c.setFillColor(SOFT_PINK)
    c.rect(0, PAGE_H - 1.3 * inch, PAGE_W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(SOFT_BLUE)
    c.rect(0, 0, PAGE_W, 1.3 * inch, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 50)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.4 * inch, "Cursive")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 3.2 * inch, "Handwriting")
    c.setFont("Helvetica", 15)
    c.setFillColor(PRIMARY)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 3.8 * inch,
                        "A-Z Practice  ·  Letters, Words & Sentences")

    # 装飾：大きな cursive A B C
    deco_letters = ["A", "B", "C"]
    deco_colors = [PRIMARY, ACCENT, HexColor("#EC4899")]
    c.setFont("Cursive", 130)
    spacing = 1.5 * inch
    for i, ch in enumerate(deco_letters):
        c.setFillColor(deco_colors[i])
        cx = PAGE_W / 2 + (i - 1) * spacing
        c.drawCentredString(cx, 4.0 * inch, ch)

    c.setFillColor(ACCENT)
    bw, bh = 2.4 * inch, 0.85 * inch
    c.roundRect((PAGE_W - bw) / 2, 2.2 * inch, bw, bh, 0.15 * inch, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PAGE_W / 2, 2.5 * inch, "GRADES 2-4")

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(DARK)
    c.drawCentredString(PAGE_W / 2, 0.5 * inch,
                        f"by {meta.get('author', '__YOUR_BRAND__')}")
    c.showPage()


def page_copyright(c, meta: dict) -> None:
    c.setFont("Helvetica", 11)
    c.setFillColor(DARK)
    lines = [
        f"© 2026 {meta.get('author', '__YOUR_BRAND__')}. All rights reserved.",
        "",
        "This workbook is for personal and single-classroom use only.",
        "Please do not resell, redistribute, or share the file.",
        "",
        "Cursive letterforms based on Apple Chancery typeface.",
        "All worksheet layouts were programmatically generated by the",
        "author. Cover illustration created with the help of AI image",
        "generation tools.",
        "",
        "Find more printables at: etsy.com/shop/__YOUR_SHOP__",
    ]
    y = PAGE_H - 2.2 * inch
    for line in lines:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 0.3 * inch
    c.showPage()


def page_howto(c) -> None:
    draw_header(c, "How to Use This Workbook",
                "Learn cursive writing step by step.")
    steps = [
        "1. Look at the model letter at the top of each page.",
        "2. Trace over the light gray letters carefully.",
        "3. Then write the letter on your own on the blank line.",
        "4. Use the 4-line guides to keep your letters the right size.",
        "5. Practice every day for the best results!",
    ]
    y = PAGE_H - 2.4 * inch
    c.setFont("Helvetica", 14)
    c.setFillColor(DARK)
    for s in steps:
        c.drawString(MARGIN + 0.3 * inch, y, s)
        y -= 0.45 * inch

    # 罫線の見本
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 0.3 * inch, 2.4 * inch, "The 4-line guide:")
    draw_4line(c, MARGIN + 0.3 * inch, PAGE_W - MARGIN - 0.3 * inch,
               1.5 * inch, gap=0.25 * inch)
    c.setFont("Cursive", 50)
    c.setFillColor(PRIMARY)
    c.drawString(MARGIN + 0.5 * inch, 1.52 * inch, "Aa")
    draw_footer(c, 3)
    c.showPage()


def page_letter(c, page_num: int, ch: str, is_upper: bool) -> None:
    case_word = "Uppercase" if is_upper else "Lowercase"
    display = ch if is_upper else ch.lower()
    draw_header(c, f"{case_word} Cursive  ·  {display}",
                f"Trace the cursive {display}, then write your own.")

    # 大きな手本（背景）
    c.setFillColor(TRACE_GRAY)
    c.setFont("Cursive", 220)
    c.drawCentredString(PAGE_W / 2 + 1.0 * inch, PAGE_H - 4.6 * inch, display)

    # 左上に説明
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 56)
    c.drawString(MARGIN, PAGE_H - 2.0 * inch, f"{display}")
    c.setFont("Helvetica", 12)
    c.drawString(MARGIN, PAGE_H - 2.4 * inch, "Trace 4 times, then write 4 times")

    # トレース行 ×2（descender が footer に被らないよう2行に・各8文字）
    practice_letter = display
    for row in range(2):
        baseline_y = 3.2 * inch - row * 1.6 * inch
        draw_4line(c, MARGIN, PAGE_W - MARGIN, baseline_y, gap=0.32 * inch)
        usable = PAGE_W - 2 * MARGIN
        slot = usable / 8
        c.setFont("Cursive", 56)
        for i in range(4):
            x_center = MARGIN + slot * (i + 0.5)
            c.setFillColor(TRACE_GRAY)
            c.drawCentredString(x_center, baseline_y + 0.04 * inch, practice_letter)

    draw_footer(c, page_num)
    c.showPage()


def page_word(c, page_num: int, words: list[str]) -> None:
    draw_header(c, "Cursive Word Practice",
                "Trace each word, then write it on your own.")
    rows_per_page = min(len(words), 6)
    for r in range(rows_per_page):
        baseline_y = PAGE_H - 1.9 * inch - r * 1.3 * inch
        draw_4line(c, MARGIN, PAGE_W - MARGIN, baseline_y, gap=0.3 * inch)
        word = words[r]
        c.setFont("Cursive", 40)
        # 左半分にトレース文字（薄）×2
        c.setFillColor(TRACE_GRAY)
        c.drawString(MARGIN + 0.3 * inch, baseline_y + 0.04 * inch, word)
        c.drawString(MARGIN + 2.4 * inch, baseline_y + 0.04 * inch, word)
        # 右半分は空白（生徒が書く）
    draw_footer(c, page_num)
    c.showPage()


def page_sentence(c, page_num: int, sentence: str) -> None:
    draw_header(c, "Cursive Sentence Practice",
                "Trace the sentence, then write it on your own.")
    # 1文を上下2行（trace + blank）×3セット
    for r in range(3):
        baseline_y = PAGE_H - 2.2 * inch - r * 1.6 * inch
        draw_4line(c, MARGIN, PAGE_W - MARGIN, baseline_y, gap=0.28 * inch)
        c.setFont("Cursive", 28)
        c.setFillColor(TRACE_GRAY)
        c.drawString(MARGIN + 0.2 * inch, baseline_y + 0.04 * inch, sentence)
        # 下に空白行
        baseline_y2 = baseline_y - 0.85 * inch
        draw_4line(c, MARGIN, PAGE_W - MARGIN, baseline_y2, gap=0.28 * inch)
    draw_footer(c, page_num)
    c.showPage()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", default="cursive_handwriting")
    args = parser.parse_args()

    meta = load_meta(args.book)
    out_dir = OUTPUT_BASE / args.book
    out_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = out_dir / f"{args.book}_workbook.pdf"

    c = canvas.Canvas(str(output_pdf), pagesize=letter)
    page_num = 0
    page_cover(c, meta); page_num += 1
    page_copyright(c, meta); page_num += 1
    page_howto(c); page_num += 1

    # Uppercase A-Z
    for ch in LETTERS:
        page_num += 1
        page_letter(c, page_num, ch, is_upper=True)
    # Lowercase a-z
    for ch in LETTERS:
        page_num += 1
        page_letter(c, page_num, ch, is_upper=False)

    # Words: 6 per page → 16 words / 6 = 3 pages
    for i in range(0, len(WORDS), 6):
        page_num += 1
        page_word(c, page_num, WORDS[i:i + 6])

    # Sentences: 1 per page
    for s in SENTENCES:
        page_num += 1
        page_sentence(c, page_num, s)

    c.save()
    print(f"Done. {page_num} pages total")
    print(f"Output: {output_pdf}")


if __name__ == "__main__":
    main()
