#!/usr/bin/env python3
"""
PrintNest 汎用 Etsy リスティング文生成。

meta JSON に `description` フィールドがあればそれを使い、なければ
構造定義（structure）から自動構築する。

Usage:
  python3 make_listing_universal.py --book sightwords
  python3 make_listing_universal.py --book mazes_kids
  python3 make_listing_universal.py --book sudoku
  python3 make_listing_universal.py --book wordsearch
"""

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_BASE = Path.home() / "Desktop" / "PrintNest"


# 本ごとの説明文テンプレート（meta.description 優先、なければここから）
DEFAULT_DESCRIPTIONS = {
    "sightwords": """\
Help your child build a strong reading foundation!

This {pages}-page Sight Words 100 Workbook teaches the 100 most common
high-frequency words children need to know for early reading success.
Each word is reinforced through tracing, recognition, color-the-word, and
sentence-building activities — a complete approach to mastering sight words.

━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━
• 100 high-frequency sight words (Pre-K Dolch + Kindergarten Dolch + 1st Grade)
• 2 word list / index pages (with checkboxes to track progress)
• 50 tracing pages — 2 words per page with 4-line handwriting guides
• 8 "Find the Word" search activities
• 4 "Color the Words" decoration pages
• 4 "Sentence Building" practice pages
• Total: {pages} ready-to-print pages

━━━━━━━━━━━━━━━━━━━━━━
PERFECT FOR
━━━━━━━━━━━━━━━━━━━━━━
• Pre-K & Kindergarten homeschool families
• Preschool, kindergarten, and 1st grade teachers
• Reading intervention & literacy specialists
• Parents preparing kids for reading
• Ages 4-6
""",
    "mazes_kids": """\
Hours of screen-free maze fun for kids of all ages!

This {pages}-page Kids Mazes Activity Book is packed with 100 unique
maze puzzles ranging from easy (8x8) to expert (15x15). Perfect for road
trips, summer learning, homeschool brain breaks, or quiet time. Each
puzzle was procedurally generated, so every maze is one-of-a-kind.

━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━
• 100 unique maze puzzles
• 30 Easy mazes (8x8) — perfect for beginners
• 30 Medium mazes (10x10) — building confidence
• 25 Hard mazes (12x12) — for puzzle pros
• 15 Expert mazes (15x15) — for true puzzle masters
• 30 pages of answer keys (4 mazes per page)
• Total: {pages} ready-to-print pages
• Big, clear maze designs — easy on young eyes

━━━━━━━━━━━━━━━━━━━━━━
PERFECT FOR
━━━━━━━━━━━━━━━━━━━━━━
• Kids ages 4-10
• Homeschool brain breaks & focus time
• Summer learning packets
• Road trip and travel activity book
• Birthday party favors and prizes
• Quiet time / screen-free play
""",
    "sudoku": """\
Train your brain with 65 fresh sudoku puzzles!

This {pages}-page Sudoku Puzzle Book takes you from easy warm-ups to
challenging expert puzzles. Every puzzle is procedurally generated and
unique — no recycled puzzles you've seen before. Great for daily brain
training, relaxation, and screen-free moments.

━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━
• 65 unique sudoku puzzles (9x9 grids)
• 20 Easy puzzles — warm up your brain
• 20 Medium puzzles — sharpen your logic
• 15 Hard puzzles — for confident solvers
• 10 Expert puzzles — for sudoku masters
• 17 pages of complete answer keys
• Total: {pages} ready-to-print pages

━━━━━━━━━━━━━━━━━━━━━━
PERFECT FOR
━━━━━━━━━━━━━━━━━━━━━━
• Adult brain training & mental fitness
• Senior cognitive activity
• Travel companion (road trips, flights)
• Daily morning brain boost
• Relaxation & mindfulness
• Gift for puzzle lovers
""",
    "wordsearch": """\
50 themed word search puzzles for the whole family!

This {pages}-page Word Search Puzzle Book features 50 fun themes covering
animals, food, sports, holidays, nature, and more. Every grid is 15x15
with words hidden in 8 directions. Procedurally generated for unique
puzzles every time.

━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━
• 50 unique word search puzzles, each with a fun theme
• 15x15 grids with 12-13 words hidden in 8 directions
• Themes include: Animals, Fruits, Sports, Christmas, Halloween,
  Easter, Valentine's, Summer, Winter, Music, Cooking, Space, and more
• 13 pages of complete answer keys
• Total: {pages} ready-to-print pages

━━━━━━━━━━━━━━━━━━━━━━
PERFECT FOR
━━━━━━━━━━━━━━━━━━━━━━
• Family game nights & screen-free fun
• Kids ages 8+, teens, and adults
• Long car rides, flights, and travel
• Birthday party activity
• Senior brain training & memory boost
• Classroom indoor recess
""",
}

DEFAULT_FOOTER = """\
━━━━━━━━━━━━━━━━━━━━━━
INSTANT DOWNLOAD
━━━━━━━━━━━━━━━━━━━━━━
• 1 PDF file, ready to download immediately after purchase
• Print as many copies as you need for personal or single-classroom use
• US Letter size (8.5 x 11 inch) — works with any standard printer
• Black and white design = printer-friendly and ink-saving

━━━━━━━━━━━━━━━━━━━━━━
HOW TO USE
━━━━━━━━━━━━━━━━━━━━━━
1. Purchase and download the PDF from your Etsy account
2. Open with any PDF reader
3. Print at home or your local print shop
4. Enjoy!

━━━━━━━━━━━━━━━━━━━━━━
ABOUT THIS LISTING
━━━━━━━━━━━━━━━━━━━━━━
All puzzle/worksheet content was procedurally generated by the author.
Cover illustration created with the help of AI image generation tools.

━━━━━━━━━━━━━━━━━━━━━━
TERMS
━━━━━━━━━━━━━━━━━━━━━━
For personal and single-classroom use only. Please do not resell,
redistribute, or share the file. Thank you for supporting an
independent creator!
"""


def load_meta(book):
    return json.loads((SKILL_DIR / "references" / f"{book}_meta.json").read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    args = parser.parse_args()

    meta = load_meta(args.book)
    out_dir = OUTPUT_BASE / args.book
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "etsy_listing.txt"

    title = meta.get("etsy_title", meta.get("title", ""))
    tags = meta.get("etsy_tags", [])
    pages = meta.get("pages", 50)
    price_launch = meta.get("price_launch_usd", 4.99)
    price_target = meta.get("price_target_usd", 7.99)
    ai_disclosure = meta.get("ai_disclosure", {})

    # meta.description 優先、なければテンプレ
    if meta.get("description"):
        description = meta["description"]
    else:
        template = DEFAULT_DESCRIPTIONS.get(args.book, "Beautiful printable PDF — {pages} pages of fun!\n")
        description = template.format(pages=pages) + "\n" + DEFAULT_FOOTER

    content = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ETSY LISTING — {meta.get('title', args.book)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▼ TITLE  ({len(title)}/140 chars)
─────────────────────────────────────────
{title}

▼ TAGS  (13 max, 20 chars each)
─────────────────────────────────────────
"""
    for i, tag in enumerate(tags, 1):
        content += f"{i:2}. {tag}\n"

    content += f"""
▼ PRICE
─────────────────────────────────────────
Launch:  ${price_launch}  (until 10 reviews collected)
Target:  ${price_target}  (after 10+ reviews)

▼ CATEGORY
─────────────────────────────────────────
Paper & Party Supplies > Paper > Stationery > Stationery Sets
or
Craft Supplies & Tools > Patterns & Tutorials > Tutorials

▼ TYPE
─────────────────────────────────────────
Digital Item (Instant Download)

▼ AI DISCLOSURE
─────────────────────────────────────────
Who made it:      {ai_disclosure.get('who_made_it', '')}
Outside party:    {ai_disclosure.get('outside_party', '')}

▼ DESCRIPTION
─────────────────────────────────────────
{description}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILES TO UPLOAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Product file:
  ~/Desktop/PrintNest/{args.book}/{args.book}_workbook.pdf

Listing photos (7 thumbnails):
  ~/Desktop/PrintNest/{args.book}/thumbnails/01_cover.png ... 07_summary.png

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    out_file.write_text(content)
    print(f"✓ {args.book}: listing → {out_file}")


if __name__ == "__main__":
    main()
