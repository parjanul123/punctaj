#!/usr/bin/env python3
"""
Sync employees from local JSON files to Supabase table 17485
This script reads all employees from /data folder and uploads them to Supabase
"""

import json
import os
import requests
from pathlib import Path

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

DATA_DIR = Path(__file__).parent / "data"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("SYNC EMPLOYEES FROM LOCAL JSON TO SUPABASE")
print("=" * 70)

# First, let's check what columns the table has by trying a simple read
print("\n[Step 1] Checking table structure...")
url_check = f"{SUPABASE_URL}/rest/v1/employees_discord?limit=1"

try:
    resp = requests.get(url_check, headers=headers, timeout=10)
    if resp.status_code == 200:
        print(f"✓ Table found (employees_discord)")
    else:
        print(f"✗ Table not found or error: {resp.status_code}")
        print(f"Response: {resp.text}")
except Exception as e:
    print(f"✗ Error checking table: {e}")

# Now read all employees from local files
print("\n[Step 2] Reading employees from local JSON files...")
employees_to_sync = []
employee_count = 0

for city_folder in DATA_DIR.iterdir():
    if not city_folder.is_dir():
        continue
    
    city_name = city_folder.name
    print(f"\n  📂 City: {city_name}")
    
    for json_file in city_folder.glob("*.json"):
        institution_name = json_file.stem
        print(f"    📄 Institution: {institution_name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'rows' in data:
                for employee in data['rows']:
                    employee_count += 1
                    # Prepare employee record for Supabase
                    employee_record = {
                        "city": city_name,
                        "institution": institution_name,
                        "discord": employee.get("DISCORD", ""),
                        "name": employee.get("NUME IC", ""),
                        "rank": employee.get("RANK", ""),
                        "role": employee.get("ROLE", ""),
                        "points": employee.get("PUNCTAJ", 0),
                        "id_series": employee.get("SERIE DE BULETIN", ""),
                        "last_modified": employee.get("ULTIMA_MOD", "")
                    }
                    employees_to_sync.append(employee_record)
                    print(f"      ✓ {employee.get('NUME IC', 'Unknown')} (Rank: {employee.get('RANK', '?')})")
        
        except Exception as e:
            print(f"      ✗ Error reading file: {e}")

print(f"\n[Step 3] Total employees found: {employee_count}")

# Now insert into Supabase
if employees_to_sync:
    print(f"\n[Step 4] Uploading {len(employees_to_sync)} employees to Supabase...")
    
    url_insert = f"{SUPABASE_URL}/rest/v1/employees_discord"
    
    # Try inserting all at once
    try:
        response = requests.post(url_insert, json=employees_to_sync, headers=headers, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✓ SUCCESS! Uploaded {len(employees_to_sync)} employees")
            print(f"Response: {response.text[:200]}")
        else:
            print(f"✗ FAILED (Status: {response.status_code})")
            print(f"Response: {response.text}")
            
            # Try inserting one by one to see which fails
            print("\n[Step 5] Trying individual inserts to identify issues...")
            for i, emp in enumerate(employees_to_sync, 1):
                try:
                    r = requests.post(url_insert, json=[emp], headers=headers, timeout=10)
                    if r.status_code in [200, 201]:
                        print(f"  [{i}/{len(employees_to_sync)}] ✓ {emp['name']}")
                    else:
                        print(f"  [{i}/{len(employees_to_sync)}] ✗ {emp['name']} - {r.status_code}: {r.text[:100]}")
                except Exception as e:
                    print(f"  [{i}/{len(employees_to_sync)}] ✗ {emp['name']} - Error: {e}")
    
    except Exception as e:
        print(f"\n✗ Error during upload: {e}")

print("\n" + "=" * 70)
print("SYNC COMPLETE!")
print("=" * 70)
print("\nNote: If errors occur, check that:")
print("1. Table 'employees_discord' exists in Supabase")
print("2. Columns match: city, institution, discord, name, rank, role, points, id_series, last_modified")
print("3. You have write permissions on the table")
