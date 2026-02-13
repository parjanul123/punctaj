#!/usr/bin/env python3
"""
Test Supabase Sync Flow
Verifica fluxul complet: adaugă/editează/șterge în local și verifica Supabase
"""

import json
import os
import configparser
from datetime import datetime
import requests

print("="*70)
print("SUPABASE SYNC FLOW TEST")
print("="*70)

# Load config
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), "supabase_config.ini")

if not os.path.exists(config_file):
    print(f"❌ {config_file} not found!")
    exit(1)

config.read(config_file)

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')
TABLE_SYNC = config.get('supabase', 'table_sync', fallback='police_data')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# 1. Check what's in police_data table
print(f"\n1️⃣ Viewing {TABLE_SYNC} table content...")

try:
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_SYNC}?order=updated_at.desc&limit=10"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        records = response.json()
        print(f"   ✅ Found {len(records)} records\n")
        
        for i, rec in enumerate(records, 1):
            print(f"   {i}. City: {rec.get('city', '?'):20s} | Institution: {rec.get('institution', '?'):20s}")
            print(f"      Updated: {str(rec.get('updated_at', '?'))[:19]}")
            print(f"      By: {rec.get('updated_by', '?')}")
            
            # Try to parse data_json
            try:
                data = json.loads(rec.get('data_json', '{}'))
                print(f"      Rows: {len(data.get('rows', []))} employees")
            except:
                print(f"      (Could not parse data)")
            print()
    else:
        print(f"   ❌ Error (HTTP {response.status_code}): {response.text[:100]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Check employees table
print(f"\n2️⃣ Viewing employees table content...")

try:
    url = f"{SUPABASE_URL}/rest/v1/employees?order=updated_at.desc&limit=10"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        employees = response.json()
        print(f"   ✅ Found {len(employees)} employees\n")
        
        for i, emp in enumerate(employees[:5], 1):
            print(f"   {i}. Name: {emp.get('employee_name', '?'):20s} | Rank: {emp.get('rank', '?')}")
            print(f"      Punctaj: {emp.get('punctaj', 0)} | Role: {emp.get('role', '?')}")
            print(f"      Discord: {emp.get('discord_username', 'N/A')}")
            print()
    else:
        print(f"   ⚠️  Table might not exist (HTTP {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Check local data vs Supabase
print(f"\n3️⃣ Comparing local data with Supabase...")

DATA_DIR = os.path.join(os.path.dirname(__file__), "Punctaj", "Data")
if not os.path.exists(DATA_DIR):
    print(f"   ⚠️  Local data directory not found: {DATA_DIR}")
else:
    local_count = 0
    for city in os.listdir(DATA_DIR):
        city_path = os.path.join(DATA_DIR, city)
        if not os.path.isdir(city_path):
            continue
        
        for json_file in os.listdir(city_path):
            if json_file.endswith('.json'):
                local_count += 1
                institution = json_file[:-5]
                
                # Check if this institution is in Supabase
                try:
                    url = f"{SUPABASE_URL}/rest/v1/{TABLE_SYNC}?city=eq.{city}&institution=eq.{institution}"
                    response = requests.get(url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        records = response.json()
                        if records:
                            print(f"   ✅ {city}/{institution} - IN SUPABASE")
                        else:
                            print(f"   ❌ {city}/{institution} - MISSING IN SUPABASE (local only)")
                    else:
                        print(f"   ⚠️  {city}/{institution} - Query error")
                except Exception as e:
                    print(f"   ⚠️  {city}/{institution} - Error: {str(e)[:50]}")
    
    print(f"\n   📊 Total local institutions: {local_count}")

# 4. Summary
print(f"\n" + "="*70)
print("📋 DIAGNOSTIC SUMMARY")
print("="*70)

print(f"""
✅ If police_data table is EMPTY:
   1. Run: python initialize_supabase_tables.py  (to create tables)
   2. Then restart your app and make changes
   3. Wait a few seconds and run this test again

❌ If police_data has old data but new changes don't appear:
   1. Check if SUPABASE_SYNC.enabled = true in supabase_config.ini
   2. Run: python debug_sync_connection.py  (test INSERT permission)
   3. Check application console for error messages
   4. Verify RLS is DISABLED on police_data table in Supabase

✅ If police_data is up-to-date:
   🎉 Sync is working correctly!
""")
