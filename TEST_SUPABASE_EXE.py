#!/usr/bin/env python3
"""
DEBUG: Test Supabase Connection and Superuser Lookup
Run this to see if the EXE can connect to Supabase and fetch superuser status
"""

import sys
import os

# Test if we can find and import supabase_sync
print("=" * 80)
print("🔍 SUPABASE CONNECTION DEBUG TEST")
print("=" * 80)
print()

# Check config file locations
config_paths = [
    os.path.join(os.path.dirname(__file__), "supabase_config.ini"),
    os.path.join(os.path.expanduser("~"), "Documents/PunctajManager/supabase_config.ini"),
    "supabase_config.ini",
    os.path.join(os.path.dirname(sys.executable), "supabase_config.ini"),
]

print("📁 Checking config file locations:")
for path in config_paths:
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"  {status} {path}")

print()
print("-" * 80)

# Try to import and initialize Supabase
try:
    from supabase_sync import SupabaseSync
    print("✅ Successfully imported SupabaseSync")
except ImportError as e:
    print(f"❌ Failed to import SupabaseSync: {e}")
    sys.exit(1)

# Find config
config_found = None
for path in config_paths:
    if os.path.exists(path):
        config_found = path
        break

if not config_found:
    print("❌ No supabase_config.ini found!")
    sys.exit(1)

print(f"✅ Using config: {config_found}")
print()

try:
    supabase = SupabaseSync(config_found)
    print(f"✅ Connected to Supabase: {supabase.url}")
except Exception as e:
    print(f"❌ Failed to initialize Supabase: {e}")
    sys.exit(1)

print()
print("-" * 80)
print("🔎 Testing user lookup (parjanu):")
print("-" * 80)

import requests

headers = {
    "apikey": supabase.key,
    "Authorization": f"Bearer {supabase.key}",
    "Content-Type": "application/json"
}

# parjanu's discord ID
discord_id = "703316932232872016"

url = f"{supabase.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=username,is_superuser,is_admin,can_view"
print(f"📡 Query URL: {url}")
print()

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got response data:")
        print()
        
        if data and len(data) > 0:
            user = data[0]
            print(f"   Username: {user.get('username')}")
            print(f"   is_superuser: {user.get('is_superuser')} (type: {type(user.get('is_superuser')).__name__})")
            print(f"   is_admin: {user.get('is_admin')} (type: {type(user.get('is_admin')).__name__})")
            print(f"   can_view: {user.get('can_view')} (type: {type(user.get('can_view')).__name__})")
            
            print()
            print("-" * 80)
            print("🧪 Testing boolean conversion:")
            print("-" * 80)
            
            raw_is_superuser = user.get('is_superuser', False)
            
            # Test conversion
            if isinstance(raw_is_superuser, str):
                converted = raw_is_superuser.lower() in ['true', '1', 'yes']
                print(f"String conversion: '{raw_is_superuser}' -> {converted}")
            else:
                converted = bool(raw_is_superuser)
                print(f"Bool conversion: {raw_is_superuser} -> {converted}")
            
            print()
            if converted:
                print("✅ RESULT: User WOULD be recognized as SUPERUSER")
            else:
                print("❌ RESULT: User WOULD be recognized as VIEWER (NOT SUPERUSER)")
        else:
            print("❌ No user data returned!")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
