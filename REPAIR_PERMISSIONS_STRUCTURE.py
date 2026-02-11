#!/usr/bin/env python3
"""
Fix Permissions Structure - Consolidate nested vs top-level institutions
Ensures permissions are read from correct location consistently
"""

import json
import sys
from pathlib import Path

def consolidate_permissions_structure(perms_dict):
    """
    Consolidate permissions to use ONLY the top-level institutions structure
    Removes duplicates from nested institutions
    
    Input:
    {
        "cities": {
            "CityName": {
                "can_edit": true,
                "can_view": true,
                "institutions": { ... nested ... },  ← REMOVE
                "can_add_institutions": true,
            }
        },
        "institutions": {  ← USE THIS
            "CityName": {
                "InstitutionName": { ... }
            }
        }
    }
    
    Output: Same structure but without nested institutions in cities
    """
    if not isinstance(perms_dict, dict):
        return perms_dict
    
    result = {}
    
    # Copy cities but REMOVE nested institutions
    if 'cities' in perms_dict:
        result['cities'] = {}
        for city_name, city_perms in perms_dict['cities'].items():
            if isinstance(city_perms, dict):
                # Keep all permissions EXCEPT 'institutions' key
                result['cities'][city_name] = {
                    k: v for k, v in city_perms.items() 
                    if k != 'institutions'  # ← Remove nested institutions
                }
            else:
                result['cities'][city_name] = city_perms
    
    # Keep top-level institutions (correct structure)
    if 'institutions' in perms_dict:
        result['institutions'] = perms_dict['institutions']
    
    # Keep global and other keys
    for key in perms_dict:
        if key not in ['cities', 'institutions']:
            result[key] = perms_dict[key]
    
    return result


def repair_permissions_in_supabase():
    """
    Fetch all users and repair their permissions structure
    """
    import requests
    import configparser
    
    config_path = Path(r"d:\punctaj\supabase_config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    
    supabase_url = config.get("supabase", "url")
    supabase_key = config.get("supabase", "key")
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    print("=" * 80)
    print("🔧 PERMISSIONS STRUCTURE REPAIR")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Fetch all users and their permissions")
    print("  2. Remove nested 'institutions' from cities")
    print("  3. Update Supabase with cleaned structure")
    print("\n⚠️  This will MODIFY your Supabase data!")
    print("   Make sure you have a backup.\n")
    
    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Fetch all users
    url = f"{supabase_url}/rest/v1/discord_users?select=id,discord_id,username,granular_permissions"
    
    print(f"\n📥 Fetching users...\n")
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    users = response.json()
    print(f"✅ Found {len(users)} users\n")
    
    updated_count = 0
    
    for user in users:
        user_id = user.get('id')
        discord_id = user.get('discord_id')
        username = user.get('username', 'Unknown')
        perms_raw = user.get('granular_permissions')
        
        if not perms_raw:
            print(f"⏭️  {username} - No permissions (skipped)")
            continue
        
        # Parse permissions
        try:
            if isinstance(perms_raw, str):
                perms_dict = json.loads(perms_raw)
            else:
                perms_dict = perms_raw
        except:
            print(f"❌ {username} - Failed to parse JSON (skipped)")
            continue
        
        # Check if has nested institutions
        has_nested = False
        for city_perms in perms_dict.get('cities', {}).values():
            if isinstance(city_perms, dict) and 'institutions' in city_perms:
                has_nested = True
                break
        
        if not has_nested:
            print(f"✅ {username} - Already clean (no nested institutions)")
            continue
        
        # Consolidate
        print(f"🔧 {username} - Cleaning nested institutions...")
        consolidated = consolidate_permissions_structure(perms_dict)
        
        # Update in Supabase
        update_url = f"{supabase_url}/rest/v1/discord_users?id=eq.{user_id}"
        update_data = {
            "granular_permissions": json.dumps(consolidated, ensure_ascii=False)
        }
        
        update_response = requests.patch(
            update_url,
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if update_response.status_code == 204:
            print(f"   ✅ Updated successfully")
            updated_count += 1
        else:
            print(f"   ❌ Failed: {update_response.status_code}")
            print(f"      {update_response.text}")
    
    print(f"\n{'='*80}")
    print(f"✅ REPAIR COMPLETE - Updated {updated_count} users")
    print(f"{'='*80}")
    print("\n💡 Next steps:")
    print("   1. Logout from the app")
    print("   2. Login again")
    print("   3. Check if permissions display correctly now")
    print("   4. You can delete this script after confirming it works")


if __name__ == "__main__":
    repair_permissions_in_supabase()
