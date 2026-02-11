#!/usr/bin/env python3
"""
Verify users_permissions.json is properly initialized
"""

import os
import json
from pathlib import Path

print("""
╔═══════════════════════════════════════════════════════════════════════╗
║               ✅ VERIFY Users Permissions JSON System                 ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

# Check files
data_dir = Path("data")
json_file = data_dir / "users_permissions.json"
key_file = data_dir / ".encryption_key"

print("📁 Checking files...")
print(f"   • users_permissions.json: {'✅' if json_file.exists() else '❌'}")
print(f"   • .encryption_key: {'✅' if key_file.exists() else '❌'}")

if not json_file.exists():
    print("\n❌ users_permissions.json not found!")
    exit(1)

# Read JSON
print("\n📄 Reading JSON file...")
try:
    with open(json_file) as f:
        data = json.load(f)
    print("   ✅ JSON is valid")
except json.JSONDecodeError as e:
    print(f"   ❌ Invalid JSON: {e}")
    exit(1)

# Check structure
print("\n🔍 Checking structure...")
required_keys = ["users", "last_sync", "sync_status", "user_count", "version"]
for key in required_keys:
    exists = key in data
    print(f"   • {key}: {'✅' if exists else '❌'}")

# Show statistics
print("\n📊 Statistics:")
print(f"   • Total users: {data.get('user_count', 0)}")
print(f"   • Last sync: {data.get('last_sync', 'Never')}")
print(f"   • Sync status: {data.get('sync_status', 'Unknown')}")
print(f"   • Version: {data.get('version', 'Unknown')}")

# List users
users = data.get("users", {})
print(f"\n👥 Users ({len(users)}):")
for user_id, user_data in users.items():
    username = user_data.get("username", "Unknown")
    is_admin = user_data.get("is_admin", False)
    admin_badge = "👑 ADMIN" if is_admin else ""
    print(f"   • {username} (ID: {user_id}) {admin_badge}")

# Check encryption
print("\n🔐 Encryption:")
if key_file.exists():
    size = key_file.stat().st_size
    print(f"   ✅ Key file exists ({size} bytes)")
    
    # Check file permissions (on Unix-like systems)
    try:
        import stat
        mode = key_file.stat().st_mode
        perms = oct(stat.S_IMODE(mode))
        print(f"   • Permissions: {perms}")
    except:
        pass
else:
    print("   ❌ Key file not found")

print("\n✅ Verification complete!")
print(f"\nThe system is ready to use:")
print(f"  • JSON file: {json_file.absolute()}")
print(f"  • Encryption key: {key_file.absolute()}")
print(f"  • Users loaded: {len(users)}")
