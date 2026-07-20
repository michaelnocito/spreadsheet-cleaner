"""Data models for the profiling / quality engine.

Every finding the engine produces is an ``Issue`` tagged with a
``Dimension`` (a recognized data-quality dimension) and a ``Severity``.
A ``QualityReport`` bundles the per-column profiles, the issues, and the
per-dimension statistics that drive the scorecard the report renders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Dimension(str, Enum):
    """Data-quality dimensions (DAMA-UK 2013 / DMBOK2)."""

    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
    CONFORMITY = "conformity"
    STRUCTURE = "structure"

    @property
    def label(self) -> str:
        return {
            Dimension.COMPLETENESS: "Completeness",
            Dimension.UNIQUENESS: "Uniqueness",
            Dimension.VALIDITY: "Validity",
            Dimension.CONSISTENCY: "Consistency",
            Dimension.CONFORMITY: "Conformity",
            Dimension.STRUCTURE: "Structure",
        }[self]

    @property
    def description(self) -> str:
        return {
            Dimension.COMPLETENESS: "Required values are present, not blank or placeholder.",
            Dimension.UNIQUENESS: "No record or key is recorded more than once.",
            Dimension.VALIDITY: "Values match the column's intended data type.",
            Dimension.CONSISTENCY: "The same value is spelled and cased one way.",
            Dimension.CONFORMITY: "Values follow one format for dates, numbers, and spacing.",
            Dimension.STRUCTURE: "The table has a clean shape: no blank rows or columns.",
        }[self]


# Dimensions shown on the scorecard, in report order.
DIMENSION_ORDER: tuple[Dimension, ...] = (
    Dimension.COMPLETENESS,
    Dimension.VALIDITY,
    Dimension.CONFORMITY,
    Dimension.CONSISTENCY,
    Dimension.UNIQUENESS,
    Dimension.STRUCTURE,
)


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    @property
    def rank(self) -> int:
        return {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}[self]


@dataclass
class Issue:
    """A single finding. ``column`` is ``None`` for table-level findings."""

    dimension: Dimension
    severity: Severity
    title: str
    detail: str
    column: str | None = None
    count: int = 0
    samples: list[str] = field(default_factory=list)


@dataclass
class ColumnProfile:
    """Per-column profile: what the column is and how healthy it is."""

    name: str
    inferred_type: str
    type_confidence: float
    total: int
    present: int
    missing: int
    distinct: int
    fill_rate: float
    distinct_rate: float
    is_unique: bool
    top_values: list[tuple[str, int]] = field(default_factory=list)
    sample_values: list[str] = field(default_factory=list)
    min_value: str | None = None
    max_value: str | None = None
    min_len: int | None = None
    max_len: int | None = None
    formats: list[tuple[str, int]] = field(default_factory=list)


@dataclass
class DimensionStat:
    """Affected vs. applicable units for one dimension. Drives the score."""

    affected: int = 0
    applicable: int = 0

    def add(self, affected: int, applicable: int) -> None:
        self.affected += affected
        self.applicable += applicable

    @property
    def score(self) -> float:
        if self.applicable <= 0:
            return 100.0
        ratio = min(1.0, self.affected / self.applicable)
        return round(100.0 * (1.0 - ratio), 1)


@dataclass
class QualityReport:
    """The full result of profiling one table."""

    source: str
    sheet: str | None
    generated_at: datetime
    tool_version: str
    rows: int
    cols: int
    blank_rows_ignored: int
    columns: list[ColumnProfile] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    dimension_stats: dict[Dimension, DimensionStat] = field(default_factory=dict)

    def stat(self, dimension: Dimension) -> DimensionStat:
        return self.dimension_stats.setdefault(dimension, DimensionStat())

    @property
    def total_cells(self) -> int:
        return self.rows * self.cols

    @property
    def score(self) -> float:
        scores = [self.stat(d).score for d in DIMENSION_ORDER]
        return round(sum(scores) / len(scores), 1) if scores else 100.0

    @property
    def grade(self) -> str:
        s = self.score
        if s >= 95:
            return "A"
        if s >= 85:
            return "B"
        if s >= 70:
            return "C"
        if s >= 50:
            return "D"
        return "F"

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity is Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity is Severity.WARNING)

    def issues_for(self, dimension: Dimension) -> list[Issue]:
        return [i for i in self.issues if i.dimension is dimension]

    def sorted_issues(self) -> list[Issue]:
        """Issues most-severe first, then by affected count."""
        return sorted(
            self.issues, key=lambda i: (i.severity.rank, -i.count)
        )
