# Spreadsheet Cleaner — Project Handoff
Last updated: May 10, 2026 at 8:26 PM EDT

## Purpose of this file
Compact handoff summary for continuing the Spreadsheet Cleaner project in a future chat without losing context. Use it as the first file/context reference before making any GitHub changes.

## Project Identity
- **Repo:** https://github.com/michaelnocito/spreadsheet-cleaner
- **Owner:** Michael Nocito (michaelnocito)
- **Status:** Basic tier live and publicly posted
- **Mission:** Educational Python data cleaning tool — teach real skills through real problems

## Architecture — 3-Tier System
- **Basic** (live): Terminal-only, generates analysis report, no cleaning. Teaches file I/O, pandas basics, f-strings, os.path, __main__
- **Intermediate** (next): Actual cleaning — dates, whitespace, duplicates, export change log
- **Advanced** (final): CustomTkinter GUI, color-coded output, migration-ready workflow

## Current File Structure
```
spreadsheet-cleaner/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── .github/
│   └── FUNDING.yml
├── basic/
│   ├── cleaner_basic.py
│   ├── guide_basic.md
│   └── sample_data/
└── sample_data/
```

## What Was Decided
- Quality-first approach — nothing ships until it meets the standard
- Each tier is standalone and fully teachable on its own
- No cleaning in Basic — analysis/report only
- Advanced uses CustomTkinter for GUI
- 60-day build plan: Intermediate by May 27, Advanced by Jun 10

## Open Issues / To-Do (as of May 10)
- Fix README clone instructions (Windows path clarity)
- Add requirements.txt, proper .gitignore, LICENSE
- Fix sample data — missing values need to actually fire
- Beginner-proof the file path input
- Fix teaching comments throughout
- Add smoke tests

## Monetization Status
- Buy Me a Coffee linked via FUNDING.yml
- Price was $1-3 — being raised to $5 minimum
- Suggested amounts: $5 / $15 / $30
- Monthly membership planned at $5/mo with newsletter perk

## Promotion Plan
- r/Python monthly showcase thread (mid-week only)
- Hacker News Show HN
- LinkedIn weekly posts
- No Reddit ads, no manipulation, honest framing only
