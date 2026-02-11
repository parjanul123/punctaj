#!/usr/bin/env python3
"""Check which logs table exists in Supabase"""

import requests

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

print("\nChecking which tables exist in Supabase...")
print("=" * 50)

tables_to_check = ["logs", "action_log", "action_logs"]

for table_name in tables_to_check:
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
    try:
        response = requests.get(url, headers=headers, timeout=5)
        status = response.status_code
        
        if status == 200:
            print(f"✅ {table_name:20} EXISTS (HTTP 200)")
        elif status == 404:
            print(f"❌ {table_name:20} NOT FOUND (HTTP 404)")
        else:
            print(f"⚠️  {table_name:20} ERROR (HTTP {status})")
            print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"🔥 {table_name:20} EXCEPTION: {e}")

print("=" * 50)
