#!/usr/bin/env python3
"""
Cloud Sync Testing Script
Testează funcționalităţile sistemului de sincronizare cloud
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase_sync import SupabaseSync
    from cloud_sync_manager import CloudSyncManager
    print("✅ Modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = os.path.join(BASE_DIR, "arhiva")

print(f"\n📂 Base Directory: {BASE_DIR}")
print(f"📂 Archive Directory: {ARCHIVE_DIR}")

# Initialize Supabase Sync
try:
    config_path = os.path.join(BASE_DIR, "supabase_config.ini")
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    SUPABASE_SYNC = SupabaseSync(config_path)
    print(f"✅ Supabase connected: {SUPABASE_SYNC.url}")
except Exception as e:
    print(f"❌ Supabase connection error: {e}")
    sys.exit(1)

# Initialize Cloud Sync Manager
try:
    CLOUD_SYNC = CloudSyncManager(SUPABASE_SYNC, BASE_DIR)
    print("✅ Cloud Sync Manager initialized")
except Exception as e:
    print(f"❌ Cloud Sync Manager error: {e}")
    sys.exit(1)

def test_sync_metadata_table():
    """Test 1: Check if sync_metadata table exists"""
    print("\n" + "="*60)
    print("TEST 1: Sync Metadata Table")
    print("="*60)
    
    try:
        response = SUPABASE_SYNC.table('sync_metadata').select('*').eq('sync_key', 'global_version').execute()
        
        if response.data and len(response.data) > 0:
            item = response.data[0]
            print(f"✅ Table exists and contains data:")
            print(f"   sync_key: {item.get('sync_key')}")
            print(f"   version: {item.get('version')}")
            print(f"   data_hash: {item.get('data_hash', 'None')}")
            print(f"   last_modified_at: {item.get('last_modified_at')}")
            return True
        else:
            print("❌ Table is empty - need to run CREATE_SYNC_METADATA_TABLE.sql")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_cloud_version():
    """Test 2: Get cloud version"""
    print("\n" + "="*60)
    print("TEST 2: Get Cloud Version")
    print("="*60)
    
    try:
        version, hash_val = CLOUD_SYNC._get_cloud_version()
        print(f"✅ Cloud version retrieved:")
        print(f"   Version: {version}")
        print(f"   Hash: {hash_val}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_update_cloud_version():
    """Test 3: Update cloud version"""
    print("\n" + "="*60)
    print("TEST 3: Update Cloud Version")
    print("="*60)
    
    try:
        # Get current version
        old_version, _ = CLOUD_SYNC._get_cloud_version()
        print(f"   Current version: {old_version}")
        
        # Update to new version
        new_version = old_version + 1
        result = CLOUD_SYNC.update_cloud_version(new_version)
        
        if result:
            print(f"✅ Version updated successfully to {new_version}")
            
            # Verify
            time.sleep(0.5)
            check_version, _ = CLOUD_SYNC._get_cloud_version()
            
            if check_version == new_version:
                print(f"✅ Verification: Version is now {check_version}")
                return True
            else:
                print(f"❌ Verification failed: Version is {check_version}, expected {new_version}")
                return False
        else:
            print("❌ Update failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_archive_structure():
    """Test 4: Check archive structure"""
    print("\n" + "="*60)
    print("TEST 4: Archive Structure")
    print("="*60)
    
    if not os.path.exists(ARCHIVE_DIR):
        print(f"⚠️  Archive directory does not exist: {ARCHIVE_DIR}")
        print(f"   This is normal if no resets have been performed yet")
        return True
    
    try:
        count = 0
        for city_folder in os.listdir(ARCHIVE_DIR):
            city_path = os.path.join(ARCHIVE_DIR, city_folder)
            if os.path.isdir(city_path):
                json_files = [f for f in os.listdir(city_path) if f.endswith('.json')]
                print(f"   📂 {city_folder}: {len(json_files)} JSON files")
                count += len(json_files)
        
        if count > 0:
            print(f"✅ Archive contains {count} archived reports")
            return True
        else:
            print(f"⚠️  Archive directory is empty (no resets performed yet)")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_supabase_storage_access():
    """Test 5: Check Supabase Storage access"""
    print("\n" + "="*60)
    print("TEST 5: Supabase Storage Access")
    print("="*60)
    
    try:
        # Try to list files in arhiva bucket
        response = SUPABASE_SYNC.storage.from_('arhiva').list('')
        
        if response is not None:
            count = len([f for f in response if f['name'] != '.emptyFolderPlaceholder'])
            print(f"✅ Storage bucket 'arhiva' is accessible")
            print(f"   Files in bucket: {count}")
            
            if count > 0:
                print(f"   Files: {[f['name'] for f in response if f['name'] != '.emptyFolderPlaceholder']}")
            
            return True
        else:
            print("❌ Storage bucket 'arhiva' not accessible or empty")
            return False
    except Exception as e:
        if "Bucket not found" in str(e):
            print("❌ Storage bucket 'arhiva' does not exist")
            print("   Solution: Create 'arhiva' bucket in Supabase Storage")
            return False
        else:
            print(f"❌ Error: {e}")
            return False

def test_polling_state():
    """Test 6: Check polling state"""
    print("\n" + "="*60)
    print("TEST 6: Polling State")
    print("="*60)
    
    print(f"   Polling active: {CLOUD_SYNC.polling_active}")
    print(f"   Is syncing: {CLOUD_SYNC.is_syncing}")
    print(f"   Sync pending: {CLOUD_SYNC.sync_pending}")
    
    if not CLOUD_SYNC.polling_active:
        print("⚠️  Polling not started - this is normal for test script")
        print("   It starts automatically when punctaj.py initializes")
        return True
    else:
        print("✅ Polling is active")
        return True

def test_log_sync_activity():
    """Test 7: Test sync log entry"""
    print("\n" + "="*60)
    print("TEST 7: Log Sync Activity")
    print("="*60)
    
    try:
        result = CLOUD_SYNC.log_sync_activity(
            discord_id="test_user_123",
            sync_type="test",
            status="success",
            items_count=5,
            error=None
        )
        
        if result:
            print("✅ Sync activity logged successfully")
            print("   Type: test")
            print("   Status: success")
            print("   Items: 5")
            return True
        else:
            print("❌ Failed to log sync activity")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("☁️  CLOUD SYNC SYSTEM - TEST SUITE")
    print("="*60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Version: {sys.version.split()[0]}")
    
    tests = [
        ("Sync Metadata Table", test_sync_metadata_table),
        ("Get Cloud Version", test_get_cloud_version),
        ("Update Cloud Version", test_update_cloud_version),
        ("Archive Structure", test_archive_structure),
        ("Supabase Storage Access", test_supabase_storage_access),
        ("Polling State", test_polling_state),
        ("Log Sync Activity", test_log_sync_activity),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Cloud sync is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
