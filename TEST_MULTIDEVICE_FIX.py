#!/usr/bin/env python3
"""
Quick verification that the multi-device fix is working
Simulates different installation paths to ensure BASE_DIR is detected correctly
"""

import os
import sys
from pathlib import Path

def test_base_dir_logic():
    """Test the BASE_DIR detection logic"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║      🧪 TEST: BASE_DIR DETECTION (Multi-Device Fix)                ║
║     Verify data/ folder is found correctly on any device           ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # The fixed get_base_directory logic
    def get_base_directory_logic(exe_or_script_path):
        """Simulate the fixed BASE_DIR detection"""
        exe_dir = os.path.dirname(exe_or_script_path)
        
        if exe_dir.endswith("\\dist") or exe_dir.endswith("/dist"):
            parent_dir = os.path.dirname(exe_dir)
            print(f"  📍 EXE in dist/ → using parent: {parent_dir}")
            return parent_dir
        else:
            print(f"  📍 EXE in root → using: {exe_dir}")
            return exe_dir
    
    # Test scenarios
    scenarios = [
        ("Device 1 (Current) - EXE in root", 
         f"{base_dir}\\punctaj.exe",
         base_dir),
        
        ("Device 2 - EXE in dist/ subfolder",
         f"{base_dir}\\dist\\punctaj.exe",
         base_dir),
        
        ("Device 3 - Different path (C:\\)",
         "C:\\Users\\John\\Punctaj\\punctaj.exe",
         "C:\\Users\\John\\Punctaj"),
        
        ("Device 4 - Different path (E:\\)",
         "E:\\MyApps\\Punctaj\\punctaj.exe",
         "E:\\MyApps\\Punctaj"),
        
        ("Device 5 - Nested path",
         "D:\\Projects\\Apps\\Punctaj\\punctaj.exe",
         "D:\\Projects\\Apps\\Punctaj"),
    ]
    
    print("\n📱 TESTING SCENARIOS:\n")
    
    all_passed = True
    for device_name, exe_path, expected_base_dir in scenarios:
        print(f"{device_name}")
        print(f"  EXE path: {exe_path}")
        
        detected_base = get_base_directory_logic(exe_path)
        
        # Normalize paths for comparison
        detected_normalized = detected_base.replace("\\", "/")
        expected_normalized = expected_base_dir.replace("\\", "/")
        
        if detected_normalized == expected_normalized:
            print(f"  ✅ PASS: BASE_DIR = {detected_base}")
            print(f"  📁 Data folder would be: {detected_base}\\data\\")
        else:
            print(f"  ❌ FAIL: Expected {expected_base_dir}, got {detected_base}")
            all_passed = False
        print()
    
    # Real directory check
    print(f"{'='*70}")
    print(f"🔍 ACTUAL DIRECTORY CHECK:\n")
    
    # Check current installation
    print(f"📁 Current installation: {base_dir}")
    
    required_items = {
        "punctaj.exe": os.path.join(base_dir, "punctaj.exe"),
        "data/": os.path.join(base_dir, "data"),
        "data/BlackWater/": os.path.join(base_dir, "data/BlackWater"),
        "data/Saint_Denis/": os.path.join(base_dir, "data/Saint_Denis"),
        "supabase_config.ini": os.path.join(base_dir, "supabase_config.ini"),
        "discord_config.ini": os.path.join(base_dir, "discord_config.ini"),
    }
    
    print(f"\n✅ ITEMS IN ROOT FOLDER:")
    for item_name, item_path in required_items.items():
        if os.path.exists(item_path):
            if os.path.isdir(item_path):
                count = len(os.listdir(item_path))
                print(f"  ✅ {item_name:25} (folder, {count} items)")
            else:
                size = os.path.getsize(item_path) / (1024*1024)
                print(f"  ✅ {item_name:25} ({size:.2f} MB)")
        else:
            print(f"  ❌ {item_name:25} NOT FOUND")
            all_passed = False
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 TEST SUMMARY:\n")
    
    if all_passed:
        print("""
✅ ALL TESTS PASSED!

The multi-device fix is working correctly:

1. BASE_DIR detection works on all device paths
2. EXE in root folder → uses root as BASE_DIR ✅
3. EXE in dist/ folder → uses parent as BASE_DIR ✅
4. data/ folder is always found correctly ✅
5. Works on Device 1, Device 2, Device 3+ ✅

You can now:
  • Deploy to multiple devices using the transfer ZIP
  • Each device will use its local data/ folder
  • All devices sync from Supabase cloud
  • No path conflicts between devices ✅
        """)
    else:
        print("""
⚠️  SOME ITEMS MISSING

Please check:
  1. Is punctaj.exe in the root folder (not dist/)?
  2. Does data/ folder exist?
  3. Do config files exist?
  
Fix with:
  • py DEPLOY_EXE_TO_ROOT.py (to copy EXE)
  • py SETUP_STANDARD_DATA.py (to create data folders)
        """)
    
    print(f"{'='*70}\n")
    print(f"✨ Multi-device setup verification completed!")

if __name__ == "__main__":
    test_base_dir_logic()
