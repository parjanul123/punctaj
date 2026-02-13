#!/usr/bin/env python3
"""
Debug Supabase Sync - Diagnostic tool
Verifica care e problema cu sincronizarea
"""

import json
import configparser
import os
import sys
import requests

# Get base dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load config
config = configparser.ConfigParser()
config_file = os.path.join(BASE_DIR, "supabase_config.ini")

if not os.path.exists(config_file):
    print(f"❌ {config_file} not found!")
    sys.exit(1)

config.read(config_file)

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')
TABLE_SYNC = config.get('supabase', 'table_sync', fallback='police_data')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("="*70)
print("SUPABASE SYNC DEBUG")
print("="*70)

# 1. Test conectare
print(f"\n1️⃣ Testing connection to Supabase...")
print(f"   URL: {SUPABASE_URL}")
print(f"   Table: {TABLE_SYNC}")
print(f"   Key: {SUPABASE_KEY[:20]}...")

try:
    # Simple GET request to test connection
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_SYNC}?limit=1"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        print(f"   ✅ Connected successfully (HTTP 200)")
        data = response.json()
        print(f"   📋 Records in table: {len(data) if isinstance(data, list) else '?'}")
    else:
        print(f"   ❌ Failed (HTTP {response.status_code})")
        print(f"   Error: {response.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 2. Try to insert test record
print(f"\n2️⃣ Testing INSERT to {TABLE_SYNC}...")

test_data = {
    'city': 'TEST_CITY',
    'institution': 'TEST_INSTITUTION',
    'data_json': json.dumps({"test": True}),
    'updated_at': __import__('datetime').datetime.now().isoformat(),
    'updated_by': 'debug_script'
}

try:
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_SYNC}"
    response = requests.post(url, json=test_data, headers=headers, timeout=5)
    
    if response.status_code in [200, 201]:
        print(f"   ✅ INSERT successful (HTTP {response.status_code})")
        result = response.json()
        test_record_id = result[0].get('id') if isinstance(result, list) else result.get('id')
        print(f"   📝 Record ID: {test_record_id}")
    else:
        print(f"   ❌ INSERT failed (HTTP {response.status_code})")
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Check cities table
print(f"\n3️⃣ Testing cities table...")

try:
    url = f"{SUPABASE_URL}/rest/v1/cities?limit=5"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        cities = response.json()
        print(f"   ✅ Cities table exists")
        print(f"   📋 Total cities: {len(cities)}")
        if cities:
            for city in cities[:3]:
                print(f"      - {city.get('name', 'N/A')} (ID: {city.get('id', '?')})")
    else:
        print(f"   ❌ Cities table error (HTTP {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Check employees table
print(f"\n4️⃣ Testing employees table...")

try:
    url = f"{SUPABASE_URL}/rest/v1/employees?limit=5"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        employees = response.json()
        print(f"   ✅ Employees table exists")
        print(f"   📋 Total employees: {len(employees)}")
        if employees:
            for emp in employees[:3]:
                print(f"      - {emp.get('employee_name', 'N/A')} (ID: {emp.get('id', '?')})")
    else:
        print(f"   ❌ Employees table error (HTTP {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Check police_data table  
print(f"\n5️⃣ Testing police_data table...")

try:
    url = f"{SUPABASE_URL}/rest/v1/police_data?limit=5"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        records = response.json()
        print(f"   ✅ Police_data table exists")
        print(f"   📋 Total records: {len(records)}")
        if records:
            for rec in records[:3]:
                print(f"      - {rec.get('city', '?')} / {rec.get('institution', '?')} (Updated: {str(rec.get('updated_at', 'N/A'))[:10]})")
    else:
        print(f"   ❌ Police_data table error (HTTP {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 6. Summary
print(f"\n" + "="*70)
print("📊 DIAGNOSTIC COMPLETE")
print("="*70)

print(f"""
✅ If all tests passed, Supabase is working correctly.

⚠️ If any test failed, check:
1. supabase_config.ini - verify URL and key
2. RLS (Row Level Security) settings - might need disabling for testing
3. Table permissions - ensure insert/update/delete are allowed

📝 To check RLS:
1. Go to https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai
2. Click on police_data table
3. Click "RLS" button - if RED = disabled ✅ | if GREEN = enabled ⚠️
""")

print("\n✅ If all tests passed, but sync still doesn't work:")
print("   Run: python debug_sync_flow.py")
print("   This will test the full sync flow from punctaj.py")
