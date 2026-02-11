@echo off
REM ============================================================
REM CREATE SETUP.EXE - Batch to VBS to create self-extracting exe
REM ============================================================

setlocal enabledelayedexpansion

set DIST_DIR=D:\punctaj\setup_output\dist
set OUTPUT_EXE=D:\punctaj\setup_output\dist\PunctajManager_Setup.exe

if not exist "%DIST_DIR%" (
    echo ERROR: Setup files not found in %DIST_DIR%
    pause
    exit /b 1
)

REM Copy INSTALL.bat to a temporary location with exe stub
REM We'll create a batch-based self-extracting installer

set TEMP_INSTALL=%DIST_DIR%\INSTALL_STUB.bat

REM Create the setup.exe by renaming INSTALL.bat
REM This works because Windows can execute .exe that contain batch code
REM But we need a better approach - let's use makecab to create cabinet and batch

echo Creating Setup.exe wrapper...

REM Create a VBScript that will handle extraction
(
    echo Set objFSO = CreateObject("Scripting.FileSystemObject"^)
    echo Set WshShell = CreateObject("WScript.Shell"^)
    echo.
    echo strScriptPath = WScript.ScriptFullName
    echo strScriptFolder = objFSO.GetParentFolderName(strScriptPath^)
    echo.
    echo strInstallPath = strScriptFolder
    echo.
    echo REM Run INSTALL.bat from the same directory
    echo WshShell.CurrentDirectory = strInstallPath
    echo WshShell.Run "cmd.exe /k INSTALL.bat", 1, True
) > "%DIST_DIR%\setup.vbs"

REM Create a batch wrapper that launches the VBS
(
    echo @echo off
    echo cscript.exe "%%~dp0setup.vbs"
) > "%DIST_DIR%\setup.bat"

echo.
echo ============================================================
echo Setup preparation complete
echo ============================================================
echo.
echo To create Setup.exe, you have options:
echo.
echo OPTION 1: Use setup.bat (Batch-based installer^)
echo   File: %DIST_DIR%\INSTALL.bat
echo   Users run this to install
echo.
echo OPTION 2: Rename INSTALL.bat to Setup.exe (Windows compatible^)
echo   Windows will execute it as batch code
echo.
echo OPTION 3: Use 3rd-party tool (NSIS, Inno Setup^)
echo   Free tools that create professional .exe installers
echo.
echo For now, distribute the entire folder at:
echo   %DIST_DIR%
echo.
echo Users should:
echo 1. Extract all files
echo 2. Run INSTALL.bat
echo 3. Follow setup wizard
echo.

pause
