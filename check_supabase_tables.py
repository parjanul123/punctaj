#!/usr/bin/env python3
"""
Check what table is ID 21102 in Supabase
"""

import configparser
import requests

config = configparser.ConfigParser()
config.read('supabase_config.ini')

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("🔍 CHECKING SUPABASE TABLES")
print("=" * 70)

# List all tables
try:
    url = f"{SUPABASE_URL}/rest/v1/"
    response = requests.get(url, headers=headers, timeout=5)
    print(f"\n✅ API is working (status {response.status_code})")
except Exception as e:
    print(f"❌ Cannot reach API: {e}")
    exit(1)

# Try to access common table names
tables_to_check = [
    'police_data',
    'policce_data',
    'police',
    'punctaj',
    'employees',
    'institutions',
    'cities',
    'weekly_reports',
    'audit_logs'
]

print(f"\n📋 Checking tables:")
for table_name in tables_to_check:
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {table_name:<20} EXISTS - {len(data)} records")
        elif response.status_code == 404:
            print(f"   ❌ {table_name:<20} NOT FOUND")
        else:
            print(f"   ⚠️  {table_name:<20} - Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ {table_name:<20} - Error: {e}")

print("\n" + "=" * 70)
print("🎯 Based on your link, table ID 21102 should contain punctaj data")
print("=" * 70)
