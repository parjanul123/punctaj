#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnose Sync Issue Script
Verifica problema de sincronizare cu Supabase
"""

import requests
import json
import configparser
import os

# Load Supabase config
config = configparser.ConfigParser()
config.read('supabase_config.ini')

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

headers = {
    'apikey': SUPABASE_KEY,
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {SUPABASE_KEY}'
}

print("=" * 80)
print("🔍 DIAGNOSE SYNC ISSUE")
print("=" * 80)
print()

# 1. Check Supabase connection
print("1️⃣ Testing Supabase connection...")
try:
    # Get tables info
    tables_url = f"{SUPABASE_URL}/rest/v1/?apiVersion=2024-01-01"
    response = requests.get(tables_url, headers=headers, timeout=5)
    print(f"   ✅ Supabase connection OK (Status: {response.status_code})")
except Exception as e:
    print(f"   ❌ Supabase connection FAILED: {e}")
    exit(1)

print()

# 2. Check discord_users table structure
print("2️⃣ Checking discord_users table structure...")
try:
    url = f"{SUPABASE_URL}/rest/v1/discord_users?limit=1"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            user = data[0]
            print(f"   ✅ discord_users table exists")
            print(f"   📋 Columns found:")
            for col in user.keys():
                print(f"      - {col}")
        else:
            print(f"   ⚠️ discord_users table is EMPTY")
    else:
        print(f"   ❌ Error accessing table (Status: {response.status_code})")
        print(f"      Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 3. Check police_data table structure
print("3️⃣ Checking police_data table structure...")
try:
    url = f"{SUPABASE_URL}/rest/v1/police_data?limit=1"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            record = data[0]
            print(f"   ✅ police_data table exists")
            print(f"   📋 Columns found:")
            for col in record.keys():
                value = record[col]
                if value is None:
                    value_str = "NULL"
                elif isinstance(value, (dict, list)):
                    value_str = f"{type(value).__name__}"
                else:
                    value_str = str(value)[:50]
                print(f"      - {col}: {value_str}")
        else:
            print(f"   ⚠️ police_data table is EMPTY")
    else:
        print(f"   ❌ Error accessing table (Status: {response.status_code})")
        print(f"      Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 4. Check granular_permissions column
print("4️⃣ Checking granular_permissions in discord_users...")
try:
    url = f"{SUPABASE_URL}/rest/v1/discord_users?select=discord_id,discord_username,granular_permissions,is_admin,can_view&limit=5"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"   ✅ Sample users found ({len(data)} users):")
            for user in data:
                perms = user.get('granular_permissions', '{}')
                if isinstance(perms, str):
                    try:
                        perms = json.loads(perms)
                    except:
                        pass
                print(f"      - {user.get('discord_username', 'N/A')}: {perms}")
        else:
            print(f"   ⚠️ No users found in discord_users")
    else:
        print(f"   ❌ Error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 5. Check sync functionality
print("5️⃣ Checking local punctaj.py for sync code...")
try:
    with open('punctaj.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    sync_checks = {
        'PermissionSyncManager': 'Permission sync manager' in content or 'permission_sync_fix' in content,
        'Auto sync thread': 'sync_thread' in content,
        'Supabase sync on startup': 'sync_on_startup' in content,
        'Register user on login': 'register_user' in content,
    }
    
    print(f"   Sync features check:")
    for feature, exists in sync_checks.items():
        status = "✅" if exists else "❌"
        print(f"      {status} {feature}")
        
except Exception as e:
    print(f"   ❌ Error checking code: {e}")

print()

# 6. Check if permission_sync_fix.py exists
print("6️⃣ Checking permission sync module...")
if os.path.exists('permission_sync_fix.py'):
    print(f"   ✅ permission_sync_fix.py EXISTS")
    with open('permission_sync_fix.py', 'r', encoding='utf-8') as f:
        lines = len(f.readlines())
    print(f"      Lines: {lines}")
else:
    print(f"   ❌ permission_sync_fix.py NOT FOUND")

print()

# 7. Local data folder check
print("7️⃣ Checking local data storage...")
if os.path.exists('data'):
    files = os.listdir('data')
    print(f"   ✅ data/ folder exists with {len(files)} files")
    for f in files[:5]:
        print(f"      - {f}")
    if len(files) > 5:
        print(f"      ... and {len(files) - 5} more")
else:
    print(f"   ⚠️ data/ folder NOT FOUND - no local sync")

print()

# 8. Check for sync conflicts
print("8️⃣ Checking for sync conflicts...")
try:
    url = f"{SUPABASE_URL}/rest/v1/audit_logs?select=*&order=created_at.desc&limit=10"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"   ✅ Audit logs available ({len(data)} recent logs)")
            sync_errors = [log for log in data if 'error' in str(log).lower() or 'conflict' in str(log).lower()]
            if sync_errors:
                print(f"   ⚠️ Found {len(sync_errors)} sync-related errors")
            else:
                print(f"   ✅ No sync conflicts detected")
        else:
            print(f"   ℹ️ No audit logs yet")
    else:
        print(f"   ⚠️ Audit logs table not available")
except Exception as e:
    print(f"   ℹ️ Audit logs check skipped: {e}")

print()
print("=" * 80)
print("📊 DIAGNOSIS COMPLETE")
print("=" * 80)
print()
print("NEXT STEPS:")
print("1. If connection is OK but sync not working:")
print("   - Check if permission_sync_fix.py is imported in punctaj.py")
print("   - Verify PermissionSyncManager is started after login")
print()
print("2. If discord_users is empty:")
print("   - Users haven't logged in with Discord yet")
print("   - First login will auto-create user in Supabase")
print()
print("3. If granular_permissions is missing:")
print("   - Run ADD_SUPABASE_COLUMNS.sql to add the column")
print("   - Restart the application")
print()
