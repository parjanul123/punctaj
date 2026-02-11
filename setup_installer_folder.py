#!/usr/bin/env python3
"""
Setup installer output folder with complete application
"""

import os
import shutil
from pathlib import Path

print("\n" + "="*70)
print("  PUNCTAJ MANAGER - SETUP INSTALLER")
print("="*70 + "\n")

project_root = Path("d:/punctaj")
installer_dir = project_root / "installer_output"

# Clean and create
if installer_dir.exists():
    shutil.rmtree(installer_dir)
    print("[1] Cleaned old installer_output")

installer_dir.mkdir(parents=True, exist_ok=True)
print("[2] Created installer_output directory\n")

# Copy main application folder
print("[3] Copying application files...")
app_dir = installer_dir / "Punctaj"

py_files = [
    "punctaj.py", "discord_auth.py", "supabase_sync.py",
    "admin_panel.py", "action_logger.py", "permission_decorators.py",
    "config_resolver.py", "notification_system.py"
]

for py_file in py_files:
    src = project_root / py_file
    if src.exists():
        app_dir.mkdir(exist_ok=True)
        shutil.copy(src, app_dir / py_file)
        print(f"    ✓ {py_file}")

# Copy config files
print("\n[4] Copying configuration files...")
config_files = ["discord_config.ini", "supabase_config.ini"]

for config_file in config_files:
    src = project_root / config_file
    if src.exists():
        shutil.copy(src, installer_dir / config_file)
        print(f"    ✓ {config_file}")

# Copy requirements
print("\n[5] Copying requirements...")
req_file = project_root / "requirements.txt"
if req_file.exists():
    shutil.copy(req_file, installer_dir / "requirements.txt")
    print(f"    ✓ requirements.txt")

# Create INSTALL.bat
print("\n[6] Creating INSTALL.bat...")
install_bat = installer_dir / "INSTALL.bat"
install_bat.write_text("""@echo off
cls
echo.
echo =====================================
echo   PUNCTAJ MANAGER - INSTALLER
echo =====================================
echo.

REM Ask for installation path
set INSTALL_PATH=%PROGRAMFILES%\\Punctaj Manager

echo Installing to: %INSTALL_PATH%
echo.

if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"

REM Copy all files
echo Copying files...
xcopy /E /Y /I "*.py" "%INSTALL_PATH%\\" >nul
xcopy /E /Y /I "*.ini" "%INSTALL_PATH%\\" >nul
xcopy /E /Y /I "Punctaj\\*" "%INSTALL_PATH%\\" >nul

REM Create shortcut
echo Creating shortcuts...
powershell -Command "
    $ws = New-Object -ComObject WScript.Shell
    $link = $ws.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\\Punctaj.lnk')
    $link.TargetPath = '%INSTALL_PATH%\\punctaj.py'
    $link.Save()
    Write-Host 'Installation complete!'
"

echo.
echo Installation complete!
echo Run: python %INSTALL_PATH%\\punctaj.py
echo.
pause
""")
print("    ✓ INSTALL.bat created")

# Create RUN.bat for users
print("\n[7] Creating RUN.bat...")
run_bat = installer_dir / "RUN.bat"
run_bat.write_text("""@echo off
cd /d "%~dp0"
python punctaj.py
pause
""")
print("    ✓ RUN.bat created")

# Create README
print("\n[8] Creating README...")
readme = installer_dir / "README.txt"
readme.write_text("""PUNCTAJ MANAGER - INSTALLATION GUIDE

REQUIREMENTS:
  - Windows 7+
  - Python 3.8+ installed
  - Internet connection for cloud sync

INSTALLATION:
  1. Extract this folder
  2. Double-click INSTALL.bat
  3. Follow instructions

RUNNING:
  - Double-click RUN.bat in installation folder
  - Or: python punctaj.py

CLOUD SYNC:
  - Supabase config will be loaded from supabase_config.ini
  - Data syncs automatically to cloud
  - Check internet connection if sync fails

FIRST RUN SETUP:
  1. Configure Supabase credentials
  2. Configure Discord (optional)
  3. Add employees
  4. Start tracking attendance

Files:
  - punctaj.py: Main application
  - *.ini: Configuration files
  - INSTALL.bat: Installation script
  - RUN.bat: Run application

VERSION: 2.0.0
DATE: 2026-02-02
""")
print("    ✓ README.txt created")

print("\n" + "="*70)
print("  SETUP COMPLETE - READY FOR DISTRIBUTION")
print("="*70 + "\n")

# List files
print("Files in installer_output:")
for item in sorted(installer_dir.glob("*")):
    if item.is_file():
        size = item.stat().st_size / 1024
        print(f"  - {item.name} ({size:.0f} KB)")
    else:
        count = len(list(item.glob("*")))
        print(f"  - {item.name}/ ({count} files)")

print("\nNext steps:")
print("  1. Add to installer_output: supabase_config.ini (with your credentials)")
print("  2. Distribute 'installer_output' folder to users")
print("  3. Users run INSTALL.bat to install")
print("  4. Users run RUN.bat or double-click punctaj.py")
print("\n")
