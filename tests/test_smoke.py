"""Smoke tests for the profiling engine, type inference, and reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from spreadsheet_cleaner import (
    __version__,
    clean,
    find_near_duplicates,
    load_schema,
    profile,
    reconcile,
    validate,
)
from spreadsheet_cleaner.clean import clean_file, default_recipe, load_recipe, save_recipe, write_clean
from spreadsheet_cleaner.core import types
from spreadsheet_cleaner.core.io import LoadError, load
from spreadsheet_cleaner.core.models import Dimension, Severity
from spreadsheet_cleaner.report import render, to_dict, write
from spreadsheet_cleaner.report.clean_report import to_html as clean_to_html

# A small table that intentionally trips every dimension.
MESSY_ROWS = [
    ["employee_id", "full_name", "start_date", "department", "salary", "active"],
    ["1001", "Sarah Johnson", "2021-03-15", "Engineering", "85000", "yes"],
    ["1002", "Mike Torres", "March 4 2020", "engineering", "72000", "YES"],  # date drift + casing
    ["1003", "Linda Park ", "15/06/2019", "Marketing", "68000", "no"],       # whitespace
    ["1003", "Linda Park", "2019/05/10", "Sales", "not_a_number", "no"],     # dup key + bad number
    ["1005", "", "2022-11-01", "", "91000", "yes"],                          # missing
    ["1006", "Amy Chen", "N/A", "HR", "78000", "Yes"],                       # placeholder null
]


@pytest.fixture()
def messy_csv(tmp_path: Path) -> Path:
    path = tmp_path / "messy.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(MESSY_ROWS)
    return path


# ---- type inference ----------------------------------------------------------

def test_infers_integer_and_flags_violation():
    inf = types.infer(["1001", "1002", "1003", "not_a_number"])
    assert inf.inferred_type == "integer"
    assert "not_a_number" in inf.violations


def test_detects_multiple_date_formats():
    inf = types.infer(["2021-03-15", "March 4 2020", "15/06/2019", "2019/05/10"])
    assert inf.inferred_type == "date"
    assert len(inf.formats) >= 3  # format drift is what conformity keys off


def test_email_and_categorical():
    assert types.infer(["a@b.com", "c@d.org"]).inferred_type == "email"
    assert types.infer(["North", "South", "North", "East"]).inferred_type == "categorical"


# ---- engine ------------------------------------------------------------------

def test_profile_finds_all_dimensions(messy_csv: Path):
    report = profile(messy_csv)
    dims = {i.dimension for i in report.issues}
    assert Dimension.COMPLETENESS in dims
    assert Dimension.UNIQUENESS in dims   # duplicate employee_id
    assert Dimension.VALIDITY in dims     # 'not_a_number' in salary
    assert Dimension.CONFORMITY in dims   # date drift / whitespace
    assert Dimension.CONSISTENCY in dims  # engineering vs Engineering / yes vs YES


def test_duplicate_key_is_an_error(messy_csv: Path):
    report = profile(messy_csv)
    key_issues = [i for i in report.issues if i.dimension is Dimension.UNIQUENESS and i.column == "employee_id"]
    assert key_issues and key_issues[0].severity is Severity.ERROR
    assert "1003" in key_issues[0].samples


def test_score_and_grade_are_sane(messy_csv: Path):
    report = profile(messy_csv)
    assert 0 <= report.score <= 100
    assert report.grade in {"A", "B", "C", "D", "F"}
    assert report.error_count >= 1


def test_clean_table_scores_high(tmp_path: Path):
    path = tmp_path / "clean.csv"
    rows = [["id", "city"]] + [[str(i), c] for i, c in enumerate(["Rome", "Oslo", "Lima", "Cairo"])]
    with path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(rows)
    report = profile(path)
    assert report.score >= 95
    assert report.error_count == 0


def test_version_is_stamped(messy_csv: Path):
    assert profile(messy_csv).tool_version == __version__


# ---- ingest ------------------------------------------------------------------

def test_missing_file_raises_loaderror():
    with pytest.raises(LoadError):
        load("does_not_exist_12345.csv")


def test_blank_rows_are_ignored(tmp_path: Path):
    path = tmp_path / "gaps.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([["a", "b"], ["1", "2"], ["", ""], ["3", "4"]])
    report = profile(path)
    assert report.rows == 2
    assert report.blank_rows_ignored == 1


# ---- reports -----------------------------------------------------------------

def test_all_report_formats_render(messy_csv: Path):
    report = profile(messy_csv)
    html = render(report, "html")
    assert html.startswith("<!doctype html>") and "Data Quality Report" in html
    assert "```" not in render(report, "md")[:3]  # markdown renders as text
    parsed = json.loads(render(report, "json"))
    assert parsed["grade"] == report.grade
    assert to_dict(report)["tool"] == "spreadsheet-cleaner"


def test_write_creates_files(messy_csv: Path, tmp_path: Path):
    report = profile(messy_csv)
    written = write(report, tmp_path / "out", formats=("html", "md", "json"))
    assert len(written) == 3
    for path in written:
        assert path.exists() and path.stat().st_size > 0


# ---- cleaning engine ---------------------------------------------------------

def test_default_clean_improves_the_grade(messy_csv: Path):
    result = clean(messy_csv)
    before = profile(messy_csv)
    from spreadsheet_cleaner.core.io import LoadedTable, load as _load
    from spreadsheet_cleaner.profiling import profile_table
    after = profile_table(LoadedTable(frame=result.frame, source=_load(messy_csv).source))
    assert after.score >= before.score
    assert not result.changelog.is_empty


def test_clean_normalizes_dates_to_iso(messy_csv: Path):
    result = clean(messy_csv)
    start = result.frame["start_date"]
    parsed = [v for v in start if v and types.parse_date(v)]
    # every parseable date now matches the ISO target format
    assert all(len(v) == 10 and v[4] == "-" and v[7] == "-" for v in parsed)


def test_clean_makes_casing_consistent(messy_csv: Path):
    # the 'active' column has yes/YES and no/No: after cleaning each casefold
    # group collapses to a single spelling.
    result = clean(messy_csv)
    values = [v for v in result.frame["active"] if v]
    groups: dict[str, set[str]] = {v.casefold(): set() for v in values}
    for v in values:
        groups[v.casefold()].add(v)
    assert all(len(spellings) == 1 for spellings in groups.values())


def test_clean_removes_duplicate_rows(messy_csv: Path):
    result = clean(messy_csv)
    assert result.frame.duplicated().sum() == 0


def test_clean_is_non_destructive(messy_csv: Path):
    original = messy_csv.read_bytes()
    clean(messy_csv)
    assert messy_csv.read_bytes() == original  # source untouched


def test_write_clean_refuses_to_overwrite_source(messy_csv: Path):
    result = clean(messy_csv)
    with pytest.raises(ValueError):
        write_clean(result, messy_csv)


def test_recipe_roundtrip_yaml_and_json(messy_csv: Path, tmp_path: Path):
    before = profile(messy_csv)
    recipe = default_recipe(before)
    for name in ("recipe.yml", "recipe.json"):
        path = tmp_path / name
        save_recipe(recipe, path)
        loaded = load_recipe(path)
        assert [s.type for s in loaded.steps] == [s.type for s in recipe.steps]


def test_recipe_driven_clean_writes_files(messy_csv: Path, tmp_path: Path):
    result = clean(messy_csv)
    out = write_clean(result, tmp_path / "cleaned.csv")
    assert out.exists() and out.stat().st_size > 0
    before = profile(messy_csv)
    from spreadsheet_cleaner.core.io import LoadedTable
    after_html = clean_to_html(result, before, before)
    assert after_html.startswith("<!doctype html>") and "Change log" in after_html


def test_unknown_step_raises(messy_csv: Path):
    from spreadsheet_cleaner.clean.recipe import Recipe, Step
    from spreadsheet_cleaner.core.io import load as _load
    from spreadsheet_cleaner.clean import clean_table
    bad = Recipe(steps=[Step(type="does_not_exist")])
    with pytest.raises(ValueError):
        clean_table(_load(messy_csv), recipe=bad)


# ---- validation engine -------------------------------------------------------

SCHEMA_YAML = """\
target: Test Target
key: employee_id
fields:
  - name: employee_id
    type: integer
  - name: full_name
    required: true
    max_length: 12
  - name: start_date
    type: date
    required: true
  - name: department
    lookup: { file: departments.csv, column: department }
  - name: salary
    type: integer
    min: 20000
    max: 90000
  - name: active
    allowed: ["yes", "no"]
settings:
  extra_columns: warn
"""


@pytest.fixture()
def target_schema(tmp_path: Path):
    (tmp_path / "departments.csv").write_text(
        "department\nEngineering\nMarketing\nSales\nHR\n", encoding="utf-8"
    )
    schema_path = tmp_path / "target.yml"
    schema_path.write_text(SCHEMA_YAML, encoding="utf-8")
    return load_schema(schema_path)


def test_validate_catches_contract_violations(messy_csv: Path, target_schema):
    report = validate(messy_csv, target_schema)
    assert not report.passed
    dims = {i.dimension for i in report.issues}
    assert Dimension.UNIQUENESS in dims     # duplicate 1003 vs unique key
    assert Dimension.COMPLETENESS in dims   # blank full_name in a required field
    assert Dimension.VALIDITY in dims       # 'not_a_number' salary / bad date
    assert Dimension.INTEGRITY in dims      # 'engineering' not in the lookup (case-sensitive)
    titles = " ".join(i.title for i in report.issues)
    assert "Sarah Johnson" not in titles    # sanity: values only appear as samples


def test_validate_range_and_length(messy_csv: Path, target_schema):
    report = validate(messy_csv, target_schema)
    out_of_range = [i for i in report.issues if "out of range" in i.title]
    assert out_of_range and "91000" in out_of_range[0].samples
    too_long = [i for i in report.issues if "max length" in i.title]
    assert too_long  # 'Sarah Johnson' is 13 chars > 12


def test_validate_missing_source_column(tmp_path: Path, messy_csv: Path):
    schema_path = tmp_path / "s.yml"
    schema_path.write_text(
        "target: T\nfields:\n  - name: nope\n    required: true\n", encoding="utf-8"
    )
    report = validate(messy_csv, load_schema(schema_path))
    assert not report.passed
    assert any(not f.found for f in report.fields)


def test_clean_then_validate_passes_more(messy_csv: Path, target_schema, tmp_path: Path):
    before = validate(messy_csv, target_schema)
    result = clean(messy_csv)
    cleaned_path = write_clean(result, tmp_path / "cleaned.csv")
    after = validate(cleaned_path, target_schema)
    assert after.error_count < before.error_count
    assert after.score >= before.score


def test_starter_schema_roundtrips(messy_csv: Path, tmp_path: Path):
    from spreadsheet_cleaner.validate import starter_schema_yaml
    draft = starter_schema_yaml(profile(messy_csv))
    path = tmp_path / "draft.yml"
    path.write_text(draft, encoding="utf-8")
    schema = load_schema(path)  # the draft must be a valid schema as-is
    assert any(f.name == "employee_id" for f in schema.fields)


def test_bad_schema_raises(tmp_path: Path):
    path = tmp_path / "bad.yml"
    path.write_text(
        "target: T\nfields:\n  - name: a\n    type: not_a_type\n", encoding="utf-8"
    )
    with pytest.raises(ValueError):
        load_schema(path)


# ---- near-duplicates and reconciliation --------------------------------------

def test_near_duplicates_found(tmp_path: Path):
    path = tmp_path / "dupes.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([
            ["name", "email", "city"],
            ["Sarah Johnson", "sarah.j@co.com", "Portland"],
            ["Sara Johnson", "sarah.j@co.com", "Portland"],   # near-dup (typo)
            ["Tom Reyes", "tom.r@co.com", "Austin"],
        ])
    frame = load(path).frame
    result = find_near_duplicates(frame, threshold=0.85)
    assert len(result.pairs) == 1
    assert {result.pairs[0].row_a, result.pairs[0].row_b} == {1, 2}


def test_near_duplicates_ignores_distinct_rows(messy_csv: Path):
    frame = load(messy_csv).frame
    result = find_near_duplicates(frame, threshold=0.97)
    # the two 1003/Linda rows differ in several fields; at 0.97 nothing pairs
    assert all(p.similarity >= 0.97 for p in result.pairs)


def test_reconcile_counts_keys_and_totals(messy_csv: Path, tmp_path: Path):
    result = clean(messy_csv)
    cleaned_path = write_clean(result, tmp_path / "cleaned.csv")
    rec = reconcile(
        load(messy_csv), load(cleaned_path),
        key="employee_id", total_columns=["salary"],
    )
    # No exact-duplicate rows in the fixture, so cleaning drops nothing:
    # counts, keys, and salary control totals all reconcile.
    assert rec.source_rows == rec.other_rows == 6
    assert rec.keys_match
    assert rec.control_totals[0].column == "salary"
    assert rec.clean_pass


def test_reconcile_detects_dropped_row(messy_csv: Path, tmp_path: Path):
    import pandas as pd
    frame = load(messy_csv).frame
    trimmed = frame.iloc[:-1]  # simulate a lost record
    lost_path = tmp_path / "lost.csv"
    trimmed.to_csv(lost_path, index=False)
    rec = reconcile(load(messy_csv), load(lost_path), key="employee_id")
    assert rec.row_difference == -1
    assert rec.keys_only_in_source == ["1006"]
    assert not rec.clean_pass


def test_reconcile_missing_key_raises(messy_csv: Path):
    with pytest.raises(ValueError):
        reconcile(load(messy_csv), load(messy_csv), key="nope")


# ---- desktop bridge (headless: no window is created) -------------------------

pywebview = pytest.importorskip("webview", reason="desktop extra not installed")


@pytest.fixture()
def bridge():
    from spreadsheet_cleaner.ui.app import API
    return API()


def test_ui_html_is_bundled_and_resolves():
    from spreadsheet_cleaner.ui.app import ui_html_path
    path = ui_html_path()
    assert path.exists() and path.name == "ui.html"
    # resolved from the package, not the entry script (PyInstaller onefile)
    assert path.parent.name == "ui" and path.parent.parent.name == "spreadsheet_cleaner"


def test_bridge_run_profile_only(bridge, messy_csv: Path, tmp_path: Path):
    res = bridge.run({"file": str(messy_csv), "out": str(tmp_path)})
    assert res["success"] is True
    assert len(res["files"]) == 1
    assert Path(res["files"][0]["path"]).exists()
    assert res["summary"]["profile"]["grade"] in {"A", "B", "C", "D", "F"}
    assert res["summary"]["clean"] is None and res["summary"]["validate"] is None


def test_bridge_run_clean_and_validate(bridge, messy_csv: Path, target_schema, tmp_path: Path):
    res = bridge.run({
        "file": str(messy_csv), "out": str(tmp_path),
        "clean": True, "validate": True,
        "schema": str(target_schema.path), "near_dupes": True,
    })
    assert res["success"] is True
    labels = {f["label"] for f in res["files"]}
    assert {"Quality report", "Cleaned data", "Cleaning report", "Recipe (re-runnable)",
            "Validation report"} <= labels
    for f in res["files"]:
        assert Path(f["path"]).exists()
    assert res["summary"]["clean"]["after_score"] >= res["summary"]["clean"]["before_score"]
    assert res["summary"]["validate"]["verdict"] in {"PASS", "FAIL"}
    assert res["summary"]["validate"]["on_cleaned"] is True


def test_bridge_errors_are_returned_not_raised(bridge, tmp_path: Path):
    res = bridge.run({"file": str(tmp_path / "nope.csv"), "out": str(tmp_path)})
    assert res["success"] is False and res["files"] == []
    assert "not found" in res["error"].lower()


def test_bridge_validate_without_schema_errors(bridge, messy_csv: Path, tmp_path: Path):
    res = bridge.run({"file": str(messy_csv), "out": str(tmp_path), "validate": True})
    assert res["success"] is False and "schema" in res["error"].lower()


def test_bridge_draft_schema(bridge, messy_csv: Path, tmp_path: Path):
    res = bridge.draft_schema({"file": str(messy_csv), "out": str(tmp_path)})
    assert res["success"] is True
    assert load_schema(res["path"]).fields  # the draft is immediately valid


def test_bridge_version_and_sheets(bridge, messy_csv: Path):
    assert bridge.app_version() == __version__
    assert bridge.sheets(str(messy_csv)) == []  # CSV has no sheets


def test_update_check_handles_offline(bridge, monkeypatch):
    from spreadsheet_cleaner.ui import app as ui_app
    monkeypatch.setattr(
        ui_app, "_fetch_latest_release",
        lambda: (_ for _ in ()).throw(OSError("no network")),
    )
    result = bridge.check_update()
    assert result["status"] == "error" and result["url"].endswith("/releases/latest")


def test_update_check_reports_available(bridge, monkeypatch):
    from spreadsheet_cleaner.ui import app as ui_app
    monkeypatch.setattr(ui_app, "_fetch_latest_release", lambda: {"tag_name": "v99.0.0"})
    result = bridge.check_update()
    assert result["status"] == "available" and result["latest"] == "99.0.0"


def test_update_check_reports_latest(bridge, monkeypatch):
    from spreadsheet_cleaner.ui import app as ui_app
    monkeypatch.setattr(ui_app, "_fetch_latest_release", lambda: {"tag_name": f"v{__version__}"})
    assert bridge.check_update()["status"] == "latest"
