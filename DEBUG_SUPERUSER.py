#!/usr/bin/env python3
"""
Debug superuser status reading from Supabase
"""
import supabase_sync
import requests

print("=" * 70)
print("           DEBUG: READING SUPERUSER STATUS FROM SUPABASE")
print("=" * 70)

try:
    sync = supabase_sync.SupabaseSync()
    print("✓ Supabase connected\n")
    
    # Check user "parjanu" 
    discord_id = "703316932232872016"
    
    # Query via API
    url = f"{sync.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=*"
    print(f"Query URL: {url}\n")
    
    response = requests.get(url, headers=sync.headers, timeout=5)
    
    if response.status_code == 200:
        users = response.json()
        
        if users:
            user = users[0]
            print(f"✓ User found: {user.get('username')}\n")
            print("Fields in database:")
            for key, value in user.items():
                print(f"  {key}: {value}")
        else:
            print("⚠ User not found")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
