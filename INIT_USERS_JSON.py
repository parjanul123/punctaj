#!/usr/bin/env python3
"""
Initialize Users & Permissions JSON
Creates users_permissions.json and syncs from Supabase
"""

import os
import sys

def init_users_json():
    """Initialize the users_permissions.json file"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║       🔧 INITIALIZE Users Permissions JSON                         ║
║         Create and sync users_permissions.json                     ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    # Check config
    if not os.path.exists("supabase_config.ini"):
        print("⚠️  supabase_config.ini not found!")
        print("   Create it first with Supabase credentials")
        return False
    
    # Load config
    import configparser
    config = configparser.ConfigParser()
    config.read("supabase_config.ini")
    
    try:
        url = config['supabase']['url']
        key = config['supabase']['key']
    except:
        print("❌ Invalid config format")
        return False
    
    # Import manager
    try:
        from users_permissions_json_manager import UsersPermissionsJsonManager
    except ImportError as e:
        print(f"❌ Cannot import manager: {e}")
        return False
    
    print(f"\n{'='*70}")
    print(f"1️⃣  INITIALIZING MANAGER")
    print(f"{'='*70}\n")
    
    # Create manager
    data_dir = "data"
    manager = UsersPermissionsJsonManager(url, key, data_dir)
    
    print(f"\n{'='*70}")
    print(f"2️⃣  CREATING JSON FILE")
    print(f"{'='*70}\n")
    
    # Ensure JSON exists
    manager.ensure_json_exists()
    
    print(f"\n{'='*70}")
    print(f"3️⃣  DOWNLOADING USERS FROM SUPABASE")
    print(f"{'='*70}\n")
    
    # Download from cloud
    success = manager.download_from_cloud()
    
    if success:
        print(f"\n{'='*70}")
        print(f"4️⃣  STATISTICS")
        print(f"{'='*70}\n")
        
        # Show stats
        stats = manager.get_stats()
        print(f"Total users: {stats.get('total_users', 0)}")
        print(f"Admin users: {stats.get('admin_users', 0)}")
        print(f"Regular users: {stats.get('regular_users', 0)}")
        print(f"Last sync: {stats.get('last_sync', 'Never')}")
        print(f"Sync status: {stats.get('sync_status', 'Unknown')}")
        
        # Show users
        users = manager.list_users()
        if users:
            print(f"\n👥 Users loaded:")
            for user in users[:10]:
                print(f"   • {user['username']} (ID: {user['discord_id']}, Admin: {user['is_admin']})")
            
            if len(users) > 10:
                print(f"   ... and {len(users) - 10} more")
        
        print(f"\n{'='*70}")
        print(f"✅ INITIALIZATION COMPLETE!")
        print(f"{'='*70}\n")
        
        print(f"""
📂 File created:
   Location: data/users_permissions.json
   Encryption: ENABLED (data/.encryption_key)
   Users: {stats.get('total_users', 0)}
   Status: Ready for use
        """)
        
        return True
    else:
        print(f"\n⚠️  Download failed")
        print(f"   Checking connection...")
        
        # Try to diagnose
        try:
            import requests
            response = requests.get(f"{url}/rest/v1/discord_users", 
                                   headers={"apikey": key},
                                   timeout=5)
            if response.status_code == 200:
                print(f"✅ Supabase connection OK")
                print(f"   Try again: py INIT_USERS_JSON.py")
            else:
                print(f"❌ Supabase error: {response.status_code}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        return False

if __name__ == "__main__":
    success = init_users_json()
    sys.exit(0 if success else 1)
