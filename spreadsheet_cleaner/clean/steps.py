"""Cleaning steps: the individual, deterministic transforms.

Every step takes the all-string frame plus the columns it applies to, returns
the modified frame and a list of ``ChangeRecord``. Empty cells (missing) are
left untouched unless the step is specifically about them. No randomness, no
network, no mutation of the caller's original frame beyond the returned copy.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Callable

import pandas as pd

from spreadsheet_cleaner.clean.changelog import ChangeRecord
from spreadsheet_cleaner.clean.recipe import ALL
from spreadsheet_cleaner.core import types

_MAX_SAMPLES = 5

# A step: (frame, columns, params) -> (frame, [ChangeRecord])
StepFn = Callable[[pd.DataFrame, list[str], dict], "tuple[pd.DataFrame, list[ChangeRecord]]"]

STEP_REGISTRY: dict[str, StepFn] = {}


def step(name: str) -> Callable[[StepFn], StepFn]:
    def register(fn: StepFn) -> StepFn:
        STEP_REGISTRY[name] = fn
        return fn
    return register


def resolve_columns(frame: pd.DataFrame, columns: list[str] | str) -> list[str]:
    if columns == ALL:
        return list(frame.columns)
    return [c for c in columns if c in frame.columns]


def _map_column(
    series: pd.Series, transform: Callable[[str], str]
) -> tuple[pd.Series, int, list[tuple[str, str]]]:
    """Apply transform to non-empty cells; return (new, changed, samples)."""
    new = series.map(lambda v: v if v == "" else transform(v))
    changed_mask = new != series
    changed = int(changed_mask.sum())
    samples = list(zip(series[changed_mask].tolist(), new[changed_mask].tolist()))[:_MAX_SAMPLES]
    return new, changed, samples


# ---- column steps ------------------------------------------------------------

@step("trim_whitespace")
def trim_whitespace(frame, columns, params):
    records: list[ChangeRecord] = []
    for col in columns:
        new, changed, samples = _map_column(frame[col], lambda v: re.sub(r"\s+", " ", v).strip())
        if changed:
            frame[col] = new
            records.append(ChangeRecord("trim_whitespace", col, changed,
                                        "Trimmed and collapsed whitespace.", samples))
    return frame, records


@step("normalize_case")
def normalize_case(frame, columns, params):
    mode = params.get("mode", "consistent")
    records: list[ChangeRecord] = []
    for col in columns:
        series = frame[col]
        if mode == "consistent":
            transform = _consistent_case_map(series)
            detail = "Standardized spelling/casing to the most common form."
        elif mode in ("upper", "lower", "title"):
            transform = {"upper": str.upper, "lower": str.lower, "title": str.title}[mode]
            detail = f"Set case to {mode}."
        else:
            raise ValueError(f"normalize_case: unknown mode '{mode}'.")
        new, changed, samples = _map_column(series, transform)
        if changed:
            frame[col] = new
            records.append(ChangeRecord("normalize_case", col, changed, detail, samples))
    return frame, records


def _consistent_case_map(series: pd.Series) -> Callable[[str], str]:
    counts = Counter(v for v in series if v != "")
    groups: dict[str, list[tuple[str, int]]] = {}
    for value, count in counts.items():
        groups.setdefault(value.casefold(), []).append((value, count))
    canonical: dict[str, str] = {}
    for variants in groups.values():
        best = sorted(variants, key=lambda vc: (-vc[1], vc[0]))[0][0]
        for value, _ in variants:
            canonical[value] = best
    return lambda v: canonical.get(v, v)


@step("normalize_dates")
def normalize_dates(frame, columns, params):
    fmt = params.get("format", "%Y-%m-%d")
    records: list[ChangeRecord] = []
    for col in columns:
        def transform(v: str) -> str:
            dt = types.parse_date(v)
            return dt.strftime(fmt) if dt else v

        new, changed, samples = _map_column(frame[col], transform)
        unparsed = sum(1 for v in frame[col] if v != "" and types.parse_date(v) is None)
        if changed or unparsed:
            frame[col] = new
            detail = f"Standardized dates to {fmt}."
            if unparsed:
                detail += f" {unparsed} value(s) could not be parsed and were left as-is."
            records.append(ChangeRecord("normalize_dates", col, changed, detail, samples))
    return frame, records


@step("normalize_numbers")
def normalize_numbers(frame, columns, params):
    records: list[ChangeRecord] = []
    for col in columns:
        def transform(v: str) -> str:
            return types.clean_number(v) if (types.is_integer(v) or types.is_decimal(v)) else v

        new, changed, samples = _map_column(frame[col], transform)
        if changed:
            frame[col] = new
            records.append(ChangeRecord("normalize_numbers", col, changed,
                                        "Stripped currency symbols and thousands separators.", samples))
    return frame, records


@step("map_values")
def map_values(frame, columns, params):
    mapping = params.get("map", {})
    records: list[ChangeRecord] = []
    if not mapping:
        return frame, records
    for col in columns:
        new, changed, samples = _map_column(frame[col], lambda v: mapping.get(v, v))
        if changed:
            frame[col] = new
            records.append(ChangeRecord("map_values", col, changed, "Applied value mapping.", samples))
    return frame, records


@step("fill_missing")
def fill_missing(frame, columns, params):
    value = str(params.get("value", ""))
    records: list[ChangeRecord] = []
    if value == "":
        return frame, records
    for col in columns:
        mask = frame[col] == ""
        changed = int(mask.sum())
        if changed:
            frame.loc[mask, col] = value
            records.append(ChangeRecord("fill_missing", col, changed,
                                        f"Filled blanks with '{value}'.", [("", value)]))
    return frame, records


# ---- table steps -------------------------------------------------------------

@step("dedupe_rows")
def dedupe_rows(frame, columns, params):
    before = len(frame)
    deduped = frame.drop_duplicates(keep="first").reset_index(drop=True)
    removed = before - len(deduped)
    records = []
    if removed:
        records.append(ChangeRecord("dedupe_rows", None, removed,
                                    f"Removed {removed} exact duplicate row(s), kept the first of each."))
    return deduped, records


@step("drop_empty_columns")
def drop_empty_columns(frame, columns, params):
    empties = [c for c in frame.columns if (frame[c] == "").all()]
    records = []
    if empties:
        frame = frame.drop(columns=empties)
        records.append(ChangeRecord("drop_empty_columns", None, len(empties),
                                    f"Dropped empty column(s): {', '.join(empties)}."))
    return frame, records
