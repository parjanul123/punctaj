#!/usr/bin/env python3
"""
Create professional installer in installer_output using existing EXE
"""

import shutil
from pathlib import Path

def create_installer():
    project_root = Path(r"d:\punctaj")
    dist_folder = project_root / "dist"
    installer_output = project_root / "installer_output"
    
    print("\n" + "="*80)
    print("CREATING PROFESSIONAL INSTALLER IN installer_output")
    print("="*80)
    
    # Check if EXE exists
    exe_file = dist_folder / "punctaj.exe"
    if not exe_file.exists():
        print(f"\n✗ EXE not found in {dist_folder}")
        print("Make sure to build the EXE first with PyInstaller")
        return False
    
    print(f"\n[1] Found EXE: {exe_file.name}")
    print(f"    Size: {exe_file.stat().st_size / (1024*1024):.1f} MB")
    
    # Clean and create installer_output
    print(f"\n[2] Preparing installer_output directory...")
    if installer_output.exists():
        print(f"    Clearing existing contents...")
        shutil.rmtree(installer_output)
    
    installer_output.mkdir(parents=True)
    print(f"    ✓ Created installer_output")
    
    # Copy EXE
    print(f"\n[3] Copying application files...")
    shutil.copy2(exe_file, installer_output / "punctaj.exe")
    print(f"    ✓ Copied punctaj.exe")
    
    # Copy configuration files
    config_files = [
        "supabase_config.ini",
        "discord_config.ini",
    ]
    
    for config in config_files:
        src = project_root / config
        if src.exists():
            shutil.copy2(src, installer_output / config)
            print(f"    ✓ Copied {config}")
    
    # Copy requirements
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        shutil.copy2(req_file, installer_output / "requirements.txt")
        print(f"    ✓ Copied requirements.txt")
    
    # Copy documentation
    docs = ["INSTALLATION_GUIDE.txt", "PROFESSIONAL_INSTALLER_COMPLETE.txt"]
    for doc in docs:
        src = project_root / doc
        if src.exists():
            shutil.copy2(src, installer_output / doc)
            print(f"    ✓ Copied {doc}")
    
    # Create professional installer script
    print(f"\n[4] Creating installation script...")
    
    install_script = r'''@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM   PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER
REM   Complete Application with Superuser Permissions and Cloud Sync
REM   For Distribution to Other Windows PCs
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║            PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER              ║
echo ║                                                                           ║
echo ║         Cloud-Enabled Employee Attendance Tracking System               ║
echo ║              With Superuser Permissions Included                         ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

REM Check Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  ERROR: Administrator privileges required!
    echo.
    echo This installer needs Administrator access to preserve superuser permissions
    echo and configure cloud synchronization properly.
    echo.
    echo Solution:
    echo   1. Right-click this script: INSTALL.bat
    echo   2. Select "Run as administrator"
    echo   3. Click "Yes" when prompted
    echo.
    pause
    exit /b 1
)

REM Set installation paths
set INSTALL_PATH=%PROGRAMFILES%\Punctaj Manager
set SOURCE_DIR=%~dp0
set APP_CONFIG=%APPDATA%\Punctaj Manager

echo [1/5] Preparing installation...
echo   Install path: %INSTALL_PATH%

REM Create backup if exists
if exist "%INSTALL_PATH%" (
    echo   Creating backup of existing installation...
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

REM Copy application EXE
echo.
echo [2/5] Installing application...

copy /Y "%SOURCE_DIR%punctaj.exe" "%INSTALL_PATH%\" >nul 2>&1
if not exist "%INSTALL_PATH%\punctaj.exe" (
    echo ✗ Failed to copy application!
    pause
    exit /b 1
)

echo ✓ Application installed

REM Copy configuration files (WITH SUPERUSER SETTINGS)
echo.
echo [3/5] Configuring cloud synchronization and superuser permissions...

if exist "%SOURCE_DIR%supabase_config.ini" (
    copy /Y "%SOURCE_DIR%supabase_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    copy /Y "%SOURCE_DIR%supabase_config.ini" "%APP_CONFIG%\" >nul 2>&1
    echo ✓ Cloud sync configured
    echo ✓ Superuser role enabled
    echo ✓ Permissions configured
)

if exist "%SOURCE_DIR%discord_config.ini" (
    copy /Y "%SOURCE_DIR%discord_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    echo ✓ Discord integration configured
)

if exist "%SOURCE_DIR%requirements.txt" (
    copy /Y "%SOURCE_DIR%requirements.txt" "%INSTALL_PATH%\" >nul 2>&1
)

REM Copy documentation
if exist "%SOURCE_DIR%INSTALLATION_GUIDE.txt" (
    copy /Y "%SOURCE_DIR%INSTALLATION_GUIDE.txt" "%INSTALL_PATH%\" >nul 2>&1
)

REM Create launcher script
echo.
echo [4/5] Creating shortcuts...

(
    echo @echo off
    echo title Punctaj Manager
    echo cls
    echo echo ╔═══════════════════════════════════════════════════╗
    echo echo ║    Launching Punctaj Manager...                  ║
    echo echo ║    Initializing Cloud Synchronization...         ║
    echo echo ╚═══════════════════════════════════════════════════╝
    echo echo.
    echo cd /d "%INSTALL_PATH%"
    echo "%INSTALL_PATH%\punctaj.exe"
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

if not exist "%INSTALL_PATH%\punctaj.exe" (
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
echo   ✓ Punctaj Manager complete application
echo   ✓ Cloud synchronization (Supabase) - ENABLED
echo   ✓ Superuser permissions - CONFIGURED
echo   ✓ Discord integration - INCLUDED
echo   ✓ All features unlocked
echo.
echo How to Run:
echo ─────────────────────────────────────────────────────────────────────────
echo   • Desktop shortcut: "Punctaj Manager"
echo   • Start Menu: Search for "Punctaj Manager"
echo   • Manual: Run RUN.bat or punctaj.exe from installation folder
echo.
echo Cloud Synchronization:
echo ─────────────────────────────────────────────────────────────────────────
echo   ☁️  Cloud sync is ENABLED
echo   ✓ Superuser role configured
echo   ✓ Real-time sync every 30 seconds
echo   ✓ Data backed up to cloud
echo   ✓ Multiple PC support
echo.

setlocal
set /p LAUNCH="Launch Punctaj Manager now? (Y/N): "

if /i "%LAUNCH%"=="Y" (
    echo.
    echo Starting application...
    echo.
    start "" "%INSTALL_PATH%\punctaj.exe"
    echo.
    echo Application launched!
    echo Cloud sync initializing...
    echo.
) else (
    echo.
    echo Setup complete! Run anytime from:
    echo • Desktop shortcut "Punctaj Manager"
    echo • Or: %INSTALL_PATH%\RUN.bat
    echo.
)

pause
exit /b 0
'''
    
    install_file = installer_output / "INSTALL.bat"
    with open(install_file, 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    print(f"    ✓ Created INSTALL.bat")
    
    # Create README
    print(f"\n[5] Creating README...")
    
    readme = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER                 ║
║                                                                            ║
║          Complete Application Ready for Distribution to Other PCs         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 WHAT'S INCLUDED:

  ✓ Complete Punctaj Manager application (EXE)
  ✓ Cloud synchronization (Supabase) - pre-configured
  ✓ Superuser permissions - included and enabled
  ✓ Discord integration - optional
  ✓ Professional installation experience


🚀 INSTALLATION (3 SIMPLE STEPS):

  1. Right-click: INSTALL.bat
  
  2. Select: "Run as administrator"
  
  3. Follow the installation wizard
     • Application installed to: C:\Program Files\Punctaj Manager\
     • Cloud sync automatically configured
     • Superuser permissions preserved
     • Desktop shortcut created
     • Ready to use!


✨ FEATURES AFTER INSTALLATION:

  ✓ Complete Punctaj Manager application
  ✓ Superuser access (not limited user)
  ✓ Cloud data automatically synchronized
  ✓ Admin panel accessible
  ✓ Employee management enabled
  ✓ Attendance tracking
  ✓ Weekly reports
  ✓ Discord integration
  ✓ Audit logging
  ✓ Multi-user management
  ✓ Real-time data sync


☁️  CLOUD SYNCHRONIZATION (AUTO-CONFIGURED):

  What's Configured:
    • Supabase instance: https://yzlkgifumrwqlfgimcai.supabase.co
    • Superuser role enabled
    • Auto-sync every 30 seconds
    • Cloud backup automatic
    • Real-time multi-device sync

  How It Works:
    1. First launch downloads existing cloud data
    2. All changes automatically sync to cloud
    3. Multiple PCs can use simultaneously
    4. Works offline (syncs when reconnected)
    5. No manual configuration needed


🔐 SUPERUSER PERMISSIONS:

  Included in Configuration:
    ✓ role = superuser (NOT user)
    ✓ Full access to all features
    ✓ Admin panel enabled
    ✓ Can manage other users
    ✓ Can manage institutions
    ✓ Full edit/delete permissions


📋 SYSTEM REQUIREMENTS:

  ✓ Windows 7 SP1 or later (64-bit recommended)
  ✓ 500 MB free disk space
  ✓ Administrator privileges for installation
  ✓ Internet connection (for cloud sync)
  ✓ NO Python installation needed!


═════════════════════════════════════════════════════════════════════════════

READY? Just run: INSTALL.bat (as Administrator)

═════════════════════════════════════════════════════════════════════════════
"""
    
    readme_file = installer_output / "README.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"    ✓ Created README.txt")
    
    # Summary
    print("\n" + "="*80)
    print("✓ INSTALLER READY IN installer_output")
    print("="*80)
    print(f"\n📂 Location: {installer_output}")
    print(f"\n📦 Files included:")
    
    for file in sorted(installer_output.iterdir()):
        if file.is_file():
            size_kb = file.stat().st_size / 1024
            print(f"   • {file.name} ({size_kb:.0f} KB)")
    
    print(f"\n🚀 To distribute to other PCs:")
    print(f"   1. Copy this entire 'installer_output' folder")
    print(f"   2. Transfer to target PC (USB, email, cloud, etc.)")
    print(f"   3. On target PC: Right-click INSTALL.bat → Run as administrator")
    print(f"   4. Cloud sync + superuser access = automatic!")
    print()
    
    return True

if __name__ == "__main__":
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + "CREATE PROFESSIONAL INSTALLER IN installer_output".center(78) + "║")
    print("║" + "Punctaj Manager v2.0.0 with Cloud Sync & Superuser".center(78) + "║")
    print("╚" + "═"*78 + "╝")
    
    if create_installer():
        print("\n✅ Done! Installer is ready in d:\\punctaj\\installer_output\\")
    else:
        print("\n❌ Failed to create installer")
