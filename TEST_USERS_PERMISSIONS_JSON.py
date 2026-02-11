#!/usr/bin/env python3
"""
Test Users & Permissions JSON Manager
Demonstrates sync with Supabase
"""

import os
import sys
import json
from pathlib import Path

def test_users_permissions():
    """Test the users permissions JSON manager"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║   🧪 TEST: Users & Permissions JSON Manager                        ║
║      Syncs with Supabase discord_users table                       ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    # Check if config exists
    if not os.path.exists("supabase_config.ini"):
        print("⚠️  supabase_config.ini not found!")
        print("   Create it with [supabase] section containing url and key")
        return
    
    # Load config
    import configparser
    config = configparser.ConfigParser()
    config.read("supabase_config.ini")
    
    try:
        url = config['supabase']['url']
        key = config['supabase']['key']
    except:
        print("❌ Invalid config format")
        return
    
    # Import manager
    try:
        from users_permissions_json_manager import UsersPermissionsJsonManager
    except ImportError as e:
        print(f"❌ Cannot import manager: {e}")
        return
    
    # Create manager
    data_dir = "data"
    manager = UsersPermissionsJsonManager(url, key, data_dir)
    manager.ensure_json_exists()
    
    print(f"\n{'='*70}")
    print(f"1️⃣  LOCAL JSON FILE CHECK")
    print(f"{'='*70}\n")
    
    json_file = Path(data_dir) / "users_permissions.json"
    if json_file.exists():
        print(f"✅ File exists: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📊 Current data:")
        print(f"   • Total users: {len(data.get('users', {}))}")
        print(f"   • Last sync: {data.get('last_sync', 'Never')}")
        print(f"   • Sync status: {data.get('sync_status', 'Unknown')}")
    else:
        print(f"❌ File not found: {json_file}")
        print(f"   Creating new file...")
        manager.ensure_json_exists()
    
    print(f"\n{'='*70}")
    print(f"2️⃣  DOWNLOAD FROM SUPABASE")
    print(f"{'='*70}\n")
    
    success = manager.download_from_cloud()
    
    if success:
        print(f"\n✅ Download successful!")
        
        # Show stats
        stats = manager.get_stats()
        print(f"\n📊 Statistics:")
        for key, value in stats.items():
            print(f"   • {key}: {value}")
        
        # Show sample users
        users = manager.list_users()
        if users:
            print(f"\n👥 Sample users:")
            for user in users[:5]:
                perms_count = len(user.get('permissions', {}))
                print(f"   • {user['username']} (ID: {user['discord_id']}, Admin: {user['is_admin']}, Perms: {perms_count})")
            
            if len(users) > 5:
                print(f"   ... and {len(users) - 5} more")
    else:
        print(f"⚠️  Download failed")
        print(f"   Check Supabase connection and config")
    
    print(f"\n{'='*70}")
    print(f"3️⃣  JSON FILE STRUCTURE")
    print(f"{'='*70}\n")
    
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"File structure:")
        print(f"""
{
  "users": {
    "discord_id_string": {
      "discord_id": number,
      "username": "string",
      "is_admin": boolean,
      "permissions": {
        "cities": {},
        "institutions": {},
        "employees": {},
        "cloud": {
          "upload": boolean,
          "download": boolean
        },
        "admin": {
          "view_logs": boolean,
          "manage_users": boolean,
          ...
        }
      },
      "created_at": "ISO datetime",
      "updated_at": "ISO datetime"
    }
  },
  "last_sync": "ISO datetime",
  "sync_status": "cloud_downloaded|cloud_uploaded",
  "user_count": number
}
        """)
    
    print(f"\n{'='*70}")
    print(f"4️⃣  AVAILABLE OPERATIONS")
    print(f"{'='*70}\n")
    
    print(f"""
✅ Operations available:

manager.download_from_cloud()
  → Downloads users & permissions from Supabase
  → Saves to data/users_permissions.json

manager.upload_to_cloud()
  → Uploads permissions from JSON to Supabase
  → Updates discord_users table

manager.sync_bidirectional()
  → Download → Merge → Upload
  → Full synchronization cycle

manager.get_user_permissions(discord_id)
  → Get permissions dict for specific user

manager.set_user_permissions(discord_id, permissions)
  → Update permissions for user in JSON

manager.add_user(discord_id, username, is_admin)
  → Add new user to JSON

manager.list_users()
  → Get all users from JSON

manager.get_stats()
  → Get statistics about users
    """)
    
    print(f"\n{'='*70}")
    print(f"5️⃣  INTEGRATION WITH APPLICATION")
    print(f"{'='*70}\n")
    
    print(f"""
✅ In punctaj.py:

• On startup: USERS_PERMS_JSON_MANAGER is initialized
• Location: data/users_permissions.json
• Auto-syncs with Supabase discord_users table

Usage in app:
  
  # Get permissions for user
  if USERS_PERMS_JSON_MANAGER:
    perms = USERS_PERMS_JSON_MANAGER.get_user_permissions(discord_id)
    
    if perms.get('admin', {}).get('manage_users'):
      # User can manage users
      
  # Sync on demand
  USERS_PERMS_JSON_MANAGER.sync_bidirectional()
    """)
    
    print(f"\n{'='*70}")
    print(f"✅ Test complete!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    test_users_permissions()
