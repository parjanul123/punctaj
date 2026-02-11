#!/usr/bin/env python3
"""
Quick check: Are all required files present for punctaj.exe?
"""

import os
import json
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    data_dir = os.path.join(base_dir, "data")
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           ✅ FILES VERIFICATION FOR punctaj.exe                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    checks = {
        "🔴 CRITICAL": [
            ("punctaj.exe", os.path.join(dist_dir, "punctaj.exe")),
            ("supabase_config.ini", os.path.join(dist_dir, "supabase_config.ini")),
            ("discord_config.ini", os.path.join(dist_dir, "discord_config.ini")),
        ],
        "🟡 IMPORTANT": [
            ("data/ folder", data_dir),
            ("data/BlackWater/ folder", os.path.join(data_dir, "BlackWater")),
            ("data/Saint_Denis/ folder", os.path.join(data_dir, "Saint_Denis")),
        ],
        "🟢 AUTO-CREATED": [
            ("arhiva/ folder", os.path.join(base_dir, "arhiva")),
            ("logs/ folder", os.path.join(base_dir, "logs")),
        ]
    }
    
    all_good = True
    
    for category, file_list in checks.items():
        print(f"\n{category}")
        print("-" * 70)
        
        for name, path in file_list:
            if os.path.exists(path):
                if os.path.isdir(path):
                    size = f"(folder with {len(os.listdir(path))} items)"
                else:
                    size = f"({os.path.getsize(path) / (1024*1024):.2f} MB)"
                print(f"  ✅ {name:30} {size}")
            else:
                print(f"  ❌ {name:30} MISSING!")
                all_good = False
    
    # Check config contents
    print(f"\n🔍 CONFIGURATION CHECK")
    print("-" * 70)
    
    try:
        with open(os.path.join(dist_dir, "supabase_config.ini"), 'r') as f:
            content = f.read()
            has_url = "url" in content
            has_key = "key" in content
            print(f"  {'✅' if has_url else '❌'} supabase_config.ini has 'url'")
            print(f"  {'✅' if has_key else '❌'} supabase_config.ini has 'key'")
    except:
        print(f"  ❌ supabase_config.ini not readable")
        all_good = False
    
    try:
        with open(os.path.join(dist_dir, "discord_config.ini"), 'r') as f:
            content = f.read()
            has_client = "client_id" in content
            has_secret = "client_secret" in content
            print(f"  {'✅' if has_client else '❌'} discord_config.ini has 'client_id'")
            print(f"  {'✅' if has_secret else '❌'} discord_config.ini has 'client_secret'")
    except:
        print(f"  ❌ discord_config.ini not readable")
        all_good = False
    
    # Check data files
    print(f"\n📊 DATA FILES CHECK")
    print("-" * 70)
    
    cities = ["BlackWater", "Saint_Denis"]
    for city in cities:
        json_file = os.path.join(data_dir, city, "Politie.json")
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    records = len(data.get('rows', []))
                    print(f"  ✅ {city:20} {records:5} employee records")
            except:
                print(f"  ❌ {city:20} File corrupted")
                all_good = False
        else:
            print(f"  ⚠️  {city:20} File will be created on first run")
    
    # Summary
    print(f"\n{'='*70}")
    if all_good:
        print("✅ ALL CRITICAL FILES PRESENT - READY TO USE!")
        print("\nYou can now:")
        print("  1. Double-click punctaj.exe to run")
        print("  2. Copy dist/ to another device")
        print("  3. Create deployment package with CREATE_COMPLETE_TRANSFER_ZIP.py")
    else:
        print("⚠️  SOME FILES MISSING - CHECK ABOVE")
        print("\nTo fix:")
        print("  • Run: py BUILD_EXE_MULTIDEVICE.py")
        print("  • Run: py SETUP_STANDARD_DATA.py")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    check_files()
