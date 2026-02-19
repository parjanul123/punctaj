#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import configparser

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
print("🔍 DIAGNOSING RLS POLICIES FOR audit_logs TABLE")
print("=" * 70)

# Test 1: Try to insert a log
print("\n1️⃣ TESTING INSERT...")
test_log = {
    "discord_id": "test_rls_check",
    "discord_username": "test_user_rls",
    "action_type": "test_rls",
    "city": "TEST_RLS",
    "institution": "TEST_RLS",
    "details": "Testing RLS policy",
    "timestamp": "2026-02-19T20:00:00Z"
}

url = f"{SUPABASE_URL}/rest/v1/audit_logs"
response = requests.post(url, json=test_log, headers=headers)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:300]}")

if response.status_code in [200, 201]:
    print("   ✅ INSERT WORKS")
else:
    print(f"   ❌ INSERT FAILED")
    print(f"   Possible reasons:")
    print(f"   - RLS policy blocks anonymous inserts")
    print(f"   - Authentication issue")
    print(f"   - Table permission issue")

# Test 2: Try a SELECT to check if we can read
print("\n2️⃣ TESTING SELECT...")
url_select = f"{SUPABASE_URL}/rest/v1/audit_logs?limit=1"
response_select = requests.get(url_select, headers=headers)
print(f"   Status: {response_select.status_code}")
if response_select.status_code == 200:
    print("   ✅ SELECT WORKS")
else:
    print(f"   ❌ SELECT FAILED")
    print(f"   Response: {response_select.text[:300]}")

print("\n" + "=" * 70)
print("💡 HOW TO FIX:")
print("=" * 70)
print("""
If INSERT fails, the audit_logs table likely has RLS enabled with a 
restrictive policy.

FIX OPTIONS:

1️⃣ DISABLE RLS (Simplest for internal app):
   - Go to: https://app.supabase.com/project/yzlkgifumrwqlfgimcai/editor/21181
   - Click "Authentication" → "Policies"
   - Find row that says "Row Level Security" is ON
   - Toggle it OFF
   - Or go to SQL Editor and run:
   
   ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;

2️⃣ ADD PERMISSIVE POLICY (More secure):
   CREATE POLICY "Allow all anonymous" ON audit_logs
   FOR ALL USING (true);

3️⃣ CHECK CURRENT POLICIES:
   SELECT * FROM pg_policies WHERE tablename = 'audit_logs';
""")

print("\n📊 TEST RESULT SUMMARY:")
if response.status_code in [200, 201]:
    print("   ✅ Table accepts inserts - RLS is NOT the issue")
    print("   🔍 Verify:")
    print("      - Is ActionLogger being called when you perform actions?")
    print("      - Check logs/ folder for local log files")
    print("      - Look at app console for errors")
else:
    print("   ❌ Table REJECTS inserts - RLS IS the issue")
    print("   ✅ Use solution 1️⃣ or 2️⃣ above to fix")
    print("   📋 Table is blocking INSERT operations due to RLS policy")
