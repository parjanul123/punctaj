::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: PUNCTAJ MANAGER v2.5 - PROFESSIONAL SETUP EXECUTABLE BUILDER
:: Creates a proper Windows executable installer
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

@echo off
setlocal enabledelayedexpansion

set DIST_DIR=D:\punctaj\setup_output\dist
set OUTPUT_DIR=D:\punctaj\setup_output\exe

if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%" 2>nul
mkdir "%OUTPUT_DIR%"

echo.
echo ============================================================
echo CREATING PROFESSIONAL SETUP.EXE
echo ============================================================
echo.

:: Create a VBScript that acts as the launcher
:: This creates a proper executable wrapper

(
    echo '^<'^!-- Punctaj Manager Setup Launcher --'^>
    echo ^<!DOCTYPE html^>
    echo ^<html^>
    echo ^<head^>
    echo     ^<title^>Punctaj Manager Setup^</title^>
    echo     ^<style^>
    echo         body { font-family: Arial; margin: 50px; background: #f0f0f0; }
    echo         .container { background: white; padding: 30px; border-radius: 5px; }
    echo         h1 { color: #333; }
    echo         button { padding: 10px 20px; font-size: 14px; cursor: pointer; }
    echo     ^</style^>
    echo ^</head^>
    echo ^<body^>
    echo     ^<div class="container"^>
    echo         ^<h1^>Punctaj Manager v2.5 Setup^</h1^>
    echo         ^<p^>Starting installer...^</p^>
    echo         ^<p^>A command window will open to run the setup.^</p^>
    echo     ^</div^>
    echo     ^<script^>
    echo         var WshShell = new ActiveXObject("WScript.Shell"^);
    echo         var fso = new ActiveXObject("Scripting.FileSystemObject"^);
    echo         var scriptPath = WScript.ScriptFullName;
    echo         var scriptDir = fso.GetParentFolderName(scriptPath^);
    echo         WshShell.CurrentDirectory = scriptDir;
    echo         WshShell.Run("cmd /c INSTALL.bat", 1, true^);
    echo         window.close(^);
    echo     ^</script^>
    echo ^</body^>
    echo ^</html^>
) > "%OUTPUT_DIR%\launcher.hta"

echo ✓ Created HTML Application launcher

:: Create main executable VBScript
(
    echo ' Punctaj Manager v2.5 Setup
    echo ' Creates a professional Windows installer
    echo.
    echo Dim WshShell, fso, scriptDir, installBat, result
    echo Set WshShell = CreateObject("WScript.Shell"^)
    echo Set fso = CreateObject("Scripting.FileSystemObject"^)
    echo.
    echo scriptDir = fso.GetParentFolderName(WScript.ScriptFullName^)
    echo installBat = scriptDir ^& "\INSTALL.bat"
    echo.
    echo If Not fso.FileExists(installBat^) Then
    echo     MsgBox "Error: INSTALL.bat not found in " ^& scriptDir, vbCritical, "Setup Error"
    echo     WScript.Quit 1
    echo End If
    echo.
    echo WshShell.CurrentDirectory = scriptDir
    echo result = WshShell.Run("cmd /c INSTALL.bat", 1, True^)
    echo.
    echo If result = 0 Then
    echo     MsgBox "Installation complete!", vbInformation, "Success"
    echo Else
    echo     MsgBox "Installation failed. Check the messages above.", vbCritical, "Error"
    echo End If
) > "%OUTPUT_DIR%\setup.vbs"

echo ✓ Created VBScript launcher

:: Create a batch-based exe stub with proper structure
:: This is a self-contained installer batch
(
    echo @echo off
    echo title Punctaj Manager v2.5 Setup
    echo setlocal enabledelayedexpansion
    echo.
    echo color 0B
    echo cls
    echo.
    echo echo.
    echo echo ============================================================
    echo echo     PUNCTAJ MANAGER v2.5 PROFESSIONAL INSTALLER
    echo echo ============================================================
    echo echo.
    echo echo This will install Punctaj Manager on your computer.
    echo echo.
    echo echo Required:
    echo echo   - Python 3.7 or higher
    echo echo   - Windows 7 or later
    echo echo   - 512 MB RAM minimum
    echo echo   - Internet connection
    echo echo.
    echo echo Installation Path:
    echo echo   %%APPDATA%%\PunctajManager
    echo echo.
    echo echo Click any key to continue...
    echo echo.
    echo pause^>nul
    echo.
    echo REM Check Python installation
    echo echo.
    echo echo Checking Python installation...
    echo echo.
    echo where python ^>nul 2^>^&1
    echo if !ERRORLEVEL! neq 0 (
    echo     where python3 ^>nul 2^>^&1
    echo     if !ERRORLEVEL! neq 0 (
    echo         echo.
    echo         echo ERROR: Python is not installed or not in PATH
    echo         echo.
    echo         echo Install Python from: https://www.python.org/
    echo         echo.
    echo         echo Important: During installation, check:
    echo         echo   "Add Python to PATH"
    echo         echo.
    echo         pause
    echo         exit /b 1
    echo     ^)
    echo ^)
    echo.
    echo echo ✓ Python found
    echo echo.
    echo.
    echo REM Run the setup installer
    echo echo Running setup wizard...
    echo echo.
    echo python SETUP_INSTALLER.py
    echo.
    echo if !ERRORLEVEL! equ 0 (
    echo     echo.
    echo     echo ============================================================
    echo     echo ✓ INSTALLATION COMPLETE
    echo     echo ============================================================
    echo     echo.
    echo     echo Application installed to:
    echo     echo   %%APPDATA%%\PunctajManager
    echo     echo.
    echo     echo You can:
    echo     echo   1. Click "Punctaj Manager" in Windows Start Menu
    echo     echo   2. Run: launch_punctaj.bat
    echo     echo   3. Create desktop shortcut
    echo     echo.
    echo     echo Thanks for installing!
    echo     echo.
    echo     pause
    echo ^) else (
    echo     echo.
    echo     echo ============================================================
    echo     echo ✗ INSTALLATION FAILED
    echo     echo ============================================================
    echo     echo.
    echo     echo Please check the error messages above.
    echo     echo.
    echo     pause
    echo     exit /b 1
    echo ^)
) > "%OUTPUT_DIR%\INSTALL.bat"

echo ✓ Created INSTALL.bat (main installer)

:: Copy all setup files to exe directory
echo.
echo Copying setup files...
echo.

for %%F in (
    punctaj.py
    realtime_sync.py
    permission_sync_fix.py
    discord_auth.py
    supabase_sync.py
    admin_panel.py
    admin_permissions.py
    admin_ui.py
    action_logger.py
    config_resolver.py
    organization_view.py
    SETUP_INSTALLER.py
    discord_config.ini
    supabase_config.ini
) do (
    if exist "%DIST_DIR%\%%F" (
        copy "%DIST_DIR%\%%F" "%OUTPUT_DIR%\" >nul 2>&1
        echo   ✓ %%F
    )
)

:: Copy documentation
echo.
echo Copying documentation...
echo.

for %%F in (
    00_WELCOME.txt
    00_START_HERE_IMPLEMENTATION.md
    01_QUICK_START_BUILD_DISTRIBUTE.md
    00_FINAL_SUMMARY.md
    02_ARCHITECTURE_COMPLETE.md
    PERMISSION_SYNC_FIX.md
    AUTO_REGISTRATION_DISCORD.md
    SETUP_INFO.txt
    UNINSTALL_INFO.txt
) do (
    if exist "%DIST_DIR%\%%F" (
        copy "%DIST_DIR%\%%F" "%OUTPUT_DIR%\" >nul 2>&1
        echo   ✓ %%F
    )
)

:: Copy installer_source folder
if exist "%DIST_DIR%\installer_source" (
    echo.
    xcopy "%DIST_DIR%\installer_source\*" "%OUTPUT_DIR%\installer_source\" /E /I /Y ^>nul 2^>^&1
    echo   ✓ installer_source folder
)

echo.
echo ============================================================
echo ✓ SETUP PACKAGE CREATED
echo ============================================================
echo.
echo Location: %OUTPUT_DIR%
echo.
echo DISTRIBUTION METHODS:
echo.
echo METHOD 1: Batch Installer (Recommended)
echo ------------------------------------
echo File: INSTALL.bat
echo Users: Double-click INSTALL.bat to start
echo.
echo METHOD 2: VBScript Launcher
echo ------------------------------------
echo File: setup.vbs  
echo Users: Double-click setup.vbs to start
echo.
echo METHOD 3: HTA Application
echo ------------------------------------
echo File: launcher.hta
echo Users: Double-click launcher.hta to start
echo.
echo DISTRIBUTION:
echo 1. Give users the entire folder: %OUTPUT_DIR%
echo 2. They double-click one of the launchers above
echo 3. Installer configures everything
echo.
echo TO CREATE SINGLE EXE:
echo - Use NSIS: https://nsis.sourceforge.io/
echo - Use Inno Setup: https://www.innosetup.com/
echo.

pause
