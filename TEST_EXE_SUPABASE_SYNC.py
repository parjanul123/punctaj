#!/usr/bin/env python3
"""
Test script to verify Supabase sync works correctly in the built EXE
Testează dacă sincronizarea Supabase funcționează corect în EXE-ul construit
"""

import os
import sys
import time
import subprocess
import json

print("="*80)
print("🔍 TESTING SUPABASE SYNC IN EXE")
print("="*80)

# Paths
EXE_PATH = r"d:\punctaj\dist\punctaj\Punctaj.exe"
DIST_DIR = r"d:\punctaj\dist\punctaj"
CONFIG_FILE = os.path.join(DIST_DIR, "supabase_config.ini")

# 1. Verify files exist
print("\n1️⃣ Checking if config files exist:")
print(f"   EXE: {EXE_PATH}")
if os.path.exists(EXE_PATH):
    print(f"      ✅ Found")
else:
    print(f"      ❌ NOT FOUND")
    sys.exit(1)

print(f"   Config: {CONFIG_FILE}")
if os.path.exists(CONFIG_FILE):
    print(f"      ✅ Found")
    # Read and display config
    with open(CONFIG_FILE, 'r') as f:
        config_content = f.read()
    print(f"\n   Config content:")
    for line in config_content.split('\n'):
        if 'key' in line.lower():
            # Hide API key
            print(f"      {line[:50]}...")
        elif line.strip():
            print(f"      {line}")
else:
    print(f"      ❌ NOT FOUND - This is the MAIN ISSUE!")
    sys.exit(1)

# 2. Check data folder
print(f"\n2️⃣ Checking data folder:")
data_dir = os.path.join(DIST_DIR, "data")
if os.path.exists(data_dir):
    print(f"   ✅ Data folder found: {data_dir}")
    files = os.listdir(data_dir)
    print(f"   📁 Files: {len(files)}")
    for f in files[:5]:
        print(f"      - {f}")
else:
    print(f"   ⚠️ Data folder not found")

# 3. Verify all required modules are available
print(f"\n3️⃣ Checking if all sync modules are available:")
sync_modules = [
    'supabase_sync.py',
    'cloud_sync_manager.py',
    'multi_device_sync_manager.py',
    'realtime_sync.py',
    'permission_sync_fix.py',
]

for module in sync_modules:
    module_path = os.path.join(DIST_DIR, module)
    if os.path.exists(module_path):
        print(f"   ✅ {module}")
    else:
        print(f"   ⚠️ {module} - might be in _internal/")

# 4. Run simple diagnostic
print(f"\n4️⃣ Running diagnostic script:")
diagnostic_script = """
import sys
import os
import configparser

sys.path.insert(0, '.')

try:
    from supabase_sync import SupabaseSync
    print("✅ SupabaseSync module imported successfully")
    
    if os.path.exists('supabase_config.ini'):
        sync = SupabaseSync('supabase_config.ini')
        print(f"✅ Supabase initialized: {sync.url}")
        print(f"   Table: {sync.table_sync}")
        print(f"   Enabled: {sync.enabled}")
        print(f"   Auto-sync: {sync.auto_sync}")
        
        # Try a simple connection test
        headers = {
            "apikey": sync.key,
            "Authorization": f"Bearer {sync.key}",
            "Content-Type": "application/json"
        }
        
        import requests
        url = f"{sync.url}/rest/v1/{sync.table_sync}?limit=1"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ Connection to Supabase: SUCCESS (HTTP 200)")
            else:
                print(f"⚠️ Connection to Supabase: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️ Connection test error: {e}")
    else:
        print("❌ supabase_config.ini not found")
        
except ImportError as e:
    print(f"❌ SupabaseSync import failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
"""

# Write and run diagnostic
diag_file = os.path.join(DIST_DIR, "_test_sync.py")
with open(diag_file, 'w') as f:
    f.write(diagnostic_script)

try:
    result = subprocess.run(
        [sys.executable, diag_file],
        cwd=DIST_DIR,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print(f"   Output:")
    for line in result.stdout.split('\n'):
        if line.strip():
            print(f"   {line}")
    
    if result.stderr:
        print(f"   Errors:")
        for line in result.stderr.split('\n'):
            if line.strip():
                print(f"   {line}")
                
except subprocess.TimeoutExpired:
    print("   ⚠️ Diagnostic timed out")
except Exception as e:
    print(f"   ❌ Error running diagnostic: {e}")
finally:
    if os.path.exists(diag_file):
        os.remove(diag_file)

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)
print("\n📝 SUMMARY:")
print("   If all checks passed, Supabase sync should now work in the EXE!")
print("   If config files are present, the app should sync data correctly.")
print("\n🚀 Next steps:")
print("   1. Run the EXE: d:\\punctaj\\dist\\punctaj\\Punctaj.exe")
print("   2. Login with Discord")
print("   3. Check if data syncs from Supabase cloud")
print("   4. Watch the console for sync messages")
