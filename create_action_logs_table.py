#!/usr/bin/env python3
"""
Create the action_logs table in Supabase with proper schema
Run this ONCE to initialize the table
"""

import requests
import json

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

# SQL to create table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS action_logs (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user TEXT,
  action TEXT,
  city TEXT,
  institution TEXT,
  details TEXT
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_action_logs_user ON action_logs(user);
CREATE INDEX IF NOT EXISTS idx_action_logs_city ON action_logs(city);
CREATE INDEX IF NOT EXISTS idx_action_logs_action ON action_logs(action);
"""

print("=" * 70)
print("CREATING ACTION_LOGS TABLE IN SUPABASE")
print("=" * 70)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Use SQL RPC endpoint
url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"

payload = {
    "sql": CREATE_TABLE_SQL
}

print("\nExecuting SQL...")
print(CREATE_TABLE_SQL)

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code in [200, 201]:
        print("\n✓ SUCCESS! Table created successfully.")
    else:
        print(f"\n✗ FAILED!")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nNote: If you got an error, you may need to:")
    print("1. Go to https://app.supabase.com/project/yzlkgifumrwqlfgimcai/sql/new")
    print("2. Paste this SQL and run it manually:")
    print("\n" + CREATE_TABLE_SQL)

print("\n" + "=" * 70)
