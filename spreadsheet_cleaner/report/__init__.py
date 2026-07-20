"""Report renderers: turn a QualityReport into HTML, Markdown, or JSON."""

from __future__ import annotations

from pathlib import Path

from spreadsheet_cleaner.core.models import QualityReport
from spreadsheet_cleaner.report.html import to_html
from spreadsheet_cleaner.report.json_report import to_dict, to_json
from spreadsheet_cleaner.report.markdown import to_markdown

FORMATS: tuple[str, ...] = ("html", "md", "json")
_EXT = {"html": ".html", "md": ".md", "json": ".json"}


def render(report: QualityReport, fmt: str) -> str:
    if fmt == "html":
        return to_html(report)
    if fmt == "md":
        return to_markdown(report)
    if fmt == "json":
        return to_json(report)
    raise ValueError(f"Unknown report format '{fmt}'. Choose from: {', '.join(FORMATS)}.")


def write(
    report: QualityReport,
    out_dir: str | Path,
    formats: tuple[str, ...] = ("html",),
    stem: str | None = None,
) -> list[Path]:
    """Write the report in the requested formats; return the paths written."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = stem or (Path(report.source).stem + "_quality_report")
    written: list[Path] = []
    for fmt in formats:
        path = out_dir / f"{stem}{_EXT[fmt]}"
        path.write_text(render(report, fmt), encoding="utf-8")
        written.append(path)
    return written


__all__ = ["FORMATS", "render", "write", "to_html", "to_markdown", "to_json", "to_dict"]
