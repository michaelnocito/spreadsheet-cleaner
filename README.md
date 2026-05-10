# 🧼 Spreadsheet Cleaner — Learn Python by Building a Real Data Tool
### A Python Learning Project by Michael Nocito

---

Ever received a messy spreadsheet and had no idea where to start?
This project teaches you Python by solving that exact problem.

You'll build a real data-cleaning tool — the kind used by data
migration analysts to prep client spreadsheets before importing
them into enterprise systems. No toy examples. No filler exercises.
Real, useful Python code you can actually put on a resume.

---

## How It Works

The project is split into 3 layers. Each one builds on the last.
You don't just read about Python — you build something with it.

| Layer | What You Build | Concepts Covered |
|---|---|---|
| 🟢 Basic | Load a spreadsheet, generate a quality report | imports, functions, if/else, pandas basics |
| 🟡 Intermediate | Clean the data, fix dates, log every change | loops, string methods, error handling, file writing |
| 🔴 Advanced | Full desktop app with a GUI | CustomTkinter, connecting UI to logic, app launcher |

---

## Who This Is For

- **Python beginners** who learn best by actually building things — not just reading about them
- **Anyone who works with spreadsheets** and wants to stop doing the tedious parts by hand
- **Students and career changers** looking for a portfolio project that does something real and useful

No prior Python experience needed for the Basic layer. Each layer
tells you exactly what you need before you start.

---

## New to GitHub? Start Here

GitHub is where this project lives online. To use it, you download
a copy to your own computer — that's called **cloning a repository**.
Think of it like syncing a Google Doc to your desktop, except for code.

Before you run anything, set up these four things:

**Step 1 — Install Git**
Git is the tool that lets your computer talk to GitHub and download files.
→ [git-scm.com/downloads](https://git-scm.com/downloads) — download and run the installer. Default settings are fine.

**Step 2 — Install Python 3**
Python is the programming language this project runs on.
→ [python.org/downloads](https://python.org/downloads) — pick the latest version.
⚠️ On Windows: check the box that says **"Add Python to PATH"** during install.
It's easy to miss and things won't work without it.

**Step 3 — Pick a Code Editor**
A code editor is where you'll read and write Python files. Any of these free options work:

- **[Thonny](https://thonny.org/)** *(best for total beginners)* — built specifically for learning Python. Dead simple, nothing to configure, has a terminal built in.
- **[VS Code](https://code.visualstudio.com/)** — the most popular editor used by professionals. Free, powerful, works great with Python. Slightly more setup but worth it long-term.
- **[PyCharm Community](https://www.jetbrains.com/pycharm/download/)** — free, Python-focused, lots of helpful features built in.
- **IDLE** — already installed with Python. No download needed. Works fine for simple scripts.

**Step 4 — Open a terminal**
The terminal is the text window where you type commands to run your code.
- **Thonny:** use the built-in Shell panel at the bottom of the screen
- **VS Code:** press `Ctrl + \`` `
- **Windows (no editor):** search *PowerShell* in the Start menu
- **Mac:** search *Terminal* in Spotlight

Once all four are ready, follow the steps below.

---

## How to Get Started

**1. Clone the repo**

The command below downloads the project directly to `C:\Projects\spreadsheet-cleaner`
— a folder outside OneDrive. This is intentional and explained below.

```powershell
git clone https://github.com/michaelnocito/spreadsheet-cleaner.git C:\Projects\spreadsheet-cleaner
cd C:\Projects\spreadsheet-cleaner
```

> `cd` means "change directory" — it moves you into the project folder you just downloaded.

> **Why not Desktop or Documents?**
> On most Windows computers, Desktop and Documents sync automatically to OneDrive.
> OneDrive sometimes shows files as present before they've fully downloaded to your
> hard drive. When Python tries to open one of those files it crashes with a confusing
> error — even though the file looks like it's right there.
>
> Cloning to `C:\Projects\` puts the project on your local drive where Python can
> always reach it, with no sync delays.
>
> ⚠️ **If you rely on OneDrive to back up your work:** this project folder will NOT
> be backed up automatically. If that matters to you, you have two options:
> - Back it up manually by copying the folder to OneDrive occasionally, or
> - Use Git itself as your backup — every time you push changes to GitHub,
>   your work is saved there. That's what this project uses.

**2. Create a virtual environment**

A virtual environment is like a clean workspace just for this project —
it keeps the libraries you install here from mixing with the rest of your computer:
```powershell
python -m venv .venv
```

Then activate it:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
source .venv/bin/activate
```

You'll know it worked when you see `(.venv)` at the start of your terminal line.

> ⚠️ **Windows: getting a script execution error?**
> PowerShell blocks scripts by default on many Windows machines. Run this command once to fix it:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> This only affects your user account — it's safe and is the standard fix.
> Then run the activate command above again.

> **Platform note:** This project is developed and tested on Windows.
> Mac and Linux instructions are provided as a best-effort guide but
> have not been formally tested yet.

**3. Install requirements**

This installs the two libraries the project needs:
```powershell
pip install pandas openpyxl
```

**4. Start the Basic layer**

Open [`basic/guide_basic.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md)
and follow the guide step by step. It tells you exactly what to run,
what to expect, and what every piece of the code does.

---

## Project Files

| File | What it is |
|---|---|
| [`basic/spreadsheet_cleaner.py`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/spreadsheet_cleaner.py) | The working Python program |
| [`basic/guide_basic.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md) | Step-by-step learning guide for Layer 1 |
| [`basic/glossary.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/glossary.md) | Plain-English definitions for every term in the project |
| [`sample_data/create_sample.py`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/sample_data/create_sample.py) | Run once to generate the test spreadsheet |

---

## Real World Context

This project is based on real work in data migration — the process of
moving client data from one system into another. Before any import happens,
someone has to check that the spreadsheet is clean: dates in the right format,
no missing required fields, no duplicate IDs. That's exactly what this tool does.

By the time you finish all 3 layers, you'll have built something
you can actually use, put on a resume, and show to anyone.

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

## Contributing

Found a bug? Have an idea for a better explanation?
Open an issue or submit a pull request — all experience levels welcome.
See [`CONTRIBUTING.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/CONTRIBUTING.md) for details.

---

If this project helped you, the best thing you can do is [⭐ star the repo](https://github.com/michaelnocito/spreadsheet-cleaner) — it helps other beginners find it.

If you'd like to support the work, a coffee is always appreciated but never expected.

<a href="https://buymeacoffee.com/michaelnocito" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>

---

Built with 🐍 Python | Maintained by [Michael Nocito](https://github.com/michaelnocito)
