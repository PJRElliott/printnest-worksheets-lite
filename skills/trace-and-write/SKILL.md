---
name: trace-and-write
description: Generate printable A4 CVC trace-and-write worksheet PDFs with ten handwriting strips per page. Use for CVC word-family tracing practice or Word Made Easy trace-and-write worksheets; do not use for unrelated phonics activity types.
---

# Trace and Write

Generate the requested worksheet with the bundled deterministic script:

```powershell
python scripts/generate_trace_and_write.py
```

- Use `--family at` to create one word-family worksheet, or omit it to create all families.
- Use `--vowel a` to create one workbook containing every family for a selected short vowel.
- Use `--output <path.pdf>` when the user specifies an output location.
- Begin every generated PDF with the bundled instruction-page layout. Keep the directions brief and child-friendly, and show three handwriting strips: a completely empty strip, a strip with the two grey tracing words, and a fully completed strip with the independent word added in black.
- Preserve the bundled full-page template. Use League Spartan for headings and instructions, and Edu SA Beginner only for the grey tracing words.
- Show each family word exactly once with no repetition. Use one strip per unique word and continue families longer than ten words onto another page.
- Pack complete family sections into unused page space by default. A following section includes its own title, instruction, and strips; start a new page when the complete section will not fit within the ten-position capacity.
- Identify each section with a left-aligned `-ab Family Words` title, substituting the actual family ending. Do not include `Trace and Write` in the title.
- Use a 22 pt title and 10 pt instruction, both aligned to the 0.5-inch left content margin. For every heading block, use 0.254 inches (18.3 pt) above the title, 0.08 inches (5.76 pt) between title and instruction, and 0.254 inches (18.3 pt) below the instruction.
- Keep the established strip spacing within each family. When unused rows remain, remove only the unused bottom rows.
- Treat [references/cvc_word_families.json](references/cvc_word_families.json) as the canonical strict-CVC dataset. Keep it free of blends, digraphs, silent letters, proper names, and four-phoneme `x` endings.
- Preserve the established layout: 0.5-inch left, right, and bottom margins; 1-inch top margin; 0.35-inch clear gap between strips; and two tracing examples followed by writing space.
- Open or render the generated PDF when visual verification is relevant.
