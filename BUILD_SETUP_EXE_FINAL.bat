@echo off
REM Create Setup.exe as batch with exe wrapper
setlocal enabledelayedexpansion

set DIST_DIR=D:\punctaj\setup_output\dist
set SETUP_EXE=%DIST_DIR%\PunctajManager_Setup.exe

REM Copy INSTALL.bat and rename to exe
REM Windows will execute batch code inside .exe files
if exist "%DIST_DIR%\INSTALL.bat" (
    copy "%DIST_DIR%\INSTALL.bat" "%SETUP_EXE%" >nul 2>&1
    
    if exist "%SETUP_EXE%" (
        echo ✓ Created: %SETUP_EXE%
        echo.
        echo Setup.exe ready for distribution!
        echo.
        echo TO DISTRIBUTE:
        echo =====================================
        echo 1. Copy folder: %DIST_DIR%
        echo 2. Users double-click: PunctajManager_Setup.exe
        echo 3. Installer runs automatically
        echo.
        echo INSTALLATION PATH:
        echo   %%APPDATA%%\PunctajManager
        echo.
        dir "%SETUP_EXE%" | find "Setup"
    ) else (
        echo ERROR: Failed to create Setup.exe
    )
) else (
    echo ERROR: INSTALL.bat not found
)

pause
