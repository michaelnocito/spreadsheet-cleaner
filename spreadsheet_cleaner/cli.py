"""Command-line interface (Typer).

    spreadsheet-cleaner profile data.xlsx
    spreadsheet-cleaner profile data.csv --format html,json --out reports --open
"""

from __future__ import annotations

import sys
import webbrowser
from pathlib import Path

import typer

# Windows consoles often default to cp1252; keep output from ever crashing.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

from spreadsheet_cleaner import __version__, profile as _profile
from spreadsheet_cleaner.clean import (
    clean_table as _clean_table,
    default_recipe,
    load_recipe,
    save_recipe as _save_recipe,
    write_clean,
)
from spreadsheet_cleaner.core.io import LoadError, LoadedTable, load as _load
from spreadsheet_cleaner.core.models import DIMENSION_ORDER, Severity
from spreadsheet_cleaner.profiling import profile_table
from spreadsheet_cleaner.report import FORMATS, write
from spreadsheet_cleaner.report.clean_report import to_html as _clean_to_html

app = typer.Typer(
    add_completion=False,
    help="Offline pre-migration data quality. Profile a messy spreadsheet and "
    "export a defensible quality report. Nothing leaves your machine.",
)

_SEV_MARK = {Severity.ERROR: "[error]", Severity.WARNING: "[warn] ", Severity.INFO: "[info] "}


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"spreadsheet-cleaner {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V", callback=_version_callback, is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """Spreadsheet Cleaner."""


@app.command()
def profile(
    file: Path = typer.Argument(..., help="Path to the CSV or Excel file."),
    sheet: str = typer.Option(None, "--sheet", "-s", help="Excel sheet name (default: first)."),
    fmt: str = typer.Option(
        "html", "--format", "-f",
        help=f"Comma-separated report formats: {', '.join(FORMATS)}.",
    ),
    out: Path = typer.Option(
        Path("."), "--out", "-o", help="Directory to write the report(s) into."
    ),
    open_report: bool = typer.Option(
        False, "--open", help="Open the HTML report in your browser when done."
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress the terminal summary."),
) -> None:
    """Profile a spreadsheet and write a data-quality report."""
    try:
        report = _profile(file, sheet=sheet)
    except LoadError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    formats = tuple(f.strip().lower() for f in fmt.split(",") if f.strip())
    unknown = [f for f in formats if f not in FORMATS]
    if unknown:
        typer.secho(
            f"Unknown format(s): {', '.join(unknown)}. Choose from {', '.join(FORMATS)}.",
            fg=typer.colors.RED, err=True,
        )
        raise typer.Exit(code=2)

    written = write(report, out, formats=formats)

    if not quiet:
        _print_summary(report)
        typer.echo("")
        for path in written:
            typer.secho(f"  wrote {path}", fg=typer.colors.CYAN)

    if open_report:
        html = next((p for p in written if p.suffix == ".html"), None)
        if html:
            webbrowser.open(html.resolve().as_uri())

    # Non-zero exit if there are hard errors, so CI can gate on it.
    raise typer.Exit(code=1 if report.error_count else 0)


@app.command()
def clean(
    file: Path = typer.Argument(..., help="Path to the CSV or Excel file."),
    recipe: Path = typer.Option(
        None, "--recipe", "-r",
        help="Cleaning recipe (.yml or .json). Default: a smart recipe from the profile.",
    ),
    sheet: str = typer.Option(None, "--sheet", "-s", help="Excel sheet name (default: first)."),
    out: Path = typer.Option(
        Path("."), "--out", "-o", help="Directory for the cleaned file and report."
    ),
    data_format: str = typer.Option(
        None, "--data-format", help="Cleaned output type: csv or xlsx. Default: same as input."
    ),
    save_recipe: Path = typer.Option(
        None, "--save-recipe", help="Write the recipe used to this path so you can reuse it."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would change without writing anything."
    ),
    open_report: bool = typer.Option(False, "--open", help="Open the cleaning report when done."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress the terminal summary."),
) -> None:
    """Clean a spreadsheet with a recipe (or a smart default) and log every change."""
    try:
        table = _load(file, sheet=sheet)
    except LoadError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    before = profile_table(table, version=__version__)
    try:
        the_recipe = load_recipe(recipe) if recipe else default_recipe(before)
        result = _clean_table(table, recipe=the_recipe)
    except (ValueError, RuntimeError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    after_table = LoadedTable(frame=result.frame, source=table.source, sheet=table.sheet)
    after = profile_table(after_table, version=__version__)

    written: list[Path] = []
    if save_recipe:
        _save_recipe(result.recipe, save_recipe)
        written.append(save_recipe)

    if not dry_run:
        src_ext = file.suffix.lower()
        ext = "." + data_format.lower().lstrip(".") if data_format else (
            src_ext if src_ext in (".csv", ".xlsx") else ".csv"
        )
        try:
            cleaned = write_clean(result, Path(out) / f"{file.stem}_cleaned{ext}")
        except ValueError as exc:
            typer.secho(str(exc), fg=typer.colors.RED, err=True)
            raise typer.Exit(code=2)
        written.append(cleaned)
        report_path = Path(out) / f"{file.stem}_cleaning_report.html"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(_clean_to_html(result, before, after), encoding="utf-8")
        written.append(report_path)

    if not quiet:
        _print_clean_summary(result, before, after, dry_run)
        for path in written:
            typer.secho(f"  wrote {path}", fg=typer.colors.CYAN)

    if open_report and not dry_run:
        html = next((p for p in written if p.suffix == ".html"), None)
        if html:
            webbrowser.open(html.resolve().as_uri())


def _print_clean_summary(result, before, after, dry_run: bool) -> None:
    log = result.changelog
    tag = "  (dry run, nothing written)" if dry_run else ""
    typer.echo("")
    typer.secho(f"  {Path(result.source).name}  -  cleaned{tag}", bold=True)
    typer.echo(f"  grade {before.grade} ({before.score:.0f}) -> {after.grade} ({after.score:.0f})")
    typer.echo(
        f"  {log.total_changes} cell change(s); "
        f"{log.rows_removed} row(s), {log.cols_removed} column(s) removed"
    )
    typer.echo("")
    for record in log.records:
        where = record.column or "table"
        typer.echo(f"    {record.step:<20} {where:<18} {record.changed:>6}")
    typer.echo("")


def _print_summary(report) -> None:
    grade_color = (
        typer.colors.GREEN if report.score >= 85
        else typer.colors.YELLOW if report.score >= 70
        else typer.colors.RED
    )
    typer.echo("")
    typer.secho(
        f"  {Path(report.source).name}  -  grade {report.grade} ({report.score:.0f}/100)",
        fg=grade_color, bold=True,
    )
    typer.echo(f"  {report.rows:,} rows x {report.cols} columns")
    typer.echo(f"  {report.error_count} error(s), {report.warning_count} warning(s)")
    typer.echo("")
    for dim in DIMENSION_ORDER:
        stat = report.stat(dim)
        bar_len = round(stat.score / 5)
        bar = "#" * bar_len + "-" * (20 - bar_len)
        typer.echo(f"    {dim.label:<13} {bar} {stat.score:>5.0f}")


if __name__ == "__main__":
    app()
