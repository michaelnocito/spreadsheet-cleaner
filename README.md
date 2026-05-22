# 🧼 Spreadsheet Cleaner

### Build the tool. Learn the Python. Own the project.

A Python learning project by [Michael Nocito](https://www.linkedin.com/in/michaelnocito).

**[🌐 spreadsheet-cleaner website](https://michaelnocito.github.io/spreadsheet-cleaner/)** &nbsp;·&nbsp; [GitHub](https://github.com/michaelnocito/spreadsheet-cleaner)

You will build it. You will learn Python. You will finish with a real
project written by you — code you can read, run, change, and explain.

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
then grows into automated cleaning, change logs, and a simple desktop app.

You will build each part yourself.

You will learn Python by making something that works: read real code,
run it, change it, and watch your tool get stronger one layer at a time.
Each step gives you a working result you can understand, run, and improve.
By the end, you will have an actual Python project written by you, with a
real data-cleaning workflow you can explain, extend, and show off.

---

## Your First Working Version

In the Basic layer, you run your first working version. It reads a messy
spreadsheet and prints a plain-English quality report straight to your
terminal: rows, columns, and exactly which cells are missing data.

Nothing is changed yet. That's the point. The win here is that you made
Python open a real file and explain what it found — a small, complete
result you built and can run again whenever you want.

<!--
VISUAL PLACEMENT 2 — Product screenshot or short GIF
Future path: docs/images/basic-report.png (or .gif)
Alt text: Basic cleaner printing a spreadsheet quality report in the terminal
To create: capture a screenshot (or 6–10s GIF) of running:
  python basic\spreadsheet_cleaner.py sample_data\example_messy_dates.xlsx
Show the full "--- SPREADSHEET REPORT ---" output including the
"✓ OK" / "⚠️ MISSING" lines. PNG is fine; GIF is better if easy.
When ready, replace this comment with:
![Basic cleaner printing a spreadsheet quality report in the terminal](docs/images/basic-report.png)
-->

That report is your first real milestone. From there, each layer adds
more power: real cleaning next, then a full desktop app you can launch
and hand to someone else.

---

## How It Works

The project is split into three layers. Each layer gives you a working
result you can understand, run, and improve before moving on.

| Layer | What You Build | Concepts Covered |
|---|---|---|
| 🟢 **Basic** | Load a spreadsheet, generate a quality report *(report only — no cleaning yet)* | imports, functions, if/else, pandas basics |
| 🟡 **Intermediate** | Clean the data, fix dates, log every change | loops, string methods, error handling, file writing |
| 🔴 **Advanced** | Full desktop app with a GUI | CustomTkinter, connecting UI to logic, app launcher |

> **Start with Basic.** It runs in your terminal and prints a plain-text
> report about your spreadsheet — missing values, duplicates, format issues.
> Nothing gets changed yet. Cleaning starts in the Intermediate layer.

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

- **Python beginners** who learn best by building real things, not just reading about them
- **Anyone who works with spreadsheets** and wants to automate the manual parts
- **Students and career changers** who want a portfolio project that does real work

No prior Python experience needed for the Basic layer. Each layer tells
you exactly what you need before you start. You bring the curiosity;
the project gives you the wins.

---

## New to GitHub? Start Here

GitHub is where this project lives online. To run it, you grab a copy
onto your own computer — that's called **cloning a repository**. In
plain terms: you download the project files so you can run them locally.

Set up these four things once, and you're ready for every layer:

**Step 1 — Install Git**
Git is the tool that lets your computer talk to GitHub and pull files down.
→ [git-scm.com/downloads](https://git-scm.com/downloads) — download and run the installer. Default settings are fine.

**Step 2 — Install Python 3**
Python is the programming language this project runs on.
→ [python.org/downloads](https://python.org/downloads) — grab the latest version.
⚠️ On Windows: tick the box that says **"Add Python to PATH"** during install.
It's easy to miss, and things won't work without it.

**Step 3 — Pick a code editor**
A code editor is where you read and write Python files. Any of these free options work:

- **[Thonny](https://thonny.org/)** *(great for first-time coders)* — built specifically for learning Python. Simple, nothing to configure, terminal built in.
- **[VS Code](https://code.visualstudio.com/)** — the editor most professionals use. Free, powerful, works great with Python. A little more setup, well worth it long-term.
- **[PyCharm Community](https://www.jetbrains.com/pycharm/download/)** — free, Python-focused, plenty of helpful features built in.
- **IDLE** — already installed with Python. No download needed. Works fine for simple scripts.

**Step 4 — Open a terminal**
The terminal is the text window where you type commands to run your code.

- **Thonny:** use the built-in Shell panel at the bottom of the screen
- **VS Code:** press `` Ctrl + ` ``
- **Windows (no editor):** search *PowerShell* in the Start menu
- **Mac:** search *Terminal* in Spotlight

Once all four are ready, run the steps below.

---

## Windows Quickstart

You're on Windows and you want to get running fast. Copy each block
into PowerShell, one after the other. By the end you will have run
your first working version.

**1. Clone the repo**

```powershell
git clone https://github.com/michaelnocito/spreadsheet-cleaner.git C:\Projects\spreadsheet-cleaner
cd C:\Projects\spreadsheet-cleaner
```

> **Why `C:\Projects\` instead of Desktop or Documents?**
> Desktop and Documents usually sync to OneDrive automatically. OneDrive
> can show a file as present before it's fully downloaded — and when
> Python tries to open it, you get a confusing error even though the
> file looks right there. `C:\Projects\` is local-only and always reachable.
>
> ⚠️ This folder will **not** back up to OneDrive automatically. Use Git
> pushes as your backup, or copy the folder to OneDrive manually.

**2. Create and activate a virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

You'll know it worked when `(.venv)` shows up at the start of your terminal line.
That's your green light — the project's virtual environment is active.

> ⚠️ **Getting a script execution error?** Run this once to fix it, then activate again:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

**3. Install requirements**

```powershell
pip install pandas openpyxl
```

**4. Generate the sample file**

The project ships with a script that builds a realistic messy spreadsheet for you to test against:

```powershell
python sample_data\create_sample.py
```

This creates `sample_data\example_messy_dates.xlsx` — a file packed with
intentional issues (missing values, dates in different formats) so you
can watch the tool work on real problems right away.

**5. Run the Basic cleaner**

```powershell
python basic\spreadsheet_cleaner.py sample_data\example_messy_dates.xlsx
```

A quality report prints in your terminal. That's your first working result.

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
python basic/spreadsheet_cleaner.py sample_data/example_messy_dates.xlsx
```

> **Platform note:** This project is built and tested on Windows.
> Mac and Linux instructions are a best-effort guide and have not
> been formally tested yet — if something trips you up there, an
> issue or PR is welcome.

---

## How This Project Teaches You

The code is the lesson. Every file is heavily commented — lines that
start with `#` are notes written for *you*, not the computer. They
explain what each line does, why it matters, and how it connects to
real data work.

Your job at each layer:

1. Open the Python file in your editor
2. Read every comment top to bottom — before you run anything
3. Run the code and watch it work
4. Go back and read the comments again — they will land deeper the second time

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

This project is based on real work in data migration — moving client
data from one system into another. Before any import runs, someone
has to check the spreadsheet: dates in the right format, no missing
required fields, no duplicate IDs. That's exactly what this tool does.

By the time you finish all three layers, you will own a small but
complete Python project that shows real data-cleaning workflow skills
— work you built, work you can explain, work you can put on a résumé.

---

## More from Michael Nocito

**[🕵️ NEXUS — Learn SQL by Solving a Mystery](https://michaelnocito.github.io/nexus-sql-mystery/)** —
A free game where you learn SQL by investigating $1.87M in corporate fraud. The natural next step
after Spreadsheet Cleaner — same analytical mindset, now applied to SQL.
Also includes a free **[SQL Foundations Guide](https://michaelnocito.github.io/nexus-sql-mystery/sql-foundations)** with examples and exercises.

**[📊 Analyst Prep Kit](https://michaelnocito.github.io/analyst-prep-kit/)** —
A free browser-based suite for breaking into data analytics — SQL, Excel, Python, Tableau, and Statistics.
12 lessons per module, real in-browser environments, honest readiness score. No install, no login.

**[🗂️ RecordForge](https://michaelnocito.github.io/recordforge/)** —
Generate fictional PDFs, Word docs, Excel datasets, and HTML files for testing and demos.
Free Windows app, no Python required. The **Messy Data** output pairs directly with this cleaner.

**[LinkedIn](https://www.linkedin.com/in/michaelnocito)** — data analyst · 8 years enterprise implementation

---

## Contributing

Found a bug? Have an idea for a clearer explanation? Open an issue
or send a pull request — every experience level is welcome here.
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
