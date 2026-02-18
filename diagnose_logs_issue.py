#!/usr/bin/env python3
"""
Diagnostic script to check why logs are not being recorded
"""

import os
import json
import configparser
import requests
from datetime import datetime
from pathlib import Path

print("=" * 70)
print("🔍 DIAGNOSING LOG SYNC ISSUE")
print("=" * 70)

# Step 1: Check if logs exist locally
print("\n1️⃣  Checking local logs folder...")
logs_dir = "logs"
if os.path.exists(logs_dir):
    print(f"   ✅ {logs_dir}/ folder EXISTS")
    
    # Count files
    json_files = list(Path(logs_dir).rglob("*.json"))
    print(f"   📋 Found {len(json_files)} JSON files")
    
    if json_files:
        print(f"   Recent files:")
        for f in sorted(json_files)[-5:]:
            size = os.path.getsize(f)
            print(f"      • {f.name} ({size} bytes)")
else:
    print(f"   ❌ {logs_dir}/ folder DOES NOT EXIST")

# Step 2: Check if audit_logs table exists in Supabase
print("\n2️⃣  Checking audit_logs table in Supabase...")
config = configparser.ConfigParser()
config.read('supabase_config.ini')

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

try:
    url = f"{SUPABASE_URL}/rest/v1/audit_logs?limit=1"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        logs = response.json()
        print(f"   ✅ audit_logs table EXISTS")
        print(f"   📊 Total records in table: (need to count with full query)")
        
        if logs:
            print(f"   Sample record:")
            print(f"      {json.dumps(logs[0], indent=2)[:200]}...")
    elif response.status_code == 404:
        print(f"   ❌ audit_logs table DOES NOT EXIST")
    else:
        print(f"   ⚠️  Status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Check if we can insert a test log
print("\n3️⃣  Testing if we can insert a log entry...")
try:
    test_log = {
        "discord_id": "test_123",
        "discord_username": "test_user",
        "action_type": "test_insert",
        "city": "TEST",
        "institution": "TEST",
        "entity_name": "Test",
        "entity_id": "test_id",
        "details": "Test log entry",
        "timestamp": datetime.now().isoformat()
    }
    
    url = f"{SUPABASE_URL}/rest/v1/audit_logs"
    response = requests.post(url, json=test_log, headers=headers, timeout=5)
    
    if response.status_code in [200, 201]:
        print(f"   ✅ INSERT SUCCESS!")
        print(f"      Status: {response.status_code}")
    else:
        print(f"   ❌ INSERT FAILED (status {response.status_code})")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 4: Count total logs in audit_logs
print("\n4️⃣  Counting total audit logs in Supabase...")
try:
    url = f"{SUPABASE_URL}/rest/v1/audit_logs?select=count=exact"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        count = response.headers.get('content-range', '0/0')
        print(f"   📊 Total logs in audit_logs: {count}")
    else:
        print(f"   ⚠️  Cannot count (status {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 5: Check last few logs
print("\n5️⃣  Fetching last 5 logs from Supabase...")
try:
    url = f"{SUPABASE_URL}/rest/v1/audit_logs?order=timestamp.desc&limit=5"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        logs = response.json()
        print(f"   ✅ Retrieved {len(logs)} logs")
        
        for i, log in enumerate(logs, 1):
            print(f"\n   Log {i}:")
            print(f"      User: {log.get('discord_username')}")
            print(f"      Action: {log.get('action_type')}")
            print(f"      Entity: {log.get('entity_name')}")
            print(f"      Time: {log.get('timestamp')}")
    else:
        print(f"   ❌ Failed (status {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 70)
