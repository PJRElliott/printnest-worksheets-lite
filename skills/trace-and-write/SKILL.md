---
name: trace-and-write
description: Generate printable A4 CVC trace-and-write worksheet PDFs with ten handwriting strips per page. Use for CVC word-family tracing practice or Word Made Easy trace-and-write worksheets; do not use for unrelated phonics activity types.
---

# Trace and Write

Generate the requested worksheet with the bundled deterministic script:

```powershell
python scripts/generate_trace_and_write.py
```

- Use `--family at` to create one word-family page, or omit it to create all 35 pages.
- Use `--output <path.pdf>` when the user specifies an output location.
- Preserve the bundled full-page template. Use League Spartan for headings and instructions, and Edu AU VIC WA NT Pre only for the grey tracing words.
- Keep ten unnumbered strips on every page, repeating family words as needed.
- Treat [references/cvc_word_families.json](references/cvc_word_families.json) as the canonical strict-CVC dataset. Keep it free of blends, digraphs, silent letters, proper names, and four-phoneme `x` endings.
- Preserve the established layout: 0.5-inch left, right, and bottom margins; 1-inch top margin; 0.35-inch clear gap between strips; and two tracing examples followed by writing space.
- Open or render the generated PDF when visual verification is relevant.
