# Spreadsheet Cleaner Roadmap

Spreadsheet Cleaner profiles, cleans, and validates messy CSV and Excel files
before a data migration, and exports a defensible, per-dimension data-quality
report your client can sign off. It runs on your machine. No cloud, no upload,
no account, no row caps. Use the `pip` package, the CLI, or the desktop app.

Spreadsheet Cleaner is, and will stay, **free and open source.**

---

## What guides the roadmap

Five pillars. If a feature serves none of them, it does not ship.

1. **Private by construction** - the data you clean never leaves your machine.
   No network in the cleaning path, no telemetry, no account, air-gappable. The
   only outward request is an opt-in update check you trigger yourself.
2. **Defensible and auditable** - every check is documented and every change is
   logged before and after with counts. The output is a dated, per-dimension,
   pass/fail report. Non-destructive by default: the source file is never
   overwritten.
3. **Deterministic and reproducible** - cleaning and validation are a recipe (a
   small text file). Same recipe plus same file gives the same result. Commit the
   recipe and re-run it on next month's delivery. Data-quality QA as code,
   without a pipeline.
4. **One engine, two surfaces, many formats** - a desktop app for the one-off
   client file and a `pip` library plus CLI for automation and CI. Reads CSV and
   Excel; writes cleaned CSV, Excel, and JSON; reports as HTML, Markdown, and JSON.
5. **Migration-aware** - not just generic cleaning, but the checks a migration
   actually needs: required-field completeness, key uniqueness, allowed values,
   format conformity, referential and lookup validation against target data,
   exact and fuzzy duplicate detection, and row-count reconciliation.

Every check maps to a recognized data-quality dimension (DAMA-UK 2013 /
DMBOK2): completeness, uniqueness, validity, consistency, conformity, and
integrity. The report reads as a standard data-quality scorecard.

---

## Who it is for

Anyone handed a messy spreadsheet who has to make it trustworthy before it
goes anywhere, and who cannot upload a client's real records to a cloud tool.

- **Data migration analysts** - profile and clean source data, validate it
  against the target's rules, and hand the client a signed-off quality report
  before the load runs.
- **Data analysts and junior analysts** - audit an inherited file, understand its
  shape, and clean it without a data-engineering stack.
- **Business analysts** - check a delivery for missing fields, duplicates, and
  format problems before it feeds a report.
- **Data-quality and ETL engineers** - a fast, offline first pass on ad-hoc files
  that do not justify a full pipeline.

**Spreadsheet Cleaner is not** a cloud data-prep service, an enterprise
record-matching suite, a pipeline framework that needs a warehouse connection
and code, or a BI visualization tool. It is a lightweight, offline workbench.

---

## Shipping order

### Shipped

**Phase B - Profiler and quality report (v0.1.0)**
- **Profiling engine** across the data-quality dimensions: per-column fill rate,
  distinct and unique counts, min/max, value lengths, top values.
- **Column-type inference** - integers, decimals, dates, emails, phones,
  booleans, categoricals, and free text, with per-cell violations flagged.
- **Robust ingest** - CSV with encoding and delimiter sniffing, Excel with sheet
  selection, blank-row handling, and the OneDrive placeholder guard.
- **The quality report** - dated, per-dimension, pass/fail, with error counts and
  sample offending values, as a self-contained HTML file (Zinc & Sky, works
  offline), Markdown, and JSON.
- **CLI** (`spreadsheet-cleaner profile`) with a CI-friendly exit code, and a
  **Python API** (`from spreadsheet_cleaner import profile`).

### Next: the cleaning engine
- **A-la-carte cleaning steps** - trim whitespace, normalize case, parse dates to
  a single target format, coerce numbers and currency, standardize categoricals,
  and remove exact duplicates.
- **Change log** - every edit recorded before and after with per-column counts;
  cleaned output written as a copy, source untouched.
- **Recipe files** (YAML/JSON) - an ordered, deterministic pipeline you save,
  commit, and re-run on the next delivery.

### Then: migration validation
- **Validation rules** - required, unique/primary-key, allowed values, regex, and
  range, each mapped to a data-quality dimension.
- **Source-to-target mapping** - map columns to target fields with type, length,
  and required constraints, and validate the mapped set ("will it load?").
- **Referential and lookup validation** against a reference file.
- **Row-count and control-total reconciliation** between source and cleaned data.
- **Fuzzy and near-duplicate detection** for merge review.

### Then: surfaces and adoption
- **Desktop app** (Zinc & Sky, offline) - open a file, profile, clean, validate,
  and export the report, with a Windows installer.
- **RecordForge round-trip** - clean the messy data RecordForge generates, and a
  gradable data-cleaning drill for the Analyst Prep Kit.

### Later, if the need is there
- Large-file and streaming mode; connectors to load targets; macOS/Linux desktop
  builds; locale and format internationalization.

---

*Have a use case that isn't covered? Open an issue.*
