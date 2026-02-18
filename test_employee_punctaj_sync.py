#!/usr/bin/env python3
"""
Test script to verify employee POINTS (punctaj) updates in Supabase
Column name: 'points' (not 'punctaj')
"""

import configparser
import requests
import json
from datetime import datetime

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
print("🧪 TESTING EMPLOYEE POINTS (PUNCTAJ) SYNC")
print("=" * 70)

# Step 1: Get all employees
print("\n1️⃣  Fetching employees from Supabase...")
try:
    url = f"{SUPABASE_URL}/rest/v1/employees"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        employees = response.json()
        print(f"   ✅ Found {len(employees)} employees:")
        
        for i, emp in enumerate(employees[:5]):
            print(f"      {i+1}. ID={emp['id']}, Name={emp['employee_name']}, Points={emp.get('points', 'null')}")
    else:
        print(f"   ❌ Failed (HTTP {response.status_code})")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 2: Update an employee's points
if employees:
    print(f"\n2️⃣  Testing UPDATE - changing first employee's points...")
    emp = employees[0]
    emp_id = emp['id']
    old_points = emp.get('points') or 0
    new_points = old_points + 5
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/employees?id=eq.{emp_id}"
        update_data = {
            'points': new_points,
            'updated_at': datetime.now().isoformat()
        }
        
        response = requests.patch(url, json=update_data, headers=headers, timeout=5)
        
        if response.status_code in [200, 204]:
            print(f"   ✅ UPDATE SUCCESS!")
            print(f"      Employee: {emp['employee_name']}")
            print(f"      Points: {old_points} → {new_points}")
        else:
            print(f"   ❌ UPDATE FAILED (HTTP {response.status_code})")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Step 3: Verify update
print(f"\n3️⃣  Verifying update...")
try:
    url = f"{SUPABASE_URL}/rest/v1/employees?id=eq.{emp_id}"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        result = response.json()
        if result:
            current_points = result[0].get('points')
            if current_points == new_points:
                print(f"   ✅ ✅ ✅ VERIFICATION SUCCESS!")
                print(f"      Points now is: {current_points}")
            else:
                print(f"   ⚠️  Points mismatch: expected {new_points}, got {current_points}")
        else:
            print(f"   ⚠️  Employee not found")
    else:
        print(f"   ❌ Verification failed (HTTP {response.status_code})")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
