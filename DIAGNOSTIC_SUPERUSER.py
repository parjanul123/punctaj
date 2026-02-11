#!/usr/bin/env python3
"""
Detailed Superuser Status Diagnostic
Shows exactly what is_superuser value is in Supabase and how it's being read
"""

import requests
import json
import sys
from pathlib import Path
import configparser

# Read config
config_path = Path(r"d:\punctaj\supabase_config.ini")
config = configparser.ConfigParser()
config.read(config_path)

supabase_url = config.get("supabase", "url")
supabase_key = config.get("supabase", "key")

print("=" * 80)
print("🔍 SUPERUSER STATUS DIAGNOSTIC")
print("=" * 80)

# Test user - ask which Discord ID
print("\nEnter Discord ID to check (leave blank for all users):")
# For testing, use the first known user
discord_id_input = input("Discord ID (or press Enter): ").strip()

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

# Fetch users
if discord_id_input:
    url = f"{supabase_url}/rest/v1/discord_users?discord_id=eq.{discord_id_input}&select=*"
else:
    url = f"{supabase_url}/rest/v1/discord_users?select=discord_id,username,is_superuser,is_admin"

print(f"\n📥 Fetching from: {url}\n")

response = requests.get(url, headers=headers, timeout=10)

if response.status_code != 200:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
    sys.exit(1)

users = response.json()
print(f"✅ Found {len(users)} user(s)\n")

for user in users:
    discord_id = user.get('discord_id')
    username = user.get('username', 'Unknown')
    is_superuser_raw = user.get('is_superuser')
    is_admin_raw = user.get('is_admin')
    
    print(f"\n{'='*80}")
    print(f"USER: {username} (Discord ID: {discord_id})")
    print(f"{'='*80}")
    
    print(f"\n🔷 RAW VALUES FROM SUPABASE:")
    print(f"   is_superuser:")
    print(f"     - Value: {repr(is_superuser_raw)}")
    print(f"     - Type: {type(is_superuser_raw).__name__}")
    print(f"     - Is None? {is_superuser_raw is None}")
    print(f"     - Truthy? {bool(is_superuser_raw)}")
    
    print(f"\n   is_admin:")
    print(f"     - Value: {repr(is_admin_raw)}")
    print(f"     - Type: {type(is_admin_raw).__name__}")
    print(f"     - Is None? {is_admin_raw is None}")
    print(f"     - Truthy? {bool(is_admin_raw)}")
    
    # Simulate what discord_auth.py does
    print(f"\n🔵 HOW discord_auth.py CONVERTS (exactly like in _fetch_user_role_from_supabase):")
    
    # This is the exact code from discord_auth.py lines 311-318
    raw_is_superuser = is_superuser_raw
    raw_is_admin = is_admin_raw
    
    # Convert to proper boolean
    if isinstance(raw_is_superuser, str):
        converted_superuser = raw_is_superuser.lower() in ['true', '1', 'yes']
        print(f"   is_superuser was STRING → converted to {converted_superuser}")
    else:
        converted_superuser = bool(raw_is_superuser)
        print(f"   is_superuser was {type(raw_is_superuser).__name__} → bool({raw_is_superuser}) = {converted_superuser}")
    
    if isinstance(raw_is_admin, str):
        converted_admin = raw_is_admin.lower() in ['true', '1', 'yes']
        print(f"   is_admin was STRING → converted to {converted_admin}")
    else:
        converted_admin = bool(raw_is_admin)
        print(f"   is_admin was {type(raw_is_admin).__name__} → bool({raw_is_admin}) = {converted_admin}")
    
    print(f"\n✅ FINAL VALUES:")
    print(f"   _is_superuser = {converted_superuser}")
    print(f"   _is_admin = {converted_admin}")
    
    if converted_superuser:
        print(f"\n✅ Would set role to: SUPERUSER")
    elif converted_admin:
        print(f"\n✅ Would set role to: ADMIN")
    else:
        print(f"\n⚠️  Would set role to: USER or VIEWER (not admin/superuser)")
    
    # Check what the REST query would actually return
    print(f"\n🔷 WHAT THE REST API QUERY RETURNS:")
    specific_url = f"{supabase_url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=username,is_superuser,is_admin,can_view,can_edit,can_delete"
    print(f"   URL: {specific_url}")
    
    response2 = requests.get(specific_url, headers=headers, timeout=5)
    if response2.status_code == 200:
        data = response2.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
    else:
        print(f"   ❌ Error {response2.status_code}: {response2.text}")

print(f"\n\n{'='*80}")
print("💡 TROUBLESHOOTING:")
print(f"{'='*80}")
print("""
If is_superuser is FALSE or NULL:

Option 1: UPDATE in Supabase directly
  1. Go to: https://app.supabase.com
  2. Open your project → discord_users table
  3. Find your row (by discord_id)
  4. Click is_superuser cell → change to TRUE (Boolean type)
  5. Press Enter to save
  6. Logout from app
  7. Login again (fresh authentication)

Option 2: Update via SQL (if comfortable)
  UPDATE discord_users 
  SET is_superuser = true 
  WHERE discord_id = '{discord_id}';

Option 3: Check if values are being stored as STRING instead of BOOLEAN
  The conversion code handles 'true'/'false' strings but:
  - Type should be: Boolean (not text)
  - Value should be: true/false (not 'true'/'false')

If still not working:
  - Check browser console for Discord OAuth errors
  - Verify Discord ID matches exactly
  - Make sure Supabase connection works (test with other field updates)
""")
