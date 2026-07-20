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

from spreadsheet_cleaner.core.io import LoadError, load
from spreadsheet_cleaner.core.models import (
    ColumnProfile,
    Dimension,
    Issue,
    QualityReport,
    Severity,
)
from spreadsheet_cleaner.profiling import profile_table

__version__ = "0.1.0"


def profile(path: str | Path, *, sheet: str | None = None) -> QualityReport:
    """Load and profile a CSV/Excel file, returning a QualityReport."""
    return profile_table(load(path, sheet=sheet), version=__version__)


__all__ = [
    "__version__",
    "profile",
    "load",
    "LoadError",
    "QualityReport",
    "ColumnProfile",
    "Issue",
    "Dimension",
    "Severity",
]
