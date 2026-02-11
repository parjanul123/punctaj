#!/usr/bin/env python3
"""
DEBUG SCRIPT - Check superuser status in Supabase
Tests if is_superuser value is being returned correctly from the database
"""

import requests
import json
from supabase_sync import SupabaseSync
import configparser
import os

def test_superuser_lookup():
    """Test superuser lookup from Supabase"""
    
    print("=" * 80)
    print("🔍 DEBUG: Testing Superuser Lookup in Supabase")
    print("=" * 80)
    
    # Initialize Supabase
    config_paths = [
        os.path.join(os.path.dirname(__file__), "supabase_config.ini"),
        "supabase_config.ini"
    ]
    
    config_found = None
    for path in config_paths:
        if os.path.exists(path):
            config_found = path
            print(f"✅ Found config: {path}")
            break
    
    if not config_found:
        print("❌ supabase_config.ini not found!")
        return
    
    try:
        supabase = SupabaseSync(config_found)
        print(f"✅ Supabase initialized: {supabase.url}")
        print()
        
        # Test: Get ALL discord users and their superuser status
        print("-" * 80)
        print("📋 ALL DISCORD USERS IN DATABASE:")
        print("-" * 80)
        
        headers = {
            "apikey": supabase.key,
            "Authorization": f"Bearer {supabase.key}",
            "Content-Type": "application/json"
        }
        
        # Get all users
        url = f"{supabase.url}/rest/v1/discord_users?select=discord_id,discord_username,is_superuser,is_admin,can_view"
        print(f"Query: {url}")
        print()
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Users: {len(data)}")
            print()
            
            for user in data:
                discord_id = user.get('discord_id', 'N/A')
                username = user.get('discord_username', 'Unknown')
                is_superuser = user.get('is_superuser', False)
                is_admin = user.get('is_admin', False)
                can_view = user.get('can_view', False)
                
                role = "👑 SUPERUSER" if is_superuser else ("🛡️  ADMIN" if is_admin else ("👤 USER" if can_view else "👁️  VIEWER"))
                
                print(f"  ID: {discord_id:>20} | Username: {username:>20} | Role: {role} | is_superuser={is_superuser} (type: {type(is_superuser).__name__})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        print()
        print("-" * 80)
        print("🔎 TEST SPECIFIC DISCORD ID LOOKUP:")
        print("-" * 80)
        print()
        
        # Ask user for their Discord ID
        discord_id = input("Enter your Discord ID (or press Enter to skip): ").strip()
        
        if discord_id:
            test_url = f"{supabase.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=discord_id,discord_username,is_superuser,is_admin,can_view,can_edit,can_delete"
            print(f"Query: {test_url}")
            print()
            
            response = requests.get(test_url, headers=headers, timeout=10)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    user_data = data[0]
                    print("✅ User Found!")
                    print()
                    for key, value in user_data.items():
                        if isinstance(value, bool):
                            print(f"  {key:25} = {str(value):20} (type: {type(value).__name__})")
                        else:
                            print(f"  {key:25} = {str(value):20} (type: {type(value).__name__})")
                    
                    # Test the actual parsing like discord_auth.py does
                    print()
                    print("=" * 80)
                    print("🧪 TEST PARSING (like discord_auth.py does):")
                    print("=" * 80)
                    
                    is_superuser = user_data.get('is_superuser', False)
                    is_admin = user_data.get('is_admin', False)
                    
                    print(f"is_superuser = user_data.get('is_superuser', False)")
                    print(f"  Result: {is_superuser} (type: {type(is_superuser).__name__})")
                    print(f"  Bool value: {bool(is_superuser)}")
                    print(f"  if is_superuser: {True if is_superuser else False}")
                    print()
                    
                    print(f"is_admin = user_data.get('is_admin', False)")
                    print(f"  Result: {is_admin} (type: {type(is_admin).__name__})")
                    print(f"  Bool value: {bool(is_admin)}")
                    print()
                    
                    # Test role assignment
                    if is_superuser:
                        role = "SUPERUSER"
                    elif is_admin:
                        role = "ADMIN"
                    else:
                        can_view = user_data.get('can_view', False)
                        if can_view:
                            role = "USER"
                        else:
                            role = "VIEWER"
                    
                    print(f"Final Role: {role}")
                    
                else:
                    print("❌ User not found in database!")
        
        print()
        print("=" * 80)
        print("✅ Debug test complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_superuser_lookup()
