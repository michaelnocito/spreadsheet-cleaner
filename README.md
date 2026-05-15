# 🧼 Spreadsheet Cleaner

### Build the tool. Learn the Python. Own the project.

A Python learning project by Michael Nocito.

<!--
VISUAL PLACEMENT 1 — Hero banner
Future path: docs/images/hero-banner.png
Alt text: Spreadsheet Cleaner — messy data in, clean report out
To create: a wide hero banner (~1600×500). Left side shows a messy
spreadsheet (red highlights on missing cells, inconsistent dates,
duplicate rows); right side shows a clean terminal report with green
checkmarks. Project name + tagline overlaid.
When ready, replace this comment with:
![Spreadsheet Cleaner — messy data in, clean report out](docs/images/hero-banner.png)
-->

---

Spreadsheet Cleaner turns a messy Excel file into a clear quality report,
then builds toward automated cleaning, change logs, and a simple desktop app.

You will build each part yourself.

You will learn Python by making something that works: reading real code,
running it, changing it, and seeing your tool improve one layer at a time.
By the end, you will have an actual Python project written by you, with a
real data-cleaning workflow you can explain, extend, and show.

---

## See It In Action

In the Basic layer, you run your first working version. It reads a messy
spreadsheet and prints a plain-English quality report straight to your
terminal: rows, columns, and exactly which cells are missing data.

Nothing is changed yet. The win here is that you made Python inspect a file
and explain what it found.

<!--
VISUAL PLACEMENT 2 — Product screenshot or short GIF
Future path: docs/images/basic-report.png (or .gif)
Alt text: Basic cleaner printing a spreadsheet quality report in the terminal
To create: capture a screenshot (or 6–10s GIF) of running:
  python basic\spreadsheet_cleaner.py sample_data\sample_spreadsheet.xlsx
Show the full "--- SPREADSHEET REPORT ---" output including the
"✓ OK" / "⚠️ MISSING" lines. PNG is fine; GIF is better if easy.
When ready, replace this comment with:
![Basic cleaner printing a spreadsheet quality report in the terminal](docs/images/basic-report.png)
-->

That report is your first working milestone. From there, each layer adds
more capability: first real cleaning, then a full desktop app.

---

## How It Works

The project is split into three layers. Each one gives you a working result
you can understand, run, and improve.

| Layer | What You Build | Concepts Covered |
|---|---|---|
| 🟢 **Basic** | Load a spreadsheet, generate a quality report *(report only — no cleaning yet)* | imports, functions, if/else, pandas basics |
| 🟡 **Intermediate** | Clean the data, fix dates, log every change | loops, string methods, error handling, file writing |
| 🔴 **Advanced** | Full desktop app with a GUI | CustomTkinter, connecting UI to logic, app launcher |

> **Start with Basic.** It runs in your terminal and prints a plain-text
> report about your spreadsheet — missing values, duplicates, format issues.
> No data is changed. That comes in Intermediate.

<!--
VISUAL PLACEMENT 3 — Simple workflow diagram
Future path: docs/images/workflow.svg (preferred) or docs/images/workflow.png
Alt text: Messy spreadsheet flows into Basic audit, then Intermediate cleaning, then Advanced desktop app
To create: a clean, simple horizontal flow diagram showing:
  [Messy Spreadsheet] → [Basic: Audit Report] → [Intermediate: Clean + Log] → [Advanced: Desktop App]
Keep it friendly and non-technical — use the same color cues as the table
above (green / yellow / red dots for the three layers). Excalidraw, Figma,
or a clean Keynote/PowerPoint export works.
When ready, replace this comment with:
![Messy spreadsheet flows into Basic audit, then Intermediate cleaning, then Advanced desktop app](docs/images/workflow.svg)
-->

---

## Who This Is For

- **Python beginners** who learn best by actually building things — not just reading about them
- **Anyone who works with spreadsheets** and wants to stop doing the tedious parts by hand
- **Students and career changers** who want a portfolio project that does something real

No prior Python experience needed for the Basic layer. Each layer tells
you exactly what you need before you start.

---

## New to GitHub? Start Here

GitHub is where this project lives online. To use it, you download a
copy to your own computer — that's called **cloning a repository**.
In practice, that means downloading the project files so you can run them locally.

Before you run anything, set up these four things:

**Step 1 — Install Git**
Git is the tool that lets your computer talk to GitHub and download files.
→ [git-scm.com/downloads](https://git-scm.com/downloads) — download and run the installer. Default settings are fine.

**Step 2 — Install Python 3**
Python is the programming language this project runs on.
→ [python.org/downloads](https://python.org/downloads) — pick the latest version.
⚠️ On Windows: check the box that says **"Add Python to PATH"** during install.
It's easy to miss and things won't work without it.

**Step 3 — Pick a code editor**
A code editor is where you'll read and write Python files. Any of these free options work:

- **[Thonny](https://thonny.org/)** *(best for total beginners)* — built specifically for learning Python. Dead simple, nothing to configure, has a terminal built in.
- **[VS Code](https://code.visualstudio.com/)** — the most popular editor used by professionals. Free, powerful, works great with Python. Slightly more setup but worth it long-term.
- **[PyCharm Community](https://www.jetbrains.com/pycharm/download/)** — free, Python-focused, lots of helpful features built in.
- **IDLE** — already installed with Python. No download needed. Works fine for simple scripts.

**Step 4 — Open a terminal**
The terminal is the text window where you type commands to run your code.

- **Thonny:** use the built-in Shell panel at the bottom of the screen
- **VS Code:** press `` Ctrl + ` ``
- **Windows (no editor):** search *PowerShell* in the Start menu
- **Mac:** search *Terminal* in Spotlight

Once all four are ready, follow the steps below.

---

## Windows Quickstart

If you're on Windows and want to get running fast, here's the exact
sequence from scratch — copy and paste each block into PowerShell.

**1. Clone the repo**

```powershell
git clone https://github.com/michaelnocito/spreadsheet-cleaner.git C:\Projects\spreadsheet-cleaner
cd C:\Projects\spreadsheet-cleaner
```

> **Why `C:\Projects\` instead of Desktop or Documents?**
> Desktop and Documents usually sync to OneDrive automatically. OneDrive
> can show a file as present before it's fully downloaded — when Python
> tries to open it, you get a confusing error even though the file looks
> right there. `C:\Projects\` is local-only and always reachable.
>
> ⚠️ This folder will **not** back up to OneDrive automatically. Use Git
> pushes as your backup, or copy the folder to OneDrive manually.

**2. Create and activate a virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

You'll know it worked when you see `(.venv)` at the start of your terminal line.

> ⚠️ **Getting a script execution error?** Run this once to fix it, then activate again:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

**3. Install requirements**

```powershell
pip install pandas openpyxl
```

**4. Generate the sample file**

The project includes a script that creates a realistic messy spreadsheet for you to test with:

```powershell
python sample_data\create_sample.py
```

This creates `sample_data\sample_spreadsheet.xlsx` — a file with
intentional issues (missing values, duplicate rows, messy formatting)
so you can see the tool working on real problems right away.

**5. Run the Basic cleaner**

```powershell
python basic\spreadsheet_cleaner.py sample_data\sample_spreadsheet.xlsx
```

You should see a quality report printed in your terminal.

> **Not seeing anything, or getting an error?** Open
> [`basic/guide_basic.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md)
> — it walks through every step with expected output and common fixes.

---

## Mac / Linux Setup

**1. Clone the repo**

```bash
git clone https://github.com/michaelnocito/spreadsheet-cleaner.git ~/Projects/spreadsheet-cleaner
cd ~/Projects/spreadsheet-cleaner
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install requirements**

```bash
pip install pandas openpyxl
```

**4. Generate the sample file and run**

```bash
python sample_data/create_sample.py
python basic/spreadsheet_cleaner.py sample_data/sample_spreadsheet.xlsx
```

> **Platform note:** This project is developed and tested on Windows.
> Mac and Linux instructions are provided as a best-effort guide but
> have not been formally tested yet.

---

## How This Project Teaches You

The code itself is the lesson. Every file is heavily commented —
lines that start with `#` are notes written for *you*, not the
computer. They explain what each line does, why it matters, and
how it connects to real data work.

Your job at each layer:

1. Open the Python file in your editor
2. Read every comment top to bottom — before you run anything
3. Run the code and watch it work
4. Go back and read the comments again — they'll land deeper the second time

Don't skip the comments. That's where the learning lives.

---

## Project Files

| File | What it is |
|---|---|
| [`basic/spreadsheet_cleaner.py`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/spreadsheet_cleaner.py) | The working Python program |
| [`basic/guide_basic.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md) | Step-by-step learning guide for Layer 1 |
| [`basic/glossary.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/glossary.md) | Plain-English definitions for every term in the project |
| [`sample_data/create_sample.py`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/sample_data/create_sample.py) | Run once to generate the test spreadsheet |

---

## Project Structure

```text
spreadsheet-cleaner/
├── basic/
│   ├── spreadsheet_cleaner.py   ← the working Python program
│   ├── guide_basic.md           ← step-by-step learning guide
│   └── glossary.md              ← plain-English term reference
├── intermediate/                ← coming soon
├── advanced/                    ← coming soon
├── sample_data/
│   └── create_sample.py         ← run once to generate the test spreadsheet
└── README.md                    ← you are here
```

---

## Real-World Context

This project is based on real work in data migration — the process
of moving client data from one system into another. Before any import
happens, someone has to check that the spreadsheet is clean: dates in
the right format, no missing required fields, no duplicate IDs. That's
exactly what this tool does.

By the time you finish all three layers, you will have a small but complete
Python project that demonstrates real data-cleaning workflow skills.

---

## Contributing

Found a bug? Have an idea for a better explanation? Open an issue
or submit a pull request — all experience levels welcome.
See [`CONTRIBUTING.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/CONTRIBUTING.md) for details.

---

If this project helped you, the best thing you can do is
[⭐ star the repo](https://github.com/michaelnocito/spreadsheet-cleaner)
— it helps other beginners find it.

If you'd like to support the work, a coffee is always appreciated but never expected.

<a href="https://buymeacoffee.com/michaelnocito" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>

---

Built with 🐍 Python | Maintained by [Michael Nocito](https://github.com/michaelnocito)
