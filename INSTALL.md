# Building the desktop app

For maintainers. Users should download the installer from the
[Releases page](https://github.com/michaelnocito/spreadsheet-cleaner/releases/latest).

## Prerequisites

```powershell
pip install -e ".[gui]"
pip install pyinstaller
winget install --id JRSoftware.InnoSetup
```

Inno Setup installs per-user, so `ISCC.exe` lands at
`C:\Users\<you>\AppData\Local\Programs\Inno Setup 6\ISCC.exe`, not Program Files.

## 1. Build the executable

```powershell
pyinstaller SpreadsheetCleaner.spec --noconfirm
```

Produces `dist\SpreadsheetCleaner.exe` (onefile, no console window).

The spec bundles `ui.html` under `spreadsheet_cleaner/ui/` on purpose.
`ui_html_path()` resolves it from the **package module**, not from the entry
script: in a onefile bundle the entry script's `__file__` flattens to the
bundle root, so resolving from `main.py` would look in the wrong place and the
app would crash on launch with `FileNotFoundError ... ui.html`.

## 2. Compile the installer

```powershell
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" installer.iss
```

Produces `Output\SpreadsheetCleanerSetup.exe`.

Keep `AppVersion` in `installer.iss` in step with `__version__` in
`spreadsheet_cleaner/__init__.py` **and** `version` in `pyproject.toml`. All
three must match on a release.

## 3. Verify before publishing

A `--noconsole` GUI exe that crashes on startup shows a blocking error dialog,
which still reads as a live process. **"Process is still running" is not a
pass.** Count WebView2 child processes instead: a working pywebview app spawns
several `msedgewebview2.exe` children, a crash-before-`create_window` spawns
none.

```powershell
(Get-Process msedgewebview2 -ErrorAction SilentlyContinue).Count   # before
Start-Process .\dist\SpreadsheetCleaner.exe
Start-Sleep 8
(Get-Process msedgewebview2 -ErrorAction SilentlyContinue).Count   # should be higher
```

Then run the clean-install pass: install to Program Files, launch from the
Start Menu shortcut (not the repo), profile and clean a file, confirm the
reports land in the chosen folder, click Check for Updates, and uninstall via
Windows Settings.

`dist/`, `build/`, and `Output/` are gitignored; installer artifacts are never
committed.
