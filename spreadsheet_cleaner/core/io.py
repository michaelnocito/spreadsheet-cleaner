"""Robust ingest for messy CSV / Excel files.

Everything is read as strings and blanks are preserved as empty strings, so
the profiler sees the file exactly as it is - nothing is silently coerced or
dropped. Handles encoding and delimiter sniffing for CSV, sheet selection for
Excel, the OneDrive placeholder trap, and leading/trailing/interior blank rows.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# Values that read as "present" but almost always mean missing.
PLACEHOLDER_NULLS = {"na", "n/a", "null", "none", "nil", "-", "--", "?", "."}

_ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")


class LoadError(Exception):
    """Raised with a human-readable message when a file cannot be loaded."""


@dataclass
class LoadedTable:
    frame: pd.DataFrame
    source: Path
    sheet: str | None
    sheet_names: list[str] = field(default_factory=list)
    blank_rows_ignored: int = 0

    @property
    def rows(self) -> int:
        return int(self.frame.shape[0])

    @property
    def cols(self) -> int:
        return int(self.frame.shape[1])


def is_missing(value: object) -> bool:
    """A cell is missing if it is null/NaN or blank/whitespace-only."""
    if value is None:
        return True
    text = str(value)
    return text.strip() == "" or text.lower() == "nan"


def is_placeholder_null(value: object) -> bool:
    """A present value that is a disguised null (``N/A``, ``-`` ...)."""
    if is_missing(value):
        return False
    return str(value).strip().casefold() in PLACEHOLDER_NULLS


def _read_csv(path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in _ENCODINGS:
        try:
            return pd.read_csv(
                path,
                dtype=str,
                sep=None,  # sniff the delimiter
                engine="python",
                keep_default_na=False,
                na_filter=False,
                encoding=encoding,
                skip_blank_lines=False,
            )
        except (UnicodeDecodeError, UnicodeError) as exc:
            last_error = exc
            continue
        except pd.errors.EmptyDataError as exc:
            raise LoadError(f"The file appears to be empty: {path.name}") from exc
    raise LoadError(
        f"Could not decode {path.name}. Tried: {', '.join(_ENCODINGS)}."
    ) from last_error


def _read_excel(path: Path, sheet: str | None) -> tuple[pd.DataFrame, list[str], str]:
    try:
        book = pd.ExcelFile(path, engine="openpyxl")
    except zipfile.BadZipFile as exc:
        raise LoadError(
            f"Could not open {path.name}.\n\n"
            "This usually means the file lives in OneDrive but has not fully "
            "downloaded yet. In File Explorer, right-click it and choose "
            "'Always keep on this device', wait for the green check, then try "
            "again - or move the project outside OneDrive."
        ) from exc

    sheet_names = list(book.sheet_names)
    target = sheet if sheet is not None else sheet_names[0]
    if target not in sheet_names:
        raise LoadError(
            f"Sheet '{target}' not found. Available sheets: "
            f"{', '.join(sheet_names)}."
        )
    frame = book.parse(
        sheet_name=target,
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )
    return frame, sheet_names, target


def _drop_blank_rows(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Drop rows whose every cell is missing; return (frame, dropped_count)."""
    if frame.empty:
        return frame, 0
    keep_mask = ~frame.map(is_missing).all(axis=1)
    dropped = int((~keep_mask).sum())
    cleaned = frame[keep_mask].reset_index(drop=True)
    return cleaned, dropped


def _normalize(frame: pd.DataFrame) -> pd.DataFrame:
    """Force every cell to a plain string ('' for missing) and rename blanks."""
    frame = frame.map(lambda v: "" if is_missing(v) else str(v))
    frame.columns = [
        str(c).strip() if str(c).strip() and not str(c).startswith("Unnamed:")
        else f"(unnamed column {i + 1})"
        for i, c in enumerate(frame.columns)
    ]
    return frame


def load(path: str | Path, sheet: str | None = None) -> LoadedTable:
    """Load a CSV or Excel file into a normalized, all-string table."""
    path = Path(path)
    if not path.exists():
        raise LoadError(f"File not found: {path}")

    suffix = path.suffix.lower()
    sheet_names: list[str] = []
    used_sheet: str | None = None

    if suffix == ".csv":
        frame = _read_csv(path)
    elif suffix in (".xlsx", ".xlsm", ".xls"):
        frame, sheet_names, used_sheet = _read_excel(path, sheet)
    else:
        raise LoadError(
            f"Unsupported file type '{suffix}'. Use a .csv or .xlsx file."
        )

    frame = _normalize(frame)
    frame, blank_rows = _drop_blank_rows(frame)
    return LoadedTable(
        frame=frame,
        source=path,
        sheet=used_sheet,
        sheet_names=sheet_names,
        blank_rows_ignored=blank_rows,
    )
