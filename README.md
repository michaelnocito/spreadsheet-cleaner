# 🧼 Spreadsheet Cleaner

### The offline workbench for pre-migration data quality.

Profile a messy CSV or Excel file, catch the problems that break an import, and
export a defensible, per-dimension **data-quality report** your client can sign
off. It runs on your machine. No cloud, no upload, no account, no row caps.

A free, open-source tool by [Michael Nocito](https://www.linkedin.com/in/michaelnocito).

**[🌐 Website](https://michaelnocito.github.io/spreadsheet-cleaner/)** &nbsp;·&nbsp; [GitHub](https://github.com/michaelnocito/spreadsheet-cleaner) &nbsp;·&nbsp; [Roadmap](ROADMAP.md)

---

## Why it exists

Before a data migration, someone has to look at the source file the client sent
and answer one question: *will this load, and can I prove it?* The tools that do
this well are cloud services (you cannot upload a client's real records), or
enterprise suites, or pipeline frameworks that take weeks to set up for a file
you only touch once.

Spreadsheet Cleaner is the missing piece: **a fast, offline, single-file audit
that produces a report you can hand over.** Nothing you profile ever leaves your
machine.

Every check maps to a recognized data-quality dimension (DAMA-UK 2013 /
DMBOK2), so the report reads as a standard scorecard, not ad-hoc warnings.

---

## Install

Install from source (a PyPI package is coming):

```bash
git clone https://github.com/michaelnocito/spreadsheet-cleaner.git
cd spreadsheet-cleaner
pip install -e .
```

This puts the `spreadsheet-cleaner` command on your path. You can also run it
without installing, straight from the repo, with `python -m spreadsheet_cleaner`.

---

## Quickstart

Profile a file and open the report:

```bash
spreadsheet-cleaner profile clients.xlsx --open
```

Write all three report formats into a folder:

```bash
spreadsheet-cleaner profile clients.csv --format html,md,json --out reports
```

The terminal prints a scorecard; the report files are the deliverable:

```
  clients.xlsx  -  grade B (86/100)
  11 rows x 8 columns
  5 error(s), 9 warning(s)

    Completeness  #################---    83
    Validity      ###################-    93
    Conformity    ##################--    89
    Consistency   ############--------    61
    Uniqueness    ###################-    97
    Structure     ##################--    90
```

The CLI exits non-zero when the file has hard errors, so you can gate a
migration step on it in CI.

### From Python

```python
from spreadsheet_cleaner import profile
from spreadsheet_cleaner.report import write

report = profile("clients.xlsx")
print(report.grade, report.score)        # 'B' 85.5
write(report, "reports", formats=("html", "md", "json"))
```

Try it on the included sample:

```bash
python sample_data/create_sample.py
spreadsheet-cleaner profile sample_data/messy_employees.xlsx --open
```

---

## Clean it

Profiling tells you what's wrong; `clean` fixes it, **non-destructively**. With no
recipe it builds a safe one from the profile: trim whitespace, standardize dates
to ISO, strip currency and thousands separators, make casing consistent, remove
exact duplicate rows, and drop empty columns.

```bash
spreadsheet-cleaner clean messy_employees.xlsx --save-recipe recipe.yml --open
```

```
  messy_employees.xlsx  -  cleaned
  grade B (86) -> A (98)
  19 cell change(s); 0 row(s), 1 column(s) removed
```

Your source file is never touched. You get a `*_cleaned` copy, a **cleaning
report** with before/after grades and a full change log, and the recipe as a
small YAML/JSON file you can commit and re-run on the next delivery:

```bash
spreadsheet-cleaner clean next_delivery.xlsx --recipe recipe.yml
```

Use `--dry-run` to preview the changes without writing anything. From Python:

```python
from spreadsheet_cleaner import clean, write_clean
result = clean("messy_employees.xlsx")   # or clean(path, recipe=my_recipe)
write_clean(result, "cleaned.csv")
print(result.changelog.total_changes)
```

---

## What it checks

| Dimension | What it looks for |
|---|---|
| **Completeness** | Missing required values, and placeholder text (`N/A`, `-`) that really means blank. |
| **Validity** | Values that do not match the column's intended type (a word in a number column, a bad date). |
| **Conformity** | Format drift: several date formats in one column, stray or doubled whitespace. |
| **Consistency** | The same value spelled and cased more than one way (`Active` / `active` / `ACTIVE`). |
| **Uniqueness** | Duplicate rows, and duplicate values in a column that looks like a primary key. |
| **Structure** | Blank rows, empty columns, and unlabeled headers. |

For every column it also infers the type (integer, decimal, date, email, phone,
boolean, categorical, or text), reports fill rate and distinct counts, and flags
which columns are unique-key candidates.

The report is a single, self-contained HTML file (styled in the Zinc & Sky
palette, works offline, nothing to download), plus Markdown and JSON for
pipelines.

---

## Who it is for

- **Data migration analysts** - audit and sign off a source file before the load.
- **Data and business analysts** - understand and vet an inherited spreadsheet
  without a data-engineering stack.
- **Data-quality and ETL engineers** - a fast offline first pass on ad-hoc files.

Spreadsheet Cleaner is **not** a cloud data-prep service, an enterprise
record-matching suite, or a pipeline framework. It is a lightweight, offline
workbench. Cleaning, target-schema validation, and a desktop app are on the
[roadmap](ROADMAP.md).

---

## Pairs with RecordForge

[RecordForge](https://michaelnocito.github.io/recordforge/) generates realistic,
deliberately-messy test data; Spreadsheet Cleaner is the inverse - it detects and
reports exactly the problems RecordForge can inject. Generate a messy dataset in
RecordForge, then run it through Spreadsheet Cleaner to see the audit catch them.

---

## More from Michael Nocito

**[🗂️ RecordForge](https://michaelnocito.github.io/recordforge/)** - generate
realistic, clearly-synthetic test data and documents, offline. The mirror image
of this tool.

**[📊 Analyst Prep Kit](https://michaelnocito.github.io/analyst-prep-kit/)** - a
free browser suite for breaking into data analytics: SQL, Excel, Python, Tableau,
and Statistics.

**[LinkedIn](https://www.linkedin.com/in/michaelnocito)** - data analyst · 8 years enterprise implementation

---

## Contributing

Found a bug or have an idea? Open an issue or a pull request. See
[`CONTRIBUTING.md`](CONTRIBUTING.md).

If this saved you time, a [⭐ star](https://github.com/michaelnocito/spreadsheet-cleaner)
helps others find it. A coffee is always appreciated but never expected.

<a href="https://buymeacoffee.com/michaelnocito" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>

---

Built with 🐍 Python · MIT licensed · Maintained by [Michael Nocito](https://github.com/michaelnocito)
