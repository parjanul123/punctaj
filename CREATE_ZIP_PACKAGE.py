#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Build & Zip Package Creator
Creează un fișier ZIP cu întreaga aplicație și setup
"""

import os
import shutil
import zipfile
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class BuildZipPackage:
    """Creează pachet ZIP complet cu aplicația"""
    
    def __init__(self):
        self.base_dir = r"d:\punctaj"
        self.output_dir = os.path.join(self.base_dir, "package_output")
        self.zip_name = f"PunctajManager_v2.5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        self.zip_path = os.path.join(self.output_dir, self.zip_name)
        
    def print_header(self):
        """Afisează header"""
        print("=" * 80)
        print("🔨 COMPLETE BUILD & ZIP PACKAGE")
        print("=" * 80)
        print()
        print(f"📦 Output: {self.output_dir}")
        print(f"📄 ZIP file: {self.zip_name}")
        print()
    
    def clean_output(self):
        """Șterge folderul de output anterior"""
        print("1️⃣ Cleaning previous builds...")
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        print("   ✓ Clean\n")
    
    def create_zip(self):
        """Creează fișierul ZIP"""
        print("2️⃣ Creating ZIP package...")
        
        files_to_include = {
            # Core application files
            "punctaj.py": "Application/",
            "realtime_sync.py": "Application/",
            "permission_sync_fix.py": "Application/",
            "discord_auth.py": "Application/",
            "supabase_sync.py": "Application/",
            "admin_panel.py": "Application/",
            "admin_permissions.py": "Application/",
            "admin_ui.py": "Application/",
            "action_logger.py": "Application/",
            "config_resolver.py": "Application/",
            "json_logger.py": "Application/",
            "organization_view.py": "Application/",
            
            # Setup scripts
            "SETUP_INSTALLER.py": "Setup/",
            "BUILD_SETUP_EXE.py": "Setup/",
            "DIAGNOSE_SYNC_ISSUE.py": "Tools/",
            
            # Configuration templates
            "discord_config.ini": "Config_Templates/",
            "supabase_config.ini": "Config_Templates/",
            
            # Documentation
            "00_WELCOME.txt": "Documentation/",
            "00_START_HERE_IMPLEMENTATION.md": "Documentation/",
            "00_COMPLETE.txt": "Documentation/",
            "01_QUICK_START_BUILD_DISTRIBUTE.md": "Documentation/",
            "00_FINAL_SUMMARY.md": "Documentation/",
            "02_ARCHITECTURE_COMPLETE.md": "Documentation/",
            "00_SETUP_SOLUTION_COMPLETE.md": "Documentation/",
            "00_FILES_MANIFEST.md": "Documentation/",
            "PERMISSION_SYNC_FIX.md": "Documentation/",
            "AUTO_REGISTRATION_DISCORD.md": "Documentation/",
            "CLIENT_GUIDE_PERMISSIONS_FIX.md": "Documentation/",
            "DEPLOYMENT_READY.md": "Documentation/",
        }
        
        try:
            with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for filename, folder in files_to_include.items():
                    src_path = os.path.join(self.base_dir, filename)
                    
                    if os.path.exists(src_path):
                        arcname = os.path.join(folder, filename)
                        zf.write(src_path, arcname)
                        print(f"   ✓ Added: {folder}{filename}")
                    else:
                        print(f"   ⚠️  Skipped: {filename} (not found)")
                
                # Add installer_source folder
                installer_source = os.path.join(self.base_dir, "installer_source")
                if os.path.exists(installer_source):
                    print(f"\n   ✓ Adding installer_source/ folder...")
                    for root, dirs, files in os.walk(installer_source):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.base_dir)
                            zf.write(file_path, arcname)
                
                # Add BUILD_SETUP_EXE.py sa fie clar cum se builduie
                readme_content = """
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║          PUNCTAJ MANAGER v2.5 - COMPLETE PACKAGE                    ║
║                                                                       ║
║                   Real-Time Cloud Synchronization                    ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

📦 PACKAGE CONTENTS
═══════════════════════════════════════════════════════════════════════

├── Application/              → Core application files
├── Setup/                    → Setup installer scripts
├── Tools/                    → Diagnostic tools
├── Config_Templates/         → Configuration file templates
├── Documentation/            → Complete guides
└── installer_source/         → Files for building Setup.exe


🚀 QUICK START
═══════════════════════════════════════════════════════════════════════

1. EXTRACT THIS ZIP
   Unzip to: d:\\punctaj\\

2. BUILD SETUP.EXE (Optional, if you want to create installer)
   python Setup\\BUILD_SETUP_EXE.py
   
   Creates: setup_output\\dist\\PunctajManager_Setup.exe

3. RUN APPLICATION
   python Application\\punctaj.py

4. OR DISTRIBUTE SETUP.EXE TO CLIENTS
   Send: setup_output\\dist\\PunctajManager_Setup.exe
   Clients double-click to install


📚 DOCUMENTATION
═══════════════════════════════════════════════════════════════════════

Start reading here:
→ Documentation/00_START_HERE_IMPLEMENTATION.md

Quick build guide:
→ Documentation/01_QUICK_START_BUILD_DISTRIBUTE.md

Complete overview:
→ Documentation/00_FINAL_SUMMARY.md

Technical details:
→ Documentation/02_ARCHITECTURE_COMPLETE.md


⚙️  WHAT'S INCLUDED
═══════════════════════════════════════════════════════════════════════

✅ Real-Time Cloud Sync (every 30 seconds)
   └─ Database synced automatically
   └─ Changes from other users visible instantly
   └─ No restart needed!

✅ Real-Time Permission Sync (every 5 seconds)
   └─ Permissions updated automatically
   └─ Admin changes visible instantly
   └─ No restart needed!

✅ Auto-User Registration
   └─ First Discord login creates account
   └─ No manual user creation

✅ Professional Setup Installer
   └─ Single Setup.exe file
   └─ Installs to %APPDATA%\\PunctajManager
   └─ Ready for distribution

✅ Complete Documentation
   └─ 8 comprehensive guides
   └─ Architecture diagrams
   └─ Troubleshooting guides


🔧 CONFIGURATION
═══════════════════════════════════════════════════════════════════════

Before running, edit:

1. Config_Templates/discord_config.ini
   - Add your Discord OAuth credentials

2. Config_Templates/supabase_config.ini
   - Add your Supabase API credentials

Copy these to:
- d:\\punctaj\\discord_config.ini
- d:\\punctaj\\supabase_config.ini


📊 VERSION INFO
═══════════════════════════════════════════════════════════════════════

Version: 2.5 with Real-Time Sync
Release Date: 2026-02-03
Status: Production Ready

Features:
- Real-time database sync (30 sec)
- Real-time permission sync (5 sec)
- Auto-registration on Discord login
- Professional installer
- Complete documentation


🎯 NEXT STEPS
═══════════════════════════════════════════════════════════════════════

1. Extract this ZIP to d:\\punctaj\\

2. Read: Documentation/00_START_HERE_IMPLEMENTATION.md

3. Configure Discord and Supabase credentials

4. Run: python Application/punctaj.py
   OR
   python Setup/BUILD_SETUP_EXE.py (to create Setup.exe)

5. Test the application

6. Distribute Setup.exe to clients (optional)


❓ NEED HELP?
═══════════════════════════════════════════════════════════════════════

Check these files for help:
- 01_QUICK_START_BUILD_DISTRIBUTE.md    → How to build/distribute
- 02_ARCHITECTURE_COMPLETE.md           → How it works
- 00_SETUP_SOLUTION_COMPLETE.md         → Complete guide
- Tools/DIAGNOSE_SYNC_ISSUE.py          → Troubleshooting


═══════════════════════════════════════════════════════════════════════

Ready to deploy! Good luck! 🚀

For questions, see the documentation folder.
"""
                
                zf.writestr("README.txt", readme_content)
                print(f"\n   ✓ Added: README.txt")
            
            # Get ZIP size
            zip_size_mb = os.path.getsize(self.zip_path) / (1024 * 1024)
            print(f"\n✅ ZIP created: {self.zip_name}")
            print(f"   Size: {zip_size_mb:.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ ZIP creation failed: {e}")
            return False
    
    def create_manifest(self):
        """Creează un manifest al conținutului ZIP"""
        print("\n3️⃣ Creating manifest...")
        
        manifest_path = os.path.join(self.output_dir, "MANIFEST.txt")
        manifest_content = f"""
PUNCTAJ MANAGER v2.5 - ZIP PACKAGE MANIFEST
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
File: {self.zip_name}

═══════════════════════════════════════════════════════════════════════

DIRECTORY STRUCTURE:

/Application/
  ├── punctaj.py                    Main application
  ├── realtime_sync.py              Real-time cloud sync manager
  ├── permission_sync_fix.py         Permission sync manager
  ├── discord_auth.py               Discord OAuth
  ├── supabase_sync.py              Supabase operations
  ├── admin_panel.py                Admin panel UI
  ├── admin_permissions.py          Permission management
  ├── admin_ui.py                   Admin UI components
  ├── action_logger.py              Action logging
  ├── config_resolver.py            Config resolver
  ├── json_logger.py                JSON logging
  └── organization_view.py          Organization view

/Setup/
  ├── SETUP_INSTALLER.py            Professional setup installer
  └── BUILD_SETUP_EXE.py            Setup.exe builder

/Tools/
  └── DIAGNOSE_SYNC_ISSUE.py       Diagnostic tool

/Config_Templates/
  ├── discord_config.ini            Discord OAuth template
  └── supabase_config.ini           Supabase API template

/Documentation/
  ├── 00_START_HERE_IMPLEMENTATION.md    Navigation guide
  ├── 00_WELCOME.txt                     Welcome
  ├── 00_COMPLETE.txt                    Completion notice
  ├── 01_QUICK_START_BUILD_DISTRIBUTE.md Quick start
  ├── 00_FINAL_SUMMARY.md                Complete summary
  ├── 02_ARCHITECTURE_COMPLETE.md        Technical architecture
  ├── 00_SETUP_SOLUTION_COMPLETE.md     Full setup guide
  ├── 00_FILES_MANIFEST.md               File listing
  ├── PERMISSION_SYNC_FIX.md            Permission sync docs
  ├── AUTO_REGISTRATION_DISCORD.md      Auto-registration docs
  ├── CLIENT_GUIDE_PERMISSIONS_FIX.md   Client guide
  └── DEPLOYMENT_READY.md               Deployment checklist

/installer_source/
  └── All files needed for building Setup.exe

/README.txt                         This file

═══════════════════════════════════════════════════════════════════════

REQUIREMENTS:

- Python 3.7+
- tkinter
- requests
- cryptography
- PyInstaller (for building Setup.exe)

═══════════════════════════════════════════════════════════════════════

INSTALLATION:

1. Extract ZIP to: d:\\punctaj\\

2. Configure credentials:
   - discord_config.ini (Discord OAuth)
   - supabase_config.ini (Supabase API)

3. Run application:
   python Application\\punctaj.py

4. Or build Setup.exe:
   python Setup\\BUILD_SETUP_EXE.py

═══════════════════════════════════════════════════════════════════════

KEY FEATURES:

✅ Real-Time Cloud Sync (30 seconds)
✅ Real-Time Permission Sync (5 seconds)
✅ Auto-User Registration
✅ Professional Setup Installer
✅ Complete Documentation
✅ Diagnostic Tools

═══════════════════════════════════════════════════════════════════════

VERSION: 2.5 with Real-Time Sync
STATUS: Production Ready
DATE: 2026-02-03

═══════════════════════════════════════════════════════════════════════
"""
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        print(f"   ✓ Created: MANIFEST.txt")
    
    def create_summary(self):
        """Creează un rezumat al build-ului"""
        print("\n4️⃣ Creating build summary...")
        
        summary_path = os.path.join(self.output_dir, "BUILD_SUMMARY.txt")
        
        zip_size_mb = os.path.getsize(self.zip_path) / (1024 * 1024)
        
        summary_content = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║              ✅ BUILD COMPLETE - READY TO DISTRIBUTE               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

BUILD SUMMARY
═══════════════════════════════════════════════════════════════════════

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Package: {self.zip_name}
Size: {zip_size_mb:.1f} MB
Status: ✅ READY FOR DISTRIBUTION

CONTENTS:
  ✓ Application files (12 Python modules)
  ✓ Setup scripts (2 files)
  ✓ Configuration templates (2 files)
  ✓ Documentation (8 guides)
  ✓ Installer source (complete)
  ✓ Diagnostic tools

NEXT STEPS:
═══════════════════════════════════════════════════════════════════════

Option 1: EXTRACT AND RUN LOCALLY
  1. Extract {self.zip_name} to d:\\punctaj\\
  2. Edit discord_config.ini with your credentials
  3. Edit supabase_config.ini with your credentials
  4. Run: python Application\\punctaj.py

Option 2: BUILD SETUP.EXE FOR CLIENTS
  1. Extract {self.zip_name} to d:\\punctaj\\
  2. Run: python Setup\\BUILD_SETUP_EXE.py
  3. Creates: setup_output\\dist\\PunctajManager_Setup.exe
  4. Send Setup.exe to clients

Option 3: DISTRIBUTE ZIP TO TEAM
  1. Send {self.zip_name} to team members
  2. They extract and follow steps in README.txt
  3. Everyone has complete application

DISTRIBUTION CHECKLIST:
═══════════════════════════════════════════════════════════════════════

Before distributing:
  [ ] Extract ZIP to clean directory
  [ ] Test application runs
  [ ] Test Setup.exe builds successfully
  [ ] Verify all documentation is complete
  [ ] Create credentials template
  [ ] Prepare installation instructions

When distributing:
  [ ] Send {self.zip_name} to clients
  [ ] Include installation guide
  [ ] Provide Discord credentials template
  [ ] Provide Supabase credentials template
  [ ] Include README.txt contents

TECHNICAL SPECS:
═══════════════════════════════════════════════════════════════════════

Version: 2.5 with Real-Time Sync
Python: 3.7+
Database: Supabase
Auth: Discord OAuth2
GUI: tkinter
Sync Interval (Data): 30 seconds
Sync Interval (Permissions): 5 seconds

FEATURES:
═══════════════════════════════════════════════════════════════════════

✅ Real-Time Cloud Synchronization
   └─ Database synced every 30 seconds
   └─ Changes from other users visible instantly
   └─ No restart required

✅ Real-Time Permission Management
   └─ Permissions synced every 5 seconds
   └─ Admin changes visible instantly
   └─ No restart required

✅ Automatic User Registration
   └─ Discord login creates user automatically
   └─ No manual user creation
   └─ Granular permission control

✅ Professional Installation
   └─ Setup.exe installer
   └─ Standard Windows installation path
   └─ Easy distribution

SUPPORT:
═══════════════════════════════════════════════════════════════════════

For help, see:
  • Documentation/00_START_HERE_IMPLEMENTATION.md
  • Documentation/01_QUICK_START_BUILD_DISTRIBUTE.md
  • Documentation/02_ARCHITECTURE_COMPLETE.md
  • Tools/DIAGNOSE_SYNC_ISSUE.py

═══════════════════════════════════════════════════════════════════════

You're all set! Distribute {self.zip_name} and you're ready to go! 🚀

═══════════════════════════════════════════════════════════════════════
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"   ✓ Created: BUILD_SUMMARY.txt")
    
    def run(self):
        """Execută build-ul complet"""
        self.print_header()
        
        try:
            self.clean_output()
            
            if not self.create_zip():
                return False
            
            self.create_manifest()
            self.create_summary()
            
            # Print final summary
            print("\n" + "=" * 80)
            print("✅ BUILD COMPLETE!")
            print("=" * 80)
            print()
            print(f"📦 ZIP Package: {self.zip_name}")
            print(f"📂 Location: {self.output_dir}")
            print()
            print("Files ready to distribute:")
            print(f"  • {self.zip_name}")
            print(f"  • README.txt (included in ZIP)")
            print(f"  • MANIFEST.txt")
            print(f"  • BUILD_SUMMARY.txt")
            print()
            print("Next steps:")
            print(f"1. Extract {self.zip_name} to d:\\punctaj\\")
            print("2. Edit configuration files with credentials")
            print("3. Run application or build Setup.exe")
            print("4. Distribute to clients")
            print()
            print(f"📍 Package location: {self.output_dir}")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    builder = BuildZipPackage()
    success = builder.run()
    sys.exit(0 if success else 1)
