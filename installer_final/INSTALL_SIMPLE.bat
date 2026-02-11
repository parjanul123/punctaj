@echo off
REM Punctaj Manager - Simple Installer
REM This installer copies the application and creates shortcuts

setlocal enabledelayedexpansion
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║          PUNCTAJ MANAGER - Installation                          ║
echo ║       Cloud-Enabled Employee Attendance Tracking v2.0.0           ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

REM Check Admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

set INSTALL_PATH=%PROGRAMFILES%\Punctaj Manager
echo Installing to: %INSTALL_PATH%

REM Create directory
if exist "%INSTALL_PATH%" (
    echo Backing up previous version...
    rename "%INSTALL_PATH%" "Punctaj Manager_old" >nul 2>&1
)

mkdir "%INSTALL_PATH%" 2>nul

REM Copy files
echo.
echo Copying application files...
copy /Y "punctaj.exe" "%INSTALL_PATH%\" >nul
copy /Y "*.ini" "%INSTALL_PATH%\" >nul
copy /Y "*.txt" "%INSTALL_PATH%\" >nul

if not exist "%INSTALL_PATH%\punctaj.exe" (
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo ✓ Files copied successfully

REM Create shortcuts
echo.
echo Creating shortcuts...
powershell -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$link = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Punctaj Manager.lnk'); " ^
    "$link.TargetPath = '%INSTALL_PATH%\punctaj.exe'; " ^
    "$link.WorkingDirectory = '%INSTALL_PATH%'; " ^
    "$link.Save()" >nul 2>&1

echo ✓ Shortcut created on Desktop

REM Installation complete
echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║              ✓ INSTALLATION COMPLETE!                            ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo Installed to: %INSTALL_PATH%
echo.
echo To run: Double-click "Punctaj Manager" on your Desktop
echo.
echo ☁️  Cloud sync is enabled!
echo.

setlocal
set /p LAUNCH="Launch application now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    start "" "%INSTALL_PATH%\punctaj.exe"
)

pause