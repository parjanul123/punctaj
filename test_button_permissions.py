#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify button permission enforcement
"""
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Mock DISCORD_AUTH and INSTITUTION_PERM_MANAGER
class MockDiscordAuth:
    def __init__(self):
        self._is_superuser = False
    
    def is_superuser(self):
        return self._is_superuser
    
    def get_discord_id(self):
        return "test_user_123"

class MockInstitutionPermissionManager:
    def __init__(self):
        self.permissions = {
            "test_user_123": {
                "institutions": {
                    "BlackWater": {
                        "Politie": {
                            "can_view": True,
                            "can_edit": True,
                            "can_delete": False
                        }
                    }
                }
            }
        }
    
    def check_user_institution_permission(self, discord_id, city, institution, permission_type):
        if discord_id not in self.permissions:
            return False
        
        user_perms = self.permissions[discord_id]
        if "institutions" not in user_perms:
            return False
        
        if city not in user_perms["institutions"]:
            return False
        
        if institution not in user_perms["institutions"][city]:
            return False
        
        return user_perms["institutions"][city][institution].get(permission_type, False)

# Simulate the function
DISCORD_AUTH = MockDiscordAuth()
INSTITUTION_PERM_MANAGER = MockInstitutionPermissionManager()

def check_institution_permission(city, institution, permission_type):
    """
    Verifică dacă utilizatorul curent are permisiune pentru o acțiune specifică pe o instituție
    """
    # Superuserii au acces la toate
    if DISCORD_AUTH and DISCORD_AUTH.is_superuser():
        return True
    
    # Verifică permisiunile granulare
    if INSTITUTION_PERM_MANAGER and DISCORD_AUTH:
        discord_id = DISCORD_AUTH.get_discord_id()
        if discord_id:
            return INSTITUTION_PERM_MANAGER.check_user_institution_permission(
                discord_id,
                city,
                institution,
                permission_type
            )
    
    # Default: acces dacă nu e configurat sistemul de permisiuni
    return True

# Tests
print("=" * 60)
print("TEST 1: Check if user can view Politie in BlackWater")
print("=" * 60)
result = check_institution_permission("BlackWater", "Politie", "can_view")
print(f"Result: {result}")
assert result == True, "Should have can_view permission"
print("✓ PASS\n")

print("=" * 60)
print("TEST 2: Check if user can edit Politie in BlackWater")
print("=" * 60)
result = check_institution_permission("BlackWater", "Politie", "can_edit")
print(f"Result: {result}")
assert result == True, "Should have can_edit permission"
print("✓ PASS\n")

print("=" * 60)
print("TEST 3: Check if user can delete Politie in BlackWater (SHOULD FAIL)")
print("=" * 60)
result = check_institution_permission("BlackWater", "Politie", "can_delete")
print(f"Result: {result}")
assert result == False, "Should NOT have can_delete permission"
print("✓ PASS\n")

print("=" * 60)
print("TEST 4: Check if superuser can do everything")
print("=" * 60)
DISCORD_AUTH._is_superuser = True
result = check_institution_permission("BlackWater", "Politie", "can_delete")
print(f"Result: {result}")
assert result == True, "Superuser should have all permissions"
print("✓ PASS\n")

print("=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
