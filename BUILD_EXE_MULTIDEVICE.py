#!/usr/bin/env python3
"""
Build punctaj.exe with multi-device Discord auth fix
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

def clean_build_artifacts():
    """Clean old build artifacts"""
    print("🧹 Cleaning old build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            try:
                shutil.rmtree(dir_name)
                print(f"   ✅ Removed {dir_name}/")
            except Exception as e:
                print(f"   ⚠️  Could not remove {dir_name}: {e}")

def build_exe():
    """Build punctaj.exe with PyInstaller"""
    print("\n🔨 Building punctaj.exe with multi-device fix...")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=punctaj",
        "--onefile",
        "--windowed",
        "--hidden-import=tkinter",
        "--hidden-import=requests",
        "--hidden-import=cryptography",
        "--add-data=supabase_config.ini:.",
        "--add-data=discord_config.ini:.",
        "--collect-all=tkinter",
        "--distpath=dist",
        "--workpath=build",
        "--clean",
        "punctaj.py"
    ]
    
    # Add icon if exists
    if Path("punctaj.ico").exists():
        cmd.insert(5, f"--icon=punctaj.ico")
    
    try:
        print(f"Command: {' '.join(cmd[:8])}...\n")
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Build successful!")
            return True
        else:
            print(f"\n❌ Build failed with return code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False

def verify_exe():
    """Verify the built exe"""
    print("\n✅ Verifying built executable...")
    
    exe_path = Path("dist/punctaj.exe")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ punctaj.exe created successfully")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Path: {exe_path.absolute()}")
        return True
    else:
        print(f"❌ punctaj.exe not found at {exe_path}")
        return False

def copy_config_files():
    """Copy configuration files to dist folder"""
    print("\n📋 Copying configuration files...")
    
    config_files = [
        "supabase_config.ini",
        "discord_config.ini",
    ]
    
    dist_path = Path("dist")
    
    for config_file in config_files:
        if Path(config_file).exists():
            try:
                shutil.copy2(config_file, dist_path / config_file)
                print(f"   ✅ Copied {config_file}")
            except Exception as e:
                print(f"   ⚠️  Could not copy {config_file}: {e}")

def main():
    print("="*70)
    print("🚀 BUILD PUNCTAJ.EXE WITH MULTI-DEVICE DISCORD AUTH FIX")
    print("="*70)
    print()
    
    # Step 1: Clean
    clean_build_artifacts()
    
    # Step 2: Build
    if not build_exe():
        print("\n❌ Build failed!")
        return False
    
    # Step 3: Copy configs
    copy_config_files()
    
    # Step 4: Verify
    if not verify_exe():
        print("\n❌ Verification failed!")
        return False
    
    print("\n" + "="*70)
    print("✨ BUILD COMPLETE!")
    print("="*70)
    print("""
✅ Improvements included in this build:
   - Thread-safe Discord authentication
   - Multi-device support (different devices can use same account)
   - Fresh login every session (no token caching)
   - Device isolation (each device gets unique ID)
   - Conflict prevention (locks prevent simultaneous auth)

📦 Ready to use:
   1. Find punctaj.exe in the dist/ folder
   2. Extract the portable package with CREATE_PORTABLE_PACKAGE.py
   3. Test on multiple devices with same Discord account

🔧 What changed internally:
   - Added threading lock for concurrent auth prevention
   - Device ID generation for tracking
   - Improved error handling for multi-device scenarios
""")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
