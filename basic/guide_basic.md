# Spreadsheet Cleaner — Basic Layer Guide
### Python Learning Project | Layer 1 of 3

---

## What You're Building
A command-line tool that loads a spreadsheet and reports data
quality issues — missing values, column names, and row counts.
This is the foundation every data migration analyst needs before
touching a single cell of client data.

> **What Basic does:** Loads your spreadsheet and prints a report
> in the terminal. That's it — no files are saved, nothing is changed.
> Reading and reporting is the whole point at this layer.
> Cleaning and saving happens in the Intermediate layer.

---

## How to Use This Project

Here's the thing about this project — the code teaches you.

Every file has comments built right into it. Comments are the lines
that start with a `#` symbol. Python ignores them when it runs the
code, but they're there for YOU. They explain what each line does,
why it matters, and how it connects to real world work.

Your job at the Basic layer:
1. Open `spreadsheet_cleaner.py` in VS Code
2. Read every comment top to bottom before you run anything
3. Then run the code and see it in action
4. Come back and read the comments again — they'll make more sense now

Don't skip the comments. That's where the learning lives.
If a comment doesn't make sense, that's okay — read it, run the code,
and read it again. It'll click.

---

## Before You Start

### Requirements
Make sure your virtual environment is active (you'll see `(.venv)` in
your terminal), then install the required libraries:
```bash
pip install pandas openpyxl
```

Not sure about virtual environments? See the **New to GitHub? Start Here**
section in the main [README.md](../README.md).

### Folder Structure
```text
spreadsheet-cleaner/
├── basic/
│   ├── spreadsheet_cleaner.py
│   └── guide_basic.md
├── sample_data/
│   └── example_messy_dates.xlsx
└── README.md
```

---

## How to Run the App

1. Open your terminal in VS Code (`Ctrl + backtick`)
2. Navigate to the basic folder:
```bash
cd basic
```
3. Run the script:
```bash
python spreadsheet_cleaner.py
```
4. When prompted, enter the path to your spreadsheet.

**Use the included sample file to try it right away.**
Copy and paste this path exactly when the app asks:

- **Windows:**
```
..\sample_data\example_messy_dates.xlsx
```
- **Mac / Linux:**
```
../sample_data/example_messy_dates.xlsx
```

> **Tip for Windows users:** If you copy a file path using
> "Copy as path" from File Explorer, it will include quotes.
> Paste it in and remove the quotes before hitting Enter.

---

## What the App Does

### Step 1 — Load the File
The `load_file()` function:
- Checks the file exists
- Detects if it's a `.csv` or `.xlsx`
- Loads it into a pandas DataFrame
- Returns `None` if anything goes wrong

### Step 2 — Report
The `report()` function prints:
- Total rows and columns
- Every column name
- How many values are missing per column, with a ⚠️ warning
  if any are found

### Step 3 — Entry Point
The `if __name__ == "__main__"` block:
- Asks the user for a file path
- Calls `load_file()`
- Calls `report()` if the file loaded successfully

---

## Python Concepts Introduced

| Concept | Where You See It |
|---|---|
| `import` | Top of file — loading pandas and os |
| `def` | Defining `load_file()` and `report()` |
| `if / elif / else` | Checking file type in `load_file()` |
| `return` | Sending the DataFrame back to the caller |
| `for` loop | Looping through columns and missing values |
| f-strings | Printing variables inside strings |
| `if __name__ == "__main__"` | Entry point block |
| `input()` | Asking the user for a file path |

---

## Try It Yourself
Once the app runs successfully:

1. Open `example_messy_dates.xlsx` in Excel and add some blank
   cells, then run the app again — watch the ⚠️ warnings appear
2. Try pointing it at a `.csv` file if you have one
3. Try typing a fake file path — see how the app handles it
4. Read every comment in `spreadsheet_cleaner.py` top to bottom

---

## What's Next
In the **Intermediate Layer** you will add the actual cleaning
engine — stripping whitespace, fixing dates, logging every
change the app makes. The report you built here tells you
*what* needs fixing. Intermediate teaches the app to *fix it*.
