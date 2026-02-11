# -*- coding: utf-8 -*-
"""
Test: Simuleaza o actiune si verifica daca ACTION_LOGGER se apeleaza
"""

import sys
import os
import configparser

print("="*70)
print("🧪 TEST: ACTION_LOGGER - Monitoring Actions")
print("="*70)

# Step 1: Load config
print("\n1️⃣ Loading configuration...")
config = configparser.ConfigParser()
if os.path.exists('supabase_config.ini'):
    config.read('supabase_config.ini')
    print("   ✅ supabase_config.ini loaded")
else:
    print("   ❌ supabase_config.ini NOT found!")
    sys.exit(1)

# Step 2: Import SupabaseSync
print("\n2️⃣ Importing SupabaseSync...")
try:
    from supabase_sync import SupabaseSync
    print("   ✅ SupabaseSync imported")
except Exception as e:
    print(f"   ❌ Failed to import SupabaseSync: {e}")
    sys.exit(1)

# Step 3: Initialize SupabaseSync
print("\n3️⃣ Initializing SupabaseSync...")
try:
    supabase_sync = SupabaseSync('supabase_config.ini')
    print(f"   ✅ SupabaseSync initialized")
    print(f"      URL: {supabase_sync.url[:50]}...")
    print(f"      Table logs: {supabase_sync.table_logs}")
    print(f"      Enabled: {supabase_sync.enabled}")
except Exception as e:
    print(f"   ❌ Failed to initialize SupabaseSync: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Import ActionLogger
print("\n4️⃣ Importing ActionLogger...")
try:
    from action_logger import ActionLogger
    print("   ✅ ActionLogger imported")
except Exception as e:
    print(f"   ❌ Failed to import ActionLogger: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Initialize ActionLogger
print("\n5️⃣ Initializing ActionLogger...")
try:
    action_logger = ActionLogger(supabase_sync, logs_dir="logs")
    print("   ✅ ActionLogger initialized")
except Exception as e:
    print(f"   ❌ Failed to initialize ActionLogger: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 6: Verify logs folder
print("\n6️⃣ Checking logs folder...")
if os.path.exists('logs'):
    print("   ✅ logs/ folder exists")
else:
    print("   ⚠️ logs/ folder does not exist - ActionLogger will create it")

# Step 7: SIMULATE AN ACTION - Log add_employee
print("\n7️⃣ SIMULATING USER ACTION: ADD_EMPLOYEE")
print("   User: parjanu")
print("   City: Saint_Denis")
print("   Institution: Politie")
print("   Employee: Test Agent")

try:
    result = action_logger.log_add_employee(
        discord_id="parjanu",
        city="Saint_Denis",
        institution_name="Politie",
        employee_name="Test Agent",
        employee_data={"name": "Test Agent", "points": 50}
    )
    
    if result:
        print("   ✅ log_add_employee SUCCEEDED")
    else:
        print("   ❌ log_add_employee FAILED (returned False)")
except Exception as e:
    print(f"   ❌ Error calling log_add_employee: {e}")
    import traceback
    traceback.print_exc()

# Step 8: Check if log was created
print("\n8️⃣ Checking if log file was created...")
log_file = "logs/Saint_Denis/Politie.json"
if os.path.exists(log_file):
    print(f"   ✅ Log file exists: {log_file}")
    
    import json
    with open(log_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    print(f"   📊 Number of logs in file: {len(logs)}")
    if logs:
        latest = logs[-1]
        print(f"   Latest log:")
        print(f"      - Action: {latest.get('action_type')}")
        print(f"      - User: {latest.get('discord_id')}")
        print(f"      - Details: {latest.get('details')}")
        print(f"      - Timestamp: {latest.get('timestamp')}")
else:
    print(f"   ❌ Log file NOT created: {log_file}")

# Step 9: Check global summary
print("\n9️⃣ Checking global summary...")
summary_file = "logs/SUMMARY_global.json"
if os.path.exists(summary_file):
    print(f"   ✅ Summary file exists: {summary_file}")
    
    import json
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    print(f"   📊 Summary stats:")
    print(f"      - Total actions: {summary.get('total_actions', 0)}")
    print(f"      - Users: {summary.get('users_connected', [])}")
    print(f"      - Cities: {list(summary.get('cities_modified', {}).keys())}")
else:
    print(f"   ⚠️ Summary file not yet created")

print("\n" + "="*70)
print("✅ TEST COMPLETE")
print("="*70)
print("""
If you see ✅ marks above, ACTION_LOGGER is working correctly!

Next steps:
1. Run: python punctaj.py
2. Make a change in the UI
3. Check if logs appear in: logs/Saint_Denis/Politie.json

If logs still don't appear in the app, the issue might be:
- ACTION_LOGGER not being called from the right place
- The save function not calling ACTION_LOGGER
- Something blocking the logging code path
""")
