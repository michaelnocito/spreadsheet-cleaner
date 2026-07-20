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
from spreadsheet_cleaner.report.validate_report import (
    to_html as _validate_to_html,
    to_markdown as _validate_to_md,
)
from spreadsheet_cleaner.validate import (
    find_near_duplicates,
    load_schema,
    reconcile as _reconcile,
    starter_schema_yaml,
    validate_table,
)

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


@app.command()
def validate(
    file: Path = typer.Argument(..., help="Path to the CSV or Excel file."),
    schema: Path = typer.Option(
        ..., "--schema", "-t", help="Target schema (.yml or .json). See init-schema."
    ),
    sheet: str = typer.Option(None, "--sheet", "-s", help="Excel sheet name (default: first)."),
    out: Path = typer.Option(Path("."), "--out", "-o", help="Directory for the report."),
    fmt: str = typer.Option("html", "--format", "-f", help="Report formats: html, md."),
    near_dupes: bool = typer.Option(
        True, "--near-dupes/--no-near-dupes",
        help="Also scan for near-duplicate rows.",
    ),
    threshold: float = typer.Option(
        0.90, "--threshold", help="Near-duplicate similarity threshold (0-1)."
    ),
    open_report: bool = typer.Option(False, "--open", help="Open the HTML report when done."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress the terminal summary."),
) -> None:
    """Validate a spreadsheet against a target schema: will it load?"""
    try:
        table = _load(file, sheet=sheet)
        target = load_schema(schema)
        report = validate_table(table, target, version=__version__)
        dedupe = find_near_duplicates(table.frame, threshold=threshold) if near_dupes else None
    except (LoadError, ValueError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    formats = tuple(f.strip().lower() for f in fmt.split(",") if f.strip())
    unknown = [f for f in formats if f not in ("html", "md")]
    if unknown:
        typer.secho(
            f"Unknown format(s): {', '.join(unknown)}. Choose from html, md.",
            fg=typer.colors.RED, err=True,
        )
        raise typer.Exit(code=2)

    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    stem = f"{file.stem}_validation_report"
    if "html" in formats:
        path = out / f"{stem}.html"
        path.write_text(_validate_to_html(report, dedupe), encoding="utf-8")
        written.append(path)
    if "md" in formats:
        path = out / f"{stem}.md"
        path.write_text(_validate_to_md(report, dedupe), encoding="utf-8")
        written.append(path)

    if not quiet:
        _print_validate_summary(report, dedupe)
        for path in written:
            typer.secho(f"  wrote {path}", fg=typer.colors.CYAN)

    if open_report:
        html = next((p for p in written if p.suffix == ".html"), None)
        if html:
            webbrowser.open(html.resolve().as_uri())

    raise typer.Exit(code=0 if report.passed else 1)


@app.command("init-schema")
def init_schema(
    file: Path = typer.Argument(..., help="Path to the CSV or Excel file to draft from."),
    sheet: str = typer.Option(None, "--sheet", "-s", help="Excel sheet name (default: first)."),
    out: Path = typer.Option(
        None, "--out", "-o", help="Schema path to write. Default: <file>_target.yml"
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing schema file."),
) -> None:
    """Draft a starter target schema from a file's profile, for you to edit."""
    try:
        report = _profile(file, sheet=sheet)
    except LoadError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)
    out = out or file.with_name(f"{file.stem}_target.yml")
    if out.exists() and not force:
        typer.secho(
            f"{out} already exists. Use --force to overwrite it.",
            fg=typer.colors.RED, err=True,
        )
        raise typer.Exit(code=2)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(starter_schema_yaml(report), encoding="utf-8")
    typer.secho(f"  wrote {out}", fg=typer.colors.CYAN)
    typer.echo(
        "  Edit it to match the TARGET system's contract, then run: "
        f"spreadsheet-cleaner validate {file.name} --schema {out.name}"
    )


@app.command()
def reconcile(
    source: Path = typer.Argument(..., help="The original source file."),
    cleaned: Path = typer.Argument(..., help="The cleaned / load-ready file."),
    key: str = typer.Option(None, "--key", "-k", help="Key column to compare in both files."),
    totals: str = typer.Option(
        None, "--totals", help="Comma-separated numeric columns for control totals."
    ),
    sheet: str = typer.Option(None, "--sheet", "-s", help="Sheet name for Excel inputs."),
) -> None:
    """Reconcile a cleaned file back against its source: counts, keys, totals."""
    try:
        src = _load(source, sheet=sheet)
        oth = _load(cleaned, sheet=sheet)
        total_columns = [c.strip() for c in totals.split(",") if c.strip()] if totals else None
        result = _reconcile(src, oth, key=key, total_columns=total_columns)
    except (LoadError, ValueError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    typer.echo("")
    typer.secho(f"  {source.name} vs {cleaned.name}", bold=True)
    diff = result.row_difference
    diff_note = "match" if diff == 0 else (f"{diff:+d} row(s)")
    typer.echo(f"  rows: {result.source_rows:,} -> {result.other_rows:,}  ({diff_note})")
    if key:
        if result.keys_match:
            typer.echo(f"  keys [{key}]: all present in both files")
        else:
            if result.keys_only_in_source:
                sample = ", ".join(result.keys_only_in_source[:6])
                typer.echo(
                    f"  keys only in source ({len(result.keys_only_in_source)}): {sample}"
                )
            if result.keys_only_in_other:
                sample = ", ".join(result.keys_only_in_other[:6])
                typer.echo(
                    f"  keys only in cleaned ({len(result.keys_only_in_other)}): {sample}"
                )
    for total in result.control_totals:
        mark = "match" if total.matches else f"off by {total.difference}"
        typer.echo(
            f"  total [{total.column}]: {total.source_total} -> {total.other_total}  ({mark})"
        )
    verdict = "RECONCILED" if result.clean_pass else "DIFFERENCES FOUND"
    color = typer.colors.GREEN if result.clean_pass else typer.colors.YELLOW
    typer.echo("")
    typer.secho(f"  {verdict}", fg=color, bold=True)
    typer.echo("")
    raise typer.Exit(code=0 if result.clean_pass else 1)


def _print_validate_summary(report, dedupe) -> None:
    color = typer.colors.GREEN if report.passed else typer.colors.RED
    verdict = "PASS" if report.passed else "FAIL"
    typer.echo("")
    typer.secho(
        f"  {Path(report.source).name} vs target '{report.target}'  -  {verdict} "
        f"({report.score:.0f}/100)",
        fg=color, bold=True,
    )
    typer.echo(f"  {report.rows:,} rows checked against {len(report.fields)} target field(s)")
    typer.echo(f"  {report.error_count} error(s), {report.warning_count} warning(s)")
    if dedupe is not None and not dedupe.skipped:
        typer.echo(f"  near-duplicate pairs: {len(dedupe.pairs)}")
    elif dedupe is not None:
        typer.echo(f"  {dedupe.skip_reason}")
    typer.echo("")
    for f in report.fields:
        if not f.found:
            status = "NOT FOUND"
        elif f.errors:
            status = f"{f.errors} error(s)"
        elif f.warnings:
            status = f"{f.warnings} warning(s)"
        else:
            status = "ok"
        typer.echo(f"    {f.name:<20} <- {f.source:<20} {status}")
    typer.echo("")


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
