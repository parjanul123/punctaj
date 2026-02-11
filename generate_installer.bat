@echo off
chcp 65001 >nul
REM Punctaj Manager - Professional Installer Generator

echo.
echo ========================================
echo Punctaj Manager - Installer Generator
echo ========================================
echo.

REM Verifica NSIS
echo Checking for NSIS installation...

if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    set "NSIS=C:\Program Files (x86)\NSIS\makensis.exe"
    echo OK: NSIS found
) else if exist "C:\Program Files\NSIS\makensis.exe" (
    set "NSIS=C:\Program Files\NSIS\makensis.exe"
    echo OK: NSIS found
) else (
    echo.
    echo ERROR: NSIS not installed!
    echo.
    echo Download and install NSIS from:
    echo https://nsis.sourceforge.io/
    echo.
    pause
    exit /b 1
)

REM Verifica EXE
echo Checking for Punctaj.exe...
if not exist "dist\Punctaj.exe" (
    echo ERROR: Punctaj.exe not found in dist folder
    echo Please run PyInstaller first
    pause
    exit /b 1
)
echo OK: Punctaj.exe found

REM Verifica config files
echo Checking for config files...
if not exist "discord_config.ini" (
    echo WARNING: discord_config.ini not found
)
if not exist "supabase_config.ini" (
    echo WARNING: supabase_config.ini not found
)

echo.
echo Creating NSIS installer script...

(
echo ; Punctaj Manager Installer
echo ; Generated automatically
echo.
echo ^^^!include "MUI2.nsh"
echo.
echo Name "Punctaj Manager v2.0"
echo OutFile "installer_outputs\Punctaj_Installer.exe"
echo InstallDir "$PROGRAMFILES\Punctaj Manager"
echo RequestExecutionLevel admin
echo.
echo SetCompressor /SOLID lzma
echo.
echo ^^^!insertmacro MUI_PAGE_WELCOME
echo ^^^!insertmacro MUI_PAGE_DIRECTORY
echo ^^^!insertmacro MUI_PAGE_INSTFILES
echo ^^^!insertmacro MUI_PAGE_FINISH
echo.
echo ^^^!insertmacro MUI_LANGUAGE "Romanian"
echo.
echo Section "Instaleaza Punctaj Manager"
echo   SetOutPath "$INSTDIR"
echo   File "dist\Punctaj.exe"
echo   File "discord_config.ini"
echo   File "supabase_config.ini"
echo   CreateDirectory "$INSTDIR\data"
echo   CreateDirectory "$INSTDIR\arhiva"
echo   CreateDirectory "$INSTDIR\logs"
echo   CreateDirectory "$SMPROGRAMS\Punctaj Manager"
echo   CreateShortCut "$SMPROGRAMS\Punctaj Manager\Punctaj Manager.lnk" "$INSTDIR\Punctaj.exe"
echo   CreateShortCut "$SMPROGRAMS\Punctaj Manager\Dezinstaleaza.lnk" "$INSTDIR\Uninstall.exe"
echo   CreateShortCut "$DESKTOP\Punctaj Manager.lnk" "$INSTDIR\Punctaj.exe"
echo   WriteUninstaller "$INSTDIR\Uninstall.exe"
echo   WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" "DisplayName" "Punctaj Manager v2.0"
echo   WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" "UninstallString" "$INSTDIR\Uninstall.exe"
echo   WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" "InstallLocation" "$INSTDIR"
echo   WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" "DisplayVersion" "2.0"
echo   MessageBox MB_OK "Punctaj Manager a fost instalat cu succes!"
echo SectionEnd
echo.
echo Section "Uninstall"
echo   Delete "$SMPROGRAMS\Punctaj Manager\Punctaj Manager.lnk"
echo   Delete "$SMPROGRAMS\Punctaj Manager\Dezinstaleaza.lnk"
echo   RMDir "$SMPROGRAMS\Punctaj Manager"
echo   Delete "$DESKTOP\Punctaj Manager.lnk"
echo   Delete "$INSTDIR\Punctaj.exe"
echo   Delete "$INSTDIR\Uninstall.exe"
echo   RMDir "$INSTDIR"
echo   DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager"
echo   MessageBox MB_OK "Dezinstalaree completă!"
echo SectionEnd
) > _installer_temp.nsi

echo OK: NSIS script created
echo.
echo Compiling with NSIS...
echo Please wait...
echo.

"%NSIS%" /V2 "_installer_temp.nsi"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Installer created!
    echo ========================================
    echo.
    echo Location: installer_outputs\Punctaj_Installer.exe
    echo.
    echo Files included:
    echo   - Punctaj.exe
    echo   - discord_config.ini
    echo   - supabase_config.ini
    echo   - Data directories
    echo   - Desktop and Start Menu shortcuts
    echo.
    del "_installer_temp.nsi"
    start "" "explorer.exe" "%CD%\installer_outputs"
) else (
    echo.
    echo ERROR: NSIS compilation failed!
    echo.
)

echo.
pause
