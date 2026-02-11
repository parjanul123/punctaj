#!/usr/bin/env python3
"""
Populate cities, institutions, and employees tables in Supabase
Run this AFTER creating the tables in Supabase dashboard
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
print("POPULATE CITIES, INSTITUTIONS, AND EMPLOYEES TABLES")
print("=" * 70)

# Step 1: Get or create cities
print("\n[Step 1] Processing cities...")
cities_map = {}  # {city_name: city_id}

for city_folder in DATA_DIR.iterdir():
    if not city_folder.is_dir():
        continue
    
    city_name = city_folder.name
    print(f"\n  📍 {city_name}")
    
    # Check if city already exists
    url_check = f"{SUPABASE_URL}/rest/v1/cities?name=eq.{city_name}&select=id"
    
    try:
        resp = requests.get(url_check, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            
            if data:
                city_id = data[0]['id']
                cities_map[city_name] = city_id
                print(f"    ✓ Found (ID: {city_id})")
            else:
                # Create city
                url_insert = f"{SUPABASE_URL}/rest/v1/cities"
                payload = {"name": city_name}
                
                resp_insert = requests.post(url_insert, json=payload, headers=headers, timeout=10)
                
                if resp_insert.status_code in [200, 201]:
                    result = resp_insert.json()
                    if isinstance(result, list) and result:
                        city_id = result[0]['id']
                    else:
                        city_id = result.get('id')
                    
                    cities_map[city_name] = city_id
                    print(f"    ✓ Created (ID: {city_id})")
                else:
                    print(f"    ✗ Failed to create: {resp_insert.status_code}")
                    print(f"       {resp_insert.text[:150]}")
    
    except Exception as e:
        print(f"    ✗ Error: {e}")

print(f"\n✓ Cities processed: {len(cities_map)}")

# Step 2: Get or create institutions
print("\n[Step 2] Processing institutions...")
institutions_map = {}  # {(city_id, institution_name): institution_id}

for city_folder in DATA_DIR.iterdir():
    if not city_folder.is_dir():
        continue
    
    city_name = city_folder.name
    if city_name not in cities_map:
        continue
    
    city_id = cities_map[city_name]
    
    for json_file in city_folder.glob("*.json"):
        institution_name = json_file.stem
        print(f"\n  🏢 {city_name} / {institution_name}")
        
        # Check if institution exists
        url_check = f"{SUPABASE_URL}/rest/v1/institutions?city_id=eq.{city_id}&name=eq.{institution_name}&select=id"
        
        try:
            resp = requests.get(url_check, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                
                if data:
                    institution_id = data[0]['id']
                    institutions_map[(city_id, institution_name)] = institution_id
                    print(f"    ✓ Found (ID: {institution_id})")
                else:
                    # Create institution
                    url_insert = f"{SUPABASE_URL}/rest/v1/institutions"
                    payload = {"city_id": city_id, "name": institution_name}
                    
                    resp_insert = requests.post(url_insert, json=payload, headers=headers, timeout=10)
                    
                    if resp_insert.status_code in [200, 201]:
                        result = resp_insert.json()
                        if isinstance(result, list) and result:
                            institution_id = result[0]['id']
                        else:
                            institution_id = result.get('id')
                        
                        institutions_map[(city_id, institution_name)] = institution_id
                        print(f"    ✓ Created (ID: {institution_id})")
                    else:
                        print(f"    ✗ Failed: {resp_insert.status_code}")
                        print(f"       {resp_insert.text[:150]}")
        
        except Exception as e:
            print(f"    ✗ Error: {e}")

print(f"\n✓ Institutions processed: {len(institutions_map)}")

# Step 3: Insert employees
print("\n[Step 3] Processing employees...")
total_employees = 0
inserted_employees = 0

for city_folder in DATA_DIR.iterdir():
    if not city_folder.is_dir():
        continue
    
    city_name = city_folder.name
    if city_name not in cities_map:
        continue
    
    city_id = cities_map[city_name]
    
    for json_file in city_folder.glob("*.json"):
        institution_name = json_file.stem
        key = (city_id, institution_name)
        
        if key not in institutions_map:
            continue
        
        institution_id = institutions_map[key]
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'rows' in data and data['rows']:
                print(f"\n  👥 {city_name} / {institution_name}: {len(data['rows'])} employees")
                
                for emp in data['rows']:
                    total_employees += 1
                    
                    emp_record = {
                        "institution_id": institution_id,
                        "discord_username": emp.get("DISCORD", ""),
                        "employee_name": emp.get("NUME IC", ""),
                        "rank": emp.get("RANK", ""),
                        "role": emp.get("ROLE", ""),
                        "points": int(emp.get("PUNCTAJ", 0)),
                        "id_card_series": emp.get("SERIE DE BULETIN", "")
                    }
                    
                    url_insert = f"{SUPABASE_URL}/rest/v1/employees"
                    
                    try:
                        resp = requests.post(url_insert, json=emp_record, headers=headers, timeout=10)
                        
                        if resp.status_code in [200, 201]:
                            inserted_employees += 1
                            emp_name = emp_record['employee_name']
                            print(f"    ✓ {emp_name}")
                        else:
                            print(f"    ✗ {emp.get('NUME IC', 'Unknown')}: {resp.status_code}")
                            if total_employees <= 2:
                                print(f"       {resp.text[:150]}")
                    
                    except Exception as e:
                        print(f"    ✗ Error: {e}")
        
        except Exception as e:
            print(f"  ✗ Error reading {json_file}: {e}")

print("\n" + "=" * 70)
print(f"RESULT: {inserted_employees}/{total_employees} employees inserted")
print("=" * 70)

# Verify
print("\n[Step 4] Verifying data...")

try:
    url_cities = f"{SUPABASE_URL}/rest/v1/cities?select=count"
    resp = requests.get(url_cities, headers=headers, timeout=10)
    cities_count = len(resp.json()) if resp.status_code == 200 else 0
    print(f"✓ Cities: {cities_count}")
    
    url_inst = f"{SUPABASE_URL}/rest/v1/institutions?select=count"
    resp = requests.get(url_inst, headers=headers, timeout=10)
    inst_count = len(resp.json()) if resp.status_code == 200 else 0
    print(f"✓ Institutions: {inst_count}")
    
    url_emp = f"{SUPABASE_URL}/rest/v1/employees?select=count"
    resp = requests.get(url_emp, headers=headers, timeout=10)
    emp_count = len(resp.json()) if resp.status_code == 200 else 0
    print(f"✓ Employees: {emp_count}")

except Exception as e:
    print(f"Error verifying: {e}")

print("\n✅ DONE! Tables populated in Supabase.")
print("\nYou can now view the data in Supabase dashboard:")
print("https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/editor")
