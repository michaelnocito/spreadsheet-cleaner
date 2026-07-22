# PyInstaller spec for the Spreadsheet Cleaner desktop app.
#   pyinstaller SpreadsheetCleaner.spec --noconfirm
# Produces dist/SpreadsheetCleaner.exe (onefile, no console window).
#
# ui.html must be bundled UNDER spreadsheet_cleaner/ui/ so ui_html_path()
# (which resolves from the package module, not the entry script) finds it
# when frozen.

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("spreadsheet_cleaner/ui/ui.html", "spreadsheet_cleaner/ui")],
    hiddenimports=["openpyxl", "yaml"],
    hookspath=[],
    runtime_hooks=[],
    # Keep the installer lean: none of these are used by the desktop app.
    # pyarrow is only an optional pandas extra (parquet/feather); bundling it
    # added ~130 MB for code paths this app never touches.
    excludes=[
        "pyarrow", "scipy", "matplotlib", "pytest", "tkinter",
        "PyQt5", "PySide2", "IPython", "notebook", "numpy.f2py",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="SpreadsheetCleaner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
