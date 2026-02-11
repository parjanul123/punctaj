#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNOSTIC COMPLET - Citește din toate 7 tabelele Supabase
Caută problema cu superuser pentru host
"""

import requests
import json
from datetime import datetime

# Supabase config
URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}

# Host Discord ID
HOST_ID = "703316932232872016"

def query_table(table_name, query_filter=None, limit=1000):
    """Citeste din orice tabelă Supabase"""
    try:
        url = f"{URL}/rest/v1/{table_name}?limit={limit}"
        
        if query_filter:
            url += f"&{query_filter}"
        
        print(f"\n📡 Querying: {table_name}")
        print(f"   URL: {url}")
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: 200")
            print(f"   📊 Rows: {len(data)}")
            return data
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

print("\n" + "="*80)
print("🔍 DIAGNOSTIC COMPLET - SUPABASE")
print("="*80)
print(f"Project: yzlkgifumrwqlfgimcai")
print(f"Host ID: {HOST_ID}")
print(f"Time: {datetime.now()}")

# ============================================================================
# 1. DISCORD USERS - Caută host
# ============================================================================
print("\n\n" + "─"*80)
print("1️⃣  TABLE: discord_users")
print("─"*80)

users_data = query_table(
    "discord_users",
    f"discord_id=eq.{HOST_ID}&select=*"
)

if users_data and len(users_data) > 0:
    user = users_data[0]
    print("\n🎯 HOST FOUND IN discord_users:")
    print(f"   Username: {user.get('username')}")
    print(f"   Discord ID: {user.get('discord_id')}")
    print(f"   is_superuser: {user.get('is_superuser')} (type: {type(user.get('is_superuser')).__name__})")
    print(f"   is_admin: {user.get('is_admin')} (type: {type(user.get('is_admin')).__name__})")
    print(f"   can_view: {user.get('can_view')}")
    print(f"   can_edit: {user.get('can_edit')}")
    print(f"   can_delete: {user.get('can_delete')}")
    
    perms = user.get('granular_permissions')
    if perms:
        if isinstance(perms, str):
            try:
                perms = json.loads(perms)
            except:
                pass
        print(f"   granular_permissions: {type(perms).__name__}, keys: {list(perms.keys())[:5] if isinstance(perms, dict) else 'N/A'}")
    
    print(f"   created_at: {user.get('created_at')}")
    print(f"   updated_at: {user.get('updated_at')}")
else:
    print("\n❌ HOST NOT FOUND in discord_users!")

# ============================================================================
# 2. EMPLOYEES - Angajații
# ============================================================================
print("\n\n" + "─"*80)
print("2️⃣  TABLE: employees")
print("─"*80)

employees_data = query_table("employees", limit=50)
if employees_data:
    print(f"\n📋 Total employees: {len(employees_data)}")
    # Show first 3
    for emp in employees_data[:3]:
        print(f"   - {emp.get('name')} (ID: {emp.get('id')}) in {emp.get('institution')}")

# ============================================================================
# 3. INSTITUTIONS - Instituții
# ============================================================================
print("\n\n" + "─"*80)
print("3️⃣  TABLE: institutions")
print("─"*80)

institutions_data = query_table("institutions", limit=50)
if institutions_data:
    print(f"\n🏛️  Total institutions: {len(institutions_data)}")
    for inst in institutions_data[:5]:
        print(f"   - {inst.get('name')} in {inst.get('city')}")

# ============================================================================
# 4. CITIES - Orașe
# ============================================================================
print("\n\n" + "─"*80)
print("4️⃣  TABLE: cities")
print("─"*80)

cities_data = query_table("cities", limit=50)
if cities_data:
    print(f"\n🏙️  Total cities: {len(cities_data)}")
    for city in cities_data[:10]:
        print(f"   - {city.get('name')}")

# ============================================================================
# 5. INSTITUTION LOGS - Loguri per instituție
# ============================================================================
print("\n\n" + "─"*80)
print("5️⃣  TABLE: institution_logs")
print("─"*80)

inst_logs = query_table("institution_logs", limit=50)
if inst_logs:
    print(f"\n📝 Total institution logs: {len(inst_logs)}")
    for log in inst_logs[:3]:
        print(f"   - {log.get('action')} by {log.get('user')} in {log.get('institution')}")

# ============================================================================
# 6. BACKUP - Backup table
# ============================================================================
print("\n\n" + "─"*80)
print("6️⃣  TABLE: backup")
print("─"*80)

backup_data = query_table("backup", limit=50)
if backup_data:
    print(f"\n💾 Total backups: {len(backup_data)}")
    for bkp in backup_data[:3]:
        print(f"   - {bkp.get('id')} ({bkp.get('backup_date')})")

# ============================================================================
# 7. PERMISSION LOGS - Loguri permisiuni
# ============================================================================
print("\n\n" + "─"*80)
print("7️⃣  TABLE: permission_logs")
print("─"*80)

perm_logs = query_table("permission_logs", limit=50)
if perm_logs:
    print(f"\n🔐 Total permission logs: {len(perm_logs)}")
    for log in perm_logs[:3]:
        print(f"   - {log.get('action')} for {log.get('user')} ({log.get('timestamp')})")

# ============================================================================
# ANALYSIS
# ============================================================================
print("\n\n" + "="*80)
print("🔎 ANALYSIS")
print("="*80)

if users_data and len(users_data) > 0:
    user = users_data[0]
    is_super = user.get('is_superuser')
    is_admin = user.get('is_admin')
    
    print(f"\n🎯 HOST STATUS:")
    print(f"   is_superuser = {is_super}")
    print(f"   is_admin = {is_admin}")
    
    if is_super:
        print(f"   ✅ SHOULD HAVE ADMIN BUTTONS - Check code if not showing")
    elif is_admin:
        print(f"   ⚠️  Is ADMIN but not SUPERUSER - Admin buttons should show")
    else:
        print(f"   ❌ NOT SUPERUSER or ADMIN - This is the problem!")
        print(f"   💡 ACTION: Set is_superuser=true for Discord ID {HOST_ID}")

print("\n\n" + "="*80)
print("✅ DIAGNOSTIC COMPLETE")
print("="*80)
print(f"\nLog written at: {datetime.now()}")
