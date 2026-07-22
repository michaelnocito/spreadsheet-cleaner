# The RecordForge round-trip

[RecordForge](https://github.com/michaelnocito/recordforge) and Spreadsheet
Cleaner are mirror images. RecordForge *injects* data-quality problems on
purpose; Spreadsheet Cleaner *detects and fixes* them. Running one into the
other is the cleanest way to prove the audit catches what it should, and it
makes a gradable data-cleaning exercise with a known answer key.

Both tools are offline, and both are deterministic given a seed, so the whole
loop is reproducible.

## 1. Generate a messy dataset with known problems

```bash
recordforge generate --type customers --format csv --rows 500 --seed 42 \
  --dirty "nulls=0.08,duplicates=0.05,case_drift=0.10,format_drift=0.10,whitespace=0.06"
```

You now know exactly what was injected: roughly 8% nulls, 5% duplicate rows,
casing drift on 10% of values, mixed formats on 10%, stray whitespace on 6%.

## 2. Audit it

```bash
spreadsheet-cleaner profile customers.csv --open
```

The report should surface those same problems, mapped to dimensions:

| RecordForge injected | Spreadsheet Cleaner reports |
|---|---|
| `nulls` | **Completeness** - missing values per column |
| `duplicates` | **Uniqueness** - duplicate rows, duplicate keys |
| `case_drift` | **Consistency** - same value spelled several ways |
| `format_drift` | **Conformity** - several date/number formats in one column |
| `whitespace` | **Conformity** - stray or doubled whitespace |
| `encoding` (mojibake) | **Validity** - values that do not fit the column type |

If a category was injected and the report does not show it, that is a real bug
in the profiler. This is the regression check to run when adding a new
detector.

## 3. Clean it and prove the fix

```bash
spreadsheet-cleaner clean customers.csv --save-recipe recipe.yml
spreadsheet-cleaner reconcile customers.csv customers_cleaned.csv --key customer_id
```

The cleaning report shows the grade climbing and lists every change; the
reconcile step proves no record was lost on the way.

## Using it as a teaching exercise

Because RecordForge is seeded, an instructor can hand out the *same* messy file
to everyone and hold the answer key:

1. Generate the file with a fixed seed and a known dirty profile.
2. Learners run `profile`, interpret the report, then write their own recipe
   rather than accepting the default one.
3. Grade by running `validate` against a target schema, and by comparing their
   cleaned output's score to the reference run.

That gives a data-cleaning drill with an objective, reproducible result, which
is hard to build from real-world files.
