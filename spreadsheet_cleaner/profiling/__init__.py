"""The profiling engine: turn a loaded table into a QualityReport."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from spreadsheet_cleaner.core.io import LoadedTable, load
from spreadsheet_cleaner.core.models import QualityReport
from spreadsheet_cleaner.profiling.checks import run_checks
from spreadsheet_cleaner.profiling.columns import profile_column


def profile_table(table: LoadedTable, *, version: str = "0.0.0") -> QualityReport:
    """Profile an already-loaded table and assess its quality."""
    profiles = [profile_column(name, table.frame[name]) for name in table.frame.columns]
    issues, stats = run_checks(table, profiles)
    return QualityReport(
        source=str(table.source),
        sheet=table.sheet,
        generated_at=datetime.now(timezone.utc),
        tool_version=version,
        rows=table.rows,
        cols=table.cols,
        blank_rows_ignored=table.blank_rows_ignored,
        columns=profiles,
        issues=issues,
        dimension_stats=stats,
    )


def profile_file(
    path: str | Path, *, sheet: str | None = None, version: str = "0.0.0"
) -> QualityReport:
    """Load a CSV/Excel file and profile it in one call."""
    return profile_table(load(path, sheet=sheet), version=version)


__all__ = ["profile_table", "profile_file"]
