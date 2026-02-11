@echo off
REM ============================================================
REM PUNCTAJ MANAGER v2.5 - SETUP.EXE INSTALLER
REM Self-Extracting Archive
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo  PUNCTAJ MANAGER v2.5 - SETUP INSTALLER
echo ============================================================
echo.

REM Check if we can create the installer
set SCRIPT_DIR=%~dp0
set OUTPUT_DIR=%SCRIPT_DIR%setup_output
set DIST_DIR=%OUTPUT_DIR%\dist

if exist "%OUTPUT_DIR%" (
    echo Cleaning previous builds...
    rmdir /s /q "%OUTPUT_DIR%" 2>nul
)

mkdir "%DIST_DIR%" 2>nul

echo.
echo Creating installer files...
echo.

REM Copy all necessary files to dist
set FILES=^
    punctaj.py ^
    realtime_sync.py ^
    permission_sync_fix.py ^
    discord_auth.py ^
    supabase_sync.py ^
    admin_panel.py ^
    admin_permissions.py ^
    admin_ui.py ^
    action_logger.py ^
    config_resolver.py ^
    json_logger.py ^
    organization_view.py ^
    SETUP_INSTALLER.py ^
    discord_config.ini ^
    supabase_config.ini

for %%F in (%FILES%) do (
    if exist "%SCRIPT_DIR%%%F" (
        copy "%SCRIPT_DIR%%%F" "%DIST_DIR%\" >nul 2>&1
        echo   ✓ %%F
    )
)

REM Copy documentation
echo.
echo Copying documentation...
echo.

set DOCS=^
    00_WELCOME.txt ^
    00_START_HERE_IMPLEMENTATION.md ^
    01_QUICK_START_BUILD_DISTRIBUTE.md ^
    00_FINAL_SUMMARY.md ^
    02_ARCHITECTURE_COMPLETE.md ^
    PERMISSION_SYNC_FIX.md ^
    AUTO_REGISTRATION_DISCORD.md

for %%F in (%DOCS%) do (
    if exist "%SCRIPT_DIR%%%F" (
        copy "%SCRIPT_DIR%%%F" "%DIST_DIR%\" >nul 2>&1
        echo   ✓ %%F
    )
)

REM Copy installer_source
if exist "%SCRIPT_DIR%installer_source" (
    echo.
    echo Copying installer_source...
    xcopy "%SCRIPT_DIR%installer_source\*" "%DIST_DIR%\installer_source\" /E /I /Y >nul 2>&1
    echo   ✓ installer_source folder
)

REM Create launcher scripts
echo.
echo Creating launcher scripts...
echo.

REM Create launch.bat
(
    echo @echo off
    echo title Punctaj Manager Launcher
    echo cd /d "%%APPDATA%%\PunctajManager"
    echo python punctaj.py
    echo pause
) > "%DIST_DIR%\launch_punctaj.bat"
echo   ✓ launch_punctaj.bat

REM Create README
(
    echo.
    echo PUNCTAJ MANAGER v2.5 INSTALLER
    echo ========================================
    echo.
    echo This installer contains:
    echo   ✓ Complete Python application
    echo   ✓ All necessary modules
    echo   ✓ Configuration templates
    echo   ✓ Setup wizard
    echo.
    echo INSTALLATION:
    echo 1. Extract all files to d:\punctaj\
    echo 2. Edit discord_config.ini with your credentials
    echo 3. Edit supabase_config.ini with your Supabase API
    echo 4. Run: python SETUP_INSTALLER.py
    echo.
    echo After installation:
    echo   Application installs to: %%APPDATA%%\PunctajManager
    echo   You can launch it anytime from:
    echo   - Start Menu (Punctaj Manager)
    echo   - launch_punctaj.bat
    echo   - launch_punctaj.py
    echo.
    echo FEATURES:
    echo   ✓ Real-Time Cloud Sync (30 sec)
    echo   ✓ Real-Time Permission Sync (5 sec)
    echo   ✓ Auto-User Registration
    echo   ✓ Discord OAuth2 Login
    echo.
    echo Need help? See:
    echo   - 00_START_HERE_IMPLEMENTATION.md
    echo   - 01_QUICK_START_BUILD_DISTRIBUTE.md
    echo.
) > "%DIST_DIR%\INSTALLER_README.txt"
echo   ✓ INSTALLER_README.txt

REM Create main installer batch
(
    echo @echo off
    echo setlocal enabledelayedexpansion
    echo.
    echo cls
    echo echo.
    echo echo ========================================
    echo echo PUNCTAJ MANAGER v2.5 INSTALLER
    echo echo ========================================
    echo echo.
    echo echo This will install Punctaj Manager
    echo echo to your computer.
    echo echo.
    echo echo Installation path:
    echo echo   %%APPDATA%%\PunctajManager
    echo echo.
    echo pause
    echo.
    echo REM Check Python
    echo where python >nul 2^>^&1
    echo if !ERRORLEVEL! neq 0 (
    echo     echo.
    echo     echo ERROR: Python is not installed or not in PATH
    echo     echo.
    echo     echo Please install Python from https://www.python.org/
    echo     echo.
    echo     pause
    echo     exit /b 1
    echo ^)
    echo.
    echo REM Run SETUP_INSTALLER.py
    echo echo Running setup...
    echo python SETUP_INSTALLER.py
    echo.
    echo if !ERRORLEVEL! equ 0 (
    echo     echo.
    echo     echo ========================================
    echo     echo ✓ INSTALLATION COMPLETE
    echo     echo ========================================
    echo     echo.
    echo     echo Application installed to:
    echo     echo   %%APPDATA%%\PunctajManager
    echo     echo.
    echo     pause
    echo ^) else (
    echo     echo.
    echo     echo ✗ INSTALLATION FAILED
    echo     echo.
    echo     pause
    echo ^)
) > "%DIST_DIR%\INSTALL.bat"
echo   ✓ INSTALL.bat (main installer)

REM Create uninstaller info
(
    echo How to uninstall Punctaj Manager:
    echo.
    echo 1. Open Windows Start Menu
    echo 2. Find "Punctaj Manager"
    echo 3. Right-click and select "Uninstall"
    echo.
    echo OR manually:
    echo 1. Delete folder: %%APPDATA%%\PunctajManager
    echo 2. Delete Start Menu shortcut: %%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Punctaj Manager
    echo.
) > "%DIST_DIR%\UNINSTALL_INFO.txt"
echo   ✓ UNINSTALL_INFO.txt

REM Create setup info
(
    echo PUNCTAJ MANAGER v2.5
    echo Setup Information
    echo.
    echo VERSION: 2.5 with Real-Time Sync
    echo DATE: 2026-02-03
    echo STATUS: Production Ready
    echo.
    echo REQUIREMENTS:
    echo   - Python 3.7 or higher
    echo   - Windows 7 or later
    echo   - 512 MB RAM minimum
    echo   - 200 MB disk space
    echo   - Internet connection
    echo.
    echo WHAT'S INCLUDED:
    echo   ✓ Real-Time Cloud Sync (every 30 seconds^)
    echo   ✓ Real-Time Permission Sync (every 5 seconds^)
    echo   ✓ Auto-User Registration on Discord login
    echo   ✓ Professional Setup Wizard
    echo   ✓ Admin Panel with granular permissions
    echo   ✓ Complete documentation
    echo.
    echo INSTALLATION STEPS:
    echo.
    echo 1. EXTRACT
    echo    Double-click INSTALL.bat or run it from command prompt
    echo.
    echo 2. CONFIGURE (if needed^)
    echo    Edit discord_config.ini with Discord OAuth credentials
    echo    Edit supabase_config.ini with Supabase API credentials
    echo.
    echo 3. LAUNCH
    echo    Application launches automatically after setup
    echo    Or click "Punctaj Manager" in Windows Start Menu
    echo.
    echo 4. FIRST LOGIN
    echo    Click "Login cu Discord"
    echo    Your account is auto-created in Supabase
    echo    Wait for admin to assign permissions
    echo.
    echo FEATURES:
    echo.
    echo Real-Time Cloud Sync
    echo   Database syncs every 30 seconds
    echo   Changes from other users visible instantly
    echo   No restart needed
    echo.
    echo Real-Time Permission Sync
    echo   Permissions synced every 5 seconds
    echo   Admin changes visible instantly
    echo   No restart needed
    echo.
    echo Auto-Registration
    echo   First Discord login creates your account
    echo   No manual user creation needed
    echo   Initial role: VIEWER (limited access^)
    echo.
    echo SUPPORT:
    echo   See: 00_START_HERE_IMPLEMENTATION.md
    echo.
) > "%DIST_DIR%\SETUP_INFO.txt"
echo   ✓ SETUP_INFO.txt

echo.
echo ============================================================
echo ✓ INSTALLER CREATED
echo ============================================================
echo.
echo Location: %DIST_DIR%
echo.
echo Files ready:
echo   - INSTALL.bat (main installer - RUN THIS)
echo   - All application files
echo   - All documentation
echo.
echo NEXT STEPS:
echo.
echo 1. Give users the contents of: %DIST_DIR%
echo.
echo 2. Users run: INSTALL.bat
echo.
echo 3. Setup wizard configures everything
echo.
echo 4. Application installs to: %%APPDATA%%\PunctajManager
echo.
echo Ready to distribute!
echo.

pause
