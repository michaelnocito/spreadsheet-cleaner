"""Smoke tests for the profiling engine, type inference, and reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from spreadsheet_cleaner import __version__, profile
from spreadsheet_cleaner.core import types
from spreadsheet_cleaner.core.io import LoadError, load
from spreadsheet_cleaner.core.models import Dimension, Severity
from spreadsheet_cleaner.report import render, to_dict, write

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
