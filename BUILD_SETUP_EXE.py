#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Setup.exe using PyInstaller
Creates a professional installer that clients can run to set up Punctaj Manager
"""

import subprocess
import os
import sys
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed: {result.stderr}")
            return False
        print(f"✅ Success")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def build_setup_exe():
    """Build Setup.exe from SETUP_INSTALLER.py"""
    
    print("=" * 80)
    print("🔨 BUILDING SETUP.EXE")
    print("=" * 80)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not installed")
        print("   Install with: pip install pyinstaller")
        return False
    
    # Paths
    base_dir = r"d:\punctaj"
    setup_py = os.path.join(base_dir, "SETUP_INSTALLER.py")
    output_dir = os.path.join(base_dir, "setup_output")
    dist_dir = os.path.join(output_dir, "dist")
    
    # Check if SETUP_INSTALLER.py exists
    if not os.path.exists(setup_py):
        print(f"❌ {setup_py} not found")
        return False
    
    print(f"📁 Setup script: {setup_py}")
    print(f"📦 Output directory: {output_dir}")
    print()
    
    # Clean previous build
    print("1️⃣ Cleaning previous builds...")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print("   ✓ Removed previous build directory")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Build with PyInstaller
    print("\n2️⃣ Building Setup.exe with PyInstaller...")
    
    cmd = f'''pyinstaller --onefile --windowed --icon=NONE ^
    --distpath "{dist_dir}" ^
    --buildpath "{os.path.join(output_dir, 'build')}" ^
    --specpath "{output_dir}" ^
    --name "PunctajManager_Setup" ^
    --add-data "installer_source;installer_source" ^
    "{setup_py}"'''
    
    if not run_command(cmd, "Running PyInstaller"):
        return False
    
    # Check if EXE was created
    setup_exe = os.path.join(dist_dir, "PunctajManager_Setup.exe")
    if not os.path.exists(setup_exe):
        print(f"❌ Setup.exe not created at {setup_exe}")
        return False
    
    print(f"\n✅ Setup.exe created: {setup_exe}")
    
    # Get file size
    size_mb = os.path.getsize(setup_exe) / (1024 * 1024)
    print(f"   📦 Size: {size_mb:.1f} MB")
    
    # Create distribution info
    print("\n3️⃣ Creating distribution info...")
    
    info_file = os.path.join(dist_dir, "INSTALL_INSTRUCTIONS.txt")
    info_content = """
╔══════════════════════════════════════════════════════════════════════╗
║                    PUNCTAJ MANAGER - SETUP INSTALLER                 ║
║                                                                      ║
║  Installation Guide for End Users                                   ║
╚══════════════════════════════════════════════════════════════════════╝

SYSTEM REQUIREMENTS:
- Windows 7 or later
- 512 MB RAM minimum
- 200 MB disk space
- Internet connection (for Discord and Supabase sync)

INSTALLATION STEPS:

1. Double-click PunctajManager_Setup.exe

2. Wait for the installer to complete
   (Should take 1-2 minutes)

3. When prompted, configure your settings:
   
   FIRST TIME ONLY:
   ✓ You need to add your credentials:
     - Discord OAuth Client ID and Secret
     - Supabase API URL and Key
   
   Ask your system administrator for these values

4. Click "Launch PunctajManager"

5. Login with Discord
   (Your account will be automatically created)

6. Wait for admin to assign permissions
   (You'll have VIEWER role initially)

AFTER INSTALLATION:

Your application is installed in:
    C:\\Users\\YourUsername\\AppData\\Roaming\\PunctajManager

You can launch it anytime by:
- Double-clicking PunctajManager_Setup.exe again
- Clicking "Punctaj Manager" in Windows Start Menu
- Running launch_punctaj.bat from the installation folder

FEATURES:

✅ Real-Time Sync (every 30 seconds)
   - Changes from other users appear automatically
   - No restart needed!

✅ Permission Sync (every 5 seconds)
   - Permission changes are instant
   - Admin can grant/revoke access without restart

✅ Auto-Registration
   - First Discord login creates your account
   - No manual user creation needed

✅ Admin Panel
   - Granular permission control
   - User management

TROUBLESHOOTING:

Problem: "Discord login failed"
Solution: 
  1. Check your internet connection
  2. Ask admin for correct Discord Client ID
  3. Verify the redirect URI is correct

Problem: "Cannot connect to Supabase"
Solution:
  1. Check your internet connection
  2. Ask admin for correct Supabase credentials
  3. Verify the API key is valid

Problem: "Permissions not updating"
Solution:
  1. Permissions sync every 5 seconds - wait a moment
  2. Check that admin assigned you permissions
  3. Try restarting the application

Problem: "Data not syncing from cloud"
Solution:
  1. Data syncs every 30 seconds - wait a moment
  2. Check your internet connection
  3. Check if other users made changes

TECHNICAL SUPPORT:

Contact your system administrator with:
1. The error message you see
2. Screenshot of the error
3. Content of logs/ folder from installation directory

═══════════════════════════════════════════════════════════════════════

Version: 2.5 with Real-Time Sync
Last Updated: 2026-02-03

Ready to install? Good luck! 🚀
"""
    
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)
    print(f"   ✓ Created: INSTALL_INSTRUCTIONS.txt")
    
    # Create a summary
    print("\n" + "=" * 80)
    print("✅ BUILD COMPLETE!")
    print("=" * 80)
    print()
    print("📦 Distribution files:")
    print(f"   ✓ PunctajManager_Setup.exe ({size_mb:.1f} MB)")
    print(f"   ✓ INSTALL_INSTRUCTIONS.txt")
    print()
    print(f"📂 Location: {dist_dir}")
    print()
    print("🚀 Ready to distribute!")
    print()
    print("HOW TO DISTRIBUTE:")
    print("1. Copy PunctajManager_Setup.exe to users")
    print("2. Users run Setup.exe on their computers")
    print("3. Application installs to: %APPDATA%\\PunctajManager")
    print("4. Users configure credentials and launch")
    print()
    
    return True


if __name__ == "__main__":
    success = build_setup_exe()
    sys.exit(0 if success else 1)
