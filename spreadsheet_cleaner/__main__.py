"""``python -m spreadsheet_cleaner`` → the CLI.

A desktop GUI is planned (see ROADMAP.md, Phase E); until then this entry
point runs the command-line interface.
"""

from spreadsheet_cleaner.cli import app

if __name__ == "__main__":
    app()
