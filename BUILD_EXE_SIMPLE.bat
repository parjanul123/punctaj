@echo off
REM ============================================================
REM BUILD PUNCTAJ MANAGER EXE WITHOUT PYINSTALLER
REM Creates a wrapped executable that can run the Python app
REM ============================================================

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================
echo  PUNCTAJ MANAGER v2.5 - EXE BUILDER
echo ============================================================
echo.

set SOURCE_DIR=D:\punctaj
set DIST_DIR=D:\punctaj\setup_output\dist
set BUILD_DIR=D:\punctaj\build_temp

REM Check if source directory exists
if not exist "%SOURCE_DIR%\punctaj.py" (
    echo ERROR: punctaj.py not found in %SOURCE_DIR%
    exit /b 1
)

echo Checking requirements...
echo.

REM Check Python
where python >nul 2>&1
if !ERRORLEVEL! neq 0 (
    where python3 >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo ERROR: Python is not installed or not in PATH!
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

echo [OK] Python found: !PYTHON!
echo.

REM Check PyInstaller
echo Checking for PyInstaller...
%PYTHON% -m pip list 2>nul | find /I "pyinstaller" >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo [INSTALLING] PyInstaller...
    %PYTHON% -m pip install pyinstaller >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo ERROR: Failed to install PyInstaller
        exit /b 1
    )
    echo [OK] PyInstaller installed
) else (
    echo [OK] PyInstaller found
)

echo.
echo Building EXE...
echo.

REM Create build directory
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%" 2>nul
)
mkdir "%BUILD_DIR%"

REM Build EXE using PyInstaller
cd /d "%SOURCE_DIR%"

%PYTHON% -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "PunctajManager" ^
    --add-data "discord_config.ini;." ^
    --add-data "supabase_config.ini;." ^
    --add-data "data;data" ^
    --distpath "%DIST_DIR%\exe_output" ^
    --buildpath "%BUILD_DIR%" ^
    --specpath "%BUILD_DIR%" ^
    punctaj.py

if !ERRORLEVEL! neq 0 (
    echo.
    echo ERROR: Build failed!
    exit /b 1
)

echo.
echo ============================================================
echo BUILD SUCCESSFUL!
echo ============================================================
echo.
echo EXE created: %DIST_DIR%\exe_output\PunctajManager.exe
echo.

REM Clean up
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%" 2>nul
)

exit /b 0
