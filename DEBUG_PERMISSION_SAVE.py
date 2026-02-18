#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script to test permission saving in Supabase
Identifies issues with permission updates
"""

import json
import requests
import os
from dotenv import load_dotenv
import configparser

# Load config
config = configparser.ConfigParser()
config_file = "supabase_config.ini"

if os.path.exists(config_file):
    config.read(config_file)
    SUPABASE_URL = config.get('supabase', 'url')
    SUPABASE_KEY = config.get('supabase', 'key')
else:
    print("❌ supabase_config.ini not found!")
    exit(1)

print("="*80)
print("🔍 SUPABASE PERMISSION SAVE DEBUG SCRIPT")
print("="*80)
print(f"✓ Supabase URL: {SUPABASE_URL}")
print(f"✓ Supabase Key: {SUPABASE_KEY[:20]}...")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Test 1: Check if discord_users table exists and has correct columns
print("\n" + "="*80)
print("TEST 1: Check discord_users table structure")
print("="*80)

url = f"{SUPABASE_URL}/rest/v1/discord_users?select=id,discord_id,username,granular_permissions&limit=1"
print(f"Query: {url}")

try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f"Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Table exists and is accessible")
        if data:
            print(f"✅ Found {len(data)} user(s)")
            # Check structure of first user
            user = data[0]
            print(f"\nColumns found in discord_users:")
            for key, value in user.items():
                print(f"  • {key}: {type(value).__name__}")
                if key == 'granular_permissions' and value:
                    print(f"    Sample: {str(value)[:100]}...")
        else:
            print(f"⚠️  No users found in table")
    else:
        print(f"❌ Error accessing table: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Find a test user
print("\n" + "="*80)
print("TEST 2: Find a test user")
print("="*80)

url = f"{SUPABASE_URL}/rest/v1/discord_users?select=id,discord_id,username&limit=5"
try:
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        users = response.json()
        if users:
            test_user = users[0]
            print(f"✅ Found test user:")
            print(f"  • ID: {test_user['id']}")
            print(f"  • discord_id: {test_user['discord_id']}")
            print(f"  • username: {test_user['username']}")
            
            # Test 3: Try to update permissions for this user
            print("\n" + "="*80)
            print("TEST 3: Try to SAVE test permissions")
            print("="*80)
            
            test_permissions = {
                "institutions": {
                    "TestCity": {
                        "TestInstitution": {
                            "can_view": True,
                            "can_edit": False,
                            "can_delete": False,
                            "can_add_employee": True,
                            "can_edit_employee": False,
                            "can_delete_employee": False,
                            "can_add_score": True,
                            "can_reset_scores": False,
                            "can_deduct_scores": False
                        }
                    }
                }
            }
            
            print(f"Test permissions to SAVE:")
            print(json.dumps(test_permissions, indent=2))
            
            # Get current permissions first
            get_url = f"{SUPABASE_URL}/rest/v1/discord_users?id=eq.{test_user['id']}&select=granular_permissions"
            print(f"\nGetting current permissions...")
            get_response = requests.get(get_url, headers=headers, timeout=5)
            
            if get_response.status_code == 200:
                current_data = get_response.json()
                if current_data:
                    current_perms = current_data[0].get('granular_permissions', {})
                    if isinstance(current_perms, str):
                        current_perms = json.loads(current_perms)
                    print(f"✅ Current permissions: {json.dumps(current_perms, indent=2)[:200]}...")
            
            # Now try to PATCH
            update_url = f"{SUPABASE_URL}/rest/v1/discord_users?id=eq.{test_user['id']}"
            update_data = {"granular_permissions": json.dumps(test_permissions)}
            
            print(f"\n📤 Sending PATCH request...")
            print(f"URL: {update_url}")
            print(f"Data: {json.dumps(update_data, indent=2)}")
            
            patch_response = requests.patch(
                update_url,
                headers=headers,
                json=update_data,
                timeout=5
            )
            
            print(f"\n📥 PATCH Response Status: {patch_response.status_code}")
            print(f"Response Text: {patch_response.text}")
            
            if patch_response.status_code in [200, 204]:
                print(f"✅ PATCH SUCCESSFUL!")
                
                # Verify the save
                print(f"\nVerifying saved data...")
                verify_response = requests.get(get_url, headers=headers, timeout=5)
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    if verify_data:
                        saved_perms = verify_data[0].get('granular_permissions', {})
                        if isinstance(saved_perms, str):
                            saved_perms = json.loads(saved_perms)
                        print(f"✅ Saved permissions verified:")
                        print(json.dumps(saved_perms, indent=2))
                        
                        # Check if test_permissions are in saved data
                        if 'institutions' in saved_perms and 'TestCity' in saved_perms['institutions']:
                            print(f"\n✅ TEST PERMISSION WAS SAVED CORRECTLY!")
                        else:
                            print(f"\n⚠️  Test permission not found in saved data")
            else:
                print(f"❌ PATCH FAILED!")
                print(f"Possible causes:")
                print(f"  • RLS policy blocking the update")
                print(f"  • Column doesn't exist")
                print(f"  • Invalid data format")
                print(f"  • Authorization header issue")
        else:
            print(f"❌ No users found in table")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check RLS policies
print("\n" + "="*80)
print("TEST 4: Check RLS Policies")
print("="*80)
print("Note: RLS policies are set in Supabase Dashboard")
print("URL: https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/auth/policies")
print("\nCommon issues:")
print("  ❌ RLS policy requires 'authenticated' role")
print("  ❌ Policy has condition that doesn't match current user")
print("  ❌ Policy blocks UPDATE on 'granular_permissions' column")
print("✓ Recommended: Allow authenticated users to update granular_permissions")

print("\n" + "="*80)
print("DIAGNOSIS SUMMARY")
print("="*80)
print("If TEST 3 FAILED:")
print("  1. Check if granular_permissions column exists")
print("  2. Check RLS policies for discord_users table")
print("  3. Verify API key has correct permissions")
print("  4. Check Supabase project quota")
print("\nLogs location: Console output above")
print("="*80 + "\n")
