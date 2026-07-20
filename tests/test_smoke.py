"""Smoke tests for the profiling engine, type inference, and reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from spreadsheet_cleaner import __version__, clean, profile
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
