# ============================================================
# CREATE SAMPLE FILE
# ============================================================
# Run this script once to generate the test spreadsheet used
# by the Spreadsheet Cleaner app.
#
# From the root of the project, run:
#   python sample_data\create_sample.py
#
# This creates: sample_data/example_messy_dates.xlsx
#
# The file is a fake employee record spreadsheet with
# intentional problems: missing values and dates in
# multiple inconsistent formats. That's what the app
# is designed to detect and report on.
# ============================================================

import pandas as pd
import os

data = {
    "employee_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    "full_name":   ["Sarah Johnson", "Mike Torres", "Linda Park", None, "James Wu",
                    "Amy Chen", "Derek Mills", "Priya Nair", None, "Tom Reyes"],
    "start_date":  ["2021-03-15", "March 4 2020", "15/06/2019", "2022-11-01", "11-30-2021",
                    "January 2023", "2020-07-22", None, "2019/05/10", "2023-08-14"],
    "department":  ["Engineering", "Marketing", None, "Sales", "Engineering",
                    None, "HR", "Marketing", "Sales", None],
    "email":       ["sarah.j@company.com", None, "linda.p@company.com", "carlos.r@company.com",
                    "james.w@company.com", "amy.c@company.com", None, "priya.n@company.com",
                    "kenji.t@company.com", "tom.r@company.com"],
}

output_path = os.path.join(os.path.dirname(__file__), "example_messy_dates.xlsx")
pd.DataFrame(data).to_excel(output_path, index=False, engine="openpyxl")
print(f"Sample file created: {output_path}")
