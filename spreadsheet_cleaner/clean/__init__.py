"""The cleaning engine: apply a recipe to a table, logging every change.

Non-destructive: the caller's source file is never modified. Cleaning produces a
new frame plus a change log; writing goes to a separate path (and refuses to
overwrite the source).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from spreadsheet_cleaner.clean.changelog import ChangeLog
from spreadsheet_cleaner.clean.recipe import Recipe, default_recipe, load_recipe, save_recipe
from spreadsheet_cleaner.clean.steps import STEP_REGISTRY, resolve_columns
from spreadsheet_cleaner.core.io import LoadedTable, load


@dataclass
class CleanResult:
    frame: pd.DataFrame
    changelog: ChangeLog
    recipe: Recipe
    source: str
    sheet: str | None = None


def clean_table(table: LoadedTable, recipe: Recipe | None = None) -> CleanResult:
    """Apply a recipe (or a smart default) to a loaded table."""
    from spreadsheet_cleaner.profiling import profile_table

    if recipe is None:
        recipe = default_recipe(profile_table(table))

    frame = table.frame.copy()
    changelog = ChangeLog(rows_before=len(frame), cols_before=frame.shape[1])

    for step in recipe.steps:
        fn = STEP_REGISTRY.get(step.type)
        if fn is None:
            raise ValueError(
                f"Unknown cleaning step '{step.type}'. "
                f"Known steps: {', '.join(sorted(STEP_REGISTRY))}."
            )
        columns = resolve_columns(frame, step.columns)
        frame, records = fn(frame, columns, step.params)
        for record in records:
            changelog.add(record)

    changelog.rows_after = len(frame)
    changelog.cols_after = frame.shape[1]
    return CleanResult(frame, changelog, recipe, str(table.source), table.sheet)


def clean_file(
    path: str | Path, recipe: Recipe | None = None, *, sheet: str | None = None
) -> CleanResult:
    return clean_table(load(path, sheet=sheet), recipe=recipe)


def write_clean(result: CleanResult, out_path: str | Path) -> Path:
    """Write the cleaned data to CSV or Excel. Refuses to overwrite the source."""
    out_path = Path(out_path)
    if result.source and out_path.resolve() == Path(result.source).resolve():
        raise ValueError(
            "Refusing to overwrite the source file. Choose a different output path."
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = out_path.suffix.lower()
    if suffix == ".csv":
        result.frame.to_csv(out_path, index=False)
    elif suffix in (".xlsx", ".xlsm"):
        result.frame.to_excel(out_path, index=False, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported output type '{suffix}'. Use .csv or .xlsx.")
    return out_path


__all__ = [
    "CleanResult",
    "clean_table",
    "clean_file",
    "write_clean",
    "Recipe",
    "default_recipe",
    "load_recipe",
    "save_recipe",
]
