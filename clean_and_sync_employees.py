#!/usr/bin/env python3
"""
1. Delete empty employee records from discord_users
2. Sync employees from local JSON files
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
print("CLEAN & SYNC EMPLOYEES TO DISCORD_USERS TABLE")
print("=" * 70)

# Step 1: Delete all existing records
print("\n[Step 1] Deleting existing empty records...")
url_delete = f"{SUPABASE_URL}/rest/v1/discord_users"

try:
    response = requests.delete(url_delete, headers=headers, timeout=10)
    print(f"Response Status: {response.status_code}")
    
    if response.status_code in [200, 204]:
        print("✓ All old records deleted")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Step 2: Read employees from local files
print("\n[Step 2] Reading employees from local JSON files...")
employees_to_sync = []

for city_folder in DATA_DIR.iterdir():
    if not city_folder.is_dir():
        continue
    
    city_name = city_folder.name
    print(f"\n  📂 {city_name}")
    
    for json_file in city_folder.glob("*.json"):
        institution_name = json_file.stem
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'rows' in data and data['rows']:
                print(f"    📄 {institution_name}: ", end="")
                
                for employee in data['rows']:
                    emp_record = {
                        "employee_name": employee.get("NUME IC", ""),
                        "discord_username": employee.get("DISCORD", ""),
                        "city": city_name,
                        "institution": institution_name,
                        "rank": employee.get("RANK", ""),
                        "role": employee.get("ROLE", ""),
                        "points": int(employee.get("PUNCTAJ", 0)),
                        "id_card_series": employee.get("SERIE DE BULETIN", "")
                    }
                    employees_to_sync.append(emp_record)
                
                print(f"{len(data['rows'])} employees")
            else:
                print(f"    📄 {institution_name}: empty")
        
        except Exception as e:
            print(f"    ✗ Error reading {institution_name}: {e}")

print(f"\n[Step 3] Total employees to upload: {len(employees_to_sync)}")

if employees_to_sync:
    print(f"\n[Step 4] Uploading {len(employees_to_sync)} employees...")
    
    url_insert = f"{SUPABASE_URL}/rest/v1/discord_users"
    
    try:
        response = requests.post(url_insert, json=employees_to_sync, headers=headers, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✓ SUCCESS! Uploaded {len(employees_to_sync)} employees")
            print("\nUploaded:")
            for emp in employees_to_sync:
                print(f"  ✓ {emp['employee_name']} - {emp['city']}/{emp['institution']}")
        else:
            print(f"✗ FAILED: {response.text[:300]}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 70)
