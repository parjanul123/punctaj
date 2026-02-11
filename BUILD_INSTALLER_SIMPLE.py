#!/usr/bin/env python3
"""
PUNCTAJ APPLICATION - SIMPLE INSTALLER BUILDER
Creates executable without NSIS dependency
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

def build():
    print("\n" + "="*80)
    print("  PUNCTAJ MANAGER - INSTALLER BUILDER (SIMPLIFIED)")
    print("="*80 + "\n")
    
    project_root = Path("d:/punctaj")
    dist_dir = project_root / "dist"
    installer_dir = project_root / "installer_output"
    
    # Step 1: Clean previous builds
    print("[1] Cleaning previous builds...")
    for dir_path in [dist_dir, project_root / "build"]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ Cleaned: {dir_path.name}")
    
    # Step 2: Build with PyInstaller
    print("\n[2] Building executable with PyInstaller...")
    print("  This may take 5-10 minutes...")
    
    cmd = (
        f'py -m pyinstaller '
        f'--onedir '
        f'--windowed '
        f'--name=Punctaj '
        f'--add-data "discord_config.ini;." '
        f'--add-data "supabase_config.ini;." '
        f'--hidden-import=tkinter '
        f'--hidden-import=requests '
        f'--hidden-import=supabase '
        f'punctaj.py'
    )
    
    ret = os.system(cmd)
    if ret != 0:
        print("  ✗ PyInstaller build failed!")
        return False
    
    print("  ✓ Executable created successfully!")
    
    # Step 3: Create installer output
    print("\n[3] Creating installer output directory...")
    installer_dir.mkdir(exist_ok=True)
    
    src_app = dist_dir / "Punctaj"
    dst_app = installer_dir / "Punctaj"
    
    if dst_app.exists():
        shutil.rmtree(dst_app)
    
    if src_app.exists():
        shutil.copytree(src_app, dst_app)
        print(f"  ✓ Application copied to: {dst_app}")
        
        # Get size
        exe_path = dst_app / "Punctaj.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024*1024)
            print(f"  ✓ Executable size: {size_mb:.1f} MB")
    else:
        print("  ✗ Source application not found!")
        return False
    
    # Step 4: Create installation batch script
    print("\n[4] Creating installation batch script...")
    
    install_bat = installer_dir / "INSTALL.bat"
    install_script = f'''@echo off
REM Punctaj Manager Installer
REM Simple installation script

setlocal enabledelayedexpansion

echo.
echo =========================================
echo   PUNCTAJ MANAGER INSTALLER
echo =========================================
echo.

REM Ask for installation location
set INSTALL_PATH=%PROGRAMFILES%\\Punctaj Manager
echo Installation location: %INSTALL_PATH%
echo.

REM Create directory
if not exist "%INSTALL_PATH%" (
    mkdir "%INSTALL_PATH%"
    echo Created installation directory
)

REM Copy files
echo Copying files...
xcopy /E /Y "Punctaj\\*" "%INSTALL_PATH%\\"

REM Create shortcuts
echo Creating shortcuts...
powershell -Command "
    $WshShell = New-Object -ComObject WScript.Shell
    
    $DesktopPath = [System.Environment]::GetFolderPath('Desktop')
    $StartMenuPath = [System.Environment]::GetFolderPath('StartMenu') + '\\Punctaj Manager'
    
    if (-not (Test-Path $StartMenuPath)) {{
        New-Item -ItemType Directory -Path $StartMenuPath -Force | Out-Null
    }}
    
    # Desktop shortcut
    $shortcut = $WshShell.CreateShortcut(\"$DesktopPath\\Punctaj Manager.lnk\")
    $shortcut.TargetPath = \"%INSTALL_PATH%\\Punctaj.exe\"
    $shortcut.Save()
    
    # Start Menu shortcut
    $shortcut = $WshShell.CreateShortcut(\"$StartMenuPath\\Punctaj Manager.lnk\")
    $shortcut.TargetPath = \"%INSTALL_PATH%\\Punctaj.exe\"
    $shortcut.Save()
"

echo.
echo =========================================
echo   INSTALLATION COMPLETE
echo =========================================
echo.
echo Punctaj Manager has been installed to:
echo   %INSTALL_PATH%
echo.
echo Desktop and Start Menu shortcuts created!
echo.
pause
'''
    
    install_bat.write_text(install_script)
    print(f"  ✓ Installation script created: INSTALL.bat")
    
    # Step 5: Create uninstaller
    print("\n[5] Creating uninstaller script...")
    
    uninstall_bat = installer_dir / "UNINSTALL.bat"
    uninstall_script = '''@echo off
REM Punctaj Manager Uninstaller

setlocal enabledelayedexpansion

echo.
echo =========================================
echo   PUNCTAJ MANAGER UNINSTALLER
echo =========================================
echo.

set INSTALL_PATH=%PROGRAMFILES%\\Punctaj Manager

echo Removing shortcuts...
del "%USERPROFILE%\\Desktop\\Punctaj Manager.lnk" /Q 2>nul

REM Remove Start Menu folder
for /d %%x in ("%APPDATA%\\Microsoft\\Windows\\Start Menu\\*Punctaj*") do (
    rmdir /s /q "%%x" 2>nul
)

echo Removing files...
if exist "%INSTALL_PATH%" (
    rmdir /s /q "%INSTALL_PATH%"
    echo Uninstallation complete!
) else (
    echo Punctaj Manager is not installed.
)

echo.
pause
'''
    
    uninstall_bat.write_text(uninstall_script)
    print(f"  ✓ Uninstaller created: UNINSTALL.bat")
    
    # Step 6: Create README
    print("\n[6] Creating installation guide...")
    
    readme = installer_dir / "README.txt"
    readme_content = '''PUNCTAJ MANAGER - INSTALLATION GUIDE

SYSTEM REQUIREMENTS:
  - Windows 7 SP1 or later (64-bit)
  - 200 MB free disk space

INSTALLATION:
  1. Extract all files to a folder
  2. Double-click INSTALL.bat
  3. Choose installation location
  4. Wait for completion
  5. Launch from Start Menu or Desktop shortcut

FEATURES:
  ✓ Employee punctaj management
  ✓ Cloud synchronization with Supabase
  ✓ Weekly reports and archives
  ✓ Discord integration
  ✓ Audit logging

UNINSTALLATION:
  1. Double-click UNINSTALL.bat
  2. Confirm removal
  3. All files will be deleted

SUPPORT:
  For issues or questions, contact support.

CONFIGURATION:
  After installation, you can configure:
  - Discord OAuth2 credentials
  - Supabase connection settings
  - Employee management settings

Version: 2.0
Date: 2026-02-02
'''
    
    readme.write_text(readme_content)
    print(f"  ✓ README created: README.txt")
    
    # Step 7: Create package info
    print("\n[7] Creating package information...")
    
    info = {
        "application": "Punctaj Manager",
        "version": "2.0.0",
        "build_date": datetime.now().isoformat(),
        "installer_type": "Batch-based",
        "installation_method": "Run INSTALL.bat",
        "uninstallation_method": "Run UNINSTALL.bat",
        "files": {
            "executable": "Punctaj/Punctaj.exe",
            "installer_script": "INSTALL.bat",
            "uninstaller_script": "UNINSTALL.bat",
            "documentation": "README.txt"
        }
    }
    
    info_file = installer_dir / "package_info.json"
    info_file.write_text(json.dumps(info, indent=2))
    print(f"  ✓ Package info created: package_info.json")
    
    # Final summary
    print("\n" + "="*80)
    print("  BUILD COMPLETE - READY FOR DISTRIBUTION")
    print("="*80 + "\n")
    
    print(f"✓ Location: {installer_dir}")
    print(f"\nFiles created:")
    
    for file in sorted(installer_dir.glob("*")):
        if file.is_file():
            size = file.stat().st_size
            if size > 1024*1024:
                size_str = f"{size/(1024*1024):.1f} MB"
            elif size > 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size} bytes"
            
            print(f"  ✓ {file.name:<30} ({size_str})")
    
    print(f"\nTo distribute:")
    print(f"  1. ZIP the entire 'installer_output' folder")
    print(f"  2. Share the ZIP file with users")
    print(f"  3. Users extract and run INSTALL.bat")
    print(f"\n✓ Installation is simple and fast!")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
