# ============================================================
# SPREADSHEET CLEANER — BASIC LAYER
# Python Learning Project | Layer 1 of 3
# ============================================================
# Welcome! You're about to build a real tool that data analysts
# use every day. We're going to walk you through every line.
# At this layer most of the code is written for you — your job
# is to read the comments, run the code, and get comfortable
# before we hand you the wheel in the next layer.
# ============================================================

# ============================================================
# SAMPLE FILE
# ============================================================
# The project includes a ready-to-use test file:
#   sample_data/example_messy_dates.xlsx
#
# It's a fake employee record spreadsheet — the kind of file
# a company might send over before a system migration.
# It has 10 rows and 5 columns:
#
#   employee_id  — a unique ID number for each person
#   full_name    — employee name (2 missing)
#   start_date   — hire date, in 6 different messy formats (1 missing)
#   department   — which team they're on (3 missing)
#   email        — work email address (2 missing)
#
# When you run this program on that file, here's what you
# should see in the terminal:
#
#   Loading Excel file...
#
#   --- SPREADSHEET REPORT ---
#   Rows: 10 | Columns: 5
#
#   Column Names:
#     - employee_id
#     - full_name
#     - start_date
#     - department
#     - email
#
#   Missing Values Per Column:
#     employee_id: 0 missing  ✓ OK
#     full_name: 2 missing  ⚠️  MISSING
#     start_date: 1 missing  ⚠️  MISSING
#     department: 3 missing  ⚠️  MISSING
#     email: 2 missing  ⚠️  MISSING
#
#   --- END OF REPORT ---
#
# If your output matches this, everything is working correctly.
# ============================================================

# ============================================================
# IMPORTS
# ============================================================
# Think of imports like apps on your phone. Python comes with
# a lot of built-in stuff, but sometimes you need to grab a
# specific tool for the job.
#
# 'pandas' is the go-to tool for working with spreadsheet data
# in Python. Almost every data job in the real world uses it.
# We nickname it 'pd' so we don't have to type 'pandas' every
# single time — just like you might save a contact as 'Mom'
# instead of her full name.
#
# 'os' lets our program talk to the computer's file system —
# things like checking if a file exists before we try to open
# it. Like knocking before you open a door.
#
# 'zipfile' is a standard Python library for working with zip
# archives. We import it here only to catch a specific error —
# .xlsx files are zip archives under the hood, and if the file
# hasn't fully synced from OneDrive yet, Python sees a broken
# zip and crashes. We catch that and explain it clearly instead.
# ============================================================
import pandas as pd
import os
import zipfile


# ============================================================
# FUNCTION: load_file
# ============================================================
# A function is a reusable block of code. You write it once
# and call it whenever you need it — like a recipe. You don't
# rewrite a recipe every time you make cookies, you just
# follow it.
#
# 'filepath' is a parameter. It's a value we hand to the
# function when we call it — like texting someone an address
# so they know where to show up.
#
# In the real world, functions like this are used any time an
# app needs to open a file a user picked — think uploading a
# photo to Instagram or attaching a file to an email.
# ============================================================
def load_file(filepath):

    # os.path.exists() checks whether a file is actually present
    # at the path you gave it. It returns True or False.
    # 'not' flips the answer — so this reads:
    # "if the file does NOT exist, tell the user and stop."
    # Real world: ever clicked a broken download link? This is
    # the check that prevents that crash before it happens.
    if not os.path.exists(filepath):
        print("File not found. Double check your file path and try again.")
        return None
    # 'return' exits the function and sends a value back to
    # whoever called it. Returning None is our way of saying
    # "nothing to give you — something went wrong."

    # str.endswith() checks how a string of text ends.
    # Here we use it to figure out what kind of file we have.
    # Real world: your computer does this exact thing when it
    # decides which app to open a file with.
    elif filepath.endswith('.csv'):
        print("Loading CSV file...")
        return pd.read_csv(filepath)

    elif filepath.endswith('.xlsx'):
        print("Loading Excel file...")
        # We wrap this in a try/except block to catch a specific
        # error that happens when the file lives in OneDrive and
        # hasn't fully synced to your hard drive yet.
        #
        # .xlsx files are actually zip archives under the hood —
        # Excel just uses a .xlsx extension. If OneDrive hasn't
        # downloaded the real file yet, Python finds a tiny
        # placeholder instead of the actual data and crashes.
        #
        # The fix: right-click the file in File Explorer and
        # choose "Always keep on this device", then try again.
        # Or move the project outside your OneDrive folder.
        #
        # try/except is Python's way of saying: "attempt this,
        # and if a specific error happens, handle it gracefully
        # instead of crashing." Real world: think of it like a
        # form that shows 'invalid email' instead of just
        # freezing when you type something wrong.
        try:
            # engine='openpyxl' tells pandas exactly which library
            # to use to open the file. Without it, some versions of
            # pandas can't figure it out automatically and crash.
            return pd.read_excel(filepath, engine='openpyxl')
        except zipfile.BadZipFile:
            print()
            print("Could not open the file.")
            print()
            print("This usually means the file is stored in OneDrive")
            print("but hasn't fully downloaded to your computer yet.")
            print()
            print("To fix it:")
            print("  1. Open File Explorer and find the file")
            print("  2. Right-click it")
            print("  3. Select 'Always keep on this device'")
            print("  4. Wait for the green checkmark, then try again")
            print()
            print("Or move the project to a folder outside OneDrive,")
            print("such as C:\\Users\\YourName\\Projects\\spreadsheet-cleaner")
            print()
            return None

    else:
        print("Unsupported file type. Please use a .csv or .xlsx file.")
        return None


# ============================================================
# FUNCTION: report
# ============================================================
# This function takes the spreadsheet we just loaded and prints
# a plain-English summary of what's in it — before we touch
# anything. Think of it like a doctor doing a checkup before
# suggesting treatment. You want to know what you're dealing
# with first.
#
# In data migration work, this is called a 'data audit.' It's
# the first thing an analyst does when a client sends over a
# spreadsheet. How many rows? What columns? Anything missing?
# ============================================================
def report(df):
    # 'df' stands for DataFrame — that's pandas' word for a
    # spreadsheet loaded into Python. Rows, columns, the whole
    # thing. You'll see 'df' everywhere in data work.

    print("\n--- SPREADSHEET REPORT ---")

    # df.shape gives us the size of the spreadsheet as two
    # numbers: rows and columns. Like asking 'how big is this
    # table?' Real world: imagine getting a client file and
    # needing to know if it has 50 rows or 50,000.
    rows, cols = df.shape
    print(f"Rows: {rows} | Columns: {cols}")
    # f-strings let you embed a variable directly inside a
    # string using curly braces {}. The f before the opening
    # quote is what activates it. Python swaps in the value
    # at runtime — so f"Rows: {rows}" becomes "Rows: 10".
    # Way cleaner than gluing strings together with + signs.

    print("\nColumn Names:")
    # df.columns.tolist() returns all the column headers as a
    # plain Python list. Like reading the top row of a
    # spreadsheet out loud.
    for col in df.columns.tolist():
        print(f"  - {col}")
    # 'for' loops go through a list one item at a time and do
    # something with each one. Real world: think of it like a
    # cashier scanning items one by one at checkout.

    print("\nMissing Values Per Column:")
    # df.isnull() returns a True/False version of the whole
    # spreadsheet — True wherever a cell is blank, False where
    # it has a value. Calling .sum() on that adds up all the
    # Trues per column (True counts as 1, False as 0).
    # Result: a count of blank cells in each column.
    # Real world: imagine a form submission where required
    # fields were left empty — this is how you'd find them.
    missing = df.isnull().sum()
    for col, count in missing.items():
        status = "⚠️  MISSING" if count > 0 else "✓ OK"
        print(f"  {col}: {count} missing  {status}")
    # The line above uses a one-line if/else called a ternary.
    # It's shorthand for: if count > 0, label it MISSING,
    # otherwise label it OK.

    print("\n--- END OF REPORT ---\n")


# ============================================================
# ENTRY POINT
# ============================================================
# This is where the program actually starts running.
#
# 'if __name__ == "__main__"' is a Python best practice that
# means: only run this block if someone is executing THIS file
# directly (e.g. 'python spreadsheet_cleaner.py'). If another
# script imports this file to borrow our functions, this block
# stays quiet and doesn't run automatically.
# Real world: like a light switch wired to only one room —
# flipping it here doesn't affect the rest of the house.
# ============================================================
if __name__ == "__main__":

    # input() prints a prompt and waits for the user to type
    # something and press Enter. Whatever they type comes back
    # as a string — that's our file path.
    #
    # Real world: input() is behind every form you've filled
    # out — login screens, search bars, checkout forms. Any
    # time a program needs something from a human, this is
    # the building block.
    filepath = input("Enter the path to your spreadsheet: ").strip()
    # .strip() removes any accidental spaces before or after
    # the path — easy to add by mistake when copy-pasting.

    # Windows users sometimes copy a file path from Explorer
    # and it arrives wrapped in quotes, like:
    #   "C:\Users\Mike\data.xlsx"
    # Python can't open a path with literal quote marks in it,
    # so we strip them off here before doing anything else.
    if filepath.startswith('"') and filepath.endswith('"'):
        filepath = filepath[1:-1]
    if filepath.startswith("'") and filepath.endswith("'"):
        filepath = filepath[1:-1]

    # Normalize the extension to lowercase so .XLSX and .CSV
    # work the same as .xlsx and .csv. Capitalization varies
    # across operating systems and shouldn't cause a failure.
    root, ext = os.path.splitext(filepath)
    filepath = root + ext.lower()

    df = load_file(filepath)

    if df is not None:
        report(df)
