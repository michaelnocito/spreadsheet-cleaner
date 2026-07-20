"""Data-quality checks.

Each check inspects the loaded table and emits ``Issue`` records tagged with a
``Dimension``, while accumulating the affected/applicable counts that drive the
per-dimension scorecard. Nothing here mutates the data; this is read-only
assessment.
"""

from __future__ import annotations

import re

import pandas as pd

from spreadsheet_cleaner.core import types
from spreadsheet_cleaner.core.io import LoadedTable, is_missing, is_placeholder_null
from spreadsheet_cleaner.core.models import (
    ColumnProfile,
    Dimension,
    DimensionStat,
    Issue,
    Severity,
)

SPECIFIC_TYPES = {"integer", "decimal", "date", "email", "phone", "boolean"}
_KEY_HINTS = {"id", "code", "key", "email", "uuid", "guid", "pk", "account", "acct", "ssn"}
_MAX_SAMPLES = 6
_CONSISTENCY_MAX_DISTINCT = 60


def _looks_like_key(name: str) -> bool:
    lname = name.lower()
    tokens = re.findall(r"[a-z]+", lname)
    return any(t in _KEY_HINTS for t in tokens) or lname.replace(" ", "").endswith("id")


def _raw_present(series: pd.Series) -> list[str]:
    return [str(v) for v in series if not is_missing(v)]


def _has_stray_whitespace(value: str) -> bool:
    return value != value.strip() or "  " in value


def run_checks(
    table: LoadedTable, profiles: list[ColumnProfile]
) -> tuple[list[Issue], dict[Dimension, DimensionStat]]:
    frame = table.frame
    rows, cols = table.rows, table.cols
    issues: list[Issue] = []
    stats: dict[Dimension, DimensionStat] = {d: DimensionStat() for d in Dimension}

    _check_completeness(frame, profiles, rows, cols, issues, stats)

    for profile in profiles:
        series = frame[profile.name]
        raw = _raw_present(series)
        stripped = [v.strip() for v in raw]
        inference = types.infer(stripped)
        _check_validity(profile, inference, stripped, issues, stats)
        _check_conformity(profile, inference, raw, stripped, issues, stats)
        _check_consistency(profile, stripped, issues, stats)
        _check_key_uniqueness(profile, stripped, issues, stats)

    _check_row_uniqueness(frame, rows, issues, stats)
    _check_structure(table, profiles, rows, cols, issues, stats)

    return issues, stats


def _check_completeness(frame, profiles, rows, cols, issues, stats):
    total_cells = rows * cols
    missing_cells = sum(p.missing for p in profiles)
    stats[Dimension.COMPLETENESS].add(missing_cells, total_cells)

    for profile in profiles:
        # Fully empty columns are reported by the structure check instead.
        if profile.missing <= 0 or profile.total == 0 or profile.present == 0:
            continue
        rate = profile.missing / profile.total
        is_key = _looks_like_key(profile.name)
        severity = Severity.ERROR if is_key else Severity.WARNING
        issues.append(
            Issue(
                dimension=Dimension.COMPLETENESS,
                severity=severity,
                column=profile.name,
                title=f"{profile.missing} missing value(s) in '{profile.name}'",
                detail=(
                    f"{rate:.0%} of this column is blank."
                    + (" It looks like a required identifier." if is_key else "")
                ),
                count=profile.missing,
            )
        )

    placeholder = 0
    samples: list[str] = []
    for name in frame.columns:
        for v in frame[name]:
            if is_placeholder_null(v):
                placeholder += 1
                if str(v).strip() not in samples and len(samples) < _MAX_SAMPLES:
                    samples.append(str(v).strip())
    if placeholder:
        stats[Dimension.COMPLETENESS].affected += placeholder
        issues.append(
            Issue(
                dimension=Dimension.COMPLETENESS,
                severity=Severity.WARNING,
                title=f"{placeholder} cell(s) hold placeholder text that likely means missing",
                detail="Values like these read as present but are almost certainly blanks.",
                count=placeholder,
                samples=samples,
            )
        )


def _check_validity(profile, inference, stripped, issues, stats):
    if inference.inferred_type not in SPECIFIC_TYPES:
        return
    stats[Dimension.VALIDITY].applicable += len(stripped)
    if not inference.violations:
        return
    affected = len(inference.violations)
    stats[Dimension.VALIDITY].affected += affected
    issues.append(
        Issue(
            dimension=Dimension.VALIDITY,
            severity=Severity.ERROR if profile.type_confidence >= 0.8 else Severity.WARNING,
            column=profile.name,
            title=f"{affected} value(s) in '{profile.name}' are not a valid {inference.inferred_type}",
            detail=(
                f"The column reads as {inference.inferred_type} "
                f"({profile.type_confidence:.0%} of values), but these do not fit."
            ),
            count=affected,
            samples=inference.violations[:_MAX_SAMPLES],
        )
    )


def _check_conformity(profile, inference, raw, stripped, issues, stats):
    stats[Dimension.CONFORMITY].applicable += len(stripped)
    affected = 0

    if inference.inferred_type == "date" and len(inference.formats) > 1:
        drifted = sum(count for _, count in inference.formats[1:])
        affected += drifted
        breakdown = ", ".join(f"{label} ({count})" for label, count in inference.formats)
        issues.append(
            Issue(
                dimension=Dimension.CONFORMITY,
                severity=Severity.WARNING,
                column=profile.name,
                title=f"'{profile.name}' mixes {len(inference.formats)} date formats",
                detail=f"Formats found: {breakdown}. Pick one target format to standardize on.",
                count=drifted,
                samples=[v for v in stripped if types.date_format_of(v)][:_MAX_SAMPLES],
            )
        )

    whitespace = [v for v in raw if _has_stray_whitespace(v)]
    if whitespace:
        affected += len(whitespace)
        issues.append(
            Issue(
                dimension=Dimension.CONFORMITY,
                severity=Severity.WARNING,
                column=profile.name,
                title=f"{len(whitespace)} value(s) in '{profile.name}' have stray whitespace",
                detail="Leading, trailing, or doubled spaces break joins, filters, and lookups.",
                count=len(whitespace),
                samples=[repr(v) for v in whitespace[:_MAX_SAMPLES]],
            )
        )

    stats[Dimension.CONFORMITY].affected += min(affected, len(stripped))


def _check_consistency(profile, stripped, issues, stats):
    if not stripped or profile.distinct > _CONSISTENCY_MAX_DISTINCT:
        return
    if profile.inferred_type in ("integer", "decimal", "date"):
        return
    stats[Dimension.CONSISTENCY].applicable += len(stripped)

    groups: dict[str, dict[str, int]] = {}
    for v in stripped:
        groups.setdefault(v.casefold(), {})
        groups[v.casefold()][v] = groups[v.casefold()].get(v, 0) + 1

    affected = 0
    examples: list[str] = []
    for variants in groups.values():
        if len(variants) > 1:
            affected += sum(variants.values())
            if len(examples) < _MAX_SAMPLES:
                examples.append(" / ".join(sorted(variants)))
    if affected:
        stats[Dimension.CONSISTENCY].affected += affected
        issues.append(
            Issue(
                dimension=Dimension.CONSISTENCY,
                severity=Severity.WARNING,
                column=profile.name,
                title=f"'{profile.name}' spells the same value more than one way",
                detail="A computer treats these as different categories, so counts and pivots split.",
                count=affected,
                samples=examples,
            )
        )


def _check_key_uniqueness(profile, stripped, issues, stats):
    if not stripped or not _looks_like_key(profile.name):
        return
    duplicates = len(stripped) - len(set(stripped))
    stats[Dimension.UNIQUENESS].add(duplicates, len(stripped))
    if duplicates <= 0:
        return
    seen: dict[str, int] = {}
    for v in stripped:
        seen[v] = seen.get(v, 0) + 1
    dupes = [v for v, c in seen.items() if c > 1]
    issues.append(
        Issue(
            dimension=Dimension.UNIQUENESS,
            severity=Severity.ERROR,
            column=profile.name,
            title=f"'{profile.name}' looks like an identifier but has {duplicates} duplicate value(s)",
            detail="A primary key must be unique before it can load into the target.",
            count=duplicates,
            samples=dupes[:_MAX_SAMPLES],
        )
    )


def _check_row_uniqueness(frame, rows, issues, stats):
    if rows == 0:
        return
    dup_rows = int(frame.duplicated(keep="first").sum())
    stats[Dimension.UNIQUENESS].add(dup_rows, rows)
    if dup_rows:
        issues.append(
            Issue(
                dimension=Dimension.UNIQUENESS,
                severity=Severity.WARNING,
                title=f"{dup_rows} fully duplicate row(s)",
                detail="These rows repeat another row exactly and should be reviewed for merge.",
                count=dup_rows,
            )
        )


def _check_structure(table, profiles, rows, cols, issues, stats):
    blank_cols = [p.name for p in profiles if p.present == 0]
    unnamed = [p.name for p in profiles if p.name.startswith("(unnamed column")]
    stat = stats[Dimension.STRUCTURE]
    stat.applicable += rows + cols + table.blank_rows_ignored
    stat.affected += table.blank_rows_ignored + len(blank_cols)

    if table.blank_rows_ignored:
        issues.append(
            Issue(
                dimension=Dimension.STRUCTURE,
                severity=Severity.INFO,
                title=f"{table.blank_rows_ignored} fully blank row(s) ignored",
                detail="Blank rows were skipped so they do not distort the profile.",
                count=table.blank_rows_ignored,
            )
        )
    for name in blank_cols:
        issues.append(
            Issue(
                dimension=Dimension.STRUCTURE,
                severity=Severity.WARNING,
                column=name,
                title=f"Column '{name}' is completely empty",
                detail="Drop it, or confirm it is expected to arrive empty.",
                count=rows,
            )
        )
    if unnamed:
        issues.append(
            Issue(
                dimension=Dimension.STRUCTURE,
                severity=Severity.INFO,
                title=f"{len(unnamed)} column(s) have no header",
                detail="Unlabeled columns are hard to map to a target field.",
                count=len(unnamed),
                samples=unnamed[:_MAX_SAMPLES],
            )
        )
