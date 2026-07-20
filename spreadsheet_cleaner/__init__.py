"""Spreadsheet Cleaner - the offline workbench for pre-migration data quality.

Profile a messy CSV or Excel file and get a defensible, per-dimension data
quality report - all on your machine, nothing uploaded.

    from spreadsheet_cleaner import profile
    from spreadsheet_cleaner.report import to_html, write
    report = profile("clients.xlsx")
    print(report.grade, report.score)
    write(report, "out", formats=("html", "md", "json"))

See ``spreadsheet_cleaner.report`` to render HTML / Markdown / JSON.
"""

from __future__ import annotations

from pathlib import Path

from spreadsheet_cleaner.clean import (
    CleanResult,
    Recipe,
    clean_file,
    default_recipe,
    load_recipe,
    save_recipe,
    write_clean,
)
from spreadsheet_cleaner.core.io import LoadError, load
from spreadsheet_cleaner.core.models import (
    ColumnProfile,
    Dimension,
    Issue,
    QualityReport,
    Severity,
)
from spreadsheet_cleaner.profiling import profile_table

__version__ = "0.2.0"


def profile(path: str | Path, *, sheet: str | None = None) -> QualityReport:
    """Load and profile a CSV/Excel file, returning a QualityReport."""
    return profile_table(load(path, sheet=sheet), version=__version__)


def clean(
    path: str | Path, *, recipe: Recipe | None = None, sheet: str | None = None
) -> CleanResult:
    """Clean a CSV/Excel file with a recipe (or a smart default), non-destructively."""
    return clean_file(path, recipe=recipe, sheet=sheet)


__all__ = [
    "__version__",
    "profile",
    "clean",
    "load",
    "LoadError",
    "QualityReport",
    "ColumnProfile",
    "Issue",
    "Dimension",
    "Severity",
    "CleanResult",
    "Recipe",
    "write_clean",
    "default_recipe",
    "load_recipe",
    "save_recipe",
]
