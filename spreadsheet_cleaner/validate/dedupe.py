"""Near-duplicate detection: rows that are almost, but not exactly, the same.

Exact duplicates are cheap (the profiler and dedupe_rows handle them). Near
duplicates - the same record re-entered with a typo, different casing, or a
reformatted date - are what silently double-count a customer after a load.

Pure stdlib (difflib), fully offline, deterministic. Comparison is O(n^2) in
candidate-bucket size, so rows are first bucketed by a cheap signature to keep
real-world files fast, and a hard row cap protects very large files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

import pandas as pd

DEFAULT_THRESHOLD = 0.90
MAX_ROWS = 20_000


@dataclass
class NearDuplicatePair:
    row_a: int          # 1-based data row numbers (excluding header)
    row_b: int
    similarity: float
    preview_a: str
    preview_b: str


@dataclass
class DedupeResult:
    pairs: list[NearDuplicatePair] = field(default_factory=list)
    rows_checked: int = 0
    skipped: bool = False
    skip_reason: str = ""


def _normalize_cell(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _row_text(row: tuple) -> str:
    return " | ".join(_normalize_cell(str(v)) for v in row)


def _signature(text: str) -> str:
    """Cheap blocking key: the sorted first letters of each token."""
    tokens = sorted({t[0] for t in text.split() if t})
    return "".join(tokens)


def find_near_duplicates(
    frame: pd.DataFrame,
    *,
    threshold: float = DEFAULT_THRESHOLD,
    key_columns: list[str] | None = None,
) -> DedupeResult:
    """Find pairs of rows whose normalized text similarity is >= threshold.

    ``key_columns`` restricts the comparison to the columns that identify a
    record (say name + email); by default every column is compared.
    """
    result = DedupeResult(rows_checked=len(frame))
    if len(frame) > MAX_ROWS:
        result.skipped = True
        result.skip_reason = (
            f"Near-duplicate scan skipped: {len(frame):,} rows exceeds the "
            f"{MAX_ROWS:,}-row limit. Run it on a filtered subset."
        )
        return result

    columns = key_columns if key_columns else list(frame.columns)
    missing = [c for c in (key_columns or []) if c not in frame.columns]
    if missing:
        raise ValueError(f"Near-duplicate key column(s) not found: {', '.join(missing)}.")

    texts: list[str] = [_row_text(row) for row in frame[columns].itertuples(index=False)]
    previews: list[str] = [
        " | ".join(str(v) for v in row)[:120]
        for row in frame[columns].itertuples(index=False)
    ]

    buckets: dict[str, list[int]] = {}
    for idx, text in enumerate(texts):
        buckets.setdefault(_signature(text), []).append(idx)

    seen_exact: set[tuple[int, int]] = set()
    for indices in buckets.values():
        for pos, a in enumerate(indices):
            for b in indices[pos + 1:]:
                if texts[a] == texts[b]:
                    # Exact (after normalization) - report once, similarity 1.0.
                    if (a, b) in seen_exact:
                        continue
                    seen_exact.add((a, b))
                    ratio = 1.0
                else:
                    ratio = SequenceMatcher(None, texts[a], texts[b]).ratio()
                if ratio >= threshold:
                    result.pairs.append(NearDuplicatePair(
                        row_a=a + 1,
                        row_b=b + 1,
                        similarity=round(ratio, 3),
                        preview_a=previews[a],
                        preview_b=previews[b],
                    ))

    result.pairs.sort(key=lambda p: (-p.similarity, p.row_a))
    return result
