#!/usr/bin/env python3
"""
Simple Professional Installer Wrapper
Uses the existing punctaj.exe and creates a professional installer
"""

import shutil
import subprocess
from pathlib import Path
import os

def create_professional_installer():
    project_root = Path(r"d:\punctaj")
    
    print("\n" + "="*80)
    print("CREATING PROFESSIONAL INSTALLER WITH SUPERUSER SUPPORT")
    print("="*80)
    
    # Check if punctaj.exe exists
    exe_file = project_root / "dist" / "punctaj.exe"
    if not exe_file.exists():
        print("✗ punctaj.exe not found!")
        return False
    
    print(f"\n[1] Found existing EXE: {exe_file.name}")
    
    # Create installer package directory
    package_dir = project_root / "Punctaj_Manager_Professional_Installer"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print(f"[2] Creating package directory: {package_dir}")
    
    # Copy the EXE
    print(f"\n[3] Copying application files...")
    shutil.copy2(exe_file, package_dir / "Punctaj_Manager.exe")
    print(f"    ✓ Copied Punctaj_Manager.exe")
    
    # Copy configuration files with superuser settings
    config_files = [
        ("supabase_config.ini", project_root / "supabase_config.ini"),
        ("discord_config.ini", project_root / "discord_config.ini"),
    ]
    
    for dest_name, src_file in config_files:
        if src_file.exists():
            shutil.copy2(src_file, package_dir / dest_name)
            print(f"    ✓ Copied {dest_name}")
    
    # Copy requirements
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        shutil.copy2(req_file, package_dir / "requirements.txt")
        print(f"    ✓ Copied requirements.txt")
    
    # Create installation script
    print(f"\n[4] Creating installation script...")
    
    install_script = r'''@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM   PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER
REM   With Superuser Permissions and Cloud Synchronization
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║            PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER              ║
echo ║                                                                           ║
echo ║         Cloud-Enabled Employee Attendance Tracking System               ║
echo ║              With Superuser Permissions Preserved                        ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

REM Check Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  ERROR: Administrator privileges required!
    echo.
    echo This installer needs Administrator access to:
    echo   • Install to Program Files
    echo   • Preserve superuser permissions
    echo   • Configure system integration
    echo.
    echo Solution:
    echo   1. Right-click this script: INSTALL_PROFESSIONAL.bat
    echo   2. Select "Run as administrator"
    echo   3. Click "Yes" when prompted
    echo.
    pause
    exit /b 1
)

REM Set installation path
set INSTALL_PATH=%PROGRAMFILES%\Punctaj Manager
set SOURCE_DIR=%~dp0
set APP_CONFIG=%APPDATA%\Punctaj Manager

echo [1/5] Preparing installation...
echo   Install path: %INSTALL_PATH%

REM Create backup if exists
if exist "%INSTALL_PATH%" (
    echo   Creating backup...
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

REM Copy application
echo.
echo [2/5] Installing application...

copy /Y "%SOURCE_DIR%Punctaj_Manager.exe" "%INSTALL_PATH%\" >nul 2>&1
if not exist "%INSTALL_PATH%\Punctaj_Manager.exe" (
    echo ✗ Failed to copy application!
    pause
    exit /b 1
)

echo ✓ Application installed

REM Copy configuration files (with superuser settings)
echo.
echo [3/5] Configuring cloud synchronization and permissions...

if exist "%SOURCE_DIR%supabase_config.ini" (
    copy /Y "%SOURCE_DIR%supabase_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    copy /Y "%SOURCE_DIR%supabase_config.ini" "%APP_CONFIG%\" >nul 2>&1
    echo ✓ Cloud sync configured with superuser access
)

if exist "%SOURCE_DIR%discord_config.ini" (
    copy /Y "%SOURCE_DIR%discord_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    echo ✓ Discord integration configured
)

REM Copy requirements if present
if exist "%SOURCE_DIR%requirements.txt" (
    copy /Y "%SOURCE_DIR%requirements.txt" "%INSTALL_PATH%\" >nul 2>&1
)

REM Create launcher script
echo.
echo [4/5] Creating shortcuts...

(
    echo @echo off
    echo title Punctaj Manager
    echo cls
    echo echo ╔═══════════════════════════════════════════════════╗
    echo echo ║         Launching Punctaj Manager...             ║
    echo echo ╚═══════════════════════════════════════════════════╝
    echo echo.
    echo cd /d "%INSTALL_PATH%"
    echo "%INSTALL_PATH%\Punctaj_Manager.exe"
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

if not exist "%INSTALL_PATH%\Punctaj_Manager.exe" (
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
echo   ✓ Punctaj Manager application
echo   ✓ Cloud synchronization (Supabase)
echo   ✓ Superuser permissions configured
echo   ✓ Discord integration (optional)
echo.
echo How to Run:
echo ─────────────────────────────────────────────────────────────────────────
echo   • Look for "Punctaj Manager" shortcut on Desktop
echo   • Or use: RUN.bat in the installation folder
echo   • Or direct: %INSTALL_PATH%\Punctaj_Manager.exe
echo.
echo Cloud Synchronization:
echo ─────────────────────────────────────────────────────────────────────────
echo   ☁️  Cloud sync is ENABLED by default
echo   ✓ All data automatically syncs to Supabase
echo   ✓ Superuser access to all features
echo   ✓ Real-time synchronization every 30 seconds
echo.

setlocal
set /p LAUNCH="Launch Punctaj Manager now? (Y/N): "

if /i "%LAUNCH%"=="Y" (
    echo.
    echo Starting application...
    echo.
    start "" "%INSTALL_PATH%\Punctaj_Manager.exe"
    echo.
    echo Application launched!
    echo.
) else (
    echo.
    echo Setup complete! Run anytime from Desktop shortcut or:
    echo %INSTALL_PATH%\RUN.bat
    echo.
)

pause
exit /b 0
'''
    
    install_file = package_dir / "INSTALL_PROFESSIONAL.bat"
    with open(install_file, 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    print(f"    ✓ Created INSTALL_PROFESSIONAL.bat")
    
    # Create README
    print(f"\n[5] Creating documentation...")
    
    readme = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER                 ║
║                                                                            ║
║               Complete Application with Superuser Support                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 WHAT'S INCLUDED:

  ✓ Complete Punctaj Manager application (EXE)
  ✓ Cloud synchronization (Supabase) - fully configured
  ✓ Superuser permissions - preserved and active
  ✓ Discord integration (optional)
  ✓ Professional installation experience


🚀 INSTALLATION (3 EASY STEPS):

  1. Right-click: INSTALL_PROFESSIONAL.bat
  
  2. Select: "Run as administrator"
  
  3. Follow the installation wizard
     • Application installed to: C:\Program Files\Punctaj Manager\
     • Cloud sync automatically configured
     • Desktop shortcut created
     • Ready to use!


✨ KEY FEATURES AFTER INSTALLATION:

  ✓ Full application with all features
  ✓ Superuser access to all functions
  ✓ Cloud data automatically synced
  ✓ Admin panel access
  ✓ Discord integration
  ✓ Audit logging
  ✓ Multi-user management
  ✓ Real-time synchronization


☁️  CLOUD SYNCHRONIZATION (AUTO-CONFIGURED):

  • All data automatically syncs to Supabase cloud
  • Superuser permissions included in configuration
  • Real-time sync every 30 seconds
  • Works with multiple PCs simultaneously
  • Offline mode (syncs when reconnected)


🎯 SYSTEM REQUIREMENTS:

  ✓ Windows 7 or later (64-bit)
  ✓ 500 MB free disk space
  ✓ Administrator privileges for installation
  ✓ Internet connection (for cloud sync)


📋 WHAT YOU GET:

  After installation at C:\Program Files\Punctaj Manager\:
  • Punctaj_Manager.exe - Full application
  • supabase_config.ini - Cloud configuration with superuser settings
  • discord_config.ini - Discord settings (optional)
  • RUN.bat - Quick launcher script
  • requirements.txt - Dependencies list
  • Desktop shortcut - Quick access


═════════════════════════════════════════════════════════════════════════════

READY TO INSTALL?

Just run: INSTALL_PROFESSIONAL.bat (as Administrator)

═════════════════════════════════════════════════════════════════════════════
"""
    
    readme_file = package_dir / "README.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"    ✓ Created README.txt")
    
    # Create ZIP package
    print(f"\n[6] Creating distribution ZIP...")
    
    zip_path = shutil.make_archive(
        str(project_root / "Punctaj_Manager_Professional_Setup"),
        'zip',
        project_root,
        "Punctaj_Manager_Professional_Installer"
    )
    
    zip_size = Path(zip_path).stat().st_size / (1024 * 1024)
    print(f"    ✓ Created ZIP: Punctaj_Manager_Professional_Setup.zip ({zip_size:.1f} MB)")
    
    # Summary
    print("\n" + "="*80)
    print("✓ PROFESSIONAL INSTALLER CREATED SUCCESSFULLY!")
    print("="*80)
    print(f"\n📂 Package Location: {package_dir}")
    print(f"\n📦 Files included:")
    
    for file in sorted(package_dir.iterdir()):
        if file.is_file():
            size_kb = file.stat().st_size / 1024
            print(f"   • {file.name} ({size_kb:.0f} KB)")
    
    print(f"\n🎯 TO INSTALL ON OTHER PCs:")
    print(f"   1. Copy this folder or the ZIP file to target PC")
    print(f"   2. Right-click: INSTALL_PROFESSIONAL.bat")
    print(f"   3. Select: 'Run as administrator'")
    print(f"   4. Follow the wizard")
    print(f"   5. Superuser access is automatic!")
    print()
    
    return True

if __name__ == "__main__":
    if create_professional_installer():
        print("✅ Done! Your professional installer is ready.")
    else:
        print("❌ Installation failed.")
