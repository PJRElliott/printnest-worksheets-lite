---
name: printnest-worksheets-lite
description: Free Claude Code Skill that generates educational worksheet PDFs for Etsy/TPT/KDP sellers. Includes 5 worksheet types — Kindergarten Math, Alphabet Tracing Pre-K, Sight Words 100, Phonics CVC, Cursive Handwriting. Pure Python (zero AI image cost). Pro version with 40+ types available separately. Triggers on "worksheets", "PrintNest", "worksheet PDF", "Math Workbook", "Alphabet Tracing".
---

# PrintNest Worksheets — LITE (Free)

A free Claude Code Skill for educational printable PDF sellers. Generates 5 worksheet types via pure Python + ReportLab — no AI image cost.

> 💎 **40+ worksheet types in the Pro version** → https://synishida.gumroad.com/l/printnest-worksheets-pro

## Setup (one time)

```bash
pip3 install reportlab Pillow
python3 ~/.claude/skills/printnest-worksheets-lite/setup.py
```

`setup.py` asks for your brand name + Etsy shop URL once, then injects them into every generated PDF.

## Generators (5 included)

```bash
python3 ~/.claude/skills/printnest-worksheets-lite/scripts/generate_math.py --book math_kg
python3 ~/.claude/skills/printnest-worksheets-lite/scripts/generate_alphabet.py --book alphabet_prek
python3 ~/.claude/skills/printnest-worksheets-lite/scripts/generate_sightwords.py --book sightwords
python3 ~/.claude/skills/printnest-worksheets-lite/scripts/generate_phonics_cvc.py --book phonics_cvc
python3 ~/.claude/skills/printnest-worksheets-lite/scripts/generate_cursive.py --book cursive_handwriting
```

## CVC workbook design

The CVC generator uses a print-first, monochrome worksheet system:

- Do not add worksheet headers, subtitles, divider rules, page numbers, or student-name footers.
- Do not generate cover, copyright, explanation, title, or instruction pages. Exercise pages must not contain titles, word-family headings, instructional copy, or activity prompts.
- Use the bundled League Spartan Regular, Semibold, Bold, and ExtraBold fonts for all text.
- Keep worksheet text and rules black; use gray only for letters intended to be traced.
- Generate CVC pages at A4 size with 0.50-inch left/right margins and 0.75-inch top/bottom margins for all content.
- Treat those four values as one shared safe-area rectangle on every page. Account for text height, line height, box dimensions, and circle radii so visible element edges remain inside it; do not introduce page-specific outer margins.
- Render `assets/images/portrait-page-template.png` as the full-page background before drawing content. The template controls banner, footer, and outer padding; do not draw separate header or footer elements over it.
- Distribute exercise rows vertically across the full safe content area, from below the banner to above the footer. Avoid layouts that cluster content in the upper half or leave an unnecessarily empty lower half.
- Put exactly 10 four-line tracing strips on every CVC word-family tracing page. Cycle through the available family words when a family contains fewer than 10 words.
- Keep exercise content clear of the footer artwork.

Or just ask Claude:

> "Make me a Kindergarten Math Workbook"
> "Generate an Alphabet Tracing Pre-K workbook"

## Output

```
~/Desktop/PrintNest/{book_id}/
├── {book_id}_workbook.pdf       ← upload to Etsy/TPT/KDP
```

For Etsy thumbnails + listing copy, use:

```bash
python3 ~/.claude/skills/printnest-worksheets-lite/scripts/make_thumbnails_universal.py --book math_kg
python3 ~/.claude/skills/printnest-worksheets-lite/scripts/make_listing_universal.py --book math_kg
```

## Commercial use

All PDFs you generate with this skill can be **sold commercially anywhere** (Etsy / TPT / KDP / Gumroad / your own site). Free forever for personal and commercial use.

## Upgrade to Pro (40+ types)

The Pro version unlocks **40+ additional worksheet types** — Multiplication, Fractions, Money Math, Sudoku, Mazes, Word Search, Cryptogram, Sentence Building, Reading Comprehension, Recipes, and many more.

→ **https://synishida.gumroad.com/l/printnest-worksheets-pro**
