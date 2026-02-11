#!/usr/bin/env python3
"""
PUNCTAJ APPLICATION - COMPLETE INSTALLER BUILDER
Creează un installer professional cu PyInstaller + NSIS
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

class InstallerBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.installer_dir = self.project_root / "installer_output"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"  {text}")
        print("=" * 80)
    
    def print_step(self, step_num, text):
        """Print step information"""
        print(f"\n[{step_num}] {text}")
        print("-" * 60)
    
    def run_command(self, cmd, description):
        """Run command with error handling"""
        try:
            print(f"▶ {description}...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"✗ Eroare: {result.stderr}")
                return False
            print(f"✓ Completed: {description}")
            return True
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def check_python_packages(self):
        """Verific și instlez pachetele necesare"""
        self.print_step(1, "Verificare și instalare pachete Python")
        
        packages_to_check = [
            "pyinstaller",
            "tkinter",
            "requests",
            "supabase",
            "schedule"
        ]
        
        print("Pachetele necesare:")
        for pkg in packages_to_check:
            print(f"  ✓ {pkg}")
        
        # Install PyInstaller
        print("\nInstalez PyInstaller...")
        self.run_command(
            [sys.executable, "-m", "pip", "install", "pyinstaller", "-q"],
            "PyInstaller installation"
        )
        
        return True
    
    def create_spec_file(self):
        """Creez fișierul de spec pentru PyInstaller"""
        self.print_step(2, "Creare fișier de configurare PyInstaller (spec)")
        
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['punctaj.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('discord_config.ini', '.'),
        ('supabase_config.ini', '.'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.ttk',
        'requests',
        'supabase',
        'schedule',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Punctaj',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Punctaj'
)
'''
        
        spec_file = self.project_root / "Punctaj.spec"
        spec_file.write_text(spec_content)
        print(f"✓ Fișier spec creat: {spec_file}")
        return str(spec_file)
    
    def build_executable(self):
        """Construiesc executabilul cu PyInstaller"""
        self.print_step(3, "Construire executabil cu PyInstaller")
        
        # Clean previous builds
        if self.dist_dir.exists():
            print("Șterg build anterior...")
            shutil.rmtree(self.dist_dir)
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        cmd = [
            sys.executable, "-m", "pyinstaller",
            "--onedir",
            "--windowed",
            "--name=Punctaj",
            "--icon=icon.ico" if (self.project_root / "icon.ico").exists() else "",
            "--add-data", f"discord_config.ini{os.pathsep}.",
            "--add-data", f"supabase_config.ini{os.pathsep}.",
            "--hidden-import=tkinter",
            "--hidden-import=requests",
            "--hidden-import=supabase",
            "punctaj.py"
        ]
        
        # Remove empty strings
        cmd = [c for c in cmd if c]
        
        success = self.run_command(cmd, "PyInstaller build")
        
        if success and (self.dist_dir / "Punctaj").exists():
            exe_path = self.dist_dir / "Punctaj" / "Punctaj.exe"
            size = exe_path.stat().st_size / (1024 * 1024) if exe_path.exists() else 0
            print(f"✓ Executabil creat: {exe_path} ({size:.2f} MB)")
            return True
        
        return False
    
    def create_installer_directory(self):
        """Creez structura pentru installer"""
        self.print_step(4, "Creare structură installer")
        
        # Create installer output directory
        self.installer_dir.mkdir(exist_ok=True)
        
        # Copy executable and data
        src_app = self.dist_dir / "Punctaj"
        dst_app = self.installer_dir / "Punctaj"
        
        if dst_app.exists():
            shutil.rmtree(dst_app)
        
        shutil.copytree(src_app, dst_app)
        print(f"✓ Aplicație copiată în: {dst_app}")
        
        # Copy config files
        for config_file in ["discord_config.ini", "supabase_config.ini"]:
            src = self.project_root / config_file
            if src.exists():
                shutil.copy(src, dst_app / config_file)
        
        return True
    
    def create_nsis_script(self):
        """Creez script NSIS pentru installer"""
        self.print_step(5, "Creare script NSIS")
        
        nsis_content = r'''
; Punctaj Manager Installer
; NSIS Installation Script

!include "MUI2.nsh"
!include "x64.nsh"

; Basic settings
Name "Punctaj Manager"
OutFile "Punctaj_Manager_Setup.exe"
InstallDir "$PROGRAMFILES\Punctaj Manager"

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Romanian"

; Install section
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy application files
    File /r "..\installer_output\Punctaj\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\Punctaj Manager"
    CreateShortcut "$SMPROGRAMS\Punctaj Manager\Punctaj Manager.lnk" "$INSTDIR\Punctaj.exe"
    CreateShortcut "$SMPROGRAMS\Punctaj Manager\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortcut "$DESKTOP\Punctaj Manager.lnk" "$INSTDIR\Punctaj.exe"
    
    ; Register uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" \
                 "DisplayName" "Punctaj Manager"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" \
                 "UninstallString" "$INSTDIR\Uninstall.exe"
SectionEnd

; Uninstall section
Section "Uninstall"
    Delete "$SMPROGRAMS\Punctaj Manager\Punctaj Manager.lnk"
    Delete "$SMPROGRAMS\Punctaj Manager\Uninstall.lnk"
    RMDir "$SMPROGRAMS\Punctaj Manager"
    Delete "$DESKTOP\Punctaj Manager.lnk"
    
    RMDir /r "$INSTDIR"
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager"
SectionEnd
'''
        
        nsis_file = self.installer_dir / "Punctaj_Installer.nsi"
        nsis_file.write_text(nsis_content)
        print(f"✓ Script NSIS creat: {nsis_file}")
        return str(nsis_file)
    
    def build_nsis_installer(self):
        """Construiesc installerul cu NSIS"""
        self.print_step(6, "Construire installer NSIS")
        
        # Check if NSIS is installed
        nsis_exe = r"C:\Program Files (x86)\NSIS\makensis.exe"
        
        if not os.path.exists(nsis_exe):
            print("⚠ NSIS nu este instalat!")
            print("📥 Descarcă NSIS de la: https://nsis.sourceforge.io/Download")
            print("Sau rulează: choco install nsis -y")
            return False
        
        nsis_script = self.installer_dir / "Punctaj_Installer.nsi"
        
        if not nsis_script.exists():
            self.create_nsis_script()
        
        cmd = [nsis_exe, str(nsis_script)]
        success = self.run_command(cmd, "NSIS installer build")
        
        if success:
            installer_exe = self.installer_dir.parent / "Punctaj_Manager_Setup.exe"
            if installer_exe.exists():
                size = installer_exe.stat().st_size / (1024 * 1024)
                print(f"✓ Installer creat: {installer_exe} ({size:.2f} MB)")
                return True
        
        return False
    
    def create_manifest(self):
        """Creez manifest cu informații despre build"""
        self.print_step(7, "Creare manifest build")
        
        manifest = {
            "application": "Punctaj Manager",
            "version": "2.0.0",
            "build_date": datetime.now().isoformat(),
            "builder_version": "1.0.0",
            "components": {
                "executable": str(self.dist_dir / "Punctaj" / "Punctaj.exe"),
                "installer": "Punctaj_Manager_Setup.exe",
                "output_directory": str(self.installer_dir)
            },
            "requirements": [
                "Windows 7 SP1 or later (64-bit)",
                "100 MB free disk space",
                "Internet connection for cloud sync"
            ],
            "features": [
                "Employee punctaj management",
                "Cloud synchronization with Supabase",
                "Weekly reports and archives",
                "Discord integration",
                "Audit logging"
            ]
        }
        
        manifest_file = self.installer_dir / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2))
        print(f"✓ Manifest creat: {manifest_file}")
        
        return manifest
    
    def create_readme(self):
        """Creez README pentru installer"""
        readme_content = """# PUNCTAJ MANAGER - INSTALLATION GUIDE

## 📦 Installation Instructions

1. **Run the Installer**
   - Double-click `Punctaj_Manager_Setup.exe`
   - Click "Next" through the installation wizard

2. **Choose Installation Location**
   - Default: `C:\\Program Files\\Punctaj Manager`
   - Click "Next" to continue

3. **Create Shortcuts**
   - Desktop shortcut for quick access
   - Start Menu folder for easy launch

4. **Configuration**
   - Launch the application
   - Configure Discord credentials (optional)
   - Set up Supabase connection for cloud sync

## ✅ System Requirements

- **OS**: Windows 7 SP1 or later (64-bit)
- **Memory**: 2 GB RAM minimum
- **Storage**: 100 MB free space
- **Connection**: Internet (for cloud features)

## 🚀 First Run

1. Start the application from Start Menu or Desktop shortcut
2. Configure settings:
   - Discord OAuth2 credentials (optional)
   - Supabase API keys
   - Employee management settings
3. Start managing employee attendance!

## 🔧 Features

✓ Employee punctaj tracking
✓ Real-time cloud synchronization
✓ Weekly reports generation
✓ Discord integration
✓ Audit logging and history
✓ Multi-institution support
✓ Role-based access control

## 📞 Support

For issues or questions, check the application's Help menu or contact support.

## 🔄 Uninstall

1. Go to Control Panel > Programs > Programs and Features
2. Find "Punctaj Manager"
3. Click "Uninstall"
4. Follow the uninstall wizard

---
Built on: {timestamp}
Version: 2.0.0
"""
        
        readme_file = self.installer_dir.parent / "INSTALLATION_README.txt"
        readme_file.write_text(readme_content.format(timestamp=self.timestamp))
        print(f"✓ README creat: {readme_file}")
    
    def build_all(self):
        """Execut tot procesul de build"""
        self.print_header("PUNCTAJ APPLICATION INSTALLER BUILDER")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        steps = [
            (self.check_python_packages, "Verificare pachete"),
            (self.create_spec_file, "Creare spec file"),
            (self.build_executable, "Build executabil"),
            (self.create_installer_directory, "Creare director installer"),
            (self.create_nsis_script, "Criere script NSIS"),
            (self.build_nsis_installer, "Build NSIS installer"),
            (self.create_manifest, "Creare manifest"),
            (self.create_readme, "Criere README"),
        ]
        
        failed = []
        
        for step_func, step_name in steps:
            try:
                result = step_func()
                if result is False:
                    failed.append(step_name)
            except Exception as e:
                print(f"✗ Error in {step_name}: {str(e)}")
                failed.append(step_name)
        
        # Final summary
        self.print_header("BUILD SUMMARY")
        
        print(f"\n✓ Build completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n📁 Output directory: {self.installer_dir.parent}")
        
        if failed:
            print(f"\n⚠ Failed steps ({len(failed)}):")
            for step in failed:
                print(f"  ✗ {step}")
        else:
            print("\n✓ All steps completed successfully!")
            print("\n📦 Files created:")
            installer_exe = self.installer_dir.parent / "Punctaj_Manager_Setup.exe"
            if installer_exe.exists():
                size = installer_exe.stat().st_size / (1024 * 1024)
                print(f"  ✓ {installer_exe.name} ({size:.2f} MB)")
            print(f"  ✓ INSTALLATION_README.txt")
            print(f"  ✓ Documentation and manifest files")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    builder = InstallerBuilder()
    builder.build_all()
