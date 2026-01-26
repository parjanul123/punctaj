; ========================================
; Inno Setup Script pentru PunctajManager
; ========================================

#define MyAppName "Punctaj Manager"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Parjanul Dev"
#define MyAppURL "https://github.com/parjanul123/punctaj"
#define MyAppExeName "PunctajManager.exe"

[Setup]
; Informații aplicație
AppId={{3F8B9A2C-1D4E-4F5A-9B8C-7E6D5A4B3C2D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=DEPLOYMENT.md
OutputDir=installer_output
OutputBaseFilename=PunctajManager_Setup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

; Visual
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "romanian"; MessagesFile: "compiler:Languages\Romanian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Fișierul principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Documentație
Source: "DEPLOYMENT.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion
Source: "GIT_SYNC_GUIDE.md"; DestDir: "{app}"; DestName: "GIT_SYNC.txt"; Flags: ignoreversion
Source: "CHECK_SYSTEM.bat"; DestDir: "{app}"; Flags: ignoreversion

; IMPORTANT: Datele inițiale - se copiază în Documents\PunctajManager
; Acestea sunt datele de start, utilizatorul le poate modifica după instalare
Source: "data\*"; DestDir: "{userdocs}\PunctajManager\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "arhiva\*"; DestDir: "{userdocs}\PunctajManager\arhiva"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Verificare Sistem"; Filename: "{app}\CHECK_SYSTEM.bat"
Name: "{group}\Documentație"; Filename: "{app}\README.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Verificare sistem după instalare
Filename: "{app}\CHECK_SYSTEM.bat"; Description: "Verifică cerințele de sistem"; Flags: postinstall shellexec skipifsilent
; Rulează aplicația
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; La dezinstalare, datele rămân în Documents pentru siguranță
; Utilizatorul poate șterge manual Documents\PunctajManager dacă dorește
Type: filesandordirs; Name: "{app}"

[Code]
// Verifică Visual C++ Redistributables
function VCRedistInstalled: Boolean;
var
  ResultCode: Integer;
begin
  // Încearcă să detecteze VC++ Redistributables 2015-2022
  Result := RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64');
  
  if not Result then
  begin
    if MsgBox('Visual C++ Redistributables nu sunt instalate.' + #13#10 + 
              'Acestea sunt necesare pentru ca aplicația să funcționeze.' + #13#10#13#10 + 
              'Doriți să descărcați și să instalați acum?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://aka.ms/vs/17/release/vc_redist.x64.exe', '', '', SW_SHOW, ewNoWait, ResultCode);
    end;
  end;
end;

// Verificare Git (opțional)
function GitInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c where git', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

// Afișare info despre locația datelor la final
procedure CurStepChanged(CurStep: TSetupStep);
var
  DataPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Arată unde sunt datele
    DataPath := ExpandConstant('{userdocs}\PunctajManager');
    MsgBox('Instalare completă!' + #13#10#13#10 + 
           'Aplicația a fost instalată în:' + #13#10 + 
           ExpandConstant('{app}') + #13#10#13#10 + 
           'Datele tale sunt salvate în:' + #13#10 + 
           DataPath + #13#10#13#10 + 
           'Această locație va fi folosită de TOATE instanțele aplicației!', 
           mbInformation, MB_OK);
    
    if not GitInstalled then
    begin
      MsgBox('Git nu este instalat pe acest sistem.' + #13#10#13#10 + 
             'Aplicația va funcționa normal, dar FĂRĂ sincronizare automată între device-uri.' + #13#10#13#10 + 
             'Pentru sincronizare Git, consultați documentația GIT_SYNC.txt din folderul de instalare.', 
             mbInformation, MB_OK);
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Verifică VC++ la început
  VCRedistInstalled;
end;
