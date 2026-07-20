# CLAUDE.md - Spreadsheet Cleaner

Rules for Claude Code. Read this and SPEC.md before touching any file.

---

## Project

An offline Python tool that profiles, cleans, and validates messy CSV / Excel
files for data migration and QA, and exports a per-dimension data-quality
report. One engine, three surfaces (pip, CLI, and a planned desktop app). It is
the mirror image of RecordForge: RecordForge generates and dirties test data,
Spreadsheet Cleaner detects and fixes those problems. See SPEC.md for the
architecture and ROADMAP.md for the plan.

---

## Non-negotiable rules

1. **Read SPEC.md first.** The structure and contracts are already decided. Do
   not invent modules the spec does not describe.
2. **No network calls** in ingest, profiling, cleaning, or reporting. This tool
   handles the user's real client data; it must be air-gappable. The only
   sanctioned exception is a future opt-in update check in the UI layer, which
   runs on an explicit click and sends no user data.
3. **Read-only on the source.** Profiling never modifies the input file. Cleaning
   (Phase C) writes a cleaned copy plus a change log; it never overwrites the
   source.
4. **Every finding maps to a `Dimension`.** Checks emit `Issue` records tagged
   with a data-quality dimension. If a check fits no dimension, add a dimension
   deliberately - do not bolt an untagged check on.
5. **Deterministic.** Same input plus same options gives the same report and
   (later) the same cleaned output. No wall-clock or randomness in results; the
   report timestamp is the only time-dependent field.
6. **Reports are portable and offline.** The HTML report embeds its own CSS. No
   CDN, no external fonts that must download, no external assets.
7. **No monoliths.** One job per module. Ingest, inference, checks, and rendering
   stay separate.

---

## Python style

- Python 3.10+; `from __future__ import annotations` at the top of every module.
- Type hints on every function signature. `X | Y` unions.
- Dataclasses for data models, not dicts or namedtuples.
- `pathlib.Path`, never `os.path`. f-strings for formatting.
- No `print()` in library code. CLI output goes through Typer's `echo`/`secho`;
  library output is the returned value.
- Imports: stdlib, then third-party, then local, one blank line between groups.
  No wildcard imports.
- Keep terminal (CLI) output **ASCII** - Windows consoles default to cp1252 and
  crash on box-drawing or fancy punctuation. Unicode is fine in files written as
  UTF-8 (the reports).

---

## Brand

- Palette is **Zinc & Sky** (a.k.a. "teal and zinc"): deep-cyan accent `#0E7490`
  (light) / electric sky `#38BDF8` (dark), zinc neutrals. Canonical tokens:
  `analyst-prep-kit/assets/grain/zinc-sky.css`. The HTML report and any future UI
  use these, theme-aware, with no CDN.

---

## Error handling

- Load and profile paths catch failures and raise `LoadError` (or return a clean
  result) with a human-readable message. No stack trace reaches the user.
- Validation of bad options (unknown format, missing sheet) fails before any file
  I/O with a clear message.

---

## Testing

- At least one smoke test per engine area: type inference, each dimension check,
  ingest edge cases (missing file, blank rows), scoring, and every report format.
- A messy fixture that trips all six dimensions, and a clean fixture that scores
  high. Test file: `tests/test_smoke.py`.
- Run `python -m pytest -q` from the repo root; keep it green.

---

## Commit style

- One logical change per commit. `type: short description`
  (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`).
- Author commits as Michael Nocito. No AI/Co-Authored-By trailers.

---

## What not to do

- Do not use `argparse` (CLI is Typer) or any web framework.
- Do not coerce or drop data silently on load - preserve raw strings and blanks.
- Do not overwrite the user's source file, ever.
- Do not add dependencies not in SPEC.md / pyproject.toml without flagging it.
- Do not store or log the user's file paths anywhere outside the report they asked
  for.
