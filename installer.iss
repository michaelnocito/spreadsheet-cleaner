; Inno Setup script for Spreadsheet Cleaner.
; Build the exe first:  pyinstaller SpreadsheetCleaner.spec --noconfirm
; Then compile:         ISCC.exe installer.iss   -> Output\SpreadsheetCleanerSetup.exe

#define AppName "Spreadsheet Cleaner"
#define AppVersion "0.4.0"
#define AppPublisher "Michael Nocito"
#define AppURL "https://github.com/michaelnocito/spreadsheet-cleaner"
#define AppExeName "SpreadsheetCleaner.exe"

[Setup]
AppId={{7B3F1C42-9E5A-4D71-B8C3-5A2E9F4D1C88}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
DefaultDirName={autopf}\SpreadsheetCleaner
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=Output
OutputBaseFilename=SpreadsheetCleanerSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
