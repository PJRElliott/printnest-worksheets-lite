# PrintNest Worksheets — LITE

> **A free Claude Code Skill for Etsy / Teachers Pay Teachers / Amazon KDP sellers.**
> Generates print-ready educational worksheet PDFs from a single sentence.
> Pure Python. Zero AI image cost.

---

## 💎 Looking for the full version?

This is the **LITE** edition — **5 worksheet types** to try the workflow.

| | LITE (this repo) | **Pro** |
|---|---|---|
| Worksheet types | 5 | **40+** |
| Math generators | 1 (KG Math) | **19** (Multiplication, Fractions, Money Math, Telling Time, Word Problems…) |
| Language Arts | 4 | **12** (Phonics, Vowels, Synonyms, Word Search…) |
| Puzzles | 0 | **5** (Sudoku, Mazes, Dot-to-Dot, Cryptogram, Calendar) |
| Recipes (Diabetic / Baby Food / Senior Soft / Weight Loss) | 0 | **4 niches** |
| KDP cover generator | ❌ | ✅ |
| Auto bundle generator | ❌ | ✅ |
| Price | Free | **$29** ([Gumroad](https://synishida.gumroad.com/l/printnest-worksheets-pro)) |
| Commercial use of generated PDFs | ✅ | ✅ |

### → **Get Pro on Gumroad: https://synishida.gumroad.com/l/printnest-worksheets-pro**

---

## Quick start

```bash
# 1. Clone into Claude Code's skills folder
git clone https://github.com/nishidagonyuya/printnest-worksheets-lite.git \
  ~/.claude/skills/printnest-worksheets-lite

# 2. Install Python deps
pip3 install reportlab Pillow

# 3. One-time brand setup (your shop name appears on every PDF footer)
python3 ~/.claude/skills/printnest-worksheets-lite/setup.py
```

Then in Claude Code, ask:

> _"Make me a Kindergarten Math Workbook"_

or run directly:

```bash
python3 ~/.claude/skills/printnest-worksheets-lite/scripts/generate_math.py --book math_kg
```

Output appears in `~/Desktop/PrintNest/math_kg/math_kg_workbook.pdf`. Print-ready, brand-stamped, US Letter.

---

## What's included (LITE)

| Script | Output | Pages |
|---|---|---|
| `generate_math.py --book math_kg` | Kindergarten Math Workbook | ~50 |
| `generate_alphabet.py --book alphabet_prek` | Alphabet Tracing Pre-K | ~68 |
| `generate_sightwords.py --book sightwords` | Sight Words 100 (K–1st) | ~70 |
| `generate_phonics_cvc.py --book phonics_cvc` | Phonics CVC Workbook | ~60 |
| `generate_cursive.py --book cursive_handwriting` | Cursive Handwriting Practice | ~52 |

Each book also comes with:
- `make_thumbnails_universal.py --book {id}` → 7 Etsy listing thumbnails
- `make_listing_universal.py --book {id}` → ready-to-paste Etsy title, tags, description

---

## Requirements

- macOS / Linux / Windows (WSL)
- [Claude Code](https://claude.com/claude-code) — `npm install -g @anthropic-ai/claude-code`
- Python 3.9+
- `pip install reportlab Pillow`

---

## License

MIT for the skill scripts. **All PDFs you generate are yours** — sell them anywhere (Etsy / TPT / KDP / Gumroad / your own site), forever.

---

## Why I built this

I sell printable PDFs on Etsy (US shop). Designing each worksheet in Canva took hours. So I built this skill to generate them with Claude. After a few weeks of polishing the engine, I'm releasing the 5-type LITE version free, and a 40+ type [Pro version](https://synishida.gumroad.com/l/printnest-worksheets-pro) on Gumroad for serious sellers.

If this saves you time, ⭐ the repo. Bug reports & PRs welcome.

— [Yuya Nishida](https://github.com/nishidagonyuya)
