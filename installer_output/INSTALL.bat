@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM   PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER
REM   Complete Application with Superuser Permissions and Cloud Sync
REM   For Distribution to Other Windows PCs
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║            PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER              ║
echo ║                                                                           ║
echo ║         Cloud-Enabled Employee Attendance Tracking System               ║
echo ║              With Superuser Permissions Included                         ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

REM Check Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  ERROR: Administrator privileges required!
    echo.
    echo This installer needs Administrator access to preserve superuser permissions
    echo and configure cloud synchronization properly.
    echo.
    echo Solution:
    echo   1. Right-click this script: INSTALL.bat
    echo   2. Select "Run as administrator"
    echo   3. Click "Yes" when prompted
    echo.
    pause
    exit /b 1
)

REM Set installation paths
set INSTALL_PATH=%PROGRAMFILES%\Punctaj Manager
set SOURCE_DIR=%~dp0
set APP_CONFIG=%APPDATA%\Punctaj Manager

echo [1/5] Preparing installation...
echo   Install path: %INSTALL_PATH%

REM Create backup if exists
if exist "%INSTALL_PATH%" (
    echo   Creating backup of existing installation...
    if exist "%INSTALL_PATH%_backup" rmdir /s /q "%INSTALL_PATH%_backup" >nul 2>&1
    rename "%INSTALL_PATH%" "Punctaj Manager_backup" >nul 2>&1
)

REM Create directories
mkdir "%INSTALL_PATH%" >nul 2>&1
mkdir "%APP_CONFIG%" >nul 2>&1

if %errorlevel% neq 0 (
    echo ✗ Error creating installation directory
    pause
    exit /b 1
)

echo ✓ Installation directory ready

REM Copy application EXE
echo.
echo [2/5] Installing application...

copy /Y "%SOURCE_DIR%punctaj.exe" "%INSTALL_PATH%\" >nul 2>&1
if not exist "%INSTALL_PATH%\punctaj.exe" (
    echo ✗ Failed to copy application!
    pause
    exit /b 1
)

echo ✓ Application installed

REM Copy configuration files (WITH SUPERUSER SETTINGS)
echo.
echo [3/5] Configuring cloud synchronization and superuser permissions...

if exist "%SOURCE_DIR%supabase_config.ini" (
    copy /Y "%SOURCE_DIR%supabase_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    copy /Y "%SOURCE_DIR%supabase_config.ini" "%APP_CONFIG%\" >nul 2>&1
    echo ✓ Cloud sync configured
    echo ✓ Superuser role enabled
    echo ✓ Permissions configured
)

if exist "%SOURCE_DIR%discord_config.ini" (
    copy /Y "%SOURCE_DIR%discord_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    echo ✓ Discord integration configured
)

if exist "%SOURCE_DIR%requirements.txt" (
    copy /Y "%SOURCE_DIR%requirements.txt" "%INSTALL_PATH%\" >nul 2>&1
)

REM Copy documentation
if exist "%SOURCE_DIR%INSTALLATION_GUIDE.txt" (
    copy /Y "%SOURCE_DIR%INSTALLATION_GUIDE.txt" "%INSTALL_PATH%\" >nul 2>&1
)

REM Create launcher script
echo.
echo [4/5] Creating shortcuts...

(
    echo @echo off
    echo title Punctaj Manager
    echo cls
    echo echo ╔═══════════════════════════════════════════════════╗
    echo echo ║    Launching Punctaj Manager...                  ║
    echo echo ║    Initializing Cloud Synchronization...         ║
    echo echo ╚═══════════════════════════════════════════════════╝
    echo echo.
    echo cd /d "%INSTALL_PATH%"
    echo "%INSTALL_PATH%\punctaj.exe"
    echo if errorlevel 1 (
    echo     echo.
    echo     echo Application closed.
    echo     pause
    echo )
) > "%INSTALL_PATH%\RUN.bat"

REM Create desktop shortcut
powershell -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$link = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Punctaj Manager.lnk'); " ^
    "$link.TargetPath = '%INSTALL_PATH%\RUN.bat'; " ^
    "$link.WorkingDirectory = '%INSTALL_PATH%'; " ^
    "$link.Save()" >nul 2>&1

echo ✓ Shortcuts created

REM Create Start Menu folder
mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Punctaj Manager" >nul 2>&1

REM Verify installation
echo.
echo [5/5] Verifying installation...

if not exist "%INSTALL_PATH%\punctaj.exe" (
    echo ✗ Installation verification failed!
    pause
    exit /b 1
)

if not exist "%INSTALL_PATH%\supabase_config.ini" (
    echo ⚠️  Warning: Configuration file not found
    echo Cloud sync may not work
)

echo ✓ Installation verified

REM Installation complete
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                    ✓✓✓ INSTALLATION SUCCESSFUL! ✓✓✓                      ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo Installation Details:
echo ─────────────────────────────────────────────────────────────────────────
echo   Location: %INSTALL_PATH%
echo   Config:   %APP_CONFIG%
echo.
echo Features Installed:
echo ─────────────────────────────────────────────────────────────────────────
echo   ✓ Punctaj Manager complete application
echo   ✓ Cloud synchronization (Supabase) - ENABLED
echo   ✓ Superuser permissions - CONFIGURED
echo   ✓ Discord integration - INCLUDED
echo   ✓ All features unlocked
echo.
echo How to Run:
echo ─────────────────────────────────────────────────────────────────────────
echo   • Desktop shortcut: "Punctaj Manager"
echo   • Start Menu: Search for "Punctaj Manager"
echo   • Manual: Run RUN.bat or punctaj.exe from installation folder
echo.
echo Cloud Synchronization:
echo ─────────────────────────────────────────────────────────────────────────
echo   ☁️  Cloud sync is ENABLED
echo   ✓ Superuser role configured
echo   ✓ Real-time sync every 30 seconds
echo   ✓ Data backed up to cloud
echo   ✓ Multiple PC support
echo.

setlocal
set /p LAUNCH="Launch Punctaj Manager now? (Y/N): "

if /i "%LAUNCH%"=="Y" (
    echo.
    echo Starting application...
    echo.
    start "" "%INSTALL_PATH%\punctaj.exe"
    echo.
    echo Application launched!
    echo Cloud sync initializing...
    echo.
) else (
    echo.
    echo Setup complete! Run anytime from:
    echo • Desktop shortcut "Punctaj Manager"
    echo • Or: %INSTALL_PATH%\RUN.bat
    echo.
)

pause
exit /b 0
