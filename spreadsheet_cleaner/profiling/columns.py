"""Per-column profiling: fill rate, cardinality, extremes, and inferred type."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from spreadsheet_cleaner.core import types
from spreadsheet_cleaner.core.io import is_missing
from spreadsheet_cleaner.core.models import ColumnProfile

_TOP_VALUES = 5
_SAMPLE_VALUES = 5


def present_values(series: pd.Series) -> list[str]:
    """Non-missing values of a column as stripped strings."""
    return [str(v).strip() for v in series if not is_missing(v)]


def _numeric_extremes(values: list[str]) -> tuple[str | None, str | None]:
    nums: list[tuple[float, str]] = []
    for v in values:
        try:
            nums.append((float(types._clean_number(v)), v))
        except ValueError:
            continue
    if not nums:
        return None, None
    return min(nums)[1], max(nums)[1]


def profile_column(name: str, series: pd.Series) -> ColumnProfile:
    total = int(series.shape[0])
    present = present_values(series)
    n_present = len(present)
    n_missing = total - n_present
    counts = Counter(present)
    distinct = len(counts)

    inference = types.infer(present)

    if inference.inferred_type in ("integer", "decimal"):
        min_value, max_value = _numeric_extremes(present)
    elif present:
        ordered = sorted(present)
        min_value, max_value = ordered[0], ordered[-1]
    else:
        min_value = max_value = None

    lengths = [len(v) for v in present]

    return ColumnProfile(
        name=name,
        inferred_type=inference.inferred_type,
        type_confidence=inference.confidence,
        total=total,
        present=n_present,
        missing=n_missing,
        distinct=distinct,
        fill_rate=round(n_present / total, 4) if total else 0.0,
        distinct_rate=round(distinct / n_present, 4) if n_present else 0.0,
        is_unique=(n_present == total and distinct == total and total > 0),
        top_values=counts.most_common(_TOP_VALUES),
        sample_values=present[:_SAMPLE_VALUES],
        min_value=min_value,
        max_value=max_value,
        min_len=min(lengths) if lengths else None,
        max_len=max(lengths) if lengths else None,
        formats=inference.formats,
    )
