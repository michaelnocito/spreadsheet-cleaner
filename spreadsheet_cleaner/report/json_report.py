"""Render a QualityReport as machine-readable JSON."""

from __future__ import annotations

import json

from spreadsheet_cleaner.core.models import DIMENSION_ORDER, QualityReport


def to_dict(report: QualityReport) -> dict:
    return {
        "tool": "spreadsheet-cleaner",
        "tool_version": report.tool_version,
        "source": report.source,
        "sheet": report.sheet,
        "generated_at": report.generated_at.isoformat(),
        "rows": report.rows,
        "cols": report.cols,
        "blank_rows_ignored": report.blank_rows_ignored,
        "score": report.score,
        "grade": report.grade,
        "error_count": report.error_count,
        "warning_count": report.warning_count,
        "dimensions": [
            {
                "dimension": dim.value,
                "label": dim.label,
                "score": report.stat(dim).score,
                "affected": report.stat(dim).affected,
                "applicable": report.stat(dim).applicable,
            }
            for dim in DIMENSION_ORDER
        ],
        "columns": [
            {
                "name": c.name,
                "inferred_type": c.inferred_type,
                "type_confidence": c.type_confidence,
                "total": c.total,
                "present": c.present,
                "missing": c.missing,
                "distinct": c.distinct,
                "fill_rate": c.fill_rate,
                "distinct_rate": c.distinct_rate,
                "is_unique": c.is_unique,
                "min_value": c.min_value,
                "max_value": c.max_value,
                "min_len": c.min_len,
                "max_len": c.max_len,
                "top_values": [{"value": v, "count": n} for v, n in c.top_values],
                "formats": [{"format": f, "count": n} for f, n in c.formats],
            }
            for c in report.columns
        ],
        "issues": [
            {
                "dimension": i.dimension.value,
                "severity": i.severity.value,
                "column": i.column,
                "title": i.title,
                "detail": i.detail,
                "count": i.count,
                "samples": i.samples,
            }
            for i in report.sorted_issues()
        ],
    }


def to_json(report: QualityReport, *, indent: int = 2) -> str:
    return json.dumps(to_dict(report), indent=indent, ensure_ascii=False)
