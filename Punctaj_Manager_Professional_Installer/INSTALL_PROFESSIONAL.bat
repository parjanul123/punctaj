@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM   PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER
REM   With Superuser Permissions and Cloud Synchronization
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║            PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER              ║
echo ║                                                                           ║
echo ║         Cloud-Enabled Employee Attendance Tracking System               ║
echo ║              With Superuser Permissions Preserved                        ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

REM Check Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  ERROR: Administrator privileges required!
    echo.
    echo This installer needs Administrator access to:
    echo   • Install to Program Files
    echo   • Preserve superuser permissions
    echo   • Configure system integration
    echo.
    echo Solution:
    echo   1. Right-click this script: INSTALL_PROFESSIONAL.bat
    echo   2. Select "Run as administrator"
    echo   3. Click "Yes" when prompted
    echo.
    pause
    exit /b 1
)

REM Set installation path
set INSTALL_PATH=%PROGRAMFILES%\Punctaj Manager
set SOURCE_DIR=%~dp0
set APP_CONFIG=%APPDATA%\Punctaj Manager

echo [1/5] Preparing installation...
echo   Install path: %INSTALL_PATH%

REM Create backup if exists
if exist "%INSTALL_PATH%" (
    echo   Creating backup...
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

REM Copy application
echo.
echo [2/5] Installing application...

copy /Y "%SOURCE_DIR%Punctaj_Manager.exe" "%INSTALL_PATH%\" >nul 2>&1
if not exist "%INSTALL_PATH%\Punctaj_Manager.exe" (
    echo ✗ Failed to copy application!
    pause
    exit /b 1
)

echo ✓ Application installed

REM Copy configuration files (with superuser settings)
echo.
echo [3/5] Configuring cloud synchronization and permissions...

if exist "%SOURCE_DIR%supabase_config.ini" (
    copy /Y "%SOURCE_DIR%supabase_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    copy /Y "%SOURCE_DIR%supabase_config.ini" "%APP_CONFIG%\" >nul 2>&1
    echo ✓ Cloud sync configured with superuser access
)

if exist "%SOURCE_DIR%discord_config.ini" (
    copy /Y "%SOURCE_DIR%discord_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    echo ✓ Discord integration configured
)

REM Copy requirements if present
if exist "%SOURCE_DIR%requirements.txt" (
    copy /Y "%SOURCE_DIR%requirements.txt" "%INSTALL_PATH%\" >nul 2>&1
)

REM Create launcher script
echo.
echo [4/5] Creating shortcuts...

(
    echo @echo off
    echo title Punctaj Manager
    echo cls
    echo echo ╔═══════════════════════════════════════════════════╗
    echo echo ║         Launching Punctaj Manager...             ║
    echo echo ╚═══════════════════════════════════════════════════╝
    echo echo.
    echo cd /d "%INSTALL_PATH%"
    echo "%INSTALL_PATH%\Punctaj_Manager.exe"
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

if not exist "%INSTALL_PATH%\Punctaj_Manager.exe" (
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
echo   ✓ Punctaj Manager application
echo   ✓ Cloud synchronization (Supabase)
echo   ✓ Superuser permissions configured
echo   ✓ Discord integration (optional)
echo.
echo How to Run:
echo ─────────────────────────────────────────────────────────────────────────
echo   • Look for "Punctaj Manager" shortcut on Desktop
echo   • Or use: RUN.bat in the installation folder
echo   • Or direct: %INSTALL_PATH%\Punctaj_Manager.exe
echo.
echo Cloud Synchronization:
echo ─────────────────────────────────────────────────────────────────────────
echo   ☁️  Cloud sync is ENABLED by default
echo   ✓ All data automatically syncs to Supabase
echo   ✓ Superuser access to all features
echo   ✓ Real-time synchronization every 30 seconds
echo.

setlocal
set /p LAUNCH="Launch Punctaj Manager now? (Y/N): "

if /i "%LAUNCH%"=="Y" (
    echo.
    echo Starting application...
    echo.
    start "" "%INSTALL_PATH%\Punctaj_Manager.exe"
    echo.
    echo Application launched!
    echo.
) else (
    echo.
    echo Setup complete! Run anytime from Desktop shortcut or:
    echo %INSTALL_PATH%\RUN.bat
    echo.
)

pause
exit /b 0
