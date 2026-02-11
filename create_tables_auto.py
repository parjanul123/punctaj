#!/usr/bin/env python3
"""
Create normalized tables directly in Supabase via REST API
No need to manually copy-paste SQL!
"""

import requests
import json
from pathlib import Path

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

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

-- Create indexes
CREATE INDEX idx_institutions_city_id ON institutions(city_id);
CREATE INDEX idx_employees_institution_id ON employees(institution_id);
CREATE INDEX idx_employees_discord_username ON employees(discord_username);
CREATE INDEX idx_employees_employee_name ON employees(employee_name);
"""

print("=" * 70)
print("ATTEMPTING TO CREATE TABLES IN SUPABASE")
print("=" * 70)

# Try to execute SQL via the admin API
# Note: This might not work with public key, but let's try
url_rpc = f"{SUPABASE_URL}/rest/v1/rpc/sql"

# Split SQL into individual statements
statements = [s.strip() for s in CREATE_TABLES_SQL.split(';') if s.strip()]

print(f"\nFound {len(statements)} SQL statements")

for i, statement in enumerate(statements, 1):
    print(f"\n[{i}/{len(statements)}] Executing statement...")
    
    # Try different approaches
    # Approach 1: Via RPC
    try:
        payload = {"sql": statement}
        resp = requests.post(url_rpc, json=payload, headers=headers, timeout=10)
        
        if resp.status_code in [200, 201]:
            print(f"  ✓ Success")
        else:
            print(f"  ✗ Failed ({resp.status_code})")
            if i <= 2:
                print(f"     {resp.text[:200]}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("⚠️  NOTE: If the above failed, you need to create tables manually.")
print("=" * 70)

print("\n📋 MANUAL INSTRUCTIONS:")
print("1. Go to: https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/sql/new")
print("2. Click 'New Query'")
print("3. Paste this SQL and click 'Run':\n")
print(CREATE_TABLES_SQL)
print("\n4. Once tables are created, run:")
print("   python populate_employees_tables.py")
