"""``python -m spreadsheet_cleaner``.

With no arguments it opens the desktop app. With arguments it runs the CLI, so
``python -m spreadsheet_cleaner profile data.csv`` still works. If the desktop
extra is not installed, it falls back to the CLI with a note.
"""

from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) > 1:
        from spreadsheet_cleaner.cli import app

        app()
        return

    try:
        from spreadsheet_cleaner.ui.app import launch
    except ImportError:
        import typer

        from spreadsheet_cleaner.cli import app

        typer.secho(
            'The desktop app needs pywebview: pip install "spreadsheet-cleaner[gui]"\n'
            "Showing the command line instead.\n",
            fg=typer.colors.YELLOW,
        )
        app(["--help"], standalone_mode=False)
        return

    launch()


if __name__ == "__main__":
    main()
