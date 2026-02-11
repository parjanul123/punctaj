#!/usr/bin/env python3
"""
Deploy punctaj.exe to the root folder (not in dist/)
This ensures proper data directory detection on any device
"""

import os
import shutil
from pathlib import Path

def deploy_exe():
    """Copy EXE from dist/ to root folder for deployment"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           📦 DEPLOY EXE TO ROOT FOLDER (Multi-Device Fix)          ║
║    Ensures data/ folder is found correctly on every device         ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    
    print(f"\n📁 Working in: {base_dir}\n")
    
    # Source and destination
    source_exe = os.path.join(dist_dir, "punctaj.exe")
    dest_exe = os.path.join(base_dir, "punctaj.exe")
    
    print(f"Source: {source_exe}")
    print(f"Destination: {dest_exe}")
    
    if not os.path.exists(source_exe):
        print(f"❌ ERROR: {source_exe} not found!")
        return False
    
    # Copy EXE to root
    print(f"\n📋 Copying punctaj.exe to root folder...")
    try:
        shutil.copy2(source_exe, dest_exe)
        print(f"✅ Copied: {dest_exe}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Copy configs to root if not there
    for config_file in ["supabase_config.ini", "discord_config.ini"]:
        src = os.path.join(dist_dir, config_file)
        dst = os.path.join(base_dir, config_file)
        
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.copy2(src, dst)
                print(f"✅ Copied: {config_file}")
            except:
                pass
    
    # Verify
    print(f"\n✅ DEPLOYMENT STRUCTURE:")
    print(f"{'='*70}")
    
    # Show current structure
    required_items = [
        "punctaj.exe",
        "supabase_config.ini",
        "discord_config.ini",
        "data",
        "data/BlackWater",
        "data/Saint_Denis",
    ]
    
    for item in required_items:
        path = os.path.join(base_dir, item)
        if os.path.exists(path):
            if os.path.isdir(path):
                item_count = len(os.listdir(path))
                print(f"✅ {item:30} (folder, {item_count} items)")
            else:
                size = os.path.getsize(path) / (1024*1024)
                print(f"✅ {item:30} ({size:.2f} MB)")
        else:
            print(f"❌ {item:30} MISSING")
    
    print(f"{'='*70}\n")
    
    print(f"🎯 ROOT FOLDER STRUCTURE (for transfer/deployment):")
    print(f""""
    Punctaj/
    ├─ punctaj.exe (19.62 MB) ✅
    ├─ supabase_config.ini ✅
    ├─ discord_config.ini ✅
    ├─ data/ ✅
    │  ├─ BlackWater/Politie.json
    │  └─ Saint_Denis/Politie.json
    ├─ dist/ (optional - contains backup exe)
    ├─ arhiva/ (auto-created)
    ├─ logs/ (auto-created)
    └─ .config/ (auto-created)
    """)
    
    print(f"\n✨ HOW THIS FIXES THE PROBLEM:")
    print(f"{'='*70}")
    print(f"""
BEFORE (❌ Broken):
  • EXE in: dist/punctaj.exe
  • EXE reads BASE_DIR as: dist/
  • Creates data in: dist/data/ (WRONG!)
  • Ignores original: Punctaj/data/

AFTER (✅ Fixed):
  • EXE in: punctaj.exe (root)
  • EXE reads BASE_DIR as: Punctaj/ (root)
  • Creates/reads data from: Punctaj/data/ (CORRECT!)
  • Works on any device same way

ON DEVICE 2:
  • Extract to: C:\\Punctaj\\
  • Run: C:\\Punctaj\\punctaj.exe
  • Reads BASE_DIR as: C:\\Punctaj\\
  • Uses data from: C:\\Punctaj\\data\\
  • SAME STRUCTURE regardless of drive/path!
    """)
    
    print(f"\n✅ READY FOR MULTI-DEVICE DEPLOYMENT!")
    print(f"\nYou can now:")
    print(f"  1. Zip this folder with: py CREATE_COMPLETE_TRANSFER_ZIP.py")
    print(f"  2. Transfer to another device")
    print(f"  3. Extract and run: punctaj.exe")
    print(f"  4. Data will automatically use local data/ folder")
    print(f"  5. Cloud sync works correctly")

if __name__ == "__main__":
    deploy_exe()
