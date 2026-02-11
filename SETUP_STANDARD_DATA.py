#!/usr/bin/env python3
"""
Standard Data Directory Setup
Configures Punctaj/Data folder on any device for cloud sync
"""

import os
import sys
from pathlib import Path

def setup_standard_data_environment():
    """Setup standard data environment on ANY device"""
    
    print("\n" + "="*70)
    print("🏗️  SETTING UP STANDARD DATA ENVIRONMENT")
    print("="*70)
    
    # Determine where we are
    if getattr(sys, 'frozen', False):
        exe_dir = Path(os.path.dirname(sys.executable))
        running_as = "EXE"
    else:
        exe_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        running_as = "SCRIPT"
    
    print(f"\nRunning as: {running_as}")
    print(f"Installation dir: {exe_dir}")
    
    # Standard folder structure
    required_dirs = [
        "data",
        "data/BlackWater",
        "data/Saint_Denis",
        "arhiva",
        "logs",
        ".config"
    ]
    
    print(f"\n📁 Creating standard folder structure:")
    
    for dir_name in required_dirs:
        dir_path = exe_dir / dir_name
        
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created: {dir_path.relative_to(exe_dir)}")
        else:
            print(f"   ✓ Exists: {dir_path.relative_to(exe_dir)}")
    
    # Verify structure
    print(f"\n✅ Standard data structure verified at: {exe_dir}")
    print(f"\nOn ANY device, this app will:")
    print(f"  📂 Store local data in: <installation>/data/")
    print(f"  ☁️  Download cloud data to: <installation>/data/")
    print(f"  📋 Keep logs in: <installation>/logs/")
    print(f"  📦 Archive old data in: <installation>/arhiva/")
    
    return exe_dir

def print_multidevice_data_setup():
    """Print guide for setting up multiple devices"""
    
    guide = """
═══════════════════════════════════════════════════════════════════════════════
📋 MULTI-DEVICE DATA SYNCHRONIZATION SETUP
═══════════════════════════════════════════════════════════════════════════════

HOW IT WORKS:
─────────────────────────────────────────────────────────────────────────────

Each device has its own folder: Punctaj_Device1, Punctaj_Device2, etc.

DEVICE 1 (PC):
  C:\\Punctaj_Device1\\
  ├── punctaj.exe
  ├── supabase_config.ini
  ├── data/                    ← Local cache
  │   ├── BlackWater/
  │   │   └── Politie.json    ← Downloaded from cloud
  │   └── Saint_Denis/
  │       └── Politie.json    ← Downloaded from cloud
  └── arhiva/                  ← Archive

DEVICE 2 (Laptop):
  C:\\Punctaj_Device2\\
  ├── punctaj.exe
  ├── supabase_config.ini
  ├── data/                    ← Local cache (SAME structure)
  │   ├── BlackWater/
  │   │   └── Politie.json    ← Auto-downloads from cloud
  │   └── Saint_Denis/
  │       └── Politie.json    ← Auto-downloads from cloud
  └── arhiva/

DEVICE 3 (Tablet):
  C:\\Punctaj_Device3\\        ← SAME structure as Device 1 & 2
  └── data/


HOW DATA FLOWS:
─────────────────────────────────────────────────────────────────────────────

1. Device 1 adds employee record
   ↓
2. Save locally to Punctaj_Device1/data/BlackWater/Politie.json
   ↓
3. Upload to Cloud (Supabase)
   ↓
4. Device 2 starts app
   ↓
5. App downloads from Cloud
   ↓
6. Save to Punctaj_Device2/data/BlackWater/Politie.json
   ↓
7. Device 2 sees all data from Device 1 ✅


STARTUP SEQUENCE:
─────────────────────────────────────────────────────────────────────────────

On ANY device:

1. App starts
2. Detects: Punctaj_Device1/ folder structure
3. Creates standard data dirs if missing
4. Initializes DataDirectoryManager
5. Loads config from supabase_config.ini
6. Connects to Supabase
7. Downloads cloud data → data/ folder
8. App ready to use ✅


DATA LOCATIONS (STANDARDIZED):
─────────────────────────────────────────────────────────────────────────────

Local data:     <app_folder>/data/[CityName]/Politie.json
Archive:        <app_folder>/arhiva/
Logs:           <app_folder>/logs/
Config:         <app_folder>/.config/

This is IDENTICAL across all devices.


SYNCHRONIZATION:
─────────────────────────────────────────────────────────────────────────────

When you edit data:
  1. Changes saved to local file (data/...)
  2. Synced to cloud (Supabase)
  3. Other devices auto-download when they load the app

All devices see the SAME data because:
  ✅ Same Supabase database
  ✅ Same Discord account
  ✅ Standard data folders
  ✅ Automatic cloud sync


TESTING MULTI-DEVICE:
─────────────────────────────────────────────────────────────────────────────

Device 1:
  1. Extract ZIP → C:\\Punctaj_Device1
  2. Run punctaj.exe
  3. Add employee: "John Doe"
  4. Save

Device 2:
  1. Extract ZIP → C:\\Punctaj_Device2
  2. Run punctaj.exe
  3. Should see "John Doe" automatically ✅

Device 1 (refresh):
  1. Restart app or sync manually
  2. Should see any changes from Device 2 ✅


TROUBLESHOOTING:
─────────────────────────────────────────────────────────────────────────────

If data folder is empty:
  → Run: py DIAGNOSE_SUPABASE.py
  → Check cloud connection
  → Re-run app to sync

If files are in wrong folder:
  → Check that Punctaj/data/ exists
  → Verify supabase_config.ini is present
  → Run app startup setup

If devices don't sync:
  → Both must use SAME Discord account
  → Both must use SAME supabase_config.ini
  → Check internet connection
  → Manually run cloud sync


KEY FEATURES:
─────────────────────────────────────────────────────────────────────────────

✅ Standard folder structure on all devices
✅ Automatic cloud download on startup  
✅ Local cache in Punctaj/data/
✅ Real-time sync between devices
✅ No file conflicts
✅ Automatic backup to arhiva/
✅ Audit logs in logs/


═══════════════════════════════════════════════════════════════════════════════
"""
    
    print(guide)

if __name__ == "__main__":
    exe_dir = setup_standard_data_environment()
    print_multidevice_data_setup()
    
    print("\n✨ Setup complete!")
    print(f"App is ready to store and sync data in: {exe_dir}/data/")
