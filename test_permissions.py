# -*- coding: utf-8 -*-
"""Test the permission system"""

import sys
import json
import os

# Add project dir to path
sys.path.insert(0, 'd:\\punctaj')

# Test Discord Auth role-based permissions
from discord_auth import DiscordAuth

print("Testing Permission System...")
print("=" * 50)

# Create a mock Discord auth instance
auth = DiscordAuth("test_id", "test_secret")

# Mock user info
auth.user_info = {
    "id": "123456789",
    "username": "testuser",
    "email": "test@example.com"
}

# Test with viewer role
print("\n1. Testing VIEWER role (read-only)")
print("-" * 50)
auth.user_role = "viewer"

print(f"is_admin(): {auth.is_admin()}")  # Should be False
print(f"can_view(): {auth.can_view()}")  # Should be True
print(f"can_perform_action('add_employee'): {auth.can_perform_action('add_employee')}")  # Should be False
print(f"get_user_role(): {auth.get_user_role()}")  # Should be 'viewer'

# Test with user role
print("\n2. Testing USER role (read + write)")
print("-" * 50)
auth.user_role = "user"

print(f"is_admin(): {auth.is_admin()}")  # Should be False
print(f"can_view(): {auth.can_view()}")  # Should be True
print(f"can_perform_action('add_employee'): {auth.can_perform_action('add_employee')}")  # Should be True
print(f"can_edit_city_granular('TestCity'): {auth.can_edit_city_granular('TestCity')}")  # Should be True
print(f"get_user_role(): {auth.get_user_role()}")  # Should be 'user'

# Test with admin role
print("\n3. Testing ADMIN role (full access)")
print("-" * 50)
auth.user_role = "admin"

print(f"is_admin(): {auth.is_admin()}")  # Should be True
print(f"can_view(): {auth.can_view()}")  # Should be True
print(f"can_perform_action('add_employee'): {auth.can_perform_action('add_employee')}")  # Should be True
print(f"can_manage_institution_employees('City', 'Inst'): {auth.can_manage_institution_employees('City', 'Inst')}")  # Should be True
print(f"get_user_role(): {auth.get_user_role()}")  # Should be 'admin'

print("\n" + "=" * 50)
print("All permission tests completed!")
