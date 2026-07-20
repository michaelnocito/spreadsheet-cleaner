# Spreadsheet Cleaner - Architecture Spec

## Overview

Spreadsheet Cleaner is an offline workbench for pre-migration data quality. It
profiles, cleans, and validates messy CSV / Excel files and exports a
per-dimension quality report. Fully offline: no network calls in the analysis
or cleaning path. One engine, delivered three ways - a `pip` library, a CLI,
and (Phase E) a desktop app.

**Phase B (shipped, v0.1.0):** the profiling engine, robust ingest, type
inference, the data-quality checks, and the HTML / Markdown / JSON report, plus
the CLI and Python API. No cleaning or target validation yet.

---

## Repo / Package

- Repo name: `spreadsheet-cleaner`
- Python package: `spreadsheet_cleaner`
- Entry points: CLI (`spreadsheet-cleaner`) and `python -m spreadsheet_cleaner`
- Python: 3.10+

---

## Package Structure

```
spreadsheet_cleaner/
├── __init__.py            # public API: profile(); __version__
├── __main__.py            # python -m spreadsheet_cleaner → CLI (GUI in Phase E)
├── cli.py                 # Typer CLI: `profile`
├── core/
│   ├── __init__.py
│   ├── models.py          # Dimension, Severity, Issue, ColumnProfile,
│   │                      #   DimensionStat, QualityReport (+ scoring)
│   ├── io.py              # LoadedTable, load() - CSV/Excel ingest, blank rows,
│   │                      #   encoding/delimiter sniff, OneDrive guard
│   └── types.py           # column type inference + per-value violations + formats
├── profiling/
│   ├── __init__.py        # profile_table(), profile_file() - orchestrators
│   ├── columns.py         # profile_column() - per-column stats
│   └── checks.py          # run_checks() - dimension checks → Issues + stats
└── report/
    ├── __init__.py        # render(), write() dispatch
    ├── html.py            # self-contained Zinc & Sky HTML report (no CDN)
    ├── markdown.py        # Markdown report
    └── json_report.py     # machine-readable JSON report
```

Planned (later phases, not yet built):

```
├── clean/                 # Phase C: steps.py, recipe.py, changelog.py
├── validate/              # Phase D: rules.py, mapping.py, reconcile.py
└── ui/                    # Phase E: app.py (pywebview bridge) + ui.html
```

---

## Data model (`core/models.py`)

- `Dimension` - the DAMA data-quality dimensions checked: `COMPLETENESS`,
  `UNIQUENESS`, `VALIDITY`, `CONSISTENCY`, `CONFORMITY`, `STRUCTURE`. Each carries
  a `label` and `description`. `DIMENSION_ORDER` fixes report order.
- `Severity` - `INFO`, `WARNING`, `ERROR`, with a `rank` for sorting.
- `Issue` - one finding: dimension, severity, optional `column`, title, detail,
  affected `count`, and up to a handful of sample values.
- `ColumnProfile` - name, inferred type and confidence, totals, fill/distinct
  rates, unique-key flag, top values, min/max, lengths, and format breakdown.
- `DimensionStat` - `affected` vs. `applicable` counts; `score` = `100 * (1 -
  affected/applicable)`.
- `QualityReport` - source, sheet, timestamp, version, row/col counts, the list
  of `ColumnProfile`, the list of `Issue`, and the per-dimension `DimensionStat`.
  Computes overall `score` (mean of dimension scores), `grade` (A-F), and error /
  warning counts.

## Scoring

Each dimension scores `100 * (1 - affected/applicable)`, where the denominator is
the number of values that check applied to (e.g. present cells for validity, rows
for uniqueness). Overall score is the mean of the six dimension scores; grade is
A (>=95), B (>=85), C (>=70), D (>=50), else F. The report shows the
affected/applicable basis for every dimension so the number is defensible.

## Ingest contract (`core/io.py`)

- Everything loads as **strings**; blanks are preserved as empty strings.
  Nothing is silently coerced or dropped - the profiler sees the raw file.
- CSV: encoding sniff (`utf-8-sig`, `utf-8`, `cp1252`, `latin-1`), delimiter
  sniff via the python engine.
- Excel: `openpyxl`, sheet selectable by name (first sheet default), sheet list
  reported. `zipfile.BadZipFile` is caught and explained (the OneDrive
  not-yet-downloaded trap).
- Fully-blank rows are dropped and counted; a cell is missing if it is
  null/NaN or whitespace-only. Placeholder nulls (`N/A`, `-`, ...) are detected
  as present-but-likely-missing.
- Errors raise `LoadError` with a human-readable message. No stack trace reaches
  the user.

---

## API and CLI contract

- `from spreadsheet_cleaner import profile; report = profile(path, sheet=None)`
  returns a `QualityReport`.
- `from spreadsheet_cleaner.report import render, write` renders a report to a
  string (`render(report, "html"|"md"|"json")`) or writes files (`write(report,
  out_dir, formats)`).
- `spreadsheet-cleaner profile FILE [--sheet] [--format html,md,json] [--out DIR]
  [--open] [--quiet]`. Exit code is `1` when the file has hard errors (so CI can
  gate on it), `2` on load failure, `0` otherwise.

---

## Non-negotiables (see CLAUDE.md)

- No network calls in ingest, profiling, or reporting.
- Read-only: the profiler never modifies the source file. When cleaning lands
  (Phase C) it writes a copy and a change log; it never overwrites the source.
- Every finding maps to a `Dimension`. If a check does not fit a dimension, the
  dimension list grows deliberately, not the check.
- All output is portable and offline: the HTML report embeds its own CSS, no CDN.
