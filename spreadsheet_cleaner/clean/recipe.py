"""Cleaning recipes.

A recipe is an ordered, declarative list of steps. It is a small text file
(YAML or JSON) you can save, commit, and re-run on the next delivery, so
cleaning is deterministic and reproducible rather than a pile of one-off edits.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from spreadsheet_cleaner.core.models import Dimension, QualityReport

# Column selector "all" means every column; otherwise an explicit list.
ALL = "all"


@dataclass
class Step:
    type: str
    columns: list[str] | str = ALL
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        out: dict = {"type": self.type, "columns": self.columns}
        out.update(self.params)
        return out

    @classmethod
    def from_dict(cls, data: dict) -> "Step":
        data = dict(data)
        step_type = data.pop("type")
        columns = data.pop("columns", ALL)
        return cls(type=step_type, columns=columns, params=data)


@dataclass
class Recipe:
    steps: list[Step] = field(default_factory=list)
    version: int = 1

    def to_dict(self) -> dict:
        return {"version": self.version, "steps": [s.to_dict() for s in self.steps]}

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        steps = [Step.from_dict(s) for s in data.get("steps", [])]
        return cls(steps=steps, version=int(data.get("version", 1)))


def _dump_yaml(recipe: Recipe) -> str:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - yaml is a declared dependency
        raise RuntimeError(
            "Writing YAML recipes needs PyYAML. Install it, or save as .json."
        ) from exc
    return yaml.safe_dump(recipe.to_dict(), sort_keys=False)


def save_recipe(recipe: Recipe, path: str | Path) -> Path:
    path = Path(path)
    if path.suffix.lower() in (".yml", ".yaml"):
        path.write_text(_dump_yaml(recipe), encoding="utf-8")
    else:
        path.write_text(json.dumps(recipe.to_dict(), indent=2), encoding="utf-8")
    return path


def load_recipe(path: str | Path) -> Recipe:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yml", ".yaml"):
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError(
                "Reading YAML recipes needs PyYAML. Install it, or use a .json recipe."
            ) from exc
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Recipe {path.name} must be a mapping with a 'steps' list.")
    return Recipe.from_dict(data)


def default_recipe(report: QualityReport) -> Recipe:
    """Build a safe, sensible cleaning recipe from a profile.

    Trims every column, standardizes dates and numbers on the columns that are
    those types, makes categorical casing consistent, removes exact duplicate
    rows, and drops empty columns. It never fills missing values or changes
    text columns' casing - those are judgment calls left to an explicit recipe.
    """
    steps: list[Step] = [Step(type="trim_whitespace", columns=ALL)]

    date_cols = [c.name for c in report.columns if c.inferred_type == "date"]
    number_cols = [c.name for c in report.columns if c.inferred_type in ("integer", "decimal")]

    # Standardize casing/spelling on the columns the consistency check flagged,
    # plus any categorical/boolean columns (safe to canonicalize, never free text).
    case_cols = {c.name for c in report.columns if c.inferred_type in ("categorical", "boolean")}
    case_cols |= {i.column for i in report.issues_for(Dimension.CONSISTENCY) if i.column}

    if date_cols:
        steps.append(Step(type="normalize_dates", columns=date_cols, params={"format": "%Y-%m-%d"}))
    if number_cols:
        steps.append(Step(type="normalize_numbers", columns=number_cols))
    if case_cols:
        steps.append(Step(type="normalize_case", columns=sorted(case_cols), params={"mode": "consistent"}))

    steps.append(Step(type="dedupe_rows", columns=ALL))
    steps.append(Step(type="drop_empty_columns", columns=ALL))
    return Recipe(steps=steps)
