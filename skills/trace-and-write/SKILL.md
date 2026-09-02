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
- Begin every generated PDF with the bundled instruction-page layout. Keep the directions brief, child-friendly, and applicable to words of different lengths. Show two grey model words, those words traced in black, and an example of continuing the word with clear finger spaces. Tell learners to repeat the word only as many times as fit comfortably.
- Treat `assets/canonical_instruction_page.pdf` as the locked instruction page. Generate a first-page placeholder, then use `insert_canonical_instruction_page()` after saving so every workbook receives that exact PDF page instead of rebuilding it.
- Preserve the bundled full-page template. Use League Spartan for headings and instructions, and Edu SA Beginner only for the grey tracing words.
- Keep illustrations consistent with the approved source or supplied style reference. Colour is permitted when requested. For the Word Made Easy blue-and-gold style, use navy `#193A63`, gold `#E1AE43`, and white `#FFFFFF`; do not substitute black outlines or introduce other colours. Do not use kawaii, realistic, or photorealistic imagery.
- Place every illustration on an opaque white background so handwriting guides or other page elements never show through the image area.
- In paired practice strips, show the illustration on the first strip only; keep the second strip image-free and full width.
- Show each target word once in the word list, but provide two complete handwriting strips for that word. A ten-strip page therefore holds no more than five unique words.
- For alphabet practice only, provide one strip for the uppercase letter and one strip for the lowercase letter.
- Pack complete family sections into unused page space by default. A following section includes its own title, instruction, and strips; start a new page when the complete section will not fit within the ten-position capacity.
- Identify each section with a left-aligned `-ab Family Words` title, substituting the actual family ending. Do not include `Trace and Write` in the title.
- Use a 22 pt title and 10 pt instruction, both aligned to the 0.5-inch left content margin. For every heading block, use 0.254 inches (18.3 pt) above the title, 0.08 inches (5.76 pt) between title and instruction, and 0.254 inches (18.3 pt) below the instruction.
- Keep the established strip spacing within each family. When unused rows remain, remove only the unused bottom rows.
- Treat [references/cvc_word_families.json](references/cvc_word_families.json) as the canonical strict-CVC dataset. Keep it free of blends, digraphs, silent letters, proper names, and four-phoneme `x` endings.
- Preserve the established layout: 0.5-inch left, right, and bottom margins; 1-inch top margin; 0.35-inch clear gap between strips; and two tracing examples followed by writing space.
- Open or render the generated PDF when visual verification is relevant.
