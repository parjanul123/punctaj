#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: Check if logs are actually being saved to Supabase
"""

import requests
import configparser
from datetime import datetime

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
print("🔍 DEBUGGING: Are logs actually being saved to Supabase?")
print("=" * 70)

# Get ALL logs from past 30 minutes
print("\n1️⃣ Fetching all logs from past 30 minutes...")

now = datetime.now()
thirty_min_ago = datetime.fromtimestamp(now.timestamp() - 1800).isoformat()

url = f"{SUPABASE_URL}/rest/v1/audit_logs?timestamp=gte.{thirty_min_ago}&order=timestamp.desc&limit=50"
print(f"   URL: {url[:100]}...")

response = requests.get(url, headers=headers)
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    logs = response.json()
    print(f"   ✅ Found {len(logs)} logs in past 30 minutes")
    
    if logs:
        print(f"\n📊 RECENT LOGS:")
        for i, log in enumerate(logs[:5], 1):
            timestamp = log.get('timestamp', 'N/A')[:19]
            action = log.get('action_type', 'unknown')
            user = log.get('discord_username', 'unknown')
            details = log.get('details', '')[:40]
            print(f"   {i}. [{timestamp}] {action:15} | {user:15} | {details}")
    else:
        print(f"   ⚠️ NO LOGS in past 30 minutes!")
else:
    print(f"   ❌ Failed to fetch (status {response.status_code})")
    print(f"   Response: {response.text}")

# Try inserting a test log with MORE debugging
print(f"\n2️⃣ Attempting test insert with detailed debugging...")

test_log = {
    "discord_id": "DEBUG_TEST",
    "discord_username": "DEBUG_USER",
    "action_type": "debug_test_insert",
    "city": "DEBUG_CITY",
    "institution": "DEBUG_INST",
    "details": "Testing if logs actually save",
    "timestamp": datetime.now().isoformat()
}

url_insert = f"{SUPABASE_URL}/rest/v1/audit_logs"
print(f"   Posting to: {url_insert}")
print(f"   Headers: {headers}")
print(f"   Data: {test_log}")

response_insert = requests.post(url_insert, json=test_log, headers=headers)
print(f"\n   Status Code: {response_insert.status_code}")
print(f"   Response Text: {response_insert.text}")

if response_insert.status_code in [200, 201]:
    print(f"   ✅ INSERT SUCCEEDED")
    
    # Now check if we can retrieve it
    print(f"\n3️⃣ Verifying the test log was saved...")
    url_verify = f"{SUPABASE_URL}/rest/v1/audit_logs?action_type=eq.debug_test_insert&order=timestamp.desc&limit=1"
    response_verify = requests.get(url_verify, headers=headers)
    
    if response_verify.status_code == 200:
        verify_logs = response_verify.json()
        if verify_logs:
            print(f"   ✅ TEST LOG FOUND IN SUPABASE!")
            print(f"   Log: {verify_logs[0]}")
        else:
            print(f"   ❌ INSERT SUCCEEDED but LOG NOT FOUND in Supabase!")
            print(f"   This suggests data is being lost or not committed")
    else:
        print(f"   ❌ Could not verify (status {response_verify.status_code})")
else:
    print(f"   ❌ INSERT FAILED")

# Check if it's a credentials issue
print(f"\n4️⃣ Checking Supabase connectivity...")
url_test = f"{SUPABASE_URL}/rest/v1/audit_logs?limit=1"
response_test = requests.get(url_test, headers=headers)
print(f"   Basic connectivity: {response_test.status_code}")

if response_test.status_code != 200:
    print(f"   ⚠️ Issue with Supabase connection!")
    print(f"   Response: {response_test.text}")
else:
    print(f"   ✅ Supabase connection is OK")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
