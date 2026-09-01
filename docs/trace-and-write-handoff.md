# Trace and Write Handoff

## Completed

- The reusable skill is in `skills/trace-and-write`.
- Short A and Short E word-family data have been researched and updated.
- Vowel workbooks use the locked packed-family layout.
- Every PDF begins with the approved instruction page showing:
  - two grey `cat` models;
  - the same two words in black;
  - six evenly spaced black `cat` words.
- Final generated workbooks are in `outputs/trace-and-write`.

## Continue At Home

Create or refresh a vowel workbook from the repository root:

```powershell
python skills/trace-and-write/scripts/generate_trace_and_write.py --vowel e --output outputs/trace-and-write/short_e_trace_and_write.pdf
```

Replace `e` with the required vowel.

## Next Task

Research curriculum-supported strict-CVC words for Short I, Short O, and Short U, update `skills/trace-and-write/references/cvc_word_families.json`, then generate their PDFs. Exclude blends, digraphs, silent letters, proper names, and four-phoneme `x` endings.
