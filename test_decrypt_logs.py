#!/usr/bin/env python3
"""Test decryption of local encrypted log files"""

import os
import sys
import glob
import json

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("🔐 TESTING ENCRYPTED LOG DECRYPTION")
print("=" * 80)

# Test 1: Find encrypted log files
print("\n1️⃣  SCANNING FOR ENCRYPTED LOG FILES")
print("-" * 80)

logs_dir = "logs"
enc_files = glob.glob(os.path.join(logs_dir, "*/*.enc"))
print(f"✅ Found {len(enc_files)} encrypted files:")
for f in enc_files[:10]:
    print(f"   📄 {f}")
if len(enc_files) > 10:
    print(f"   ... and {len(enc_files) - 10} more")

# Test 2: Try to import encryption module
print("\n2️⃣  CHECKING ENCRYPTION MODULE")
print("-" * 80)

try:
    from json_encryptor import load_protected_json, save_protected_json
    print("✅ json_encryptor module imported successfully")
except ImportError as e:
    print(f"❌ FAILED to import: {e}")
    sys.exit(1)

# Test 3: Attempt to decrypt ONE file
print("\n3️⃣  TESTING DECRYPTION ON FIRST LOG FILE")
print("-" * 80)

test_file = None
for f in enc_files:
    if "SUMMARY" not in f:
        test_file = f
        break

if test_file:
    print(f"Testing file: {test_file}")
    try:
        logs_data = load_protected_json(test_file, decrypt=True)
        print(f"✅ DECRYPTED successfully!")
        print(f"   Type: {type(logs_data)}")
        print(f"   Entries: {len(logs_data) if isinstance(logs_data, list) else 'single record'}")
        
        # Show first entry
        if isinstance(logs_data, list) and len(logs_data) > 0:
            first = logs_data[0]
            print(f"\n   📝 FIRST LOG ENTRY:")
            print(f"      action_type: {first.get('action_type', 'N/A')}")
            print(f"      entity_name: {first.get('entity_name', 'N/A')}")
            print(f"      discord_username: {first.get('discord_username', 'N/A')}")
            print(f"      timestamp: {first.get('timestamp', 'N/A')}")
    except Exception as e:
        print(f"❌ FAILED to decrypt: {e}")
        import traceback
        traceback.print_exc()

# Test 4: Batch test all institution files
print("\n4️⃣  BATCH TESTING ALL INSTITUTION LOG FILES")
print("-" * 80)

success_count = 0
fail_count = 0

for log_file in enc_files:
    if "SUMMARY" in log_file:
        continue
    
    try:
        logs_data = load_protected_json(log_file, decrypt=True)
        if isinstance(logs_data, list):
            entry_count = len(logs_data)
        else:
            entry_count = 1
        
        print(f"✅ {os.path.basename(log_file)}: {entry_count} entries")
        success_count += 1
    except Exception as e:
        print(f"❌ {os.path.basename(log_file)}: {str(e)[:50]}")
        fail_count += 1

print(f"\n   Summary: {success_count} files ok, {fail_count} files failed")

# Test 5: Verify Supabase table is ready
print("\n5️⃣  VERIFYING SUPABASE AUDIT_LOGS TABLE")
print("-" * 80)

try:
    # Load Supabase config
    import configparser
    config = configparser.ConfigParser()
    config.read('supabase_config.ini')
    
    url = config.get('supabase', 'url')
    key = config.get('supabase', 'key')
    
    import requests
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    # Check if audit_logs table exists
    response = requests.get(f"{url}/rest/v1/audit_logs?limit=1", headers=headers, timeout=5)
    
    if response.status_code == 200:
        print("✅ audit_logs table is accessible")
        data = response.json()
        print(f"   Available records: {len(data) if isinstance(data, list) else 'unknown'}")
    else:
        print(f"⚠️  audit_logs table not accessible: HTTP {response.status_code}")
except Exception as e:
    print(f"⚠️  Could not verify Supabase: {e}")

print("\n" + "=" * 80)
print("✅ DECRYPTION TEST COMPLETE")
print("=" * 80)
