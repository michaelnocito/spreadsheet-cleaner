"""Core engine: models, ingest, and type inference."""

from spreadsheet_cleaner.core.io import LoadedTable, LoadError, load
from spreadsheet_cleaner.core.models import (
    ColumnProfile,
    Dimension,
    Issue,
    QualityReport,
    Severity,
)

__all__ = [
    "LoadedTable",
    "LoadError",
    "load",
    "ColumnProfile",
    "Dimension",
    "Issue",
    "QualityReport",
    "Severity",
]
