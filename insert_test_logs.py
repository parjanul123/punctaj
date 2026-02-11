#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Insert test logs into Supabase table 19922 (action_log)
to demonstrate the logging system
"""
import sys
sys.path.insert(0, 'd:\\punctaj')

import requests
import json
from datetime import datetime, timedelta

# Supabase credentials
SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"  # From supabase_config.ini

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Test logs to insert
test_logs = [
    {
        "user": "parjanu",
        "action": "add_employee",
        "city": "BlackWater",
        "institution": "Politie",
        "details": "Added employee: Dandeny Munoz"
    },
    {
        "user": "parjanu",
        "action": "edit_points",
        "city": "BlackWater",
        "institution": "Politie",
        "details": "Changed points: Dandeny Munoz from 0 to 5 (add)"
    },
    {
        "user": "parjanu",
        "action": "edit_points",
        "city": "BlackWater",
        "institution": "Politie",
        "details": "Changed points: Vulpe Fuchs from 0 to 3 (add)"
    },
    {
        "user": "parjanu",
        "action": "delete_employee",
        "city": "BlackWater",
        "institution": "Politie",
        "details": "Deleted employee: Test Employee"
    },
    {
        "user": "parjanu",
        "action": "add_employee",
        "city": "Saint_Denis",
        "institution": "Politie",
        "details": "Added employee: Popescu Ioan"
    }
]

print("=" * 70)
print("INSERTING TEST LOGS INTO SUPABASE TABLE 19922")
print("=" * 70)

url = f"{SUPABASE_URL}/rest/v1/action_logs"

for i, log in enumerate(test_logs, 1):
    print(f"\n[{i}/{len(test_logs)}] Inserting log...")
    print(f"  Action: {log['action']}")
    print(f"  City/Institution: {log['city']} / {log['institution']}")
    
    try:
        response = requests.post(url, json=log, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"  ✓ SUCCESS (Status: {response.status_code})")
        else:
            print(f"  ✗ FAILED (Status: {response.status_code})")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")

print("\n" + "=" * 70)
print("DONE!")
print("=" * 70)
print("\nNow in Admin Panel:")
print("1. Click '📋 Loguri Acțiuni' button")
print("2. Select City: 'BlackWater' or 'Saint_Denis'")
print("3. Select Institution: 'Politie'")
print("4. Click '🔄 Reîncarcă loguri'")
print("5. You should see the test logs in the table!")
print("\n" + "=" * 70)
