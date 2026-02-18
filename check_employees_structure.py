#!/usr/bin/env python3
"""
Check employees table structure
"""

import configparser
import requests
import json

config = configparser.ConfigParser()
config.read('supabase_config.ini')

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("🔍 CHECKING EMPLOYEES TABLE STRUCTURE")
print("=" * 70)

# Fetch one employee to see what fields exist
try:
    url = f"{SUPABASE_URL}/rest/v1/employees?limit=1"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        employees = response.json()
        if employees:
            emp = employees[0]
            print(f"\n📋 Employee record structure:")
            print(f"{json.dumps(emp, indent=2)}")
            
            print(f"\n📌 Available columns:")
            for key in emp.keys():
                print(f"   • {key}")
        else:
            print("❌ No employees found")
    else:
        print(f"❌ Failed (HTTP {response.status_code}): {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")
