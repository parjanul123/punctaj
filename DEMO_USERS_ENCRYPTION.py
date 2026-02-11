#!/usr/bin/env python3
"""
Demo: Users & Permissions with Encryption
Shows how new users are added and synced with encryption
"""

import os
import json
from pathlib import Path

def demo_users_with_encryption():
    """Demonstrate users management with encryption"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║        🔐 DEMO: Users & Permissions with Encryption                        ║
║           • Add new users from EXE                                          ║
║           • Automatic sync to Supabase                                      ║
║           • All data encrypted locally                                      ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Check config
    if not os.path.exists("supabase_config.ini"):
        print("⚠️  supabase_config.ini not found!")
        return
    
    # Load config
    import configparser
    config = configparser.ConfigParser()
    config.read("supabase_config.ini")
    
    try:
        url = config['supabase']['url']
        key = config['supabase']['key']
    except:
        print("❌ Invalid config")
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
    
    print(f"\n{'='*80}")
    print(f"1️⃣  ENCRYPTION STATUS")
    print(f"{'='*80}\n")
    
    if manager.encryption_enabled:
        print(f"✅ Encryption: ENABLED")
        print(f"   • Cipher: Fernet (symmetric encryption)")
        print(f"   • Key file: {manager.encryption_key_file}")
        print(f"   • Key format: Base64 encoded")
        print(f"   • Security: All sensitive data encrypted on disk")
    else:
        print(f"⚠️  Encryption: NOT AVAILABLE")
        print(f"   Install cryptography: pip install cryptography")
    
    print(f"\n{'='*80}")
    print(f"2️⃣  CURRENT JSON FILE STRUCTURE")
    print(f"{'='*80}\n")
    
    json_file = Path(data_dir) / "users_permissions.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Users in system: {len(data.get('users', {}))}")
        print(f"Last sync: {data.get('last_sync', 'Never')}")
        
        if data.get('users'):
            print(f"\nCurrent users:")
            for user_id, user in list(data.get('users', {}).items())[:3]:
                print(f"  • {user['username']} (ID: {user_id}, Admin: {user['is_admin']})")
    
    print(f"\n{'='*80}")
    print(f"3️⃣  FEATURES FOR ADDING USERS IN EXE")
    print(f"{'='*80}\n")
    
    print(f"""
✅ Available Methods:

1. add_user_and_sync(discord_id, username, is_admin=False)
   • Adds user to local JSON
   • Immediately syncs to Supabase
   • Returns: True if successful
   
   Usage in EXE:
   if USERS_PERMS_JSON_MANAGER:
       USERS_PERMS_JSON_MANAGER.add_user_and_sync(
           discord_id=123456789,
           username="john_doe#1234",
           is_admin=False
       )

2. UI Dialog: open_add_user_dialog(parent_window, manager)
   • Beautiful tkinter dialog
   • Validates Discord ID
   • Shows info about new user
   • Handles all sync automatically
   
   Usage in EXE:
   from add_user_dialog import open_add_user_dialog
   
   def add_user_from_menu():
       open_add_user_dialog(root, USERS_PERMS_JSON_MANAGER, 
                           on_user_added=refresh_users)

3. Bulk sync after changes:
   manager.sync_bidirectional()
   • Downloads from cloud
   • Merges local changes
   • Uploads to cloud
    """)
    
    print(f"\n{'='*80}")
    print(f"4️⃣  DATA SECURITY")
    print(f"{'='*80}\n")
    
    print(f"""
✅ Encryption Details:

Local JSON File:
  • Location: data/users_permissions.json
  • Encryption: Fernet (AES-128)
  • Key file: data/.encryption_key (600 permissions)
  • Encrypted fields: Sensitive data marked with __encrypted__

Supabase Storage:
  • Granular Permissions: Stored as JSON in discord_users table
  • Transport: HTTPS encrypted
  • Server-side: Encrypted at rest (Supabase default)
  • Access: Requires API key

Multi-Device:
  • Each device has own .encryption_key
  • Cloud (Supabase) is source of truth
  • Local JSON is encrypted cache
  • Sync ensures consistency across devices
    """)
    
    print(f"\n{'='*80}")
    print(f"5️⃣  EXAMPLE WORKFLOW IN EXE")
    print(f"{'='*80}\n")
    
    print(f"""
Admin adds new user from EXE:

1. Admin clicks: "Add User" button
2. Dialog appears (from add_user_dialog.py)
3. Admin enters:
   • Discord ID: 987654321
   • Username: alice_smith#5678
   • Admin: No
4. Clicks: "Add User"
5. System:
   ✅ Creates in local JSON (encrypted)
   ✅ Immediately syncs to Supabase
   ✅ User gets default permissions
   ✅ Shows success dialog
6. Changes visible:
   ✅ Locally: data/users_permissions.json (encrypted)
   ✅ Cloud: Supabase discord_users table
   ✅ Other devices: Sync on next startup

Real-time Sync:
  • Changes to user appear instantly
  • Multiple devices can work simultaneously
  • Cloud resolves conflicts (last update wins)
    """)
    
    print(f"\n{'='*80}")
    print(f"6️⃣  PERMISSIONS FOR NEW USERS")
    print(f"{'='*80}\n")
    
    print(f"""
Default Permissions Template (new users get these):

{{
  "cities": {{}},
  "institutions": {{}},
  "employees": {{}},
  "cloud": {{
    "upload": false,
    "download": false
  }},
  "admin": {{
    "view_logs": false,
    "manage_users": false,
    "manage_institutions": false,
    "manage_employees": false
  }}
}}

After adding user:
  • Admin can modify permissions via UI
  • Changes sync to Supabase
  • Changes apply to local JSON
  • All encrypted and secured
    """)
    
    print(f"\n{'='*80}")
    print(f"✅ DEMO COMPLETE")
    print(f"{'='*80}\n")
    
    print(f"""
To integrate in punctaj.py:

1. Import:
   from users_permissions_json_manager import UsersPermissionsJsonManager
   from add_user_dialog import open_add_user_dialog

2. Initialize (already done):
   USERS_PERMS_JSON_MANAGER = UsersPermissionsJsonManager(...)

3. Add menu item:
   menubar.add_command("Add User", 
       lambda: open_add_user_dialog(root, USERS_PERMS_JSON_MANAGER))

4. Use in checks:
   if USERS_PERMS_JSON_MANAGER:
       perms = USERS_PERMS_JSON_MANAGER.get_user_permissions(discord_id)
    """)

if __name__ == "__main__":
    demo_users_with_encryption()
