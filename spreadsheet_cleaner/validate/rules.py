"""Run a table against a target schema: the "will it load?" check.

Every rule emits ``Issue`` records tagged with a data-quality dimension and
accumulates affected/applicable counts, exactly like the profiler, so the
validation report reads as the same kind of scorecard - but against the
target's contract instead of the file's own shape.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as dc_field
from datetime import datetime, timezone
from pathlib import Path

from spreadsheet_cleaner.core import types
from spreadsheet_cleaner.core.io import LoadedTable, load
from spreadsheet_cleaner.core.models import (
    VALIDATION_ORDER,
    Dimension,
    DimensionStat,
    Issue,
    Severity,
)
from spreadsheet_cleaner.validate.schema import FieldSpec, TargetSchema

_MAX_SAMPLES = 6

_TYPE_TESTS = {
    "integer": types.is_integer,
    "decimal": lambda v: types.is_decimal(v) or types.is_integer(v),
    "date": types.is_date,
    "email": types.is_email,
    "phone": types.is_phone,
    "boolean": types.is_boolean,
    "text": lambda v: True,
}


@dataclass
class FieldResult:
    """How one target field mapped and fared."""

    name: str
    source: str
    found: bool
    errors: int = 0
    warnings: int = 0


@dataclass
class ValidationReport:
    source: str
    sheet: str | None
    target: str
    schema_path: str | None
    generated_at: datetime
    tool_version: str
    rows: int
    fields: list[FieldResult] = dc_field(default_factory=list)
    extra_columns: list[str] = dc_field(default_factory=list)
    issues: list[Issue] = dc_field(default_factory=list)
    dimension_stats: dict[Dimension, DimensionStat] = dc_field(default_factory=dict)

    def stat(self, dimension: Dimension) -> DimensionStat:
        return self.dimension_stats.setdefault(dimension, DimensionStat())

    @property
    def score(self) -> float:
        scores = [self.stat(d).score for d in VALIDATION_ORDER]
        return round(sum(scores) / len(scores), 1) if scores else 100.0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity is Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity is Severity.WARNING)

    @property
    def passed(self) -> bool:
        """Load-ready means zero hard errors against the target contract."""
        return self.error_count == 0

    def sorted_issues(self) -> list[Issue]:
        return sorted(self.issues, key=lambda i: (i.severity.rank, -i.count))


def _present(series) -> list[str]:
    return [str(v).strip() for v in series if str(v).strip() != ""]


def _load_lookup_values(spec: FieldSpec, schema: TargetSchema) -> set[str]:
    base = schema.path.parent if schema.path else Path(".")
    ref_path = Path(spec.lookup.file)
    if not ref_path.is_absolute():
        ref_path = base / ref_path
    ref = load(ref_path)
    if spec.lookup.column not in ref.frame.columns:
        raise ValueError(
            f"Lookup for '{spec.name}': column '{spec.lookup.column}' "
            f"not found in {ref_path.name}. "
            f"Available: {', '.join(ref.frame.columns)}."
        )
    return {v.strip() for v in ref.frame[spec.lookup.column] if str(v).strip() != ""}


def validate_table(
    table: LoadedTable, schema: TargetSchema, *, version: str = "0.0.0"
) -> ValidationReport:
    frame = table.frame
    rows = len(frame)
    report = ValidationReport(
        source=str(table.source),
        sheet=table.sheet,
        target=schema.target,
        schema_path=str(schema.path) if schema.path else None,
        generated_at=datetime.now(timezone.utc),
        tool_version=version,
        rows=rows,
    )
    for dim in Dimension:
        report.dimension_stats[dim] = DimensionStat()

    mapped_sources: set[str] = set()

    for spec in schema.fields:
        found = spec.source in frame.columns
        result = FieldResult(name=spec.name, source=spec.source, found=found)
        report.fields.append(result)

        if not found:
            severity = Severity.ERROR if spec.required else Severity.WARNING
            report.stat(Dimension.STRUCTURE).add(1, 1)
            _add(report, result, Issue(
                dimension=Dimension.STRUCTURE,
                severity=severity,
                column=spec.source,
                title=f"Target field '{spec.name}' has no source column '{spec.source}'",
                detail="Map it to an existing column, or confirm the target allows it to arrive empty.",
                count=1,
            ))
            continue

        mapped_sources.add(spec.source)
        series = frame[spec.source]
        present = _present(series)
        _check_required(report, result, spec, rows, len(present))
        _check_type(report, result, spec, present)
        _check_length(report, result, spec, present)
        _check_allowed(report, result, spec, present)
        _check_pattern(report, result, spec, present)
        _check_range(report, result, spec, present)
        _check_unique(report, result, spec, present)
        if spec.lookup:
            _check_lookup(report, result, spec, schema, present)

    report.extra_columns = [c for c in frame.columns if c not in mapped_sources]
    if report.extra_columns and schema.extra_columns != "ignore":
        severity = Severity.ERROR if schema.extra_columns == "error" else Severity.INFO
        report.issues.append(Issue(
            dimension=Dimension.STRUCTURE,
            severity=severity,
            title=f"{len(report.extra_columns)} source column(s) are not mapped to any target field",
            detail="They will be dropped by the load. Confirm that is intended.",
            count=len(report.extra_columns),
            samples=report.extra_columns[:_MAX_SAMPLES],
        ))

    return report


def validate_file(
    path: str | Path,
    schema: TargetSchema,
    *,
    sheet: str | None = None,
    version: str = "0.0.0",
) -> ValidationReport:
    return validate_table(load(path, sheet=sheet), schema, version=version)


def _add(report: ValidationReport, result: FieldResult, issue: Issue) -> None:
    report.issues.append(issue)
    if issue.severity is Severity.ERROR:
        result.errors += 1
    elif issue.severity is Severity.WARNING:
        result.warnings += 1


def _check_required(report, result, spec, rows, present_count) -> None:
    if not spec.required:
        return
    report.stat(Dimension.COMPLETENESS).add(rows - present_count, rows)
    missing = rows - present_count
    if missing:
        _add(report, result, Issue(
            dimension=Dimension.COMPLETENESS,
            severity=Severity.ERROR,
            column=spec.source,
            title=f"Required field '{spec.name}' has {missing} blank value(s)",
            detail="The target rejects records without this field.",
            count=missing,
        ))


def _check_type(report, result, spec, present) -> None:
    if spec.type == "text":
        return
    test = _TYPE_TESTS[spec.type]
    bad = [v for v in present if not test(v)]
    report.stat(Dimension.VALIDITY).add(len(bad), len(present))
    if bad:
        _add(report, result, Issue(
            dimension=Dimension.VALIDITY,
            severity=Severity.ERROR,
            column=spec.source,
            title=f"'{spec.name}' expects {spec.type}; {len(bad)} value(s) do not parse",
            detail=f"The target will reject these as invalid {spec.type} values.",
            count=len(bad),
            samples=bad[:_MAX_SAMPLES],
        ))


def _check_length(report, result, spec, present) -> None:
    if spec.max_length is None and spec.min_length is None:
        return
    too_long = [v for v in present if spec.max_length is not None and len(v) > spec.max_length]
    too_short = [v for v in present if spec.min_length is not None and len(v) < spec.min_length]
    report.stat(Dimension.CONFORMITY).add(len(too_long) + len(too_short), len(present))
    if too_long:
        _add(report, result, Issue(
            dimension=Dimension.CONFORMITY,
            severity=Severity.ERROR,
            column=spec.source,
            title=f"'{spec.name}' exceeds max length {spec.max_length} in {len(too_long)} value(s)",
            detail="These values will be truncated or rejected by the target.",
            count=len(too_long),
            samples=too_long[:_MAX_SAMPLES],
        ))
    if too_short:
        _add(report, result, Issue(
            dimension=Dimension.CONFORMITY,
            severity=Severity.WARNING,
            column=spec.source,
            title=f"'{spec.name}' is under min length {spec.min_length} in {len(too_short)} value(s)",
            detail="Check whether these are truncated or partial entries.",
            count=len(too_short),
            samples=too_short[:_MAX_SAMPLES],
        ))


def _check_allowed(report, result, spec, present) -> None:
    if not spec.allowed:
        return
    allowed = set(spec.allowed)
    bad = sorted({v for v in present if v not in allowed})
    affected = sum(1 for v in present if v not in allowed)
    report.stat(Dimension.VALIDITY).add(affected, len(present))
    if bad:
        _add(report, result, Issue(
            dimension=Dimension.VALIDITY,
            severity=Severity.ERROR,
            column=spec.source,
            title=f"'{spec.name}' has {affected} value(s) outside the allowed list",
            detail=f"Allowed: {', '.join(spec.allowed)}.",
            count=affected,
            samples=bad[:_MAX_SAMPLES],
        ))


def _check_pattern(report, result, spec, present) -> None:
    if not spec.pattern:
        return
    try:
        regex = re.compile(spec.pattern)
    except re.error as exc:
        raise ValueError(f"Field '{spec.name}': invalid pattern: {exc}") from exc
    bad = [v for v in present if not regex.fullmatch(v)]
    report.stat(Dimension.CONFORMITY).add(len(bad), len(present))
    if bad:
        _add(report, result, Issue(
            dimension=Dimension.CONFORMITY,
            severity=Severity.ERROR,
            column=spec.source,
            title=f"'{spec.name}' fails its pattern in {len(bad)} value(s)",
            detail=f"Pattern: {spec.pattern}",
            count=len(bad),
            samples=bad[:_MAX_SAMPLES],
        ))


def _check_range(report, result, spec, present) -> None:
    if spec.min is None and spec.max is None:
        return
    out: list[str] = []
    numeric = 0
    for v in present:
        try:
            num = float(types.clean_number(v))
        except ValueError:
            continue
        numeric += 1
        if (spec.min is not None and num < spec.min) or (spec.max is not None and num > spec.max):
            out.append(v)
    report.stat(Dimension.VALIDITY).add(len(out), numeric or len(present))
    if out:
        bounds = []
        if spec.min is not None:
            bounds.append(f"min {spec.min:g}")
        if spec.max is not None:
            bounds.append(f"max {spec.max:g}")
        _add(report, result, Issue(
            dimension=Dimension.VALIDITY,
            severity=Severity.ERROR,
            column=spec.source,
            title=f"'{spec.name}' is out of range ({', '.join(bounds)}) in {len(out)} value(s)",
            detail="The target's business rules reject values outside this range.",
            count=len(out),
            samples=out[:_MAX_SAMPLES],
        ))


def _check_unique(report, result, spec, present) -> None:
    if not spec.unique:
        return
    duplicates = len(present) - len(set(present))
    report.stat(Dimension.UNIQUENESS).add(duplicates, len(present))
    if duplicates:
        seen: dict[str, int] = {}
        for v in present:
            seen[v] = seen.get(v, 0) + 1
        dupes = sorted(v for v, c in seen.items() if c > 1)
        _add(report, result, Issue(
            dimension=Dimension.UNIQUENESS,
            severity=Severity.ERROR,
            column=spec.source,
            title=f"'{spec.name}' must be unique; {duplicates} duplicate value(s) found",
            detail="The target will reject or overwrite records that reuse a key.",
            count=duplicates,
            samples=dupes[:_MAX_SAMPLES],
        ))


def _check_lookup(report, result, spec, schema, present) -> None:
    valid = _load_lookup_values(spec, schema)
    orphans = sorted({v for v in present if v not in valid})
    affected = sum(1 for v in present if v not in valid)
    report.stat(Dimension.INTEGRITY).add(affected, len(present))
    if orphans:
        _add(report, result, Issue(
            dimension=Dimension.INTEGRITY,
            severity=Severity.ERROR,
            column=spec.source,
            title=f"'{spec.name}' has {affected} value(s) with no match in {spec.lookup.file}",
            detail=f"Every value must exist in {spec.lookup.file} [{spec.lookup.column}] or the load creates orphans.",
            count=affected,
            samples=orphans[:_MAX_SAMPLES],
        ))
