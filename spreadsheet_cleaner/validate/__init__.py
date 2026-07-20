"""The validation engine: rules, lookups, near-duplicates, reconciliation."""

from __future__ import annotations

from pathlib import Path

from spreadsheet_cleaner.core.models import QualityReport
from spreadsheet_cleaner.validate.dedupe import DedupeResult, find_near_duplicates
from spreadsheet_cleaner.validate.reconcile import ReconcileResult, reconcile
from spreadsheet_cleaner.validate.rules import (
    ValidationReport,
    validate_file,
    validate_table,
)
from spreadsheet_cleaner.validate.schema import TargetSchema, load_schema


def starter_schema_yaml(report: QualityReport) -> str:
    """Draft a target schema from a profile, for the user to edit.

    Types come from inference; ``required`` is proposed where a column is fully
    filled, ``unique`` where it is a key candidate. Everything is a starting
    point - the target system's real contract is the user's call.
    """
    lines = [
        f"# Target schema drafted from {Path(report.source).name} by Spreadsheet Cleaner.",
        "# Edit to match the TARGET system's contract: this draft only reflects",
        "# what the source file happens to look like today.",
        f"target: {Path(report.source).stem}",
        "fields:",
    ]
    for col in report.columns:
        ftype = col.inferred_type
        if ftype in ("categorical", "empty", "text"):
            ftype = "text"
        lines.append(f"  - name: {col.name}")
        if ftype != "text":
            lines.append(f"    type: {ftype}")
        if col.missing == 0 and col.total > 0:
            lines.append("    required: true")
        if col.is_unique:
            lines.append("    unique: true")
        if col.inferred_type == "categorical" and col.top_values:
            values = ", ".join(v for v, _ in col.top_values)
            lines.append(f"    # allowed: [{values}]")
    lines.append("settings:")
    lines.append("  extra_columns: warn   # ignore | warn | error")
    lines.append("")
    return "\n".join(lines)


__all__ = [
    "TargetSchema",
    "load_schema",
    "ValidationReport",
    "validate_table",
    "validate_file",
    "DedupeResult",
    "find_near_duplicates",
    "ReconcileResult",
    "reconcile",
    "starter_schema_yaml",
]
