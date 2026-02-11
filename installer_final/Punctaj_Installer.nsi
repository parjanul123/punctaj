; Punctaj Manager Installer Script
; Generated automatically for distributing the application

!include "MUI2.nsh"
!include "x64.nsh"

; Basic Settings
Name "Punctaj Manager v2.0.0"
OutFile "Punctaj_Manager_Installer.exe"
InstallDir "$PROGRAMFILES\Punctaj Manager"

; Version Info
VIProductVersion "2.0.0.0"
VIAddVersionKey "ProductName" "Punctaj Manager"
VIAddVersionKey "ProductVersion" "2.0.0"
VIAddVersionKey "CompanyName" "Punctaj Manager"
VIAddVersionKey "FileVersion" "2.0.0"
VIAddVersionKey "FileDescription" "Cloud-Enabled Employee Attendance Tracking"

; Default Folder
InstallDirRegKey HKCU "Software\Punctaj Manager" "InstallDir"

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Romanian"

; Installer Sections
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy application files
    File "punctaj.exe"
    File "supabase_config.ini"
    File "discord_config.ini"
    File "INSTALLATION_GUIDE.txt"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\Punctaj Manager"
    CreateShortcut "$SMPROGRAMS\Punctaj Manager\Punctaj Manager.lnk" "$INSTDIR\punctaj.exe"
    CreateShortcut "$SMPROGRAMS\Punctaj Manager\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortcut "$DESKTOP\Punctaj Manager.lnk" "$INSTDIR\punctaj.exe"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Registry entries
    WriteRegStr HKCU "Software\Punctaj Manager" "InstallDir" "$INSTDIR"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" \
                     "DisplayName" "Punctaj Manager"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" \
                     "DisplayVersion" "2.0.0"
    
    MessageBox MB_OK "Punctaj Manager installed successfully!$\nClick OK to launch."
    Exec "$INSTDIR\punctaj.exe"
SectionEnd

; Uninstaller
Section "Uninstall"
    RMDir /r "$INSTDIR"
    RMDir /r "$SMPROGRAMS\Punctaj Manager"
    Delete "$DESKTOP\Punctaj Manager.lnk"
    DeleteRegKey HKCU "Software\Punctaj Manager"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager"
    MessageBox MB_OK "Punctaj Manager has been uninstalled."
SectionEnd