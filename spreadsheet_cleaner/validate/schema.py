"""Target schemas: what the destination system requires.

A target schema is a small YAML or JSON file describing the fields the target
expects - names, source-column mapping, types, required/unique flags, lengths,
allowed values, patterns, ranges, and lookups against reference files. It is
the contract the migration must satisfy, committed next to the recipe.

Example (YAML):

    target: CRM Contacts
    key: employee_id
    fields:
      - name: employee_id
        type: integer
        required: true
        unique: true
      - name: full_name
        required: true
        max_length: 80
      - name: department
        allowed: [Engineering, Marketing, Sales, HR]
      - name: region_code
        lookup: { file: regions.csv, column: code }
    settings:
      extra_columns: warn   # ignore | warn | error
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

VALID_TYPES = {"integer", "decimal", "date", "email", "phone", "boolean", "text"}
EXTRA_COLUMN_MODES = {"ignore", "warn", "error"}


@dataclass
class Lookup:
    file: str
    column: str


@dataclass
class FieldSpec:
    name: str
    source: str
    type: str = "text"
    required: bool = False
    unique: bool = False
    max_length: int | None = None
    min_length: int | None = None
    allowed: list[str] | None = None
    pattern: str | None = None
    min: float | None = None
    max: float | None = None
    lookup: Lookup | None = None


@dataclass
class TargetSchema:
    target: str
    fields: list[FieldSpec] = field(default_factory=list)
    extra_columns: str = "warn"
    path: Path | None = None

    def field_by_name(self, name: str) -> FieldSpec | None:
        return next((f for f in self.fields if f.name == name), None)


def _parse_field(data: dict, key: str | None) -> FieldSpec:
    if "name" not in data:
        raise ValueError("Every schema field needs a 'name'.")
    name = str(data["name"])
    ftype = str(data.get("type", "text")).lower()
    if ftype not in VALID_TYPES:
        raise ValueError(
            f"Field '{name}': unknown type '{ftype}'. "
            f"Choose from: {', '.join(sorted(VALID_TYPES))}."
        )
    lookup = None
    if "lookup" in data:
        raw = data["lookup"]
        if not isinstance(raw, dict) or "file" not in raw or "column" not in raw:
            raise ValueError(f"Field '{name}': lookup needs 'file' and 'column'.")
        lookup = Lookup(file=str(raw["file"]), column=str(raw["column"]))
    allowed = data.get("allowed")
    if allowed is not None:
        allowed = [str(v) for v in allowed]
    is_key = key is not None and name == key
    return FieldSpec(
        name=name,
        source=str(data.get("source", name)),
        type=ftype,
        required=bool(data.get("required", False)) or is_key,
        unique=bool(data.get("unique", False)) or is_key,
        max_length=int(data["max_length"]) if "max_length" in data else None,
        min_length=int(data["min_length"]) if "min_length" in data else None,
        allowed=allowed,
        pattern=str(data["pattern"]) if "pattern" in data else None,
        min=float(data["min"]) if "min" in data else None,
        max=float(data["max"]) if "max" in data else None,
        lookup=lookup,
    )


def load_schema(path: str | Path) -> TargetSchema:
    path = Path(path)
    if not path.exists():
        raise ValueError(f"Target schema not found: {path}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yml", ".yaml"):
        import yaml

        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict) or "fields" not in data:
        raise ValueError(f"Schema {path.name} must be a mapping with a 'fields' list.")

    key = data.get("key")
    fields = [_parse_field(f, key) for f in data["fields"]]
    if key is not None and not any(f.name == key for f in fields):
        raise ValueError(f"Schema key '{key}' is not one of the declared fields.")

    names = [f.name for f in fields]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise ValueError(f"Duplicate field name(s) in schema: {', '.join(sorted(dupes))}.")

    settings = data.get("settings", {}) or {}
    extra = str(settings.get("extra_columns", "warn")).lower()
    if extra not in EXTRA_COLUMN_MODES:
        raise ValueError(
            f"settings.extra_columns must be one of: {', '.join(sorted(EXTRA_COLUMN_MODES))}."
        )
    return TargetSchema(
        target=str(data.get("target", path.stem)),
        fields=fields,
        extra_columns=extra,
        path=path,
    )
