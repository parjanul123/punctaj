# -*- coding: utf-8 -*-
"""
Diagnostic: Verifica status ACTION_LOGGER si SUPABASE_SYNC
"""

import configparser
import os
import json

print("="*60)
print("🔍 DIAGNOSTIC: LOGGING SYSTEM STATUS")
print("="*60)

# 1. Verifica config
print("\n1️⃣ CHECKING CONFIGURATION...")
config = configparser.ConfigParser()
if os.path.exists('supabase_config.ini'):
    config.read('supabase_config.ini')
    url = config.get('supabase', 'url', fallback='NOT FOUND')
    key = config.get('supabase', 'key', fallback='NOT FOUND')
    table_logs = config.get('supabase', 'table_logs', fallback='NOT FOUND')
    sync_enabled = config.get('sync', 'enabled', fallback='NOT FOUND')
    
    print(f"   ✅ supabase_config.ini exists")
    print(f"      URL: {url[:50]}...")
    print(f"      Table logs: {table_logs}")
    print(f"      Sync enabled: {sync_enabled}")
else:
    print(f"   ❌ supabase_config.ini NOT FOUND!")

# 2. Verifica action_logger.py
print("\n2️⃣ CHECKING ACTION_LOGGER MODULE...")
if os.path.exists('action_logger.py'):
    print(f"   ✅ action_logger.py exists")
    with open('action_logger.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'class ActionLogger' in content:
            print(f"   ✅ ActionLogger class found")
        else:
            print(f"   ❌ ActionLogger class NOT found")
else:
    print(f"   ❌ action_logger.py NOT FOUND!")

# 3. Verifica folder logs
print("\n3️⃣ CHECKING LOGS FOLDER...")
if os.path.exists('logs'):
    print(f"   ✅ logs/ folder exists")
    files = []
    for root, dirs, filelist in os.walk('logs'):
        for file in filelist:
            files.append(os.path.join(root, file))
    
    if files:
        print(f"   ✅ Found {len(files)} log files:")
        for f in files:
            print(f"      - {f}")
    else:
        print(f"   ⚠️ logs/ folder is EMPTY")
else:
    print(f"   ❌ logs/ folder does NOT exist")
    print(f"   📌 Creating it now...")
    os.makedirs('logs', exist_ok=True)
    print(f"   ✅ Created logs/ folder")

# 4. Verifica supabase_sync.py
print("\n4️⃣ CHECKING SUPABASE_SYNC MODULE...")
if os.path.exists('supabase_sync.py'):
    print(f"   ✅ supabase_sync.py exists")
    with open('supabase_sync.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'class SupabaseSync' in content:
            print(f"   ✅ SupabaseSync class found")
        if 'enabled = True' in content or 'enabled=True' in content:
            print(f"   ✅ Sync appears to be enabled by default")
else:
    print(f"   ❌ supabase_sync.py NOT FOUND!")

# 5. Verifica punctaj.py
print("\n5️⃣ CHECKING PUNCTAJ.PY INTEGRATION...")
if os.path.exists('punctaj.py'):
    print(f"   ✅ punctaj.py exists")
    with open('punctaj.py', 'r', encoding='utf-8') as f:
        content = f.read()
        checks = {
            'ACTION_LOGGER initialization': 'ACTION_LOGGER = ActionLoggerNew(SUPABASE_SYNC)',
            'log_add_employee calls': 'ACTION_LOGGER.log_add_employee',
            'log_delete_employee calls': 'ACTION_LOGGER.log_delete_employee',
            'log_edit_points calls': 'ACTION_LOGGER.log_edit_points',
            'log_edit_employee_safe calls': 'ACTION_LOGGER.log_edit_employee_safe',
        }
        
        for check_name, search_string in checks.items():
            if search_string in content:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name} - NOT FOUND")
else:
    print(f"   ❌ punctaj.py NOT FOUND!")

# 6. Recomandari
print("\n" + "="*60)
print("📋 RECOMMENDATIONS:")
print("="*60)

print("""
To test if logging works:

1. Run the application:
   python punctaj.py

2. Look for this in console output:
   ✓ Action logger initialized for automatic logging
     📊 Logs table: audit_logs

3. Perform an action (add/edit/delete employee or adjust points)

4. Look in console for:
   📝 Logging: <action_type> | User: <discord_id> | Table: audit_logs
   💾 Log saved locally: logs/<city>/<institution>.json

5. Check the logs folder:
   ls logs/
   cat logs/Saint_Denis/Politie.json

6. Check Supabase Admin Panel:
   Table: audit_logs
   Should contain new log entries
""")

print("="*60)
print("If logs don't appear after doing these steps, check:")
print("  1. Console output for error messages")
print("  2. If ACTION_LOGGER initialized successfully")
print("  3. If SUPABASE_SYNC.enabled = True")
print("="*60)
