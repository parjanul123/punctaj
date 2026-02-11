#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check actual columns in action_logs table
"""
import requests

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Fetch one row to see structure
url = f"{SUPABASE_URL}/rest/v1/action_logs?limit=1"

print("=" * 70)
print("CHECKING action_logs TABLE STRUCTURE")
print("=" * 70)

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print("\n✓ Table exists!")
            print(f"\nColumns found:")
            for col in data[0].keys():
                print(f"  - {col}: {type(data[0][col]).__name__}")
            print(f"\nExample row:")
            print(f"  {data[0]}")
        else:
            print("\nTable exists but is empty")
    else:
        print(f"\n✗ Error: Status {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "=" * 70)
