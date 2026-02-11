@echo off
REM ============================================================
REM PREPARE DISTRIBUTION - WITHOUT PYINSTALLER
REM Copies all files needed for distribution
REM ============================================================

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================
echo  PREPARE DISTRIBUTION PACKAGE
echo ============================================================
echo.

set SOURCE_DIR=D:\punctaj
set DIST_DIR=D:\punctaj\setup_output\dist
set EXE_OUTPUT=%DIST_DIR%\PunctajManager_v2.5

echo Creating distribution folder...
if exist "%EXE_OUTPUT%" (
    rmdir /s /q "%EXE_OUTPUT%" 2>nul
)
mkdir "%EXE_OUTPUT%"

echo.
echo Copying application files...

REM Core application files
set APP_FILES=^
    punctaj.py ^
    admin_permissions.py ^
    discord_auth.py ^
    supabase_sync.py ^
    realtime_sync.py ^
    permission_sync_fix.py ^
    permission_check_helpers.py ^
    action_logger.py ^
    config_resolver.py ^
    organization_view.py ^
    admin_panel.py ^
    admin_permissions.py ^
    admin_ui.py

for %%F in (%APP_FILES%) do (
    if exist "%SOURCE_DIR%\%%F" (
        copy "%SOURCE_DIR%\%%F" "%EXE_OUTPUT%\" >nul 2>&1
        echo   ✓ %%F
    )
)

echo.
echo Copying configuration templates...

set CONFIG_FILES=^
    discord_config.ini ^
    supabase_config.ini

for %%F in (%CONFIG_FILES%) do (
    if exist "%SOURCE_DIR%\%%F" (
        copy "%SOURCE_DIR%\%%F" "%EXE_OUTPUT%\" >nul 2>&1
        echo   ✓ %%F
    )
)

echo.
echo Copying documentation...

set DOC_FILES=^
    GRANULAR_PERMISSIONS_GUIDE.md ^
    QUICK_PERMISSIONS_REFERENCE.md ^
    00_START_HERE_IMPLEMENTATION.md ^
    00_FINAL_SUMMARY.md ^
    PERMISSION_SYNC_FIX.md ^
    AUTO_REGISTRATION_DISCORD.md

for %%F in (%DOC_FILES%) do (
    if exist "%SOURCE_DIR%\%%F" (
        copy "%SOURCE_DIR%\%%F" "%EXE_OUTPUT%\" >nul 2>&1
        echo   ✓ %%F
    )
)

echo.
echo Creating launcher scripts...

REM Create main launcher batch
(
    echo @echo off
    echo title Punctaj Manager v2.5
    echo cd /d "%%~dp0"
    echo python punctaj.py
    echo if !ERRORLEVEL! neq 0 (
    echo     echo.
    echo     echo Error: Python not found or application crashed
    echo     pause
    echo ^)
) > "%EXE_OUTPUT%\launch.bat"
echo   ✓ launch.bat

REM Create launcher VBS (runs hidden)
(
    echo Set WshShell = CreateObject("WScript.Shell"^)
    echo Set fso = CreateObject("Scripting.FileSystemObject"^)
    echo scriptDir = fso.GetParentFolderName(WScript.ScriptFullName^)
    echo WshShell.CurrentDirectory = scriptDir
    echo WshShell.Run "python punctaj.py", 0, False
) > "%EXE_OUTPUT%\launch.vbs"
echo   ✓ launch.vbs

REM Create PowerShell launcher
(
    echo $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    echo Set-Location $scriptDir
    echo ^& python punctaj.py
) > "%EXE_OUTPUT%\launch.ps1"
echo   ✓ launch.ps1

REM Create README
(
    echo PUNCTAJ MANAGER v2.5
    echo ===================
    echo.
    echo TO RUN:
    echo -------
    echo 1. Double-click: launch.bat
    echo 2. Or: launch.vbs (silent launch^)
    echo.
    echo REQUIREMENTS:
    echo ------------
    echo - Python 3.7 or higher
    echo - Internet connection
    echo - Discord account
    echo.
    echo CONFIGURATION:
    echo ---------------
    echo 1. Edit discord_config.ini with Discord OAuth credentials
    echo 2. Edit supabase_config.ini with Supabase API key
    echo 3. Run launch.bat
    echo.
    echo FEATURES:
    echo --------
    echo - Real-Time Cloud Sync ^(30 seconds^)
    echo - Real-Time Permission Sync ^(5 seconds^)
    echo - Auto-User Registration on Discord login
    echo - Granular Permission Control per Institution
    echo - Admin Panel for user management
    echo.
    echo DOCUMENTATION:
    echo ---------------
    echo - GRANULAR_PERMISSIONS_GUIDE.md - Permission system
    echo - QUICK_PERMISSIONS_REFERENCE.md - Quick setup guide
    echo - 00_START_HERE_IMPLEMENTATION.md - Full implementation guide
    echo.
) > "%EXE_OUTPUT%\README.txt"
echo   ✓ README.txt

echo.
echo ============================================================
echo DISTRIBUTION PACKAGE READY
echo ============================================================
echo.
echo Location: %EXE_OUTPUT%
echo.
echo Files: %EXE_OUTPUT%\
echo.
echo To distribute:
echo   1. Zip the entire folder: %EXE_OUTPUT%
echo   2. Send to clients
echo   3. Clients extract and run: launch.bat
echo.
echo Requirements for clients:
echo   - Python 3.7+ (must be in PATH^)
echo   - Discord account
echo   - Supabase API key
echo.

pause
