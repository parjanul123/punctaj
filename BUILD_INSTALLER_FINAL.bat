@echo off
REM ==================================================================
REM Punctaj Manager Installer Builder - Fixed UI
REM ==================================================================

setlocal enabledelayedexpansion

REM Cauta Python instalat
for /F "delims=" %%A in ('py --version 2^>nul') do set PYTHON=py
if "!PYTHON!"=="" (
    REM Incearca python3
    for /F "delims=" %%A in ('python3 --version 2^>nul') do set PYTHON=python3
)
if "!PYTHON!"=="" (
    REM Incearca python
    for /F "delims=" %%A in ('python --version 2^>nul') do set PYTHON=python
)
if "!PYTHON!"=="" (
    echo.
    echo ===============================================================
    echo ERROR: Python not found!
    echo ===============================================================
    echo.
    echo Install Python 3.8+ from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Found Python: !PYTHON!
echo.

REM Run the installer builder
echo Starting installer build...
echo.

!PYTHON! CREATE_INSTALLER_FIXED.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful! Check dist folder for punctaj_installer.exe
pause
