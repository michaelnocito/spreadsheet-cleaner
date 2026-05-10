# Spreadsheet Cleaner — Basic Layer Guide
### Python Learning Project | Layer 1 of 3

---

## What You're Building

A tool that opens a spreadsheet and prints a plain-English report:
how many rows, what columns, and which cells are missing data.

That might sound simple — and it is, intentionally. In the real world,
this is called a **data audit**. It's the first thing an analyst does
before touching a client's spreadsheet. You need to know what you're
dealing with before you change anything.

> **What Basic does:** Loads your spreadsheet and prints a report
> in the terminal. Nothing is saved, nothing is changed.
> Cleaning and saving starts in the Intermediate layer.

---

## How This Project Teaches You

Here's the thing — the code teaches you.

Every file has comments built right into it. Comments are lines
that start with `#`. Python ignores them when it runs, but they're
there for YOU. They explain what each line does, why it matters,
and how it connects to real work.

Your job at the Basic layer:
1. Open `spreadsheet_cleaner.py` in your code editor
2. Read every comment top to bottom — before you run anything
3. Run the code and watch it work
4. Go back and read the comments again — they'll make more sense now

Don't skip the comments. That's where the learning lives.
If something doesn't click right away, that's normal — read it,
run it, and come back. It'll land.

---

## Before You Start

Make sure you've completed the setup in the main README first.
→ [README.md — New to GitHub? Start Here](../README.md)

That covers installing Git, Python, your code editor, and
setting up a virtual environment. Once your terminal shows
`(.venv)`, you're ready. Then install the two libraries this project needs:

```bash
pip install pandas openpyxl
```

### What's in the project folder

```text
spreadsheet-cleaner/
├── basic/
│   ├── spreadsheet_cleaner.py   ← the Python program you'll run
│   └── guide_basic.md           ← this file
├── sample_data/
│   └── example_messy_dates.xlsx ← the test spreadsheet
└── README.md
```

---

## About the Sample File

The included test file — `example_messy_dates.xlsx` — is a fake employee
record spreadsheet. Think of it as something a company might send over
before moving their data into a new HR system.

It has **10 rows and 5 columns**:

| Column | What It Contains | Issues |
|---|---|---|
| `employee_id` | Unique ID for each person | None — all present |
| `full_name` | Employee name | 2 missing |
| `start_date` | Hire date | 1 missing + 6 different date formats |
| `department` | Which team they're on | 3 missing |
| `email` | Work email address | 2 missing |

The messy dates are intentional — cleaning them is what the Intermediate
layer is all about. At the Basic layer, the tool just spots them as missing
or present. The chaos of formats is something to notice, not fix yet.

---

## How to Run the App

**1. Open your terminal**
- Thonny: use the Shell panel at the bottom of the screen
- VS Code: press `Ctrl + \`` `
- PowerShell / Terminal: open it directly from your Start menu or Spotlight

**2. Navigate into the basic folder:**
```bash
cd basic
```
> `cd` means "change directory" — it moves you into a folder.
> You need to be inside the `basic` folder before running the script.

**3. Run the script:**
```bash
python spreadsheet_cleaner.py
```

**4. When it asks for a file path, paste one of these:**

- **Windows:**
```
..\sample_data\example_messy_dates.xlsx
```
- **Mac / Linux:**
```
../sample_data/example_messy_dates.xlsx
```

> **Windows tip:** If you used "Copy as path" from File Explorer,
> the path will have quotes around it. Remove the quotes before hitting Enter.

---

## Expected Output

If everything is working correctly, you should see this in your terminal:

```
Loading Excel file...

--- SPREADSHEET REPORT ---
Rows: 10 | Columns: 5

Column Names:
  - employee_id
  - full_name
  - start_date
  - department
  - email

Missing Values Per Column:
  employee_id: 0 missing  ✓ OK
  full_name: 2 missing  ⚠️  MISSING
  start_date: 1 missing  ⚠️  MISSING
  department: 3 missing  ⚠️  MISSING
  email: 2 missing  ⚠️  MISSING

--- END OF REPORT ---
```

If your output matches this exactly, you're in great shape.
If something looks different, check that you're pointing at the right file
and that your virtual environment is active.

---

## What the App Does

### Step 1 — Load the File
The `load_file()` function handles opening your spreadsheet safely:
- Checks that the file actually exists before trying to open it
- Figures out whether it's a `.csv` or `.xlsx` file
- Loads it into a pandas DataFrame (think of that as Python's version of a spreadsheet)
- If something goes wrong, it tells you and stops cleanly

### Step 2 — Report
The `report()` function prints a plain-English summary:
- Total number of rows and columns
- The name of every column
- How many values are missing in each column — with a ⚠️ warning if any are found

### Step 3 — Entry Point
The `if __name__ == "__main__"` block is where the program starts:
- Asks you to type a file path
- Passes it to `load_file()`
- If the file loaded successfully, runs `report()`

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

## While You Wait for Intermediate

Intermediate isn't available yet — but that doesn't mean you're stuck.
Here are three ways to go deeper with what you've already built.
Each one is a real skill, not busywork.

---

### Challenge 1 — Break It on Purpose

The best way to understand how code works is to make it fail — deliberately.
Try each of these and read what the program prints back:

- Type a file path that doesn't exist — what message do you get?
- Type a path to a `.pdf` or `.txt` file — what happens?
- Run it on the sample file, then open the `.xlsx` in Excel, delete
  a whole column of values, save it, and run the app again — do the
  ⚠️ warnings change the way you expected?
- Try adding a row in Excel where every cell is blank, then run the app

For each one, read the comment in the code that's responsible for handling
that situation. You're not just testing — you're connecting the code to
real behavior. That's how developers think.

---

### Challenge 2 — Run It on a Real File

Find or create your own spreadsheet and run the app on it.

Ideas:
- Export a Google Sheet as `.xlsx` or `.csv` (File → Download)
- Create a small `.csv` in Excel or Google Sheets with a few columns
  and intentionally leave some cells blank
- If you have a school project or personal data in a spreadsheet,
  use that — the app doesn't change anything, it only reads

Once it runs, ask yourself:
- Were any columns missing values you didn't expect?
- Does the column count match what you thought the file had?
- What would you want to fix first if this were a real client file?

This is exactly what an analyst does on day one of a migration project.

---

### Challenge 3 — Read the Code Like a Book

Open `spreadsheet_cleaner.py` and go through it line by line —
not to run it, just to read it. For each comment block, try to answer:

1. **What does this line do?** (The comment tells you — rephrase it in your own words)
2. **Why does it matter?** (The comment gives a real-world connection — do you believe it?)
3. **What would break if this line weren't here?** (Delete it mentally and think through it)

Then try this: close the file, open a blank `.py` file in your editor,
and write the `report()` function from memory. Don't copy — just try.
It doesn't need to be perfect. When you get stuck, look at one line,
continue, and keep going.

This is called **active recall** — one of the most effective ways to
learn anything. You'll remember far more from one attempt at writing
it yourself than from reading it ten times.

---

## What's Next

In the **Intermediate Layer** you'll add the actual cleaning engine —
stripping whitespace, fixing dates, and logging every change the app makes.

The report you built here tells you *what* needs fixing.
Intermediate teaches the app to *fix it*.
