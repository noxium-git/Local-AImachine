; Inno Setup script for Court local installer
[Setup]
AppName=Court
AppVersion=1.0
DefaultDirName={pf}\Court
DefaultGroupName=Court
OutputBaseFilename=CourtInstaller
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\Court\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Court"; Filename: "{app}\app.exe"
Name: "{userdesktop}\Court"; Filename: "{app}\app.exe"

[Run]
Filename: "{app}\app.exe"; Description: "Launch Court"; Flags: nowait postinstall skipifsilent
