@echo off
title Punctaj Manager v2.5 Setup
setlocal enabledelayedexpansion

color 0B
cls

echo.
echo ============================================================
echo     PUNCTAJ MANAGER v2.5 PROFESSIONAL INSTALLER
echo ============================================================
echo.
echo This will install Punctaj Manager on your computer.
echo.
echo Required:
echo   - Python 3.7 or higher
echo   - Windows 7 or later
echo   - 512 MB RAM minimum
echo   - Internet connection
echo.
echo Installation Path:
echo   %APPDATA%\PunctajManager
echo.
echo Click any key to continue...
echo.
pause>nul

REM Check Python installation
echo.
echo Checking Python installation...
echo.
where python >nul 2>&1
if 0 neq 0 (
    where python3 >nul 2>&1
    if 0 neq 0 (
        echo.
        echo ERROR: Python is not installed or not in PATH
        echo.
        echo Install Python from: https://www.python.org/
        echo.
        echo Important: During installation, check:
        echo   "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
)

echo ✓ Python found
echo.

REM Run the setup installer
echo Running setup wizard...
echo.
python SETUP_INSTALLER.py

if 0 equ 0 (
    echo.
    echo ============================================================
    echo ✓ INSTALLATION COMPLETE
    echo ============================================================
    echo.
    echo Application installed to:
    echo   %APPDATA%\PunctajManager
    echo.
    echo You can:
    echo   1. Click "Punctaj Manager" in Windows Start Menu
    echo   2. Run: launch_punctaj.bat
    echo   3. Create desktop shortcut
    echo.
    echo Thanks for installing
    echo.
    pause
) else (
    echo.
    echo ============================================================
    echo ✗ INSTALLATION FAILED
    echo ============================================================
    echo.
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)
