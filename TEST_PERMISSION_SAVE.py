#!/usr/bin/env python3
"""
DEBUG: Test Permission Saving to Database
This script tests if permissions are being saved correctly to Supabase
"""

import sys
import os
import json

# Initialize Supabase
from supabase_sync import SupabaseSync
from admin_permissions import PermissionManager

config_paths = [
    os.path.join(os.path.dirname(__file__), "supabase_config.ini"),
    "supabase_config.ini",
]

config_found = None
for path in config_paths:
    if os.path.exists(path):
        config_found = path
        break

if not config_found:
    print("❌ supabase_config.ini not found!")
    sys.exit(1)

print("=" * 80)
print("🔍 TEST PERMISSION SAVING")
print("=" * 80)
print()

supabase = SupabaseSync(config_found)
perm_manager = PermissionManager(supabase)

# Test with parjanu (703316932232872016)
discord_id = "703316932232872016"
username = "parjanu"

print(f"User: {username} (ID: {discord_id})")
print()

# Step 1: Get current permissions
print("-" * 80)
print("1️⃣ Fetching CURRENT permissions...")
print("-" * 80)

current_perms = perm_manager.get_user_institution_permissions(discord_id)
print(f"Current permissions: {json.dumps(current_perms, indent=2)}")
print()

# Step 2: Try to save test permissions
print("-" * 80)
print("2️⃣ Saving TEST permissions...")
print("-" * 80)

test_perms = {
    "BlackWater": {
        "Politie": {
            "can_view": True,
            "can_edit": True,
            "can_delete": False,
            "can_add_employee": True,
            "can_delete_employee": False,
            "can_add_score": True,
            "can_reset_scores": False,
            "can_deduct_scores": False
        }
    }
}

print(f"Test permissions to save: {json.dumps(test_perms, indent=2)}")
print()

result = perm_manager.save_user_institution_permissions(discord_id, test_perms)
print(f"Save result: {result}")
print()

# Step 3: Verify they were saved
print("-" * 80)
print("3️⃣ Verifying SAVED permissions...")
print("-" * 80)

import time
time.sleep(1)  # Wait for database to update

saved_perms = perm_manager.get_user_institution_permissions(discord_id)
print(f"Saved permissions: {json.dumps(saved_perms, indent=2)}")
print()

# Step 4: Check if BlackWater/Politie permissions were saved
print("-" * 80)
print("4️⃣ Checking specific permission...")
print("-" * 80)

if "BlackWater" in saved_perms and "Politie" in saved_perms.get("BlackWater", {}):
    politie_perms = saved_perms["BlackWater"]["Politie"]
    print(f"✅ BlackWater/Politie permissions found:")
    print(json.dumps(politie_perms, indent=2))
    
    # Check if our test values are there
    if politie_perms.get("can_add_employee") == True:
        print("✅ can_add_employee=True (SAVED CORRECTLY)")
    else:
        print(f"❌ can_add_employee={politie_perms.get('can_add_employee')} (WRONG VALUE)")
else:
    print("❌ BlackWater/Politie permissions NOT found in database!")

print()
print("=" * 80)
print("✅ Test complete!")
print("=" * 80)
