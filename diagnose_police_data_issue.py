#!/usr/bin/env python3
"""
Diagnostic script to check why police_data table is not syncing
Run this to identify the exact issue
"""

import configparser
import os
import requests
import json

# Load Supabase config
config = configparser.ConfigParser()
config.read('supabase_config.ini')

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

print(f"🔍 DIAGNOSING police_data SYNC ISSUE")
print(f"=" * 60)
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Test 1: Check if police_data table exists
print(f"\n1️⃣  CHECKING IF police_data TABLE EXISTS...")
try:
    url = f"{SUPABASE_URL}/rest/v1/police_data?limit=1"
    response = requests.get(url, headers=headers, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print(f"   ✅ police_data table EXISTS")
        data = response.json()
        print(f"   Records: {len(data)}")
        if data:
            print(f"   Sample record: {json.dumps(data[0], indent=2)}")
    elif response.status_code == 404:
        print(f"   ❌ police_data table DOES NOT EXIST!")
    else:
        print(f"   ⚠️  Unexpected status")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: List all tables
print(f"\n2️⃣  LISTING ALL AVAILABLE TABLES...")
try:
    url = f"{SUPABASE_URL}/rest/v1/information_schema.tables?schema=eq.public&select=table_name"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        tables = response.json()
        print(f"   Found {len(tables)} tables:")
        for table in tables:
            print(f"      • {table['table_name']}")
    else:
        print(f"   ⚠️  Cannot list tables (status {response.status_code})")
except Exception as e:
    print(f"   ⚠️  Error listing tables: {e}")

# Test 3: Check employees table
print(f"\n3️⃣  CHECKING employees TABLE...")
try:
    url = f"{SUPABASE_URL}/rest/v1/employees?limit=5"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        employees = response.json()
        print(f"   ✅ employees table exists with {len(employees)} records")
        if employees:
            print(f"   Sample employee:")
            print(f"      ID: {employees[0].get('id')}")
            print(f"      Name: {employees[0].get('employee_name')}")
            print(f"      Punctaj: {employees[0].get('punctaj')}")
    else:
        print(f"   ❌ employees table error (status {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Check if there's data in police_data
print(f"\n4️⃣  CHECKING police_data TABLE CONTENT...")
try:
    url = f"{SUPABASE_URL}/rest/v1/police_data?select=*"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        police_data = response.json()
        print(f"   ✅ police_data table has {len(police_data)} records")
        if police_data:
            for i, record in enumerate(police_data[:3]):
                print(f"\n   Record {i+1}:")
                print(f"      City: {record.get('city')}")
                print(f"      Institution: {record.get('institution')}")
                print(f"      Updated: {record.get('updated_at')}")
                print(f"      Data: {type(record.get('data'))}")
    elif response.status_code == 404:
        print(f"   ❌ police_data table MISSING or INACCESSIBLE")
    else:
        print(f"   ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Try to insert test record
print(f"\n5️⃣  TESTING INSERT INTO police_data...")
try:
    test_record = {
        "city": "TEST_CITY",
        "institution": "TEST_INSTITUTION",
        "data": {"test": True, "timestamp": "2026-02-18"},
        "version": 1,
        "last_synced": "2026-02-18T19:00:00Z",
        "synced_by": "test_script"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/police_data"
    response = requests.post(url, json=test_record, headers=headers, timeout=5)
    
    if response.status_code in [200, 201]:
        print(f"   ✅ INSERT SUCCESS (status {response.status_code})")
        print(f"   Response: {response.json()}")
    elif response.status_code == 401:
        print(f"   ⚠️  AUTH ERROR (401) - Check API key permissions")
    elif response.status_code == 404:
        print(f"   ❌ TABLE NOT FOUND (404) - police_data table doesn't exist!")
    else:
        print(f"   ⚠️  Status: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n" + "=" * 60)
print(f"✅ DIAGNOSTIC COMPLETE")
print(f"\nNEXT STEPS:")
print(f"1. If police_data table doesn't exist:")
print(f"   - Run SQL from CREATE_POLICE_DATA_TABLE.sql in Supabase")
print(f"2. If it exists but not syncing:")
print(f"   - Check if the sync_data() function is being called")
print(f"   - Check app logs for permission errors")
