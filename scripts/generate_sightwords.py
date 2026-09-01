#!/usr/bin/env python3
"""
PrintNest - Sight Words 100 Workbook 70ページPDFを一発生成。

Pre-K + Kindergarten の高頻出100単語をなぞり書き＋アクティビティで定着。
完全純Python・画像生成AI不要。

Usage:
  python3 generate_sightwords.py --book sightwords [--seed 42]
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

PRIMARY = HexColor("#8B5CF6")
ACCENT = HexColor("#F59E0B")
SOFT_PINK = HexColor("#FCE7F3")
SOFT_BLUE = HexColor("#DBEAFE")
SOFT_GREEN = HexColor("#D1FAE5")
LIGHT_GRAY = HexColor("#E5E7EB")
MID_GRAY = HexColor("#D1D5DB")
DARK = HexColor("#1F2937")


def load_meta(book: str) -> dict:
    return json.loads((SKILL_DIR / "references" / f"{book}_meta.json").read_text())


def draw_header(c, title: str) -> None:
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN - 5, title)
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(2)
    c.line(MARGIN, PAGE_H - MARGIN - 25, PAGE_W - MARGIN, PAGE_H - MARGIN - 25)


def draw_footer(c, page_num: int) -> None:
    c.setFont("Helvetica", 9)
    c.setFillColor(gray)
    c.drawString(MARGIN, MARGIN / 2, "__YOUR_BRAND__")
    c.drawCentredString(PAGE_W / 2, MARGIN / 2, f"Page {page_num}")
    c.drawRightString(PAGE_W - MARGIN, MARGIN / 2, "Name: ____________________")


def page_cover(c, meta: dict) -> None:
    c.setFillColor(SOFT_PINK)
    c.rect(0, PAGE_H - 1.3 * inch, PAGE_W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(SOFT_BLUE)
    c.rect(0, 0, PAGE_W, 1.3 * inch, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 56)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.5 * inch, "Sight Words")
    c.drawCentredString(PAGE_W / 2, PAGE_H - 3.4 * inch, "100")

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(PRIMARY)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.1 * inch, "Pre-K & Kindergarten Workbook")

    c.setFont("Helvetica", 14)
    c.setFillColor(DARK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.7 * inch,
                        "Trace · Read · Spell · Use in Sentences")

    # 単語サンプル装飾（中央寄せで均等配置）
    samples = ["the", "and", "you", "play", "look"]
    sample_colors = [PRIMARY, ACCENT, HexColor("#10B981"), HexColor("#EC4899"), HexColor("#3B82F6")]
    c.setFont("Helvetica-Bold", 34)
    spacing = 1.35 * inch
    start_x = PAGE_W / 2 - (len(samples) - 1) * spacing / 2
    for i, w in enumerate(samples):
        c.setFillColor(sample_colors[i])
        c.drawCentredString(start_x + i * spacing, 3.3 * inch, w)

    c.setFillColor(ACCENT)
    badge_w, badge_h = 2.4 * inch, 0.8 * inch
    bx = (PAGE_W - badge_w) / 2
    by = 2.0 * inch
    c.roundRect(bx, by, badge_w, badge_h, 0.15 * inch, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(PAGE_W / 2, by + 0.25 * inch, "AGES 4-6")

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(DARK)
    c.drawCentredString(PAGE_W / 2, 0.5 * inch, f"by {meta.get('author', '__YOUR_BRAND__')}")
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
        "All worksheet content (words, layouts, activities) was",
        "designed and generated programmatically by the author.",
        "Cover illustration created with the help of AI image",
        "generation tools.",
        "",
        "Sight word list based on commonly-used Pre-K and",
        "Kindergarten high-frequency word collections.",
        "",
        "Find more printables at: etsy.com/shop/__YOUR_SHOP__",
    ]
    y = PAGE_H - 2.0 * inch
    for line in lines:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 0.3 * inch
    c.showPage()


def page_word_list(c, words: list[str], page_num: int, part: int, total_parts: int) -> None:
    draw_header(c, f"Sight Words Index ({part}/{total_parts})")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 13)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.4 * inch,
                        "These are the 100 most common words your child will see. Master them all!")

    # 5列×10行で50語
    cols = 5
    rows = 10
    cell_w = (PAGE_W - 2 * MARGIN) / cols
    cell_h = 0.6 * inch
    top_y = PAGE_H - 2.0 * inch

    c.setFont("Helvetica-Bold", 16)
    cbox = 0.16 * inch
    for i, w in enumerate(words):
        col = i % cols
        row = i // cols
        if row >= rows:
            break
        cell_left = MARGIN + cell_w * col + 0.12 * inch
        y = top_y - cell_h * row
        # チェックマーク欄（ベースラインに揃える）
        c.setStrokeColor(MID_GRAY)
        c.setLineWidth(1)
        c.rect(cell_left, y - 0.01 * inch, cbox, cbox, stroke=1, fill=0)
        # 単語（チェック欄の右側に左寄せ）
        c.setFillColor(DARK)
        c.drawString(cell_left + cbox + 0.08 * inch, y, w)

    draw_footer(c, page_num)
    c.showPage()


def draw_4line_guide(c, x_left: float, x_right: float, baseline_y: float, scale: float = 1.0) -> None:
    gap = 0.28 * inch * scale
    top = baseline_y + 2 * gap
    mid_high = baseline_y + gap
    base = baseline_y
    descender = baseline_y - gap
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(1)
    c.setDash(1, 0)
    c.line(x_left, top, x_right, top)
    c.setDash(3, 3)
    c.line(x_left, mid_high, x_right, mid_high)
    c.setDash(1, 0)
    c.setStrokeColor(DARK)
    c.setLineWidth(1.4)
    c.line(x_left, base, x_right, base)
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(1)
    c.setDash(3, 3)
    c.line(x_left, descender, x_right, descender)
    c.setDash(1, 0)


def page_word_tracing(c, page_num: int, word_a: str, word_b: str) -> None:
    """2単語/ページ、トレース+書く+使う"""
    draw_header(c, "Trace · Write · Read")

    def render_word_block(word: str, top_y: float) -> None:
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 42)
        c.drawString(MARGIN, top_y, word)

        # 「Trace it」ラベル
        c.setFont("Helvetica", 13)
        c.setFillColor(PRIMARY)
        c.drawString(MARGIN, top_y - 0.4 * inch, "Trace it:")

        # トレース行：4線罫線 + 薄文字
        baseline_y_1 = top_y - 0.95 * inch
        draw_4line_guide(c, MARGIN, PAGE_W - MARGIN, baseline_y_1)

        usable_w = PAGE_W - 2 * MARGIN
        slot_w = usable_w / 6
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(LIGHT_GRAY)
        for i in range(3):
            x_center = MARGIN + slot_w * (i + 0.5)
            c.drawCentredString(x_center, baseline_y_1 + 0.04 * inch, word)

        # 「Write it」ラベル
        c.setFont("Helvetica", 13)
        c.setFillColor(PRIMARY)
        c.drawString(MARGIN, top_y - 1.55 * inch, "Now write it yourself:")

        # 自分で書く行：4線罫線（薄文字なし）
        baseline_y_2 = top_y - 2.15 * inch
        draw_4line_guide(c, MARGIN, PAGE_W - MARGIN, baseline_y_2)

    render_word_block(word_a, PAGE_H - 1.5 * inch)
    render_word_block(word_b, PAGE_H - 4.7 * inch)

    draw_footer(c, page_num)
    c.showPage()


def page_find_word(c, page_num: int, target: str, decoys: list[str]) -> None:
    draw_header(c, f"Find the Word: '{target}'")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        f"Circle every '{target}' you can find below.")

    # 5×6 グリッド
    cols, rows = 5, 6
    cell_w = (PAGE_W - 2 * MARGIN) / cols
    cell_h = 0.95 * inch
    top_y = PAGE_H - 2.4 * inch

    pool: list[str] = []
    target_count = random.randint(8, 12)
    pool.extend([target] * target_count)
    while len(pool) < cols * rows:
        pool.append(random.choice(decoys))
    random.shuffle(pool)

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(DARK)
    for r in range(rows):
        for col in range(cols):
            i = r * cols + col
            x = MARGIN + cell_w * (col + 0.5)
            y = top_y - cell_h * r
            c.drawCentredString(x, y, pool[i])

    c.setFont("Helvetica", 16)
    c.drawString(MARGIN, 1.4 * inch, f"How many '{target}'s did you find? Answer: ______")
    c.setFillColor(gray)
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(MARGIN, 1.0 * inch, f"(Correct answer: {target_count})")

    draw_footer(c, page_num)
    c.showPage()


def page_color_word(c, page_num: int, words: list[str]) -> None:
    draw_header(c, "Color the Words")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        "Color each letter inside the word. Say the word out loud!")

    # 大きな単語をアウトラインで描画（中を塗れる）
    n = len(words)
    spacing = (PAGE_H - 3.5 * inch) / n
    top_y = PAGE_H - 2.2 * inch

    c.setFont("Helvetica-Bold", 80)
    c.setFillColor(LIGHT_GRAY)  # 薄色で塗りやすく
    for i, w in enumerate(words):
        y = top_y - i * spacing
        c.drawString(MARGIN + 0.4 * inch, y, w)
        # 下線
        c.setStrokeColor(MID_GRAY)
        c.setLineWidth(1.5)
        c.setDash(3, 3)
        c.line(MARGIN, y - 0.1 * inch, PAGE_W - MARGIN, y - 0.1 * inch)
        c.setDash(1, 0)
        c.setFillColor(LIGHT_GRAY)
        c.setFont("Helvetica-Bold", 80)

    draw_footer(c, page_num)
    c.showPage()


def page_sentence_building(c, page_num: int, words: list[str]) -> None:
    draw_header(c, "Use Words in a Sentence")

    c.setFillColor(DARK)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch,
                        "Write a sentence using each word below. (Adults can help!)")

    n = len(words)
    spacing = (PAGE_H - 3.5 * inch) / n
    top_y = PAGE_H - 2.0 * inch

    for i, w in enumerate(words):
        y = top_y - i * spacing
        # 単語表示
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(MARGIN, y, w)
        # 記入欄罫線
        c.setStrokeColor(MID_GRAY)
        c.setLineWidth(1)
        c.setDash(1, 0)
        c.line(MARGIN + 1.5 * inch, y - 0.05 * inch, PAGE_W - MARGIN, y - 0.05 * inch)
        c.line(MARGIN + 1.5 * inch, y - 0.45 * inch, PAGE_W - MARGIN, y - 0.45 * inch)

    draw_footer(c, page_num)
    c.showPage()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    meta = load_meta(args.book)
    words = meta["words"]
    if len(words) != 100:
        sys.exit(f"Expected 100 words, got {len(words)}")

    out_dir = OUTPUT_BASE / args.book
    out_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = out_dir / f"{args.book}_workbook.pdf"

    c = canvas.Canvas(str(output_pdf), pagesize=letter)

    page_num = 0
    page_cover(c, meta)
    page_num += 1
    page_copyright(c, meta)
    page_num += 1

    # Word List Index (2 pages, 50 words each)
    page_num += 1
    page_word_list(c, words[:50], page_num, 1, 2)
    page_num += 1
    page_word_list(c, words[50:], page_num, 2, 2)

    # Word Tracing (50 pages, 2 words per page)
    for i in range(0, 100, 2):
        page_num += 1
        page_word_tracing(c, page_num, words[i], words[i + 1])

    # Find the Word (8 pages)
    find_targets = random.sample(words, 8)
    for target in find_targets:
        decoys = [w for w in words if w != target]
        page_num += 1
        page_find_word(c, page_num, target, decoys)

    # Color the Words (4 pages, 5 words each)
    color_words = random.sample(words, 20)
    for i in range(0, 20, 5):
        page_num += 1
        page_color_word(c, page_num, color_words[i : i + 5])

    # Sentence Building (4 pages, 6 words each)
    sentence_words = random.sample(words, 24)
    for i in range(0, 24, 6):
        page_num += 1
        page_sentence_building(c, page_num, sentence_words[i : i + 6])

    c.save()
    print(f"Done. {page_num} pages total")
    print(f"Output: {output_pdf}")


if __name__ == "__main__":
    main()
