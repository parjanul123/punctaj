#!/usr/bin/env python3
"""
Test end-to-end logging workflow
Verifică dacă ActionLogger uploadează direct pe Supabase
"""

import os
import sys
import configparser
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("🔍 DIAGNOSTIC: TESTING ACTIONLOGGER UPLOAD")
print("=" * 80)

# Load config
config = configparser.ConfigParser()
config.read('supabase_config.ini')
url = config.get('supabase', 'url')
key = config.get('supabase', 'key')

# Check if ActionLogger exists
print("\n1️⃣  CHECKING ACTIONLOGGER MODULE")
print("-" * 80)

try:
    from action_logger import ActionLogger
    print("✅ ActionLogger imported")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

# Create mock Supabase sync
print("\n2️⃣  CREATING MOCK SUPABASE SYNC")
print("-" * 80)

class MockSupabaseSync:
    def __init__(self):
        self.url = url
        self.key = key
        self.table_logs = "audit_logs"

mock_sync = MockSupabaseSync()
print(f"✅ Mock sync created")
print(f"   URL: {url[:50]}...")
print(f"   Table: audit_logs")

# Initialize ActionLogger
print("\n3️⃣  INITIALIZING ACTIONLOGGER")
print("-" * 80)

action_logger = ActionLogger(mock_sync, logs_dir="logs")
print("✅ ActionLogger initialized")

# Test logging an action
print("\n4️⃣  TESTING LOG_ACTION")
print("-" * 80)

test_log_result = action_logger.log_action(
    file_path="TestEmployee",
    discord_id="123456",
    discord_username="testuser",
    action_type="test_add_employee",
    details="Test action for diagnostic"
)

print(f"   Result: {test_log_result}")

# Check Supabase table
print("\n5️⃣  CHECKING SUPABASE audit_logs TABLE")
print("-" * 80)

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

try:
    response = requests.get(
        f"{url}/rest/v1/audit_logs?order=id.desc&limit=5",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        logs = response.json()
        print(f"✅ Got {len(logs)} recent logs:")
        for log in logs:
            ts = log.get('timestamp', 'N/A')[:19]
            action = log.get('action_type', 'N/A')
            entity = log.get('entity_name', log.get('details', 'N/A')[:30])
            user = log.get('discord_username', 'N/A')
            print(f"   📝 {ts} | {action:20} | {entity:30} | {user}")
    else:
        print(f"❌ Could not fetch: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Check local encrypted logs
print("\n6️⃣  CHECKING LOCAL ENCRYPTED LOGS")
print("-" * 80)

import glob
enc_files = glob.glob("logs/*/*.enc")
enc_files = [f for f in enc_files if "SUMMARY" not in f]

if enc_files:
    print(f"✅ Found {len(enc_files)} local encrypted files:")
    for f in enc_files:
        print(f"   📄 {f}")
else:
    print("ℹ️  No local encrypted logs found")

print("\n" + "=" * 80)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 80)
