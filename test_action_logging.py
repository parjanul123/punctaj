#!/usr/bin/env python3
"""Test action logging directly"""

import requests
from datetime import datetime

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Simulate what ACTION_LOGGER.log_add_employee does
test_logs = [
    {
        "discord_id": "parjanu",
        "action_type": "add_employee",
        "city": "Saint_Denis",
        "institution": "Politie",
        "details": "Added employee: Ion Popescu",
        "timestamp": datetime.now().isoformat()
    },
    {
        "discord_id": "parjanu",
        "action_type": "edit_points",
        "city": "Saint_Denis",
        "institution": "Politie",
        "details": "Ion Popescu: 10 → 15 (add)",
        "timestamp": datetime.now().isoformat()
    },
    {
        "discord_id": "parjanu",
        "action_type": "edit_employee",
        "city": "BlackWater",
        "institution": "Politie",
        "details": "Mihai Dumitrescu: PRENUME: Mihai → M",
        "timestamp": datetime.now().isoformat()
    },
    {
        "discord_id": "parjanu",
        "action_type": "delete_employee",
        "city": "Saint_Denis",
        "institution": "Politie",
        "details": "Deleted employee: Ana Popescu",
        "timestamp": datetime.now().isoformat()
    }
]

url = f"{SUPABASE_URL}/rest/v1/audit_logs"

print("=" * 70)
print("Testing Action Logging")
print("=" * 70)

for i, log in enumerate(test_logs, 1):
    print(f"\n{i}. Inserting {log['action_type']}...")
    print(f"   User: {log['discord_id']}")
    print(f"   City: {log['city']} / {log['institution']}")
    print(f"   Details: {log['details']}")
    
    response = requests.post(url, json=log, headers=headers, timeout=5)
    
    if response.status_code in [200, 201]:
        print(f"   ✅ SUCCESS (HTTP {response.status_code})")
    else:
        print(f"   ❌ FAILED (HTTP {response.status_code}): {response.text}")

print("\n" + "=" * 70)
print("Now check the logs in Admin Panel > Logs")
print("=" * 70)
