#!/usr/bin/env python3
"""
Punctaj Installer
Self-extracting installer for Punctaj Application
"""

import sys
import os
import shutil
from pathlib import Path

def setup_application():
    """Setup Punctaj application"""
    print("\n" + "="*60)
    print("PUNCTAJ APPLICATION - INSTALLATION")
    print("="*60 + "\n")
    
    app_dir = Path.cwd()
    
    # Check for Punctaj.exe
    exe_path = app_dir / "Punctaj.exe"
    if not exe_path.exists():
        print("ERROR: Punctaj.exe not found in current directory!")
        print(f"Expected location: {exe_path}")
        input("\nPress Enter to exit...")
        return False
    
    print(f"✓ Punctaj.exe found: {exe_path.name}")
    
    # Create required folders
    print("\nCreating application folders...")
    folders = ["data", "arhiva", "logs"]
    for folder in folders:
        folder_path = app_dir / folder
        folder_path.mkdir(exist_ok=True)
        print(f"  ✓ {folder}/")
    
    # Check configuration files
    print("\nConfiguration files:")
    config_files = ["discord_config.ini", "supabase_config.ini"]
    for config in config_files:
        config_path = app_dir / config
        if config_path.exists():
            print(f"  ✓ {config}")
        else:
            print(f"  ✗ {config} (missing)")
    
    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60 + "\n")
    
    print("✓ Punctaj is ready to use!")
    print("\nIMPORTANT:")
    print("1. Edit supabase_config.ini with your database credentials")
    print("2. (Optional) Edit discord_config.ini for Discord OAuth")
    print("3. Run Punctaj.exe to start the application")
    
    print("\n" + "="*60)
    print("\nPress Enter to open the application folder...")
    input()
    
    # Open folder in Explorer
    os.startfile(str(app_dir))
    
    return True

if __name__ == "__main__":
    try:
        success = setup_application()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
