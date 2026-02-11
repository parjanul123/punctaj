; Punctaj Manager Professional Installer
; NSIS Installer Script v2.0
; Includes: Application, Discord Config, Supabase Config, Encryption Keys

!include "MUI2.nsh"
!include "x64.nsh"
!include "LogicLib.nsh"

; Constants
!define PRODUCT_NAME "Punctaj Manager"
!define PRODUCT_VERSION "2.0"
!define PRODUCT_PUBLISHER "Punctaj Team"
!define PRODUCT_WEB_SITE "https://punctaj.local"

; Name and file
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Punctaj_Manager_Professional_Setup.exe"
InstallDir "$PROGRAMFILES\Punctaj"
InstallDirRegKey HKLM "Software\Punctaj" "Install_Dir"

; Request application privileges for Windows Vista and higher
RequestExecutionLevel admin

; UI Settings
!define MUI_ICON "punctaj.ico"
!define MUI_UNICON "punctaj.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\Punctaj_Manager.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${PRODUCT_NAME}"

; Variables
Var StartMenuFolder

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU "Application" $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Romanian"

; Installer sections
Section "Install ${PRODUCT_NAME}" SEC_APP
  SetOutPath "$INSTDIR"
  
  ; Copy main executable (renamed to Punctaj_Manager.exe)
  File /oname=Punctaj_Manager.exe "dist\punctaj.exe"
  
  ; Copy configuration files with proper settings
  SetOverwrite on
  ${If} ${FileExists} "discord_config.ini"
    File "discord_config.ini"
  ${Else}
    FileOpen $0 "$INSTDIR\discord_config.ini" w
    FileWrite $0 "[discord]$\r$\nCLIENT_ID = 1465698276375527622$\r$\nCLIENT_SECRET = aM0uvwRSZSIEkzxHG7k01rs_xlF3SW5Q$\r$\nREDIRECT_URI = http://localhost:8888/callback$\r$\nWEBHOOK_URL =$\r$\n"
    FileClose $0
  ${EndIf}
  
  ${If} ${FileExists} "supabase_config.ini"
    File "supabase_config.ini"
  ${Else}
    FileOpen $0 "$INSTDIR\supabase_config.ini" w
    FileWrite $0 "[supabase]$\r$\nurl = https://yzlkgifumrwqlfgimcai.supabase.co$\r$\nkey = sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM$\r$\ntable_sync = police_data$\r$\ntable_logs = audit_logs$\r$\ntable_users = users$\r$\n$\r$\n[sync]$\r$\nenabled = true$\r$\nauto_sync = true$\r$\nsync_interval = 30$\r$\nconflict_resolution = latest_timestamp$\r$\nsync_on_startup = true$\r$\n$\r$\n[permissions]$\r$\ndefault_role = superuser$\r$\nadmin_role = superuser$\r$\nsuperuser_enabled = true$\r$\nenforce_hierarchy = true$\r$\ninstitution_level = system$\r$\n"
    FileClose $0
  ${EndIf}
  
  ; Copy encryption key if it exists (for data protection)
  ${If} ${FileExists} ".secure_key"
    File ".secure_key"
  ${EndIf}
  
  ; Copy JSON encryptor module
  ${If} ${FileExists} "json_encryptor.py"
    File "json_encryptor.py"
  ${EndIf}
  
  ; Create data directories
  CreateDirectory "$INSTDIR\data"
  CreateDirectory "$INSTDIR\logs"
  CreateDirectory "$INSTDIR\arhiva"
  
  ; Write the installation path into the registry
  WriteRegStr HKLM "Software\Punctaj" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Punctaj" "Version" "${PRODUCT_VERSION}"
  
  ; Create Add/Remove Programs entry
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" "DisplayName" "${PRODUCT_NAME} ${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" "DisplayIcon" "$INSTDIR\Punctaj_Manager.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Create Start Menu shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\${PRODUCT_NAME}.lnk" "$INSTDIR\Punctaj_Manager.exe" "" "$INSTDIR\Punctaj_Manager.exe" 0
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  !insertmacro MUI_STARTMENU_WRITE_END
  
  ; Create Desktop shortcut
  CreateShortcut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\Punctaj_Manager.exe" "" "$INSTDIR\Punctaj_Manager.exe" 0
  
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\Punctaj_Manager.exe"
  Delete "$INSTDIR\discord_config.ini"
  Delete "$INSTDIR\supabase_config.ini"
  Delete "$INSTDIR\.secure_key"
  Delete "$INSTDIR\json_encryptor.py"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remove directories (keeping data for safety)
  RMDir /r "$INSTDIR\logs"
  RMDir /r "$INSTDIR\arhiva"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Punctaj"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj"
  
  ; Remove Start Menu shortcuts
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  Delete "$SMPROGRAMS\$StartMenuFolder\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"
  
  ; Remove Desktop shortcut
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  
SectionEnd

; Language strings
LangString DESC_Install ${LANG_ENGLISH} "Install Punctaj Manager application"
LangString DESC_Install ${LANG_ROMANIAN} "Instalează aplicația Punctaj Manager"
