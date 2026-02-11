#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check what's in local users_permissions.json
"""

import os
import json

# Find users_permissions.json
search_paths = [
    os.path.join(os.path.expanduser("~"), "Documents/PunctajManager/users_permissions.json"),
    os.path.join(os.path.expanduser("~"), "Documents/PunctajManager/data/users_permissions.json"),
    "data/users_permissions.json",
    "users_permissions.json"
]

HOST_ID = "703316932232872016"

print("\n" + "="*80)
print("🔍 LOCAL JSON STATUS")
print("="*80)

json_file = None
for path in search_paths:
    if os.path.exists(path):
        json_file = path
        break

if not json_file:
    print(f"\n❌ users_permissions.json NOT FOUND")
    print(f"   Searched in:")
    for path in search_paths:
        print(f"   - {path}")
else:
    print(f"\n✅ Found: {json_file}")
    print(f"   Size: {os.path.getsize(json_file)} bytes")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        users = data.get('users', {})
        print(f"   Total users in JSON: {len(users)}")
        
        if str(HOST_ID) in users:
            user_data = users[str(HOST_ID)]
            print(f"\n🎯 HOST ({HOST_ID}) FOUND IN JSON:")
            print(f"   username: {user_data.get('username')}")
            print(f"   is_superuser: {user_data.get('is_superuser')}")
            print(f"   is_admin: {user_data.get('is_admin')}")
            print(f"   last_synced: {user_data.get('last_synced')}")
            
            perms = user_data.get('permissions', {})
            print(f"   permissions keys: {list(perms.keys())}")
        else:
            print(f"\n⚠️  HOST ({HOST_ID}) NOT in local JSON")
            print(f"   Users in JSON: {list(users.keys())[:5]}")
    
    except Exception as e:
        print(f"\n❌ Error reading JSON: {e}")

print("\n" + "="*80)
