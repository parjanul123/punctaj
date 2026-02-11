#!/usr/bin/env python3
"""
Professional Windows Installer Generator for Punctaj Manager
Creates a complete NSIS installer that can be distributed to other PCs
Version: 2.0.0
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

class InstallerGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_folder = self.project_root / "dist"
        self.build_folder = self.project_root / "build"
        self.output_folder = self.project_root / "installer_final"
        self.nsi_file = self.project_root / "Punctaj_Installer.nsi"
        
        print(f"Project Root: {self.project_root}")
        print(f"Dist Folder: {self.dist_folder}")
        print()

    def step1_create_exe(self):
        """Step 1: Create EXE using PyInstaller"""
        print("=" * 80)
        print("STEP 1: Building executable with PyInstaller")
        print("=" * 80)
        
        # Check if PyInstaller is installed
        try:
            import PyInstaller
            print(f"✓ PyInstaller found: {PyInstaller.__version__}")
        except ImportError:
            print("✗ PyInstaller not installed!")
            print("Installing PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Clean previous builds
        if self.dist_folder.exists():
            print(f"Removing old dist folder...")
            shutil.rmtree(self.dist_folder)
        if self.build_folder.exists():
            print(f"Removing old build folder...")
            shutil.rmtree(self.build_folder)
        
        # Build with PyInstaller
        print("Building executable...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",  # Single exe file
            "--windowed",  # No console window
            "--icon", "punctaj.ico" if (self.project_root / "punctaj.ico").exists() else "",
            "--add-data", f"supabase_config.ini{os.pathsep}.",
            "--add-data", f"discord_config.ini{os.pathsep}.",
            "--distpath", str(self.dist_folder),
            "--buildpath", str(self.build_folder),
            "--specpath", str(self.project_root),
            "punctaj.py"
        ]
        
        # Remove empty string from command
        cmd = [c for c in cmd if c]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error building: {result.stderr}")
                return False
            print("✓ Executable built successfully")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def step2_prepare_installer_files(self):
        """Step 2: Prepare files for NSIS installer"""
        print("\n" + "=" * 80)
        print("STEP 2: Preparing installer files")
        print("=" * 80)
        
        # Create output folder
        if self.output_folder.exists():
            shutil.rmtree(self.output_folder)
        self.output_folder.mkdir(parents=True)
        
        # Copy exe to installer folder
        if not self.dist_folder.exists() or not list(self.dist_folder.glob("*.exe")):
            print("✗ No EXE found in dist folder!")
            return False
        
        exe_file = list(self.dist_folder.glob("*.exe"))[0]
        print(f"Found EXE: {exe_file.name}")
        
        shutil.copy2(exe_file, self.output_folder / "punctaj.exe")
        print(f"✓ Copied {exe_file.name} to installer folder")
        
        # Copy configuration files
        for config_file in ["supabase_config.ini", "discord_config.ini"]:
            if (self.project_root / config_file).exists():
                shutil.copy2(self.project_root / config_file, self.output_folder / config_file)
                print(f"✓ Copied {config_file}")
        
        # Copy documentation
        docs = ["INSTALLATION_GUIDE.txt", "README.txt"]
        for doc in docs:
            if (self.project_root / doc).exists():
                shutil.copy2(self.project_root / doc, self.output_folder / doc)
                print(f"✓ Copied {doc}")
        
        return True

    def step3_create_nsis_script(self):
        """Step 3: Create NSIS installer script"""
        print("\n" + "=" * 80)
        print("STEP 3: Creating NSIS installer script")
        print("=" * 80)
        
        nsis_script = '''
; Punctaj Manager Installer Script
; Generated automatically for distributing the application

!include "MUI2.nsh"
!include "x64.nsh"

; Basic Settings
Name "Punctaj Manager v2.0.0"
OutFile "Punctaj_Manager_Installer.exe"
InstallDir "$PROGRAMFILES\\Punctaj Manager"

; Version Info
VIProductVersion "2.0.0.0"
VIAddVersionKey "ProductName" "Punctaj Manager"
VIAddVersionKey "ProductVersion" "2.0.0"
VIAddVersionKey "CompanyName" "Punctaj Manager"
VIAddVersionKey "FileVersion" "2.0.0"
VIAddVersionKey "FileDescription" "Cloud-Enabled Employee Attendance Tracking"

; Default Folder
InstallDirRegKey HKCU "Software\\Punctaj Manager" "InstallDir"

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Romanian"

; Installer Sections
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy application files
    File "punctaj.exe"
    File "supabase_config.ini"
    File "discord_config.ini"
    File "INSTALLATION_GUIDE.txt"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\Punctaj Manager"
    CreateShortcut "$SMPROGRAMS\\Punctaj Manager\\Punctaj Manager.lnk" "$INSTDIR\\punctaj.exe"
    CreateShortcut "$SMPROGRAMS\\Punctaj Manager\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    CreateShortcut "$DESKTOP\\Punctaj Manager.lnk" "$INSTDIR\\punctaj.exe"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    ; Registry entries
    WriteRegStr HKCU "Software\\Punctaj Manager" "InstallDir" "$INSTDIR"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Punctaj Manager" \\
                     "DisplayName" "Punctaj Manager"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Punctaj Manager" \\
                     "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Punctaj Manager" \\
                     "DisplayVersion" "2.0.0"
    
    MessageBox MB_OK "Punctaj Manager installed successfully!$\\nClick OK to launch."
    Exec "$INSTDIR\\punctaj.exe"
SectionEnd

; Uninstaller
Section "Uninstall"
    RMDir /r "$INSTDIR"
    RMDir /r "$SMPROGRAMS\\Punctaj Manager"
    Delete "$DESKTOP\\Punctaj Manager.lnk"
    DeleteRegKey HKCU "Software\\Punctaj Manager"
    DeleteRegKey HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Punctaj Manager"
    MessageBox MB_OK "Punctaj Manager has been uninstalled."
SectionEnd
'''
        
        nsi_path = self.output_folder / "Punctaj_Installer.nsi"
        with open(nsi_path, 'w', encoding='utf-8') as f:
            f.write(nsis_script.strip())
        
        print(f"✓ Created NSIS script: {nsi_path}")
        return True

    def step4_build_installer(self):
        """Step 4: Compile NSIS script to create installer EXE"""
        print("\n" + "=" * 80)
        print("STEP 4: Building NSIS installer")
        print("=" * 80)
        
        # Check if NSIS is installed
        nsis_paths = [
            Path("C:\\Program Files\\NSIS\\makensis.exe"),
            Path("C:\\Program Files (x86)\\NSIS\\makensis.exe"),
        ]
        
        nsis_exe = None
        for path in nsis_paths:
            if path.exists():
                nsis_exe = path
                break
        
        if not nsis_exe:
            print("\n⚠️  WARNING: NSIS not installed!")
            print("\nNSIS is required to create the professional installer.")
            print("You can:")
            print("  1. Install NSIS from: https://nsis.sourceforge.io/")
            print("  2. Or manually compile using: makensis Punctaj_Installer.nsi")
            print(f"  3. Or I can create a simple batch installer instead")
            return False
        
        print(f"Found NSIS: {nsis_exe}")
        nsi_file = self.output_folder / "Punctaj_Installer.nsi"
        
        try:
            print("Compiling NSIS script...")
            result = subprocess.run([str(nsis_exe), str(nsi_file)], 
                                   cwd=str(self.output_folder),
                                   capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Compilation error: {result.stderr}")
                return False
            print("✓ Installer compiled successfully!")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def step5_create_fallback_installer(self):
        """Step 5: Create batch-based fallback installer (no NSIS required)"""
        print("\n" + "=" * 80)
        print("STEP 5: Creating fallback batch installer (no NSIS required)")
        print("=" * 80)
        
        install_bat = '''@echo off
REM Punctaj Manager - Simple Installer
REM This installer copies the application and creates shortcuts

setlocal enabledelayedexpansion
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║          PUNCTAJ MANAGER - Installation                          ║
echo ║       Cloud-Enabled Employee Attendance Tracking v2.0.0           ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

REM Check Admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

set INSTALL_PATH=%PROGRAMFILES%\\Punctaj Manager
echo Installing to: %INSTALL_PATH%

REM Create directory
if exist "%INSTALL_PATH%" (
    echo Backing up previous version...
    rename "%INSTALL_PATH%" "Punctaj Manager_old" >nul 2>&1
)

mkdir "%INSTALL_PATH%" 2>nul

REM Copy files
echo.
echo Copying application files...
copy /Y "punctaj.exe" "%INSTALL_PATH%\\" >nul
copy /Y "*.ini" "%INSTALL_PATH%\\" >nul
copy /Y "*.txt" "%INSTALL_PATH%\\" >nul

if not exist "%INSTALL_PATH%\\punctaj.exe" (
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo ✓ Files copied successfully

REM Create shortcuts
echo.
echo Creating shortcuts...
powershell -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$link = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\\Punctaj Manager.lnk'); " ^
    "$link.TargetPath = '%INSTALL_PATH%\\punctaj.exe'; " ^
    "$link.WorkingDirectory = '%INSTALL_PATH%'; " ^
    "$link.Save()" >nul 2>&1

echo ✓ Shortcut created on Desktop

REM Installation complete
echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║              ✓ INSTALLATION COMPLETE!                            ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo Installed to: %INSTALL_PATH%
echo.
echo To run: Double-click "Punctaj Manager" on your Desktop
echo.
echo ☁️  Cloud sync is enabled!
echo.

setlocal
set /p LAUNCH="Launch application now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    start "" "%INSTALL_PATH%\\punctaj.exe"
)

pause
'''
        
        installer_path = self.output_folder / "INSTALL_SIMPLE.bat"
        with open(installer_path, 'w', encoding='utf-8') as f:
            f.write(install_bat.strip())
        
        print(f"✓ Created batch installer: {installer_path}")
        return True

    def step6_create_package(self):
        """Step 6: Create distributable ZIP package"""
        print("\n" + "=" * 80)
        print("STEP 6: Creating distributable package")
        print("=" * 80)
        
        zip_name = f"Punctaj_Manager_Installer_{datetime.now().strftime('%Y%m%d')}.zip"
        zip_path = self.project_root / zip_name
        
        print(f"Creating: {zip_name}")
        
        shutil.make_archive(
            str(self.project_root / "Punctaj_Manager_Installer"),
            'zip',
            self.output_folder
        )
        
        # Rename to include date
        temp_zip = self.project_root / "Punctaj_Manager_Installer.zip"
        if temp_zip.exists():
            temp_zip.rename(zip_path)
        
        print(f"✓ Package created: {zip_path}")
        print(f"  Size: {zip_path.stat().st_size / (1024*1024):.1f} MB")
        
        return True

    def create_readme(self):
        """Create README for distribution"""
        readme = '''╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║               PUNCTAJ MANAGER v2.0.0 - INSTALLER PACKAGE                  ║
║                                                                            ║
║            Cloud-Enabled Employee Attendance Tracking System              ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 INSTALLATION OPTIONS:

Option 1: Professional NSIS Installer (Recommended)
──────────────────────────────────────────────────
  • File: Punctaj_Manager_Installer.exe
  • Features: Professional Windows installer with uninstall support
  • Steps: Double-click and follow the wizard
  • Best for: Most users

Option 2: Simple Batch Installer (If NSIS Installer doesn't work)
──────────────────────────────────────────────────────────────────
  • File: INSTALL_SIMPLE.bat
  • Steps:
    1. Right-click INSTALL_SIMPLE.bat
    2. Select "Run as administrator"
    3. Wait for completion
    4. Click "Yes" to launch

🎯 SYSTEM REQUIREMENTS:
  • Windows 7 or later (64-bit recommended)
  • 100 MB free disk space
  • Internet connection (for cloud sync)

✨ FEATURES:
  ✓ Employee attendance tracking
  ✓ Cloud synchronization with Supabase
  ✓ Weekly reports generation
  ✓ Discord integration (optional)
  ✓ Multi-user support
  ✓ Admin dashboard

☁️  CLOUD SYNCHRONIZATION:
  • All data automatically syncs to the cloud
  • Access from any device after installation
  • No manual backup needed
  • Real-time synchronization

❓ TROUBLESHOOTING:

If "Punctaj_Manager_Installer.exe" doesn't work:
  → Use "INSTALL_SIMPLE.bat" instead
  → Make sure to run as Administrator

If installation fails:
  1. Check Windows Defender/Antivirus settings
  2. Ensure you have 100 MB free space
  3. Make sure you have Administrator privileges
  4. Try again

If cloud sync doesn't work:
  1. Check your internet connection
  2. Look for configuration errors in the app
  3. See INSTALLATION_GUIDE.txt for details

📞 SUPPORT:
  See INSTALLATION_GUIDE.txt included in the package for detailed help.

═════════════════════════════════════════════════════════════════════════════
Ready to install? Start with: Punctaj_Manager_Installer.exe
═════════════════════════════════════════════════════════════════════════════
'''
        
        readme_path = self.output_folder / "README_INSTALLER.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        print(f"✓ Created README: README_INSTALLER.txt")

    def run(self):
        """Run the complete installation generation process"""
        print("\n")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  PROFESSIONAL INSTALLER GENERATOR FOR PUNCTAJ MANAGER".center(78) + "║")
        print("║" + "  This will create a distributable installer for Windows".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        
        steps = [
            ("Creating executable with PyInstaller", self.step1_create_exe),
            ("Preparing installer files", self.step2_prepare_installer_files),
            ("Creating NSIS script", self.step3_create_nsis_script),
            ("Building NSIS installer", self.step4_build_installer),
            ("Creating fallback batch installer", self.step5_create_fallback_installer),
            ("Creating distributable package", self.step6_create_package),
        ]
        
        success_count = 0
        for description, step_func in steps:
            try:
                if step_func():
                    success_count += 1
                elif "Building NSIS" in description:
                    # NSIS building failure is not critical
                    continue
                else:
                    print(f"⚠️  Step failed: {description}")
            except Exception as e:
                print(f"❌ Error in {description}: {e}")
        
        # Create README for distribution
        self.create_readme()
        
        # Final summary
        print("\n" + "=" * 80)
        print("INSTALLATION GENERATION COMPLETE!")
        print("=" * 80)
        print(f"\n📂 Output folder: {self.output_folder}")
        print(f"\n📦 Distributable files:")
        
        for file in sorted(self.output_folder.iterdir()):
            if file.is_file():
                size_kb = file.stat().st_size / 1024
                print(f"   • {file.name} ({size_kb:.0f} KB)")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Choose installer:")
        print(f"      • Punctaj_Manager_Installer.exe (professional)")
        print(f"      • INSTALL_SIMPLE.bat (if NSIS not available)")
        print(f"   2. Copy installer to another PC")
        print(f"   3. Run installer on target PC")
        print(f"   4. Application automatically syncs with cloud!")
        print()

if __name__ == "__main__":
    generator = InstallerGenerator()
    generator.run()
