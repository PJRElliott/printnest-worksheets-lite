#!/usr/bin/env python3
"""
PrintNest - Phonics CVC Words Workbook を一発生成。

12個の word family (-at, -an, ...) × 2ページ + 混合復習。
trace / fill missing letter / build-a-word の3活動。純Python。

Usage:
  python3 generate_phonics_cvc.py --book phonics_cvc
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

try:
    from PIL import Image
    from reportlab.lib.colors import black, Color, white
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
except ImportError:
    sys.exit("Install reportlab and Pillow: pip install reportlab Pillow")

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_BASE = Path.home() / "Desktop" / "PrintNest"
PAGE_W, PAGE_H = letter
MARGIN = 0.6 * inch

BLACK = black
LIGHT_GRAY = Color(0.82, 0.82, 0.82)
MID_GRAY = Color(0.55, 0.55, 0.55)
TRACE_GRAY = Color(0.72, 0.72, 0.72)
PRIMARY = BLACK
ACCENT = BLACK
SOFT_PURPLE = white
SOFT_YELLOW = white
SOFT_BLUE = white
DARK = BLACK

FONT_DIR = SKILL_DIR / "assets" / "fonts"
FOOTER_IMAGE = SKILL_DIR / "assets" / "images" / "portrait-footer.png"
BANNER_IMAGE = SKILL_DIR / "assets" / "images" / "portrait-banner.png"
FONTS = {
    "LeagueSpartan-Regular": "LeagueSpartan-Regular.ttf",
    "LeagueSpartan-SemiBold": "LeagueSpartan-SemiBold.ttf",
    "LeagueSpartan-Bold": "LeagueSpartan-Bold.ttf",
    "LeagueSpartan-ExtraBold": "LeagueSpartan-ExtraBold.ttf",
}


def register_fonts() -> None:
    for font_name, filename in FONTS.items():
        path = FONT_DIR / filename
        pdfmetrics.registerFont(TTFont(font_name, str(path)))

FAMILIES = [
    ("-at", ["cat", "bat", "hat", "mat", "rat", "sat", "fat", "pat"]),
    ("-an", ["man", "pan", "ran", "tan", "van", "can", "fan"]),
    ("-en", ["hen", "pen", "ten", "den", "men"]),
    ("-et", ["jet", "pet", "wet", "get", "net", "let", "set", "vet"]),
    ("-in", ["pin", "win", "fin", "tin", "bin", "kin"]),
    ("-ip", ["zip", "lip", "tip", "dip", "hip", "rip", "sip"]),
    ("-it", ["sit", "bit", "fit", "hit", "kit", "lit", "pit"]),
    ("-og", ["dog", "log", "fog", "jog", "hog", "bog"]),
    ("-op", ["top", "hop", "mop", "pop", "cop", "shop"]),
    ("-ot", ["hot", "pot", "dot", "got", "lot", "not", "rot"]),
    ("-ub", ["cub", "hub", "rub", "tub", "sub", "pub"]),
    ("-un", ["bun", "fun", "run", "sun", "gun"]),
]


def load_meta(book: str) -> dict:
    return json.loads(
        (SKILL_DIR / "references" / f"{book}_meta.json").read_text(encoding="utf-8")
    )


def draw_header(c, title: str = "", subtitle: str = "") -> None:
    c.drawImage(
        str(BANNER_IMAGE),
        0,
        PAGE_H - 0.16 * inch,
        width=PAGE_W,
        height=0.16 * inch,
        mask="auto",
    )


def draw_footer(c, page_num: int) -> None:
    with Image.open(FOOTER_IMAGE) as source:
        artwork = source.crop(source.getbbox())
        width = PAGE_W
        height = width * artwork.height / artwork.width
        c.drawImage(
            ImageReader(artwork),
            0,
            0.12 * inch,
            width=width,
            height=height,
            mask="auto",
        )


def draw_4line(c, x_left, x_right, baseline_y, gap=0.28 * inch) -> None:
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
    draw_header(c)
    c.setFillColor(SOFT_PURPLE)
    c.rect(0, PAGE_H - 1.3 * inch, PAGE_W, 1.3 * inch, fill=1, stroke=0)
    c.setFillColor(SOFT_YELLOW)
    c.rect(0, 0, PAGE_W, 1.3 * inch, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("LeagueSpartan-ExtraBold", 54)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.4 * inch, "Phonics")
    c.setFont("LeagueSpartan-ExtraBold", 64)
    c.setFillColor(PRIMARY)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 3.4 * inch, "CVC")
    c.setFont("LeagueSpartan-Regular", 15)
    c.setFillColor(DARK)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 4.0 * inch,
                        "Word Families  ·  Trace · Write · Read  ·  K-1st Grade")

    # 装飾：CVC 例（stringWidth で各文字の実幅で配置）
    from reportlab.pdfbase.pdfmetrics import stringWidth
    examples = [("c", "a", "t"), ("d", "o", "g"), ("s", "i", "t")]
    colors = [BLACK, BLACK, BLACK]
    font_name, font_size = "LeagueSpartan-Bold", 70
    c.setFont(font_name, font_size)
    spacing = 2.1 * inch
    for i, (a, b, cc) in enumerate(examples):
        word = a + b + cc
        total_w = stringWidth(word, font_name, font_size)
        cx = PAGE_W / 2 + (i - 1) * spacing
        x = cx - total_w / 2
        for j, ch in enumerate((a, b, cc)):
            c.setFillColor(colors[i] if j != 1 else DARK)
            c.drawString(x, 4.7 * inch, ch)
            x += stringWidth(ch, font_name, font_size)

    c.setFillColor(white)
    c.setStrokeColor(BLACK)
    bw, bh = 2.4 * inch, 0.85 * inch
    c.roundRect((PAGE_W - bw) / 2, 2.6 * inch, bw, bh, 0.15 * inch, fill=0, stroke=1)
    c.setFillColor(black)
    c.setFont("LeagueSpartan-Bold", 22)
    c.drawCentredString(PAGE_W / 2, 2.9 * inch, f"AGES {meta.get('ages', '5-7')}")

    draw_footer(c, 1)
    c.showPage()


def page_copyright(c, meta: dict) -> None:
    draw_header(c)
    c.setFont("LeagueSpartan-Regular", 11)
    c.setFillColor(DARK)
    lines = [
        "This workbook is for personal and single-classroom use only.",
        "Please do not resell, redistribute, or share the file.",
        "",
        "All worksheet content was programmatically generated by the",
        "author. Cover illustration created with the help of AI image",
        "generation tools.",
    ]
    y = PAGE_H - 1.2 * inch
    for line in lines:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 0.3 * inch
    draw_footer(c, 2)
    c.showPage()


def page_howto(c) -> None:
    draw_header(c, "What are CVC Words?",
                "Consonant - Vowel - Consonant: the simplest 3-letter words.")
    steps = [
        "1. A CVC word is made of 3 letters: consonant + vowel + consonant.",
        "2. Examples: cat (c-a-t), dog (d-o-g), sit (s-i-t).",
        "3. Words ending in the same 2 letters belong to a word family.",
        "4. -at words: cat, bat, hat, mat, rat, sat...",
        "5. Reading one word family makes the others easier!",
    ]
    y = PAGE_H - 1.2 * inch
    c.setFont("LeagueSpartan-Regular", 13)
    c.setFillColor(DARK)
    for s in steps:
        c.drawString(MARGIN + 0.3 * inch, y, s)
        y -= 0.40 * inch
    # 見本
    c.setFillColor(SOFT_BLUE)
    c.roundRect(MARGIN + 0.3 * inch, 1.6 * inch, PAGE_W - 2 * MARGIN - 0.6 * inch,
                1.6 * inch, 0.15 * inch, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("LeagueSpartan-SemiBold", 14)
    c.drawString(MARGIN + 0.55 * inch, 2.85 * inch, "Example  ·  -at family")
    examples = ["cat", "bat", "hat", "mat", "rat", "sat"]
    c.setFont("LeagueSpartan-Bold", 22)
    for i, w in enumerate(examples):
        row, col = divmod(i, 3)
        x = MARGIN + 0.7 * inch + col * 2.0 * inch
        y = 2.45 * inch - row * 0.55 * inch
        c.setFillColor(DARK)
        c.drawString(x, y, w[0])
        c.setFillColor(PRIMARY)
        c.drawString(x + 0.27 * inch, y, w[1:])
    draw_footer(c, 3)
    c.showPage()


def page_family_intro(c, page_num: int, family: str, words: list[str]) -> None:
    """word family の紹介＋全単語トレース"""
    draw_header(c, f"Word Family  ·  {family}",
                f"Read and trace each {family} word.")
    # 大きな family 表示
    c.setFillColor(SOFT_PURPLE)
    c.roundRect(MARGIN, PAGE_H - 1.3 * inch, PAGE_W - 2 * MARGIN, 0.9 * inch,
                0.15 * inch, fill=1, stroke=0)
    c.setFillColor(PRIMARY)
    c.setFont("LeagueSpartan-ExtraBold", 56)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.1 * inch, family)

    # 単語をトレース行に配置（4本罫線 × N行）
    show_count = min(len(words), 6)
    for i in range(show_count):
        baseline_y = PAGE_H - 2.4 * inch - i * 1.0 * inch
        draw_4line(c, MARGIN + 0.3 * inch, PAGE_W - MARGIN - 0.3 * inch,
                   baseline_y, gap=0.22 * inch)
        # 番号
        c.setFillColor(DARK)
        c.setFont("LeagueSpartan-SemiBold", 14)
        c.drawString(MARGIN, baseline_y + 0.05 * inch, f"{i + 1}.")
        # トレース文字（薄）×2
        word = words[i]
        c.setFillColor(TRACE_GRAY)
        c.setFont("LeagueSpartan-Bold", 34)
        c.drawString(MARGIN + 0.45 * inch, baseline_y + 0.04 * inch, word)
        c.drawString(MARGIN + 2.0 * inch, baseline_y + 0.04 * inch, word)
        # 残りは空白（自由に書く）

    draw_footer(c, page_num)
    c.showPage()


def page_missing_letter(c, page_num: int, family: str, words: list[str],
                        rng: random.Random) -> list[str]:
    """各単語の最初の文字を空欄にして埋めさせる"""
    draw_header(c, f"Fill the Missing Letter  ·  {family}",
                "Write the first letter to make a word from this family.")
    answers = []
    # 各行：[__]  a  t   ← 大きく描画
    show = min(len(words), 8)
    for i in range(show):
        baseline_y = PAGE_H - 1.2 * inch - i * 0.8 * inch
        word = words[i]
        answers.append(word[0])
        # 番号
        c.setFillColor(DARK)
        c.setFont("LeagueSpartan-SemiBold", 14)
        c.drawString(MARGIN, baseline_y + 0.05 * inch, f"{i + 1}.")
        # 空欄ボックス
        bx = MARGIN + 0.4 * inch
        by = baseline_y - 0.05 * inch
        c.setStrokeColor(PRIMARY)
        c.setLineWidth(2)
        c.setFillColor(white)
        c.roundRect(bx, by, 0.55 * inch, 0.55 * inch, 0.06 * inch,
                    fill=1, stroke=1)
        # 残り2文字
        c.setFillColor(DARK)
        c.setFont("LeagueSpartan-Bold", 36)
        c.drawString(bx + 0.75 * inch, baseline_y + 0.05 * inch, word[1:])
    draw_footer(c, page_num)
    c.showPage()
    return answers


def page_mixed_review(c, page_num: int, rng: random.Random,
                      all_words: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """混合復習：CVC を見せて family を選択させる"""
    draw_header(c, "Mixed Review  ·  Word Family Sort",
                "Read the word, then circle its family ending.")
    items = rng.sample(all_words, 10)
    for i, (word, fam) in enumerate(items):
        row, col = divmod(i, 2)
        x0 = MARGIN + col * (PAGE_W - 2 * MARGIN) / 2
        y = PAGE_H - 1.1 * inch - row * 1.2 * inch
        # 番号 + 単語
        c.setFillColor(DARK)
        c.setFont("LeagueSpartan-SemiBold", 14)
        c.drawString(x0, y + 0.1 * inch, f"{i + 1}.")
        c.setFont("LeagueSpartan-Bold", 30)
        c.drawString(x0 + 0.4 * inch, y + 0.05 * inch, word)
        # 3つの family 候補（正解 + 2つのダミー）
        choices = [fam]
        all_fams = list({f for _w, f in all_words})
        distractors = [f for f in all_fams if f != fam]
        rng.shuffle(distractors)
        choices.extend(distractors[:2])
        rng.shuffle(choices)
        for ci, ch in enumerate(choices):
            cx = x0 + 1.4 * inch + ci * 0.55 * inch
            c.setStrokeColor(DARK)
            c.setLineWidth(1.4)
            c.setFillColor(white)
            c.circle(cx, y + 0.18 * inch, 0.22 * inch, fill=1, stroke=1)
            c.setFillColor(DARK)
            c.setFont("LeagueSpartan-SemiBold", 10)
            c.drawCentredString(cx, y + 0.12 * inch, ch)
    draw_footer(c, page_num)
    c.showPage()
    return items


def page_build_word(c, page_num: int, family: str, letters: list[str]) -> None:
    """family の前に文字を足して何語作れるか練習"""
    draw_header(c, f"Build a Word  ·  {family}",
                f"Add a letter at the start to make {family} family words.")
    # ヘッダー: [__]  a t  → make as many as you can
    c.setFillColor(SOFT_YELLOW)
    c.roundRect(MARGIN, PAGE_H - 1.4 * inch, PAGE_W - 2 * MARGIN, 0.9 * inch,
                0.15 * inch, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("LeagueSpartan-ExtraBold", 42)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.15 * inch,
                        f"_ _   +   {family}   =   ?")
    # 候補文字
    c.setFillColor(DARK)
    c.setFont("LeagueSpartan-SemiBold", 14)
    c.drawString(MARGIN + 0.3 * inch, PAGE_H - 1.9 * inch,
                 "Try these letters:  " + " · ".join(letters))
    # 書き欄 8つ
    for i in range(8):
        row, col = divmod(i, 2)
        x = MARGIN + 0.5 * inch + col * 3.4 * inch
        y = PAGE_H - 2.6 * inch - row * 1.0 * inch
        c.setFillColor(DARK)
        c.setFont("LeagueSpartan-SemiBold", 14)
        c.drawString(x - 0.35 * inch, y + 0.1 * inch, f"{i + 1}.")
        # 空ボックス + family
        c.setStrokeColor(PRIMARY)
        c.setLineWidth(2)
        c.setFillColor(white)
        c.roundRect(x, y - 0.05 * inch, 0.55 * inch, 0.55 * inch, 0.06 * inch,
                    fill=1, stroke=1)
        c.setFillColor(DARK)
        c.setFont("LeagueSpartan-Bold", 32)
        c.drawString(x + 0.75 * inch, y + 0.05 * inch, family[1:])  # eg "at"
    draw_footer(c, page_num)
    c.showPage()


def page_answers(c, page_num: int, items: list) -> None:
    """items: [(page_label, [(question, answer), ...]), ...]"""
    draw_header(c, "Answer Key",
                "Here are the answers for each Mixed Review page.")
    y = PAGE_H - 1.0 * inch
    for label, pairs in items:
        c.setFillColor(PRIMARY)
        c.setFont("LeagueSpartan-Bold", 12)
        c.drawString(MARGIN, y, label)
        y -= 0.22 * inch
        c.setFillColor(DARK)
        c.setFont("LeagueSpartan-Regular", 11)
        for q, a in pairs:
            c.drawString(MARGIN + 0.3 * inch, y, f"{q}  →  {a}")
            y -= 0.20 * inch
        y -= 0.15 * inch
        if y < MARGIN + 0.8 * inch:
            break
    draw_footer(c, page_num)
    c.showPage()


def main() -> None:
    register_fonts()
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", default="phonics_cvc")
    parser.add_argument("--seed", type=int, default=20260524)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    meta = load_meta(args.book)
    out_dir = OUTPUT_BASE / args.book
    out_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = out_dir / f"{args.book}_workbook.pdf"

    c = canvas.Canvas(str(output_pdf), pagesize=letter)
    page_num = 0
    page_cover(c, meta); page_num += 1
    page_copyright(c, meta); page_num += 1
    page_howto(c); page_num += 1

    # 各family: intro + missing-letter + build-word = 3ページ
    all_word_pairs = []
    for fam, words in FAMILIES:
        page_num += 1
        page_family_intro(c, page_num, fam, words)
        page_num += 1
        page_missing_letter(c, page_num, fam, words, rng)
        page_num += 1
        # build-word の候補文字（実際の単語の先頭文字を提示）
        starters = sorted(set(w[0] for w in words))
        page_build_word(c, page_num, fam, starters)
        for w in words:
            all_word_pairs.append((w, fam))

    # 混合復習: 3ページ
    review_items = []
    for _ in range(3):
        page_num += 1
        items = page_mixed_review(c, page_num, rng, all_word_pairs)
        review_items.append((f"Page {page_num}", [(w, f) for w, f in items]))

    # answer key: 1ページ
    page_num += 1
    page_answers(c, page_num, review_items)

    c.save()
    print(f"Done. {page_num} pages total")
    print(f"Output: {output_pdf}")


if __name__ == "__main__":
    main()
