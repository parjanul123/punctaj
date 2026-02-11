#!/usr/bin/env python3
"""
Check and Set Superuser Status in Supabase
"""
import supabase_sync
import requests
import json

print("=" * 70)
print("           CHECKING DISCORD USERS IN SUPABASE")
print("=" * 70)

try:
    sync = supabase_sync.SupabaseSync()
    print("✓ Supabase connected\n")
    
    # Get all users via API
    url = f"{sync.url}/rest/v1/discord_users?select=id,discord_id,username,is_superuser,is_admin"
    response = requests.get(url, headers=sync.headers, timeout=5)
    
    if response.status_code == 200:
        users = response.json()
        
        if users:
            print(f"📊 Found {len(users)} users:\n")
            for i, user in enumerate(users, 1):
                print(f"  [{i}] Username: {user.get('username', 'N/A')}")
                print(f"      Discord ID: {user.get('discord_id', 'N/A')}")
                print(f"      DB ID: {user.get('id', 'N/A')}")
                print(f"      is_superuser: {user.get('is_superuser', False)}")
                print(f"      is_admin: {user.get('is_admin', False)}")
                print()
            
            # Ask which user to make superuser
            print("\n" + "=" * 70)
            print("TO SET A USER AS SUPERUSER:")
            print("=" * 70)
            
            choice = input("\nEnter the number of user to make superuser (1-{}): ".format(len(users)))
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(users):
                    user_id = users[idx]['id']
                    username = users[idx]['username']
                    
                    # Update to superuser
                    update_url = f"{sync.url}/rest/v1/discord_users?id=eq.{user_id}"
                    update_data = {
                        'is_superuser': True,
                        'is_admin': True
                    }
                    
                    update_response = requests.patch(update_url, headers=sync.headers, json=update_data, timeout=5)
                    
                    if update_response.status_code in [200, 204]:
                        print(f"\n✅ SUCCESS!")
                        print(f"   User '{username}' is now SUPERUSER!")
                        print(f"   is_superuser = True")
                        print(f"   is_admin = True")
                    else:
                        print(f"\n❌ Update failed: {update_response.status_code}")
                        print(update_response.text)
                else:
                    print("Invalid choice")
            except ValueError:
                print("Invalid input")
        else:
            print("⚠️ No users found in discord_users table")
            print("   User need to login with Discord first!")
    else:
        print(f"❌ Error fetching users: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
