; Inno Setup script for Betten AI local installer
[Setup]
AppName=Betten AI
AppVersion=1.0
DefaultDirName={pf}\Betten AI
DefaultGroupName=Betten AI
OutputBaseFilename=BettenAIInstaller
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\BettenAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Betten AI"; Filename: "{app}\app.exe"
Name: "{userdesktop}\Betten AI"; Filename: "{app}\app.exe"

[Run]
Filename: "{app}\app.exe"; Description: "Launch Betten AI"; Flags: nowait postinstall skipifsilent
