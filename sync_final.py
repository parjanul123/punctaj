#!/usr/bin/env python3
"""
Sync data from /data folders to Supabase with proper response handling
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
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

print("=" * 70)
print("SYNC DATA: /data folders → Supabase tables")
print("=" * 70)

# Check tables exist
print("\n[Check] Verifying tables...")
for table_name in ["cities", "institutions", "employees"]:
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=0"
    resp = requests.get(url, headers=headers, timeout=10)
    
    if resp.status_code == 200:
        print(f"  ✓ {table_name}")
    else:
        print(f"\n❌ Table '{table_name}' NOT FOUND!")
        print("Create tables first in Supabase dashboard using the SQL!")
        exit(1)

# Read local data
print("\n[Read] Reading from /data folders...\n")

cities_data = {}

for city_folder in sorted(DATA_DIR.iterdir()):
    if not city_folder.is_dir():
        continue
    
    city_name = city_folder.name
    cities_data[city_name] = {}
    print(f"  📍 {city_name}")
    
    for json_file in sorted(city_folder.glob("*.json")):
        institution_name = json_file.stem
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            employees = []
            if 'rows' in data:
                for emp in data['rows']:
                    employees.append({
                        "discord_username": emp.get("DISCORD", ""),
                        "employee_name": emp.get("NUME IC", ""),
                        "rank": emp.get("RANK", ""),
                        "role": emp.get("ROLE", ""),
                        "points": int(emp.get("PUNCTAJ", 0)),
                        "id_card_series": emp.get("SERIE DE BULETIN", "")
                    })
            
            cities_data[city_name][institution_name] = employees
            print(f"    📄 {institution_name}: {len(employees)} employees")
        except Exception as e:
            print(f"    ✗ Error: {e}")

# Delete old data
print("\n[Clear] Deleting old data...")
for table in ["employees", "institutions", "cities"]:
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=gte.0"
    try:
        resp = requests.delete(url, headers=headers, timeout=10)
        if resp.status_code in [200, 204]:
            print(f"  ✓ Cleared {table}")
    except:
        pass

# Insert cities
print("\n[Insert] Cities...")
cities_map = {}

for city_name in sorted(cities_data.keys()):
    url = f"{SUPABASE_URL}/rest/v1/cities"
    payload = {"name": city_name}
    
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    
    if resp.status_code in [200, 201]:
        result = resp.json()
        if isinstance(result, list) and result:
            city_id = result[0]['id']
            cities_map[city_name] = city_id
            print(f"  ✓ {city_name} (ID: {city_id})")
        else:
            print(f"  ✗ {city_name}: bad response")
    else:
        print(f"  ✗ {city_name}: {resp.status_code} - {resp.text[:100]}")

# Insert institutions
print("\n[Insert] Institutions...")
institutions_map = {}

for city_name in sorted(cities_data.keys()):
    if city_name not in cities_map:
        continue
    
    city_id = cities_map[city_name]
    
    for institution_name in sorted(cities_data[city_name].keys()):
        url = f"{SUPABASE_URL}/rest/v1/institutions"
        payload = {"city_id": city_id, "name": institution_name}
        
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if resp.status_code in [200, 201]:
            result = resp.json()
            if isinstance(result, list) and result:
                institution_id = result[0]['id']
                institutions_map[(city_id, institution_name)] = institution_id
                print(f"  ✓ {city_name}/{institution_name} (ID: {institution_id})")
        else:
            print(f"  ✗ {city_name}/{institution_name}: {resp.status_code}")

# Insert employees
print("\n[Insert] Employees...")
total_inserted = 0

for city_name in sorted(cities_data.keys()):
    if city_name not in cities_map:
        continue
    
    city_id = cities_map[city_name]
    
    for institution_name in sorted(cities_data[city_name].keys()):
        key = (city_id, institution_name)
        
        if key not in institutions_map:
            continue
        
        institution_id = institutions_map[key]
        employees = cities_data[city_name][institution_name]
        
        if not employees:
            continue
        
        for emp in employees:
            emp['institution_id'] = institution_id
            
            url = f"{SUPABASE_URL}/rest/v1/employees"
            resp = requests.post(url, json=emp, headers=headers, timeout=10)
            
            if resp.status_code in [200, 201]:
                total_inserted += 1
                print(f"  ✓ {emp['employee_name']} ({city_name}/{institution_name})")
            else:
                print(f"  ✗ {emp['employee_name']}: {resp.status_code}")

# Verify
print("\n" + "=" * 70)
print("[Verify] Checking final counts...")

try:
    for table in ["cities", "institutions", "employees"]:
        url = f"{SUPABASE_URL}/rest/v1/{table}?limit=9999&select=id"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            count = len(resp.json())
            print(f"  ✓ {table}: {count}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("✅ SYNC COMPLETE!")
print("=" * 70)
