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

Open `printnest-worksheets-lite.code-workspace` in VS Code. The workspace uses relative paths, selects the repository `.venv`, and includes tasks for regenerating the Short A and Short E PDFs.

If the virtual environment does not exist after cloning, create it and install the project:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Create or refresh a vowel workbook from the repository root:

```powershell
python skills/trace-and-write/scripts/generate_trace_and_write.py --vowel e --output outputs/trace-and-write/short_e_trace_and_write.pdf
```

Replace `e` with the required vowel.

## Next Task

Research curriculum-supported strict-CVC words for Short I, Short O, and Short U, update `skills/trace-and-write/references/cvc_word_families.json`, then generate their PDFs. Exclude blends, digraphs, silent letters, proper names, and four-phoneme `x` endings.
