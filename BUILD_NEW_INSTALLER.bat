@echo off
REM ====================================================================
REM PUNCTAJ APPLICATION - COMPLETE INSTALLER BUILDER
REM ====================================================================
REM Usage: BUILD_INSTALLER.bat
REM Creates: Punctaj_Manager_Setup.exe
REM ====================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================================================
echo  PUNCTAJ MANAGER v2.0 - INSTALLER BUILDER
echo ====================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or later from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [1/3] Installing PyInstaller...
    python -m pip install pyinstaller -q
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo [OK] PyInstaller installed
) else (
    echo [OK] PyInstaller already installed
)

echo.
echo [2/3] Building executable with PyInstaller...
echo.

REM Run the main builder script
python BUILD_INSTALLER_COMPLETE.py
if errorlevel 1 (
    echo.
    echo [ERROR] Installer build failed
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo  BUILD COMPLETE
echo ====================================================================
echo.
echo Location: %CD%\installer_output\
echo.
echo Next steps:
echo   1. Check the installer_output directory
echo   2. Look for Punctaj_Manager_Setup.exe
echo   3. Run the installer to test it
echo.
pause
exit /b 0
