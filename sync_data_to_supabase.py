#!/usr/bin/env python3
"""
Check if tables exist and populate with data from local JSON files
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
print("CHECK TABLES & POPULATE WITH DATA")
print("=" * 70)

# Check if tables exist
print("\n[Check] Verifying tables exist...")
tables_to_check = ["cities", "institutions", "employees"]
tables_exist = {}

for table_name in tables_to_check:
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=0"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            tables_exist[table_name] = True
            print(f"  ✓ {table_name} exists")
        elif resp.status_code == 404:
            tables_exist[table_name] = False
            print(f"  ✗ {table_name} NOT FOUND")
        else:
            print(f"  ? {table_name} - Status {resp.status_code}")
    except Exception as e:
        print(f"  ✗ Error checking {table_name}: {e}")

# If tables don't exist, stop
if not all(tables_exist.values()):
    print("\n⚠️  MISSING TABLES!")
    print("Please create tables first in Supabase Dashboard using this SQL:")
    print("\nhttps://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/sql/new")
    exit(1)

print("\n✓ All tables exist! Proceeding with data population...\n")

# Read data from local folders
cities_data = {}

print("[Read] Reading data from local files...\n")

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
            emp_count = len(employees)
            print(f"    📄 {institution_name}: {emp_count} employees")
        
        except Exception as e:
            print(f"    ✗ Error reading {institution_name}: {e}")

print("\n" + "=" * 70)
print("POPULATING SUPABASE")
print("=" * 70)

# Clear existing data
print("\n[Clear] Deleting old data...")
for table in ["employees", "institutions", "cities"]:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    try:
        # Delete with WHERE 1=1 (all rows)
        resp = requests.delete(f"{url}?id=gt.-1", headers=headers, timeout=10)
        
        if resp.status_code in [200, 204]:
            print(f"  ✓ Cleared {table}")
        else:
            print(f"  ⚠ {table}: {resp.status_code}")
    except Exception as e:
        print(f"  ⚠ Error clearing {table}: {e}")

# Insert cities
print("\n[Insert] Creating cities...")
cities_map = {}

for city_name in sorted(cities_data.keys()):
    url = f"{SUPABASE_URL}/rest/v1/cities"
    payload = {"name": city_name}
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if resp.status_code in [200, 201]:
            try:
                result = resp.json()
                if isinstance(result, list) and result:
                    city_id = result[0]['id']
                elif isinstance(result, dict):
                    city_id = result.get('id')
                else:
                    city_id = None
            except:
                # If no JSON, try to extract ID from Location header
                location = resp.headers.get('location', '')
                if '/' in location:
                    city_id = location.split('/')[-1]
                else:
                    city_id = None
            
            if city_id:
                cities_map[city_name] = city_id
                print(f"  ✓ {city_name} (ID: {city_id})")
            else:
                print(f"  ✗ {city_name}: No ID in response")
        else:
            print(f"  ✗ {city_name}: {resp.status_code}")
    except Exception as e:
        print(f"  ✗ {city_name}: {e}")

# Insert institutions
print("\n[Insert] Creating institutions...")
institutions_map = {}

for city_name in sorted(cities_data.keys()):
    if city_name not in cities_map:
        continue
    
    city_id = cities_map[city_name]
    
    for institution_name in sorted(cities_data[city_name].keys()):
        url = f"{SUPABASE_URL}/rest/v1/institutions"
        payload = {
            "city_id": city_id,
            "name": institution_name
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if resp.status_code in [200, 201]:
                try:
                    result = resp.json()
                    if isinstance(result, list) and result:
                        institution_id = result[0]['id']
                    elif isinstance(result, dict):
                        institution_id = result.get('id')
                    else:
                        institution_id = None
                except:
                    institution_id = None
                
                if institution_id:
                    institutions_map[(city_id, institution_name)] = institution_id
                    print(f"  ✓ {city_name} / {institution_name} (ID: {institution_id})")
                else:
                    print(f"  ✗ {city_name} / {institution_name}: No ID in response")
            else:
                print(f"  ✗ {city_name} / {institution_name}: {resp.status_code}")
        except Exception as e:
            print(f"  ✗ {city_name} / {institution_name}: {e}")

# Insert employees
print("\n[Insert] Adding employees...")
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
            print(f"  - {city_name} / {institution_name}: 0 employees")
            continue
        
        print(f"  📥 {city_name} / {institution_name}: {len(employees)} employees")
        
        for emp in employees:
            emp['institution_id'] = institution_id
            
            url = f"{SUPABASE_URL}/rest/v1/employees"
            
            try:
                resp = requests.post(url, json=emp, headers=headers, timeout=10)
                
                if resp.status_code in [200, 201]:
                    total_inserted += 1
                    print(f"     ✓ {emp['employee_name']}")
                else:
                    print(f"     ✗ {emp['employee_name']}: {resp.status_code}")
                    if total_inserted == 0:  # Show error for first failure
                        print(f"        {resp.text[:200]}")
            except Exception as e:
                print(f"     ✗ {emp['employee_name']}: {e}")

# Verify
print("\n" + "=" * 70)
print("[Verify] Final counts...")

try:
    for table in ["cities", "institutions", "employees"]:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=count&limit=1"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            count = len(resp.json())
            print(f"  ✓ {table}: {count}")
except Exception as e:
    print(f"  Error verifying: {e}")

print("\n" + "=" * 70)
print("✅ DONE!")
print("=" * 70)
print("\nYou can now view the data in Supabase:")
print("https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/editor")
