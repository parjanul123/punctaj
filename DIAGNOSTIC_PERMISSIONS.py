#!/usr/bin/env python3
"""
Diagnostic Tool - Verify Permissions Structure
Compares what's in Supabase vs what the app reads
"""

import requests
import json
import sys
from pathlib import Path

# Read Supabase config
config_path = Path(r"d:\punctaj\supabase_config.ini")
if not config_path.exists():
    print("❌ supabase_config.ini not found!")
    sys.exit(1)

import configparser
config = configparser.ConfigParser()
config.read(config_path)

supabase_url = config.get("supabase", "url")
supabase_key = config.get("supabase", "key")

print("=" * 80)
print("🔍 PERMISSIONS DIAGNOSTIC TOOL")
print("=" * 80)

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

# Fetch all users with their permissions
url = f"{supabase_url}/rest/v1/discord_users?select=discord_id,username,granular_permissions"

print(f"\n📥 Fetching users from: {supabase_url}")
print(f"   Select: discord_id, username, granular_permissions\n")

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Error: HTTP {response.status_code}")
        print(f"   {response.text}")
        sys.exit(1)
    
    users = response.json()
    print(f"✅ Found {len(users)} users\n")
    
    for i, user in enumerate(users, 1):
        discord_id = user.get('discord_id', 'N/A')
        username = user.get('username', 'Unknown')
        perms_raw = user.get('granular_permissions')
        
        print(f"\n{'='*80}")
        print(f"USER #{i}: {username} (Discord ID: {discord_id})")
        print(f"{'='*80}")
        
        # Show raw value
        print(f"\n📦 RAW VALUE (from Supabase):")
        print(f"   Type: {type(perms_raw).__name__}")
        print(f"   Value: {repr(perms_raw)[:200]}...")
        
        # Try to parse as JSON if string
        perms_parsed = None
        if isinstance(perms_raw, str):
            try:
                perms_parsed = json.loads(perms_raw)
                print(f"\n✅ Successfully parsed as JSON string")
            except json.JSONDecodeError as e:
                print(f"\n❌ Failed to parse as JSON: {e}")
                print(f"   First 500 chars: {perms_raw[:500]}")
        elif isinstance(perms_raw, dict):
            perms_parsed = perms_raw
            print(f"\n✅ Already a JSON object (dict)")
        elif perms_raw is None:
            print(f"\n⚠️  granular_permissions is NULL")
        
        # Show parsed structure
        if perms_parsed:
            print(f"\n🔵 PARSED STRUCTURE:")
            
            def show_structure(d, indent=0):
                """Recursively show structure"""
                if isinstance(d, dict):
                    for key, value in d.items():
                        if isinstance(value, dict):
                            print(f"{'  ' * indent}├─ {key}: <dict> with {len(value)} items")
                            show_structure(value, indent + 1)
                        elif isinstance(value, list):
                            print(f"{'  ' * indent}├─ {key}: <list> with {len(value)} items")
                        else:
                            print(f"{'  ' * indent}├─ {key}: {type(value).__name__} = {value}")
                elif isinstance(d, list):
                    for idx, item in enumerate(d[:3]):  # Show first 3 items
                        print(f"{'  ' * indent}├─ [{idx}]: {item}")
                    if len(d) > 3:
                        print(f"{'  ' * indent}└─ ... and {len(d) - 3} more items")
            
            show_structure(perms_parsed)
            
            # Show full JSON for reference
            print(f"\n📋 FULL PARSED JSON:")
            print(json.dumps(perms_parsed, indent=2, ensure_ascii=False)[:1000])
            if len(json.dumps(perms_parsed, indent=2, ensure_ascii=False)) > 1000:
                print("   ... (truncated)")
        
        # Check what the app expects
        print(f"\n🔷 EXPECTED APP FORMAT:")
        print("""
   {
     "cities": {
       "CityName": {
         "can_view": true/false,
         "can_edit": true/false
       }
     },
     "institutions": {
       "CityName": {
         "InstitutionName": {
           "can_view": true/false,
           "can_edit": true/false
         }
       }
     },
     "admin": { ... }
   }
        """)
        
        # Check if structure matches
        if isinstance(perms_parsed, dict):
            has_cities = 'cities' in perms_parsed
            has_institutions = 'institutions' in perms_parsed
            has_admin = 'admin' in perms_parsed
            
            print(f"\n✓ Structure keys found:")
            print(f"   {'✅' if has_cities else '❌'} 'cities' key")
            print(f"   {'✅' if has_institutions else '❌'} 'institutions' key")
            print(f"   {'✅' if has_admin else '❌'} 'admin' key")
            
            if not (has_cities or has_institutions or has_admin):
                print(f"\n⚠️  This structure doesn't match app expectations!")
                print(f"   Keys found: {list(perms_parsed.keys())}")
    
    print(f"\n\n{'='*80}")
    print("✅ DIAGNOSTIC COMPLETE")
    print(f"{'='*80}")
    print("\n💡 TIPS:")
    print("   1. If granular_permissions shows NULL → user has no permissions yet")
    print("   2. If structure doesn't match (cities/institutions) → need to rebuild it")
    print("   3. If stored as STRING instead of JSON → app will parse it automatically")
    print("   4. Check the keys - they must match the app's expected structure")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Network error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
