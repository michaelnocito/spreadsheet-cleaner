"""Generate the demo dataset used in the README and quickstart.

Produces a deliberately messy employee file (CSV + Excel) that trips every
data-quality dimension Spreadsheet Cleaner checks: missing values, a duplicate
key, six date formats, numbers stored as text, casing gremlins, stray
whitespace, a placeholder null, a blank row, and an empty column.

    python sample_data/create_sample.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Columns chosen so each one demonstrates a specific finding.
ROWS = [
    # id,   name,             start_date,       department,    email,                    salary,     status,   notes
    ["1001", "Sarah Johnson", "2021-03-15",     "Engineering", "sarah.j@company.com",     "$85,000",  "Active", ""],
    ["1002", "Mike Torres",   "March 4 2020",   "engineering", "mike.t@company.com",      "72000",    "active", ""],
    ["1003", "Linda Park ",   "15/06/2019",     "Marketing",   "linda.p@company.com",     "68,000",   "ACTIVE", ""],
    ["1004", "James Wu",      "11-30-2021",     "Sales",       "james.w@company.com",     "77500",    "Active", ""],
    ["1005", "",              "January 2023",   "",            "amy.c@company.com",       "91000",    "Active", ""],
    ["1006", "Amy Chen",      "2020-07-22",     "HR",          "amy.chen[at]company.com", "78000",    "Inactive", ""],
    ["1007", "Derek Mills",   "N/A",            "Marketing",   "",                        "not given","active", ""],
    ["1007", "Derek Mills",   "2019/05/10",     "Sales",       "derek.m@company.com",     "68000",    "Active", ""],
    ["1009", "Priya Nair",    "2023-08-14",     "Engineering", "priya.n@company.com",     "$102,000", "Active", ""],
    ["1010", "Tom Reyes",     "2022-11-01",     "hr",          "tom.r@company.com",       "64000",    "inactive", ""],
    ["",     "",              "",               "",            "",                        "",         "",       ""],  # blank row
    ["1012", "Nadia Reyes",   "07/19/2021",     "Sales ",      "nadia.r@company.com",     "70,500",   "Active", ""],
]

COLUMNS = [
    "employee_id", "full_name", "start_date", "department",
    "email", "salary", "status", "notes",
]


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    frame = pd.DataFrame(ROWS, columns=COLUMNS)

    csv_path = out_dir / "messy_employees.csv"
    xlsx_path = out_dir / "messy_employees.xlsx"
    frame.to_csv(csv_path, index=False)
    frame.to_excel(xlsx_path, index=False, engine="openpyxl")

    print(f"Wrote {csv_path}")
    print(f"Wrote {xlsx_path}")


if __name__ == "__main__":
    main()
