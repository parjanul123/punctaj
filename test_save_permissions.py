#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for saving permissions"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from supabase_sync import SupabaseSync
from admin_permissions import InstitutionPermissionManager

# Initialize Supabase
try:
    supabase = SupabaseSync('supabase_config.ini')
    print(f"✅ Supabase initialized: {supabase.url}")
except Exception as e:
    print(f"❌ Error initializing Supabase: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Initialize InstitutionPermissionManager
try:
    manager = InstitutionPermissionManager(supabase, 'data')
    print(f"✅ InstitutionPermissionManager initialized")
except Exception as e:
    print(f"❌ Error initializing manager: {e}")
    sys.exit(1)

# Test getting all institutions
try:
    all_institutions = manager.get_all_institutions_by_city()
    print(f"✅ All institutions: {all_institutions}")
except Exception as e:
    print(f"❌ Error getting institutions: {e}")
    sys.exit(1)

# Test permissions for a user
discord_id = "1449374935196893197"  # paulstanciu6_48913

# Get current permissions
try:
    current_perms = manager.get_user_institution_permissions(discord_id)
    print(f"✅ Current permissions for {discord_id}: {current_perms}")
except Exception as e:
    print(f"❌ Error getting current permissions: {e}")
    sys.exit(1)

# Create test permissions
test_perms = {
    'BlackWater': {
        'Politie': {
            'can_view': True,
            'can_edit': True,
            'can_delete': False
        }
    },
    'Saint_Denis': {
        'Politie': {
            'can_view': False,
            'can_edit': False,
            'can_delete': False
        }
    }
}

print(f"\n📝 Test permissions to save:")
print(json.dumps(test_perms, indent=2))

# Try to save
print(f"\n💾 Attempting to save permissions...")
try:
    result = manager.save_user_institution_permissions(discord_id, test_perms)
    if result:
        print(f"✅ Permissions saved successfully!")
    else:
        print(f"❌ Failed to save permissions (returned False)")
except Exception as e:
    print(f"❌ Error saving permissions: {e}")
    import traceback
    traceback.print_exc()
