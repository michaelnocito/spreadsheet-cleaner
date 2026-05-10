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

## Try It Yourself

Once the app runs successfully, push it further:

1. Open `example_messy_dates.xlsx` in Excel, delete a few cell values,
   save it, then run the app again — watch the ⚠️ warnings appear
2. Try pointing it at a `.csv` file if you have one
3. Type a fake file path on purpose — see how the app handles it
4. Try a path with the wrong file type (like a `.pdf`) — what happens?

Each of these is a real testing technique. You're not just playing around —
you're learning how to break things on purpose so you can build things that don't break.

---

## What's Next

In the **Intermediate Layer** you'll add the actual cleaning engine —
stripping whitespace, fixing dates, and logging every change the app makes.

The report you built here tells you *what* needs fixing.
Intermediate teaches the app to *fix it*.
