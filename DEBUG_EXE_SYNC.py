#!/usr/bin/env python3
"""
Diagnostica: Testeaza daca EXE-ul sincronizeaza datele din Supabase
"""

import os
import sys

# Verify we're in EXE
is_exe = getattr(sys, 'frozen', False)
bundle_dir = getattr(sys, '_MEIPASS', None)

print("=" * 70)
print("DEBUGGING EXE DATA LOADING")
print("=" * 70)
print(f"\n[*] Running mode: {'EXE' if is_exe else 'PYTHON SCRIPT'}")
print(f"[*] Bundle dir: {bundle_dir}")
print(f"[*] Current dir: {os.getcwd()}")
print(f"[*] Script file: {__file__}")

# Import and test
try:
    print("\n[1] Testing config loading...")
    from config_loader_robust import RobustConfigLoader
    
    cfg = RobustConfigLoader(debug=True)
    if cfg.is_valid():
        print(f"✅ Config valid: {cfg.get_url()[:50]}...")
    else:
        print(f"❌ Config invalid!")
        sys.exit(1)
    
    print("\n[2] Testing SupabaseSync module...")
    from supabase_sync import SupabaseSync
    
    sync = SupabaseSync(cfg.get_config_path())
    print(f"✅ SupabaseSync initialized")
    print(f"   URL: {sync.url[:50]}...")
    print(f"   Enabled: {sync.enabled}")
    print(f"   Auto-sync: {sync.auto_sync}")
    
    print("\n[3] Testing sync_all_from_cloud()...")
    DATA_DIR = os.path.join(os.getcwd(), "data")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    result = sync.sync_all_from_cloud(DATA_DIR)
    print(f"Sync result: {result}")
    
    if result.get("status") == "success":
        print(f"✅ Downloaded: {result.get('downloaded', 0)} files")
        print(f"   Cities: {result.get('cities', [])}")
    else:
        print(f"❌ Sync failed: {result.get('message')}")
    
    print("\n[4] Checking data files created...")
    if os.path.exists(DATA_DIR):
        for root, dirs, files in os.walk(DATA_DIR):
            level = root.replace(DATA_DIR, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for f in files[:10]:
                size = os.path.getsize(os.path.join(root, f)) / 1024
                print(f'{subindent}{f} ({size:.1f} KB)')
            if len(files) > 10:
                print(f'{subindent}... and {len(files)-10} more files')
    else:
        print(f"❌ Data dir doesn't exist: {DATA_DIR}")
    
    print("\n[5] Testing SupabaseEmployeeManager...")
    from supabase_employee_manager import SupabaseEmployeeManager
    
    emp_mgr = SupabaseEmployeeManager()
    print(f"✅ EmployeeManager initialized")
    
    # Try to get cities
    cities = emp_mgr.get_all_cities()
    print(f"   Cities: {cities}")
    
    if cities:
        for city in cities[:3]:
            insts = emp_mgr.get_institutions_by_city(city['id'])
            print(f"   - {city['name']}: {len(insts)} institutions")
    
    print("\n✅ ALL TESTS PASSED")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
