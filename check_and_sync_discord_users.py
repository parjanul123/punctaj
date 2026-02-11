#!/usr/bin/env python3
"""
Check discord_users table structure and sync employees
"""

import json
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
print("CHECK DISCORD_USERS TABLE & SYNC EMPLOYEES")
print("=" * 70)

# Check table structure
print("\n[Step 1] Checking discord_users table structure...")
url = f"{SUPABASE_URL}/rest/v1/discord_users?limit=1"

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Response Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        if data:
            print(f"✓ Table found, sample data:")
            print(json.dumps(data[0], indent=2))
        else:
            print(f"✓ Table found but empty")
    else:
        print(f"Response: {resp.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

# Read employees from local files
print("\n[Step 2] Reading employees from local JSON files...")
employees_to_sync = []

for city_folder in DATA_DIR.iterdir():
    if not city_folder.is_dir():
        continue
    
    city_name = city_folder.name
    
    for json_file in city_folder.glob("*.json"):
        institution_name = json_file.stem
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'rows' in data:
                for employee in data['rows']:
                    # Create record matching what discord_users table expects
                    emp_record = {
                        "discord_username": employee.get("DISCORD", ""),
                        "employee_name": employee.get("NUME IC", ""),
                        "city": city_name,
                        "institution": institution_name,
                        "rank": employee.get("RANK", ""),
                        "role": employee.get("ROLE", ""),
                        "points": employee.get("PUNCTAJ", 0),
                        "id_card_series": employee.get("SERIE DE BULETIN", "")
                    }
                    employees_to_sync.append(emp_record)
                    print(f"  ✓ {employee.get('NUME IC')} - {city_name}/{institution_name}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")

print(f"\n[Step 3] Found {len(employees_to_sync)} employees")

if employees_to_sync:
    print(f"\n[Step 4] Uploading to discord_users table...")
    
    url_insert = f"{SUPABASE_URL}/rest/v1/discord_users"
    
    # Try batch insert
    try:
        response = requests.post(url_insert, json=employees_to_sync, headers=headers, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✓ SUCCESS! Uploaded {len(employees_to_sync)} employees")
        else:
            print(f"✗ FAILED")
            print(f"Response: {response.text[:500]}")
            
            # Try one by one
            print(f"\n[Step 5] Trying individual inserts...")
            success_count = 0
            for i, emp in enumerate(employees_to_sync, 1):
                try:
                    r = requests.post(url_insert, json=[emp], headers=headers, timeout=10)
                    if r.status_code in [200, 201]:
                        print(f"  [{i}/{len(employees_to_sync)}] ✓ {emp['employee_name']}")
                        success_count += 1
                    else:
                        print(f"  [{i}/{len(employees_to_sync)}] ✗ {emp['employee_name']} - {r.status_code}")
                        if i <= 2:  # Show first 2 errors
                            print(f"      Error: {r.text[:150]}")
                except Exception as e:
                    print(f"  [{i}/{len(employees_to_sync)}] ✗ {emp['employee_name']} - {e}")
            
            print(f"\nResult: {success_count}/{len(employees_to_sync)} uploaded successfully")
    
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
