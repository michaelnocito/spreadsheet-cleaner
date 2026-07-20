"""The change log: an auditable record of every edit a cleaning run made.

Nothing is changed silently. Each step reports which column it touched, how
many cells (or rows/columns) changed, and a few before/after examples.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChangeRecord:
    """One step's effect on one column (or the whole table)."""

    step: str
    column: str | None
    changed: int
    detail: str = ""
    samples: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class ChangeLog:
    records: list[ChangeRecord] = field(default_factory=list)
    rows_before: int = 0
    rows_after: int = 0
    cols_before: int = 0
    cols_after: int = 0

    def add(self, record: ChangeRecord) -> None:
        if record.changed > 0 or record.detail:
            self.records.append(record)

    @property
    def total_changes(self) -> int:
        return sum(r.changed for r in self.records)

    @property
    def rows_removed(self) -> int:
        return max(0, self.rows_before - self.rows_after)

    @property
    def cols_removed(self) -> int:
        return max(0, self.cols_before - self.cols_after)

    @property
    def is_empty(self) -> bool:
        return not self.records
