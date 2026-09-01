# Trace and Write Handoff

## Completed

- The reusable skill is in `skills/trace-and-write`.
- Short A and Short E word-family data have been researched and updated.
- Vowel workbooks use the locked packed-family layout.
- Every PDF begins with the approved instruction page showing:
  - two grey `cat` models;
  - the same two words in black;
  - six evenly spaced black `cat` words.
- Final generated Short A, E, I, O, and U workbooks are in `outputs/trace-and-write`.

## Continue At Home

Open `printnest-worksheets-lite.code-workspace` in VS Code. The workspace uses relative paths, selects the repository `.venv`, and includes tasks for regenerating all five short-vowel PDFs.

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

The Short I, O, and U PDFs currently use the canonical lists already in the repository. Audit those three lists against curriculum-supported strict-CVC sources before locking their word coverage. Exclude blends, digraphs, silent letters, proper names, and four-phoneme `x` endings.
