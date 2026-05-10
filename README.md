# 🧼 Spreadsheet Cleaner
### A Python Learning Project by Michael Nocito



---

Ever received a messy spreadsheet and had no idea where to start?
This project teaches you Python by solving that exact problem.

You'll build a real data-cleaning tool — the kind used by data
migration analysts to prep client spreadsheets before importing
them into enterprise systems. No toy examples. Real, useful code.

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

- Python beginners who learn best by building real things
- Anyone who works with spreadsheets and wants to automate the tedious parts
- Students who want a portfolio project that actually does something

No prior Python experience needed for the Basic layer. Each layer
tells you what you need to know before starting.

---

## New to GitHub? Start Here

GitHub is where this project lives. To use it, you need to download
a copy to your own computer — this is called **cloning a repository**.

Here's everything you need before you run anything:

**Step 1 — Install Git**
Git is the tool that lets your computer download files from GitHub.
Download it at [git-scm.com/downloads](https://git-scm.com/downloads)
and follow the installer. No special settings needed.

**Step 2 — Install Python 3**
Download it at [python.org/downloads](https://python.org/downloads).
Choose the latest version. On Windows, check the box that says
**"Add Python to PATH"** during the install — this is easy to miss
and important to check.

**Step 3 — Open a terminal**
This is the text window where you type commands.
- **Windows:** Search for *PowerShell* in the Start menu
- **Mac:** Search for *Terminal* in Spotlight
- **VS Code:** Open the project folder, then press `` Ctrl + ` ``

Once Git, Python, and a terminal are ready, follow the steps below.

---

## How to Get Started

**1. Clone the repo**

This downloads the project files to your computer:
```bash
git clone https://github.com/michaelnocito/spreadsheet-cleaner.git
cd spreadsheet-cleaner
```

**2. Create a virtual environment**

This keeps the project's dependencies separate from the rest of
your computer — a best practice for any Python project:
```bash
python -m venv .venv
```

Then activate it:
- **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
- **Mac / Linux:** `source .venv/bin/activate`

You'll see `(.venv)` appear in your terminal when it's active.

**3. Install requirements**
```bash
pip install pandas openpyxl
```

**4. Head to the Basic layer**
Open `/basic/guide_basic.md` and follow the guide step by step.

---

## Real World Context

This project is inspired by real work in data migration. Tools like
this are used to prep client data before importing into enterprise
platforms. When a spreadsheet has bad dates, missing IDs, or messy
text — this app finds it and fixes it.

By the time you finish all 3 layers, you'll have built something
you can actually use and show off.

---

## Project Structure

```text
spreadsheet-cleaner/
├── basic/
│   ├── spreadsheet_cleaner.py
│   └── guide_basic.md
├── intermediate/         ← coming soon
├── advanced/             ← coming soon
├── sample_data/
│   └── example_messy_dates.xlsx
└── README.md
```

---


## Support the Project 💖

If you find this project helpful and would like to support its continued development, donations are always appreciated but never expected.

<p>
  <a href="https://buymeacoffee.com/michaelnocito" target="_blank">
    <img
      src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
      alt="Buy Me A Coffee"
      height="60"
    >
  </a>
</p>


---

**Important Disclaimer:**
*   **Voluntary:** Donations are entirely voluntary and are considered personal "tips" to support the developer's time and effort.
*   **No Strings Attached:** A donation does not guarantee the implementation of specific features, bug fixes, or personalized support.
*   **Non-Refundable:** All donations are final and non-refundable.
*   **As-Is:** This software is provided "as-is" without warranty of any kind.

---

## Contributing

Found a bug? Have an idea for a better explanation?
Open an issue or submit a pull request — all experience levels
welcome.

---

Built with 🐍 Python | Maintained by [Michael Nocito](https://github.com/michaelnocito)
