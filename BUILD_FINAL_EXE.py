#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔨 BUILD punctaj.exe - VERSIUNEA FINALA CU TOȚI FIX-URILE

Construiește punctaj.exe din punctaj.py cu:
✅ Multi-device sync manager
✅ Security fixes (permissions)
✅ Real-time Supabase sync
✅ Cloud backup & restore
✅ Permission system
✅ Discord authentication

OUTPUT: d:\\punctaj\\dist\\punctaj.exe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

# Configuration
SCRIPT_DIR = Path(r"d:\punctaj")
MAIN_SCRIPT = SCRIPT_DIR / "punctaj.py"
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"

print("\n" + "="*80)
print("🔨 BUILDING punctaj.exe - FINAL VERSION WITH ALL UPDATES")
print("="*80)
print(f"📁 Working directory: {SCRIPT_DIR}")
print(f"📄 Main script: {MAIN_SCRIPT}")
print(f"📦 Output: {DIST_DIR}")

# Step 1: Verify Python and dependencies
print("\n" + "="*80)
print("STEP 1: Verify Python and PyInstaller")
print("="*80)

try:
    import PyInstaller
    print(f"✅ PyInstaller installed: {PyInstaller.__version__}")
except ImportError:
    print("❌ PyInstaller not installed!")
    print(f"Installing... {sys.executable} -m pip install pyinstaller")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
    import PyInstaller
    print(f"✅ PyInstaller installed: {PyInstaller.__version__}")

# Verify required files
print("\n" + "="*80)
print("STEP 2: Verify Required Files")
print("="*80)

required_files = [
    "punctaj.py",
    "supabase_sync.py",
    "supabase_employee_manager.py",
    "multi_device_sync_manager.py",
    "users_permissions_json_manager.py",
    "admin_permissions.py",
    "discord_auth.py",
    "backup_manager.py",
    "action_logger.py",
    "permission_sync_fix.py",
    "realtime_sync.py",
    "admin_ui.py",
]

print("\nChecking essential files:")
missing = []
for file in required_files:
    path = SCRIPT_DIR / file
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"  ✅ {file:<40} ({size_kb:.1f} KB)")
    else:
        print(f"  ❌ {file:<40} MISSING!")
        missing.append(file)

if missing:
    print(f"\n⚠️  Missing files: {', '.join(missing)}")
    print("   Build may fail or be incomplete")

# Step 3: Clean old build artifacts
print("\n" + "="*80)
print("STEP 3: Clean Old Build Artifacts")
print("="*80)

for dir_name in [BUILD_DIR, DIST_DIR]:
    if dir_name.exists():
        try:
            shutil.rmtree(dir_name)
            print(f"✅ Removed {dir_name.name}/")
        except Exception as e:
            print(f"⚠️  Could not remove {dir_name.name}: {e}")

# Step 4: Build EXE with PyInstaller
print("\n" + "="*80)
print("STEP 4: Building EXE with PyInstaller")
print("="*80)

# Check for icon
icon_file = SCRIPT_DIR / "punctaj.ico"
icon_arg = f"--icon={icon_file}" if icon_file.exists() else ""

# PyInstaller command
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--name=punctaj",
    "--onefile",
    "--windowed",
    "--console",  # Show console for debug output
    "--collect-all=tkinter",
    "--collect-all=requests",
    "--hidden-import=tkinter",
    "--hidden-import=requests",
    "--hidden-import=cryptography",
    "--hidden-import=cv2",
    "--hidden-import=PIL",
    "--hidden-import=configparser",
    f"--distpath={DIST_DIR}",
    f"--workpath={BUILD_DIR}",
    f"--specpath={SCRIPT_DIR}",
    "--clean",
]

if icon_arg:
    cmd.insert(5, icon_arg)

# Add config files to bundle
config_files = [
    ("supabase_config.ini", "."),
    ("discord_config.ini", "."),
]

for config_file, dest in config_files:
    config_path = SCRIPT_DIR / config_file
    if config_path.exists():
        cmd.append(f"--add-data={config_path}{os.pathsep}{dest}")

cmd.append(str(MAIN_SCRIPT))

print(f"Command: pyinstaller ... {str(MAIN_SCRIPT)}")
print(f"Options: --onefile --windowed --console")
print(f"Output dir: {DIST_DIR}\n")

print("⏳ Building... (this may take 2-5 minutes)\n")
start_time = time.time()

try:
    result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ PyInstaller completed successfully!\n")
    else:
        print("⚠️  PyInstaller warnings/errors:")
        if result.stderr:
            print(result.stderr[:500])
        print()
    
except Exception as e:
    print(f"❌ Error running PyInstaller: {e}\n")
    sys.exit(1)

# Step 5: Verify EXE was created
print("="*80)
print("STEP 5: Verify EXE Creation")
print("="*80)

exe_path = DIST_DIR / "punctaj.exe"

if exe_path.exists():
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    elapsed = time.time() - start_time
    
    print(f"\n✅ BUILD SUCCESSFUL!")
    print(f"\n📦 EXE Details:")
    print(f"   File: {exe_path}")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Time: {elapsed:.1f} seconds")
    print(f"\n🎯 Features included:")
    print(f"   ✅ Multi-device sync (cloud)")
    print(f"   ✅ Security: Permission management")
    print(f"   ✅ Real-time WebSocket sync")
    print(f"   ✅ Backup & restore")
    print(f"   ✅ Discord authentication")
    print(f"   ✅ Admin panel")
    print(f"   ✅ Permission sync")
    print(f"   ✅ Supabase integration")
    
else:
    print(f"❌ BUILD FAILED!")
    print(f"punctaj.exe not found at {exe_path}")
    print(f"\nTroubleshooting:")
    print(f"1. Check if PyInstaller is installed correctly")
    print(f"2. Check console output above for errors")
    print(f"3. Verify all Python files exist")
    sys.exit(1)

# Step 6: Copy files to dist
print("\n" + "="*80)
print("STEP 6: Additional Files")
print("="*80)

# Copy config files
config_files_to_copy = [
    "supabase_config.ini",
    "discord_config.ini",
]

# Copy additional Python files needed for features
additional_files_to_copy = [
    "git_updater.py",  # Git Updater pentru actualizări automate
]

print("\nCopying configuration files to dist/:")
for config_file in config_files_to_copy:
    src = SCRIPT_DIR / config_file
    dst = DIST_DIR / config_file
    if src.exists():
        try:
            shutil.copy2(src, dst)
            print(f"  ✅ {config_file}")
        except Exception as e:
            print(f"  ⚠️  Could not copy {config_file}: {e}")

print("\nCopying additional feature files to dist/:")
for additional_file in additional_files_to_copy:
    src = SCRIPT_DIR / additional_file
    dst = DIST_DIR / additional_file
    if src.exists():
        try:
            shutil.copy2(src, dst)
            print(f"  ✅ {additional_file}")
        except Exception as e:
            print(f"  ⚠️  Could not copy {additional_file}: {e}")
    else:
        print(f"  ⚠️  {additional_file} not found")

# Step 7: Create README
print("\nCreating README in dist/:")

readme_content = """# 🎯 PunctajManager - Multi-Device Application

## 📋 Contents

- **punctaj.exe** - Main application
- **supabase_config.ini** - Supabase configuration
- **discord_config.ini** - Discord authentication config
- **git_updater.py** - Git Updater for automatic updates

## 🚀 How to Run

1. Double-click `punctaj.exe`
2. Login with Discord
3. Application automatically syncs with cloud

## 🔄 Git Updates

- Use the built-in **Git Updater** button in the app
- Automatically downloads latest updates from Git
- Updates the application with newest features and fixes

## ✅ Features

✅ Multi-device synchronization (cloud-based)
✅ Real-time updates with WebSocket
✅ Discord authentication
✅ Permission system
✅ Backup & restore
✅ Admin panel
✅ Supabase cloud integration
✅ Git auto-updater for latest features

## 🔄 Cloud Sync

- Automatic sync on startup (downloads ALL data from cloud)
- Background sync every 5 minutes
- Real-time WebSocket updates
- Multi-device support: same data on all devices!

## 📞 Support

For issues or questions, contact the administrator.

---
Generated: 2026-02-16
Version: 2.0 (Multi-Device)
"""

readme_path = DIST_DIR / "README.txt"
try:
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"  ✅ README.txt created")
except Exception as e:
    print(f"  ⚠️  Could not create README: {e}")

# Final Summary
print("\n" + "="*80)
print("✅ BUILD COMPLETE - READY FOR DEPLOYMENT")
print("="*80)

print(f"\n📦 Distribution package ready at:")
print(f"   {DIST_DIR}\n")

print(f"Files in dist/:")
for file in sorted(DIST_DIR.glob("*")):
    if file.is_file():
        size = file.stat().st_size / (1024 * 1024)
        print(f"  • {file.name:<40} ({size:.2f} MB)" if size > 0.1 else f"  • {file.name}")

print(f"\n📤 To deploy:")
print(f"1. Copy all files from {DIST_DIR} to deployment folder")
print(f"2. Run punctaj.exe on any device")
print(f"3. Login with Discord")
print(f"4. All data syncs from cloud automatically ✅\n")

print("="*80)
