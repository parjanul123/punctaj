#!/usr/bin/env python3
"""
Create normalized table structure in Supabase:
- cities (orașe)
- institutions (instituții cu FK la cities)
- employees (angajați cu FK la institutions)

Then populate with data from local JSON files
"""

import json
import requests
from pathlib import Path
from collections import defaultdict

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

DATA_DIR = Path(__file__).parent / "data"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# SQL for creating tables - COPY THIS TO SUPABASE DASHBOARD
CREATE_TABLES_SQL = """
-- Drop existing tables if they exist
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS institutions CASCADE;
DROP TABLE IF EXISTS cities CASCADE;

-- Create cities table
CREATE TABLE cities (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create institutions table
CREATE TABLE institutions (
  id BIGSERIAL PRIMARY KEY,
  city_id BIGINT NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(city_id, name)
);

-- Create employees table
CREATE TABLE employees (
  id BIGSERIAL PRIMARY KEY,
  institution_id BIGINT NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
  discord_username TEXT,
  employee_name TEXT NOT NULL,
  rank TEXT,
  role TEXT,
  points INT DEFAULT 0,
  id_card_series TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_institutions_city_id ON institutions(city_id);
CREATE INDEX idx_employees_institution_id ON employees(institution_id);
CREATE INDEX idx_employees_discord_username ON employees(discord_username);
CREATE INDEX idx_employees_employee_name ON employees(employee_name);
"""

print("=" * 70)
print("CREATE NORMALIZED TABLES IN SUPABASE")
print("=" * 70)

print("\n📋 SQL TO RUN IN SUPABASE DASHBOARD:")
print("-" * 70)
print(CREATE_TABLES_SQL)
print("-" * 70)

print("\nInstruction: Copy the SQL above and paste in:")
print("https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/sql/new")
print("\nThen run this script again to populate tables with data.")

# Read data from JSON files
print("\n" + "=" * 70)
print("READING DATA FROM JSON FILES")
print("=" * 70)

cities = {}  # {city_name: {institution_name: [employees]}}

for city_folder in DATA_DIR.iterdir():
    if not city_folder.is_dir():
        continue
    
    city_name = city_folder.name
    cities[city_name] = {}
    print(f"\n📍 {city_name}")
    
    for json_file in city_folder.glob("*.json"):
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
            
            cities[city_name][institution_name] = employees
            print(f"  📄 {institution_name}: {len(employees)} employees")
        
        except Exception as e:
            print(f"  ✗ Error reading {institution_name}: {e}")

# Save data to file for later insertion
print("\n" + "=" * 70)
print("SAVING DATA STRUCTURE")
print("=" * 70)

data_file = Path(__file__).parent / "synced_data.json"
with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(cities, f, indent=2, ensure_ascii=False)

print(f"\n✓ Data saved to: {data_file}")
print(f"\nData structure:")
for city, institutions in cities.items():
    print(f"\n  {city}")
    for institution, employees in institutions.items():
        print(f"    └─ {institution}: {len(employees)} employees")
        for emp in employees:
            print(f"       • {emp['employee_name']} (Rank: {emp['rank']})")

print("\n" + "=" * 70)
print("\nNEXT STEPS:")
print("1. Go to Supabase dashboard")
print("2. Run the SQL above to create tables")
print("3. Run: python populate_employees_tables.py")
print("=" * 70)
