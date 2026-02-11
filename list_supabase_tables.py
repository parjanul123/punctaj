#!/usr/bin/env python3
"""
List all tables in Supabase to find the employees table
"""

import requests

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("LISTING ALL TABLES IN SUPABASE")
print("=" * 70)

# Query information_schema to get all tables
sql_query = """
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
"""

url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"

payload = {
    "sql": sql_query
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response: {response.text}\n")
    
except Exception as e:
    print(f"Error: {e}")
    
# Alternative: try to list tables directly by attempting common names
print("\nTrying to access tables with common names...")
common_names = [
    "employees",
    "employees_discord", 
    "angajati",
    "staff",
    "members",
    "users",
    "employees_table",
    "discord_users",
    "action_logs"
]

for table_name in common_names:
    url_test = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
    try:
        r = requests.get(url_test, headers=headers, timeout=5)
        if r.status_code == 200:
            print(f"✓ Found: {table_name}")
        elif r.status_code == 401:
            print(f"⚠ {table_name} - Unauthorized")
        elif r.status_code != 404:
            print(f"? {table_name} - Status {r.status_code}")
    except:
        pass

print("\n" + "=" * 70)
