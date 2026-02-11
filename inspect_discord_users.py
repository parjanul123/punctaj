#!/usr/bin/env python3
"""
Inspect discord_users table structure to see what columns it has
"""

import requests
import json

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("INSPECTING DISCORD_USERS TABLE STRUCTURE")
print("=" * 70)

# Try to get a single record and inspect its structure
url = f"{SUPABASE_URL}/rest/v1/discord_users?limit=1"

print("\nFetching sample record...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        if data:
            print("\n✓ Sample record found:")
            print(json.dumps(data[0], indent=2))
            
            print("\n📋 Available columns:")
            for col_name in sorted(data[0].keys()):
                value = data[0][col_name]
                print(f"  • {col_name}: {type(value).__name__} = {repr(value)}")
        else:
            print("\n⚠️  Table is empty, cannot inspect columns from data")
            print("\nTrying alternative method...")
            
            # Try to get schema info via information_schema
            # This might not work with REST API
            print("\n(Note: Cannot query information_schema via REST API)")
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("\nTo see table structure, go to:")
print("https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/editor/17485")
print("=" * 70)
