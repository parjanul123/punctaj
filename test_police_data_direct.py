#!/usr/bin/env python3
"""
Test script to verify police_data table is working and syncing data
"""

import configparser
import os
import requests
import json
from datetime import datetime

# Load config
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
print("🔬 TESTING police_data TABLE")
print("=" * 70)

# Test 1: Check table exists
print("\n1️⃣  Checking if police_data table exists...")
try:
    url = f"{SUPABASE_URL}/rest/v1/police_data?limit=1"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        print(f"   ✅ Table EXISTS")
    elif response.status_code == 404:
        print(f"   ❌ Table MISSING!")
        print(f"   You need to run SQL to create it in Supabase")
        exit(1)
    else:
        print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: Try inserting test data
print("\n2️⃣  Testing INSERT into police_data...")
test_data = {
    "city": "TEST_" + datetime.now().strftime("%H%M%S"),
    "institution": "TEST_INSTITUTION",
    "data": {
        "rows": [
            {"NUME IC": "Test Employee", "PUNCTAJ": 999, "RANK": "Test"},
        ],
        "synced_at": datetime.now().isoformat()
    },
    "version": 1,
    "last_synced": datetime.now().isoformat(),
    "synced_by": "test_script"
}

try:
    url = f"{SUPABASE_URL}/rest/v1/police_data"
    response = requests.post(url, json=test_data, headers=headers, timeout=5)
    
    if response.status_code in [200, 201]:
        print(f"   ✅ INSERT SUCCESS! (HTTP {response.status_code})")
        result = response.json()
        print(f"   Record ID: {result.get('id')}")
        print(f"   City: {result.get('city')}")
    else:
        print(f"   ❌ INSERT FAILED (HTTP {response.status_code})")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Read back all records
print("\n3️⃣  Reading all records from police_data...")
try:
    url = f"{SUPABASE_URL}/rest/v1/police_data?select=*&order=created_at.desc&limit=5"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        records = response.json()
        print(f"   ✅ Found {len(records)} records")
        
        if records:
            print(f"\n   📋 Last 5 records:")
            for i, record in enumerate(records, 1):
                print(f"\n      {i}. {record.get('city')} / {record.get('institution')}")
                print(f"         Created: {record.get('created_at')}")
                print(f"         Updated: {record.get('updated_at')}")
                print(f"         Synced by: {record.get('synced_by')}")
                if record.get('data'):
                    rows = record.get('data', {}).get('rows', [])
                    print(f"         Employees: {len(rows)}")
    else:
        print(f"   ⚠️  Status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Try to UPDATE a record
print("\n4️⃣  Testing UPDATE police_data...")
try:
    # Find a record to update
    url = f"{SUPABASE_URL}/rest/v1/police_data?limit=1&order=id.desc"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        records = response.json()
        if records:
            record_id = records[0]['id']
            
            # Update its data
            updated_data = {
                "data": {
                    "rows": [
                        {"NUME IC": "Updated Employee", "PUNCTAJ": 888, "UPDATED": True}
                    ],
                    "updated_at": datetime.now().isoformat()
                },
                "synced_by": "test_script_update",
                "last_synced": datetime.now().isoformat()
            }
            
            update_url = f"{SUPABASE_URL}/rest/v1/police_data?id=eq.{record_id}"
            response = requests.patch(update_url, json=updated_data, headers=headers, timeout=5)
            
            if response.status_code in [200, 204]:
                print(f"   ✅ UPDATE SUCCESS! (HTTP {response.status_code})")
            else:
                print(f"   ❌ UPDATE FAILED (HTTP {response.status_code})")
                print(f"   Response: {response.text[:200]}")
        else:
            print(f"   ⚠️  No records to update yet")
    else:
        print(f"   ⚠️  Cannot find records (HTTP {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
