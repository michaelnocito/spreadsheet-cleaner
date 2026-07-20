"""Reconciliation: prove nothing was lost or invented between two versions.

Compares a source file against its cleaned/load-ready counterpart: row counts,
key coverage in both directions, and control totals on numeric columns. This is
the step an auditor asks for - "show me the record you dropped and why."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from spreadsheet_cleaner.core import types
from spreadsheet_cleaner.core.io import LoadedTable


@dataclass
class ControlTotal:
    column: str
    source_total: Decimal
    other_total: Decimal

    @property
    def difference(self) -> Decimal:
        return self.other_total - self.source_total

    @property
    def matches(self) -> bool:
        return self.source_total == self.other_total


@dataclass
class ReconcileResult:
    source_rows: int
    other_rows: int
    key: str | None = None
    keys_only_in_source: list[str] = field(default_factory=list)
    keys_only_in_other: list[str] = field(default_factory=list)
    control_totals: list[ControlTotal] = field(default_factory=list)

    @property
    def row_difference(self) -> int:
        return self.other_rows - self.source_rows

    @property
    def keys_match(self) -> bool:
        return not self.keys_only_in_source and not self.keys_only_in_other

    @property
    def totals_match(self) -> bool:
        return all(t.matches for t in self.control_totals)

    @property
    def clean_pass(self) -> bool:
        """True when counts, keys, and totals all reconcile exactly."""
        return self.row_difference == 0 and self.keys_match and self.totals_match


def _column_total(series) -> Decimal | None:
    total = Decimal(0)
    numeric = 0
    for v in series:
        text = str(v).strip()
        if text == "":
            continue
        cleaned = types.clean_number(text)
        try:
            total += Decimal(cleaned)
            numeric += 1
        except InvalidOperation:
            continue
    return total if numeric else None


def reconcile(
    source: LoadedTable,
    other: LoadedTable,
    *,
    key: str | None = None,
    total_columns: list[str] | None = None,
) -> ReconcileResult:
    """Reconcile ``other`` (cleaned/load-ready) back against ``source``."""
    result = ReconcileResult(
        source_rows=len(source.frame), other_rows=len(other.frame), key=key
    )

    if key is not None:
        for name, table in (("source", source), ("cleaned", other)):
            if key not in table.frame.columns:
                raise ValueError(f"Key column '{key}' not found in the {name} file.")
        src_keys = {str(v).strip() for v in source.frame[key] if str(v).strip() != ""}
        oth_keys = {str(v).strip() for v in other.frame[key] if str(v).strip() != ""}
        result.keys_only_in_source = sorted(src_keys - oth_keys)
        result.keys_only_in_other = sorted(oth_keys - src_keys)

    if total_columns:
        for column in total_columns:
            if column not in source.frame.columns or column not in other.frame.columns:
                raise ValueError(f"Control-total column '{column}' must exist in both files.")
            src_total = _column_total(source.frame[column])
            oth_total = _column_total(other.frame[column])
            result.control_totals.append(ControlTotal(
                column=column,
                source_total=src_total if src_total is not None else Decimal(0),
                other_total=oth_total if oth_total is not None else Decimal(0),
            ))

    return result
