"""Column type inference.

Given the present (non-missing) string values of a column, decide what the
column *intends* to be (integer, decimal, date, email, phone, boolean,
categorical, or free text), how confidently, which values violate that
intent, and - for dates and numbers - which surface formats appear (so the
conformity checks can catch format drift like six different date styles).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

# Ordered list of (strptime pattern, human label). Bare-year is deliberately
# excluded so numeric IDs / years are not misread as dates.
DATE_FORMATS: list[tuple[str, str]] = [
    ("%Y-%m-%d", "YYYY-MM-DD"),
    ("%Y/%m/%d", "YYYY/MM/DD"),
    ("%m/%d/%Y", "MM/DD/YYYY"),
    ("%d/%m/%Y", "DD/MM/YYYY"),
    ("%m-%d-%Y", "MM-DD-YYYY"),
    ("%d-%m-%Y", "DD-MM-YYYY"),
    ("%m/%d/%y", "MM/DD/YY"),
    ("%d.%m.%Y", "DD.MM.YYYY"),
    ("%B %d, %Y", "Month DD, YYYY"),
    ("%B %d %Y", "Month DD YYYY"),
    ("%b %d, %Y", "Mon DD, YYYY"),
    ("%b %d %Y", "Mon DD YYYY"),
    ("%d %B %Y", "DD Month YYYY"),
    ("%B %Y", "Month YYYY"),
    ("%Y-%m-%d %H:%M:%S", "YYYY-MM-DD HH:MM:SS"),
]

_INT_RE = re.compile(r"-?\d+")
_DECIMAL_RE = re.compile(r"-?\d*\.\d+")
_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_BOOL_TOKENS = {"true", "false", "yes", "no", "t", "f", "y", "n"}
_CURRENCY = str.maketrans("", "", "$€£¥,%  ")


def _clean_number(value: str) -> str:
    """Strip currency symbols, thousands separators, spaces, and () negatives."""
    v = value.strip()
    negative = v.startswith("(") and v.endswith(")")
    if negative:
        v = v[1:-1]
    v = v.translate(_CURRENCY)
    return ("-" + v) if (negative and not v.startswith("-")) else v


def is_integer(value: str) -> bool:
    return bool(_INT_RE.fullmatch(_clean_number(value)))


def is_decimal(value: str) -> bool:
    return bool(_DECIMAL_RE.fullmatch(_clean_number(value)))


def is_boolean(value: str) -> bool:
    return value.strip().casefold() in _BOOL_TOKENS


def is_email(value: str) -> bool:
    return bool(_EMAIL_RE.fullmatch(value.strip()))


def is_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    if not (7 <= len(digits) <= 15):
        return False
    # Reject values that carry letters beyond common separators.
    return bool(re.fullmatch(r"[\d\s()+\-.]+", value.strip()))


def date_format_of(value: str) -> str | None:
    """Return the human format label a value parses as, or ``None``."""
    v = value.strip()
    for pattern, label in DATE_FORMATS:
        try:
            datetime.strptime(v, pattern)
            return label
        except ValueError:
            continue
    return None


def is_date(value: str) -> bool:
    return date_format_of(value) is not None


def parse_date(value: str) -> datetime | None:
    """Parse a value using the first matching known format, or return None."""
    v = value.strip()
    for pattern, _label in DATE_FORMATS:
        try:
            return datetime.strptime(v, pattern)
        except ValueError:
            continue
    return None


def clean_number(value: str) -> str:
    """Public wrapper: strip currency, separators, and () negatives."""
    return _clean_number(value)


# Specific types worth flagging violations for, in priority order. Boolean is
# first so flag columns don't get swallowed by "integer"; categorical/text are
# resolved separately (no violations flagged for them).
_TYPE_TESTS: list[tuple[str, callable]] = [
    ("boolean", is_boolean),
    ("integer", is_integer),
    ("decimal", is_decimal),
    ("date", is_date),
    ("email", is_email),
    ("phone", is_phone),
]

_CONFIDENCE_FLOOR = 0.60
_CATEGORICAL_MAX_DISTINCT = 40
_CATEGORICAL_MAX_RATE = 0.6
_CATEGORICAL_SMALL_SET = 6


@dataclass
class TypeInference:
    inferred_type: str
    confidence: float
    violations: list[str] = field(default_factory=list)
    formats: list[tuple[str, int]] = field(default_factory=list)


def infer(present_values: list[str]) -> TypeInference:
    """Infer the intended type of a column from its present values."""
    n = len(present_values)
    if n == 0:
        return TypeInference("empty", 0.0)

    # Pick the specific type with the highest match fraction.
    best_type = ""
    best_matches = 0
    for type_name, test in _TYPE_TESTS:
        matches = sum(1 for v in present_values if test(v))
        if matches > best_matches:
            best_matches, best_type = matches, type_name

    confidence = best_matches / n
    if best_type and confidence >= _CONFIDENCE_FLOOR:
        violations = [v for v in present_values if not dict(_TYPE_TESTS)[best_type](v)]
        formats: list[tuple[str, int]] = []
        if best_type == "date":
            counter = Counter(
                fmt for v in present_values if (fmt := date_format_of(v))
            )
            formats = counter.most_common()
        return TypeInference(best_type, round(confidence, 3), violations, formats)

    # No dominant specific type: categorical vs. free text. A column is
    # categorical if it draws from a small, repeating set of values (bounded
    # distinct count, with repetition), otherwise it is free text.
    distinct = len(set(present_values))
    rate = distinct / n
    is_categorical = (
        distinct <= _CATEGORICAL_MAX_DISTINCT
        and distinct < n
        and (rate <= _CATEGORICAL_MAX_RATE or distinct <= _CATEGORICAL_SMALL_SET)
    )
    if is_categorical:
        return TypeInference("categorical", round(1 - rate, 3))
    return TypeInference("text", round(rate, 3))
