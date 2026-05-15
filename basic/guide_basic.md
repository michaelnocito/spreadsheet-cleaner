# Spreadsheet Cleaner — Basic Layer Guide
### Python Learning Project | Layer 1 of 3

---

## What You're Building

A tool that opens a spreadsheet and prints a plain-English report:
how many rows, what columns, and which cells are missing data.

Sounds simple — and it is, on purpose. In the real world, this is
called a **data audit**. It's the first thing an analyst does before
touching a client's spreadsheet. You need to know what you're dealing
with before you change anything. By the end of this layer, you will
have run a working data audit you wrote yourself.

> **What Basic does:** Loads your spreadsheet and prints a report
> in the terminal. Nothing is saved, nothing is changed. Cleaning
> and saving starts in the Intermediate layer.

---

## How This Project Teaches You

The code teaches you. That's the whole approach.

Every file has comments built right into it. Comments are lines that
start with `#`. Python ignores them when it runs, but they're there
for *you*. They explain what each line does, why it matters, and how
it connects to real work.

Your job at the Basic layer:
1. Open [`spreadsheet_cleaner.py`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/spreadsheet_cleaner.py) in your code editor
2. Read every comment top to bottom — before you run anything
3. Run the code and watch it work
4. Go back and read the comments again — they will land deeper the second time

Don't skip the comments. That's where the learning lives. If something
doesn't click right away, that's normal — read it, run it, come back.
It will land.

> **New to some of the words in this guide?**
> [`glossary.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/glossary.md)
> has plain-English definitions for every term used here — written the
> way a coach would explain them, not a textbook.

---

## Before You Start

Before running anything here, finish the full setup in the main README:
→ [README.md — New to GitHub? Start Here](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/README.md#new-to-github-start-here)

That walkthrough covers installing Git, Python, a code editor, and
creating your virtual environment. Come back once your terminal shows
`(.venv)` at the start of the line — that's your green light.

Then install the two libraries this project needs:
```bash
pip install pandas openpyxl
```

### What's in the project folder

```text
spreadsheet-cleaner/
├── basic/
│   ├── spreadsheet_cleaner.py   ← the Python program you'll run
│   ├── guide_basic.md           ← this file
│   └── glossary.md              ← plain-English term reference
├── sample_data/
│   ├── create_sample.py         ← run this once to create the test file
│   └── example_messy_dates.xlsx ← the test spreadsheet (created by above)
└── README.md
```

---

## Step 0 — Create the Sample File

Before running the app, generate the test spreadsheet. Run this
one-time command from the project folder:

```powershell
python sample_data\create_sample.py
```

You should see:
```
Sample file created: sample_data\example_messy_dates.xlsx
```

That's a fake employee spreadsheet with intentional problems — missing
names, missing departments, dates in messy formats. That's the file
the app will read and report on.

You only need to run this once. After that the file lives in
`sample_data` and you can run the main app as many times as you want.

---

## How to Run the App

**1. Open your terminal**
- Thonny: use the Shell panel at the bottom of the screen
- VS Code: press `` Ctrl + ` ``
- PowerShell: search *PowerShell* in the Start menu

**2. Navigate into the basic folder:**
```powershell
cd basic
```
> `cd` means "change directory" — it moves you into a folder.
> You need to be inside the `basic` folder before the next step will work.

**3. Run the script:**
```powershell
python spreadsheet_cleaner.py
```

**4. When it asks for a file path, paste in this:**

**Windows:**
```
..\sample_data\example_messy_dates.xlsx
```
**Mac / Linux:**
```
../sample_data/example_messy_dates.xlsx
```

> **Windows tip:** If you used "Copy as path" from File Explorer,
> the path will have quotes around it. Remove the quotes before hitting Enter.

---

## What to Expect

When it works, your terminal will print exactly this:

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

The ⚠️ warnings are meant to be there — the sample file was built to
be messy on purpose. If your output matches this exactly, the app is
working. You wrote a tool that audits a real spreadsheet. Take the win.

> **Got an error instead?** Good news — errors are Python telling you
> exactly what it needs. Read the last line of the error message first.
> It's more helpful than it looks.
> Common ones and what they mean → [`glossary.md — Error / Exception`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/glossary.md#error--exception)

---

## What the App Does

### Step 1 — Load the File
The `load_file()` function opens your spreadsheet safely:
- Checks the file actually exists before trying to open it
- Figures out whether it's a `.csv` or `.xlsx` file
- Loads it into a pandas DataFrame (Python's version of a spreadsheet)
- If something goes wrong, it tells you clearly and stops

### Step 2 — Report
The `report()` function prints a plain-English summary:
- Total number of rows and columns
- The name of every column
- How many values are missing in each column — with a ⚠️ warning if any show up

### Step 3 — Entry Point
The `if __name__ == "__main__"` block is where the program starts:
- Asks you for a file path
- Passes it to `load_file()`
- If the file loaded successfully, calls `report()`

---

## Python Concepts Introduced

> **Unfamiliar with any of these?**
> [`glossary.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/glossary.md)
> has a plain-English definition for every term in this table.

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

## Now Play With It

You built something that works. That's the foundation — now go break
it on purpose. That's how developers actually learn:

1. **Make the warnings louder** — open `example_messy_dates.xlsx`
   in Excel, delete a few more cell values, save it, then run the app
   again. Watch the ⚠️ count climb.

2. **Try a different file** — point it at any `.csv` file on your
   computer. The app handles it the same way.

3. **Break it with a fake path** — type something like `fake_file.xlsx`
   when it asks for a path. See exactly how the app handles a file
   that doesn't exist.

4. **Break it with the wrong type** — point it at a `.pdf` or `.txt`
   file. What happens? What does the error tell you?

Each of these is a real testing technique. You're not just playing —
you're learning to break things on purpose so you can build things
that don't break.

---

## What's Next

You just built a real data audit tool. Layer 1 — done.

Layer 2 is where the actual cleaning happens: stripping whitespace,
fixing dates, and logging every change the app makes. The report you
built here tells you *what* needs fixing. Intermediate teaches the app
to *fix it*.

Not ready to move on yet? Run the app again on a different file. The
more you use it, the more the code will click.

> **Layer 2 — Intermediate is coming soon.**
> Check back when it's ready and it will pick up exactly where this layer leaves off.

---

If this guide helped you learn something, the best thing you can do is [⭐ star the repo](https://github.com/michaelnocito/spreadsheet-cleaner) — it helps other beginners find it.

If you'd like to support the work, a coffee is always appreciated but never expected.

<a href="https://buymeacoffee.com/michaelnocito" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>
