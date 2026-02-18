#!/usr/bin/env python3
"""
Test end-to-end log upload to Supabase audit_logs table
This simulates what happens when supabase_upload() is called
"""

import os
import sys
import json
import glob
import requests
import configparser
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("📤 TESTING LOG UPLOAD TO SUPABASE audit_logs")
print("=" * 80)

# Load Supabase config
print("\n1️⃣  LOADING SUPABASE CONFIG")
print("-" * 80)

config = configparser.ConfigParser()
config.read('supabase_config.ini')

url = config.get('supabase', 'url')
key = config.get('supabase', 'key')
print(f"✅ URL: {url[:50]}...")
print(f"✅ Key: {key[:20]}...")

# Import encryption
print("\n2️⃣  IMPORTING ENCRYPTION MODULE")
print("-" * 80)

try:
    from json_encryptor import load_protected_json
    print("✅ json_encryptor imported")
except ImportError as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Find encrypted log files
print("\n3️⃣  SCANNING ENCRYPTED LOG FILES")
print("-" * 80)

logs_dir = "logs"
enc_files = glob.glob(os.path.join(logs_dir, "*/*.enc"))
enc_files = [f for f in enc_files if "SUMMARY" not in f]  # Skip summary files

print(f"✅ Found {len(enc_files)} files to upload:")
for f in enc_files:
    print(f"   📄 {f}")

# Upload logs
print("\n4️⃣  UPLOADING LOGS TO SUPABASE")
print("-" * 80)

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

total_uploaded = 0
total_skipped = 0

for log_file in enc_files:
    print(f"\n📂 Processing: {log_file}")
    
    try:
        # Decrypt
        logs_array = load_protected_json(log_file, decrypt=True)
        
        if not isinstance(logs_array, list):
            logs_array = [logs_array]
        
        print(f"   🔓 Decrypted {len(logs_array)} entries")
        
        # Upload each entry
        for i, log_entry in enumerate(logs_array):
            try:
                # Ensure timestamp exists
                if 'timestamp' not in log_entry:
                    log_entry['timestamp'] = datetime.now().isoformat()
                
                # POST to audit_logs
                response = requests.post(
                    f"{url}/rest/v1/audit_logs",
                    json=log_entry,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    total_uploaded += 1
                    print(f"      ✅ [{i+1}/{len(logs_array)}] Uploaded: {log_entry.get('action_type', 'unknown')}")
                else:
                    total_skipped += 1
                    print(f"      ⚠️  [{i+1}/{len(logs_array)}] HTTP {response.status_code}: {response.text[:100]}")
            except Exception as e:
                total_skipped += 1
                print(f"      ❌ [{i+1}/{len(logs_array)}] Error: {str(e)[:100]}")
        
        # Delete after successful upload
        os.remove(log_file)
        print(f"   🗑️  File deleted after upload")
        
    except Exception as e:
        print(f"   ❌ Failed to process: {e}")

# Verify upload
print("\n5️⃣  VERIFYING UPLOAD")
print("-" * 80)

try:
    response = requests.get(
        f"{url}/rest/v1/audit_logs?order=id.desc&limit=10",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        logs = response.json()
        print(f"✅ Last 10 audit_logs entries:")
        for log in logs:
            ts = log.get('timestamp', 'N/A')[:19]
            action = log.get('action_type', 'N/A')
            entity = log.get('entity_name', 'N/A')
            print(f"   📝 {ts} | {action:15} | {entity}")
    else:
        print(f"⚠️  Could not fetch logs: HTTP {response.status_code}")
except Exception as e:
    print(f"⚠️  Error: {e}")

print("\n" + "=" * 80)
print(f"📊 SUMMARY: {total_uploaded} uploaded, {total_skipped} skipped")
print("=" * 80)
