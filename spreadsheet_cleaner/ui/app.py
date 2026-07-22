"""pywebview API bridge for the Spreadsheet Cleaner desktop app.

The bridge runs the same engine the CLI does. Its contract with ui.html:

    run(payload) -> {"success": True, "files": [{"path", "label"}],
                     "folder": str, "summary": {...}}
                 or {"success": False, "error": str, "files": []}

Everything is local. The only outward request is check_update(), which runs
only when the user clicks Check for Updates.
"""

from __future__ import annotations

import json as _json
import os
import subprocess
import sys
import urllib.request as _urlreq
import webbrowser
from pathlib import Path

import webview

from spreadsheet_cleaner import __version__
from spreadsheet_cleaner.clean import clean_table, default_recipe, save_recipe, write_clean
from spreadsheet_cleaner.core.io import LoadError, LoadedTable, load
from spreadsheet_cleaner.profiling import profile_table
from spreadsheet_cleaner.report import write as write_quality
from spreadsheet_cleaner.report.clean_report import to_html as clean_to_html
from spreadsheet_cleaner.report.validate_report import to_html as validate_to_html
from spreadsheet_cleaner.validate import (
    find_near_duplicates,
    load_schema,
    starter_schema_yaml,
    validate_table,
)

REPO_URL = "https://github.com/michaelnocito/spreadsheet-cleaner"
RELEASES_URL = f"{REPO_URL}/releases/latest"
API_URL = "https://api.github.com/repos/michaelnocito/spreadsheet-cleaner/releases/latest"

DATA_FILTER = ("Spreadsheets (*.csv;*.xlsx;*.xlsm)",)
SCHEMA_FILTER = ("Target schema (*.yml;*.yaml;*.json)",)


def ui_html_path() -> Path:
    """Absolute path to ui.html, resolved from this package module.

    Not from the entry script: inside a PyInstaller onefile bundle the entry
    script's __file__ flattens to the bundle root, while a package module keeps
    its spreadsheet_cleaner/ui/ prefix, so this works frozen and from source.
    """
    return Path(__file__).parent / "ui.html"


def _parse_version(v: str) -> tuple[int, ...]:
    """Parse a version string into comparable ints; never raises."""
    core = str(v).strip().lstrip("v").split("-")[0].split("+")[0]
    return tuple(int(p) if p.isdigit() else 0 for p in core.split("."))


def _fetch_latest_release() -> dict:
    """The ONLY network request this app makes, and only on an explicit click."""
    req = _urlreq.Request(
        API_URL,
        headers={
            "User-Agent": f"SpreadsheetCleaner/{__version__}",
            "Accept": "application/vnd.github+json",
        },
    )
    with _urlreq.urlopen(req, timeout=8) as resp:
        return _json.loads(resp.read().decode("utf-8"))


def open_path(path: str) -> bool:
    """Open a file or folder with the OS default handler."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def _default_out_dir() -> str:
    return str(Path.home() / "Documents" / "spreadsheet-cleaner")


class API:
    """Methods called from ui.html. Every one returns JSON-safe data."""

    # ---- pickers and OS helpers ----

    def _window(self):
        return webview.windows[0] if webview.windows else None

    def choose_file(self) -> str | None:
        window = self._window()
        if not window:
            return None
        result = window.create_file_dialog(
            webview.OPEN_DIALOG, allow_multiple=False, file_types=DATA_FILTER
        )
        return result[0] if result else None

    def choose_schema(self) -> str | None:
        window = self._window()
        if not window:
            return None
        result = window.create_file_dialog(
            webview.OPEN_DIALOG, allow_multiple=False, file_types=SCHEMA_FILTER
        )
        return result[0] if result else None

    def choose_folder(self) -> str | None:
        window = self._window()
        if not window:
            return None
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else None

    def open_path(self, path: str) -> bool:
        return open_path(path)

    def open_folder(self, path: str) -> bool:
        return open_path(path)

    def default_out_dir(self) -> str:
        return _default_out_dir()

    def app_version(self) -> str:
        return __version__

    def open_releases(self) -> bool:
        try:
            webbrowser.open(RELEASES_URL)
            return True
        except Exception:
            return False

    def sheets(self, path: str) -> list[str]:
        """Sheet names for an Excel file; empty list for CSV or on failure."""
        if not path or Path(path).suffix.lower() not in (".xlsx", ".xlsm", ".xls"):
            return []
        try:
            import pandas as pd

            with pd.ExcelFile(path, engine="openpyxl") as book:
                return list(book.sheet_names)
        except Exception:
            return []

    # ---- update check (opt-in only) ----

    def check_update(self) -> dict:
        try:
            data = _fetch_latest_release()
            latest = str(data.get("tag_name") or data.get("name") or "").strip()
            if not latest:
                raise ValueError("No release tag found.")
            if _parse_version(latest) > _parse_version(__version__):
                return {
                    "status": "available",
                    "current": __version__,
                    "latest": latest.lstrip("v"),
                    "url": RELEASES_URL,
                }
            return {
                "status": "latest",
                "current": __version__,
                "latest": latest.lstrip("v"),
                "url": RELEASES_URL,
            }
        except Exception as exc:
            return {
                "status": "error",
                "current": __version__,
                "latest": "",
                "url": RELEASES_URL,
                "message": f"Could not check for updates ({exc.__class__.__name__}).",
            }

    # ---- schema drafting ----

    def draft_schema(self, payload: dict) -> dict:
        """Write a starter target schema next to the chosen file."""
        try:
            path = Path(payload["file"])
            sheet = payload.get("sheet") or None
            report = profile_table(load(path, sheet=sheet), version=__version__)
            out = Path(payload.get("out") or _default_out_dir())
            out.mkdir(parents=True, exist_ok=True)
            target = out / f"{path.stem}_target.yml"
            target.write_text(starter_schema_yaml(report), encoding="utf-8")
            return {"success": True, "path": str(target)}
        except (LoadError, ValueError, OSError) as exc:
            return {"success": False, "error": str(exc)}

    # ---- the main action ----

    def run(self, payload: dict) -> dict:
        """Profile, optionally clean, optionally validate. Writes reports."""
        try:
            source = Path(payload["file"])
            sheet = payload.get("sheet") or None
            out = Path(payload.get("out") or _default_out_dir())
            do_clean = bool(payload.get("clean"))
            do_validate = bool(payload.get("validate"))
            schema_path = payload.get("schema") or None
            near_dupes = bool(payload.get("near_dupes", True))

            if do_validate and not schema_path:
                raise ValueError("Choose a target schema, or turn off validation.")

            out.mkdir(parents=True, exist_ok=True)
            table = load(source, sheet=sheet)
            files: list[dict] = []

            report = profile_table(table, version=__version__)
            written = write_quality(report, out, formats=("html",))
            files.append({"path": str(written[0]), "label": "Quality report"})
            summary: dict = {
                "rows": report.rows,
                "cols": report.cols,
                "profile": {
                    "grade": report.grade,
                    "score": report.score,
                    "errors": report.error_count,
                    "warnings": report.warning_count,
                },
                "clean": None,
                "validate": None,
            }

            checked = table  # what validation runs against
            if do_clean:
                result = clean_table(table, recipe=default_recipe(report))
                ext = source.suffix.lower() if source.suffix.lower() in (".csv", ".xlsx") else ".csv"
                cleaned_path = write_clean(result, out / f"{source.stem}_cleaned{ext}")
                after_table = LoadedTable(
                    frame=result.frame, source=table.source, sheet=table.sheet
                )
                after = profile_table(after_table, version=__version__)
                clean_report = out / f"{source.stem}_cleaning_report.html"
                clean_report.write_text(
                    clean_to_html(result, report, after), encoding="utf-8"
                )
                recipe_path = out / f"{source.stem}_recipe.yml"
                save_recipe(result.recipe, recipe_path)
                files.append({"path": str(cleaned_path), "label": "Cleaned data"})
                files.append({"path": str(clean_report), "label": "Cleaning report"})
                files.append({"path": str(recipe_path), "label": "Recipe (re-runnable)"})
                summary["clean"] = {
                    "before_grade": report.grade,
                    "before_score": report.score,
                    "after_grade": after.grade,
                    "after_score": after.score,
                    "changes": result.changelog.total_changes,
                    "rows_removed": result.changelog.rows_removed,
                    "cols_removed": result.changelog.cols_removed,
                }
                checked = after_table

            if do_validate:
                target = load_schema(schema_path)
                vreport = validate_table(checked, target, version=__version__)
                dedupe = find_near_duplicates(checked.frame) if near_dupes else None
                vpath = out / f"{source.stem}_validation_report.html"
                vpath.write_text(validate_to_html(vreport, dedupe), encoding="utf-8")
                files.append({"path": str(vpath), "label": "Validation report"})
                summary["validate"] = {
                    "target": vreport.target,
                    "verdict": "PASS" if vreport.passed else "FAIL",
                    "score": vreport.score,
                    "errors": vreport.error_count,
                    "warnings": vreport.warning_count,
                    "near_dupes": len(dedupe.pairs) if dedupe and not dedupe.skipped else 0,
                    "on_cleaned": bool(do_clean),
                }

            return {
                "success": True,
                "files": files,
                "folder": str(out),
                "summary": summary,
            }
        except (LoadError, ValueError, OSError, KeyError) as exc:
            return {"success": False, "error": str(exc), "files": []}
        except Exception as exc:  # never let a stack trace reach the window
            return {
                "success": False,
                "error": f"Unexpected error: {exc.__class__.__name__}: {exc}",
                "files": [],
            }


def launch() -> None:
    """Create and start the desktop window."""
    api = API()
    webview.create_window(
        "Spreadsheet Cleaner",
        str(ui_html_path()),
        js_api=api,
        width=940,
        height=780,
        min_size=(720, 600),
    )
    webview.start()
