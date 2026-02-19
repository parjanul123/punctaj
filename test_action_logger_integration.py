#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test if ActionLogger is being called and saves logs correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from action_logger import ActionLogger
from supabase_sync import SupabaseSync
import json

print("=" * 70)
print("🧪 TESTING ACTION LOGGER - SIMULATING ACTUAL USAGE")
print("=" * 70)

# Initialize SupabaseSync
print("\n1️⃣ Initializing SupabaseSync...")
try:
    supabase_sync = SupabaseSync()
    print(f"   ✅ SupabaseSync initialized")
    print(f"   📊 Table: {supabase_sync.table_logs}")
    print(f"   🔗 URL: {supabase_sync.url[:50]}...")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    sys.exit(1)

# Initialize ActionLogger
print("\n2️⃣ Initializing ActionLogger...")
try:
    action_logger = ActionLogger(supabase_sync, logs_dir="logs_test")
    print(f"   ✅ ActionLogger initialized")
    print(f"   📋 Logs dir: {os.path.abspath('logs_test')}")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    sys.exit(1)

# Test log_add_employee
print("\n3️⃣ Testing log_add_employee...")
try:
    employee_data = {
        "NOME_IC": "Ion Popescu",
        "RANK": "1",
        "PUNCTAJ": 0
    }
    
    result = action_logger.log_add_employee(
        discord_id="test_user_123",
        city="Saint_Denis",
        institution_name="Politie",
        employee_name="Ion Popescu",
        employee_data=employee_data,
        discord_username="test_user"
    )
    
    if result:
        print(f"   ✅ log_add_employee returned TRUE")
    else:
        print(f"   ❌ log_add_employee returned FALSE")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test log_edit_points
print("\n4️⃣ Testing log_edit_points...")
try:
    result = action_logger.log_edit_points(
        discord_id="test_user_123",
        city="Saint_Denis",
        institution_name="Politie",
        employee_name="Ion Popescu",
        old_points=0,
        new_points=5,
        discord_username="test_user"
    )
    
    if result:
        print(f"   ✅ log_edit_points returned TRUE")
    else:
        print(f"   ❌ log_edit_points returned FALSE")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Check local logs
print("\n5️⃣ Checking local logs...")
logs_dir = os.path.abspath("logs_test")
if os.path.exists(logs_dir):
    print(f"   ✅ logs_test folder exists")
    
    # Walk through directories
    for city in os.listdir(logs_dir):
        city_path = os.path.join(logs_dir, city)
        if os.path.isdir(city_path):
            for file in os.listdir(city_path):
                if file.endswith('.json'):
                    file_path = os.path.join(city_path, file)
                    print(f"   📋 Found: {city}/{file}")
                    
                    # Show content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            print(f"      📊 Contains {len(data)} log entries")
                            if data:
                                print(f"      First entry: {data[0].get('action_type', 'N/A')} - {data[0].get('details', 'N/A')[:50]}")
else:
    print(f"   ⚠️ logs_test folder does NOT exist")

# Check Supabase logs
print("\n6️⃣ Checking Supabase logs...")
try:
    import requests
    url = f"{supabase_sync.url}/rest/v1/{supabase_sync.table_logs}?order=timestamp.desc&limit=5"
    response = requests.get(url, headers={
        "apikey": supabase_sync.key,
        "Authorization": f"Bearer {supabase_sync.key}"
    })
    
    if response.status_code == 200:
        logs = response.json()
        print(f"   ✅ Retrieved {len(logs)} logs from Supabase")
        
        for i, log in enumerate(logs, 1):
            action_type = log.get('action_type', 'unknown')
            details = log.get('details', 'no details')[:40]
            timestamp = log.get('timestamp', 'no time')[:19]
            user = log.get('discord_username', 'unknown')
            
            print(f"      {i}. [{timestamp}] {action_type:15} | {user:15} | {details}")
    else:
        print(f"   ❌ Failed to retrieve logs (status {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("📊 DIAGNOSIS COMPLETE")
print("=" * 70)
print("""
NEXT STEPS:

If all tests passed:
✅ ActionLogger is working correctly
✅ Logs are being saved locally
✅ Logs are being saved to Supabase
→ Issue is that ActionLogger is NOT BEING CALLED in the UI

Check:
1. When you perform an action (Add/Edit/Delete employee), do you see 
   "📝 Logging:" messages in the console?
2. Check the logs/ folder to see if new files appear after actions
3. If no logs appear locally or on Supabase after performing actions,
   then ActionLogger.log_*() methods are not being called

If logs appear during this test but not in the app:
❌ ActionLogger is working but not integrated in the UI correctly
→ Need to check if ACTION_LOGGER global variable is None
→ Need to verify log methods are called after user actions
""")
