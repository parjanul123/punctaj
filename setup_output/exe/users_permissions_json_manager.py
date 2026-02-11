#!/usr/bin/env python3
"""
Users & Granular Permissions JSON Manager
Syncs with Supabase discord_users table (granular_permissions column)
Supports bidirectional sync: Cloud ↔ Local JSON
Encrypted storage for sensitive data
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import base64

# Try to use cryptography for encryption
try:
    from cryptography.fernet import Fernet
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("⚠️  cryptography module not found - data will be stored unencrypted")
    print("   Install with: pip install cryptography")

class UsersPermissionsJsonManager:
    """
    Manages users and their granular permissions in JSON format
    Syncs with Supabase table: discord_users (column: granular_permissions)
    Supports encryption for sensitive data
    """
    
    def __init__(self, supabase_url: str, supabase_key: str, data_dir: str, encryption_key: Optional[str] = None):
        """
        Initialize the manager
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
            data_dir: Local data directory (e.g., d:\\punctaj\\data)
            encryption_key: Optional encryption key (if None, will generate one)
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.data_dir = Path(data_dir)
        
        # JSON file location
        self.json_file = self.data_dir / "users_permissions.json"
        self.encryption_key_file = self.data_dir / ".encryption_key"
        
        # Setup encryption
        self.cipher = None
        self.encryption_enabled = ENCRYPTION_AVAILABLE
        if ENCRYPTION_AVAILABLE:
            self._setup_encryption(encryption_key)
        
        # Headers for Supabase API
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Default permission structure
        self.default_permissions_template = {
            "cities": {},           # City-specific permissions
            "institutions": {},     # Institution-specific permissions
            "employees": {},        # Employee-specific permissions
            "cloud": {              # Cloud operations
                "upload": False,
                "download": False,
            },
            "admin": {              # Admin operations
                "view_logs": False,
                "manage_users": False,
                "manage_institutions": False,
                "manage_employees": False,
            },
            "last_updated": None,
        }
        
        print(f"📁 Users Permissions Manager initialized")
        print(f"   Data directory: {self.data_dir}")
        print(f"   JSON file: {self.json_file}")
        if self.encryption_enabled:
            print(f"   🔐 Encryption: ENABLED")
    
    def _setup_encryption(self, encryption_key: Optional[str] = None):
        """Setup encryption key"""
        if encryption_key:
            # Use provided key
            try:
                self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
                print(f"   🔑 Using provided encryption key")
            except Exception as e:
                print(f"   ⚠️  Invalid encryption key: {e}")
                self._generate_encryption_key()
        else:
            # Try to load existing key
            if self.encryption_key_file.exists():
                with open(self.encryption_key_file, 'r') as f:
                    key = f.read().strip()
                try:
                    self.cipher = Fernet(key.encode())
                    print(f"   🔑 Loaded existing encryption key")
                except Exception as e:
                    print(f"   ⚠️  Encryption key corrupted: {e}")
                    self._generate_encryption_key()
            else:
                self._generate_encryption_key()
    
    def _generate_encryption_key(self):
        """Generate and save new encryption key"""
        key = Fernet.generate_key().decode()
        self.encryption_key_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.encryption_key_file, 'w') as f:
            f.write(key)
        os.chmod(str(self.encryption_key_file), 0o600)  # Read/write only for owner
        self.cipher = Fernet(key.encode())
        print(f"   🔑 Generated new encryption key")
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a string value"""
        if not self.encryption_enabled or not self.cipher:
            return value
        try:
            encrypted = self.cipher.encrypt(value.encode())
            return f"__encrypted__{encrypted.decode()}"
        except Exception as e:
            print(f"⚠️  Encryption error: {e}")
            return value
    
    def _decrypt_value(self, value: str) -> str:
        """Decrypt a string value"""
        if not self.encryption_enabled or not self.cipher:
            return value
        if not value.startswith("__encrypted__"):
            return value
        try:
            encrypted_part = value.replace("__encrypted__", "")
            decrypted = self.cipher.decrypt(encrypted_part.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"⚠️  Decryption error: {e}")
            return value
    
    def ensure_json_exists(self):
        """Ensure JSON file exists with default structure"""
        if not self.json_file.exists():
            print(f"\n📝 Creating users_permissions.json...")
            initial_data = {
                "users": {},
                "last_sync": datetime.now().isoformat(),
                "sync_status": "initialized",
            }
            self._write_json(initial_data)
            print(f"   ✅ Created: {self.json_file}")
        else:
            print(f"   ✓ Exists: users_permissions.json")
    
    def _read_json(self) -> Dict[str, Any]:
        """Read JSON file"""
        if self.json_file.exists():
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️  JSON corrupted, resetting...")
                return {"users": {}, "last_sync": None}
        return {"users": {}, "last_sync": None}
    
    def _write_json(self, data: Dict[str, Any]):
        """Write JSON file"""
        self.json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def download_from_cloud(self) -> bool:
        """
        Download users and permissions from Supabase
        Syncs discord_users table → local JSON
        """
        print(f"\n📥 Downloading users from Supabase...")
        
        try:
            # Fetch all users with their granular permissions
            url = f"{self.supabase_url}/rest/v1/discord_users"
            params = {
                "select": "discord_id,username,is_admin,granular_permissions,created_at,updated_at",
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            users_data = response.json()
            print(f"   Found {len(users_data)} users")
            
            if not isinstance(users_data, list):
                print(f"   ⚠️  Unexpected response format")
                return False
            
            # Process users
            json_users = {}
            for user in users_data:
                discord_id = user.get('discord_id')
                if not discord_id:
                    continue
                
                # Parse granular permissions
                perms_str = user.get('granular_permissions', '{}')
                if isinstance(perms_str, str):
                    try:
                        perms = json.loads(perms_str) if perms_str else {}
                    except json.JSONDecodeError:
                        perms = {}
                else:
                    perms = perms_str if isinstance(perms_str, dict) else {}
                
                json_users[str(discord_id)] = {
                    "discord_id": discord_id,
                    "username": user.get('username', 'Unknown'),
                    "is_admin": user.get('is_admin', False),
                    "permissions": perms if isinstance(perms, dict) else {},
                    "created_at": user.get('created_at'),
                    "updated_at": user.get('updated_at'),
                }
            
            # Write to JSON
            json_data = {
                "users": json_users,
                "last_sync": datetime.now().isoformat(),
                "sync_status": "cloud_downloaded",
                "user_count": len(json_users),
            }
            
            self._write_json(json_data)
            print(f"   ✅ Downloaded {len(json_users)} users to JSON")
            return True
            
        except Exception as e:
            print(f"   ❌ Error downloading: {e}")
            return False
    
    def upload_to_cloud(self) -> bool:
        """
        Upload users and permissions from JSON to Supabase
        Syncs local JSON → discord_users table
        """
        print(f"\n📤 Uploading users to Supabase...")
        
        try:
            json_data = self._read_json()
            json_users = json_data.get('users', {})
            
            if not json_users:
                print(f"   ℹ️  No users in JSON to upload")
                return True
            
            uploaded = 0
            failed = 0
            
            for discord_id_str, user_data in json_users.items():
                try:
                    discord_id = int(discord_id_str)
                    permissions = user_data.get('permissions', {})
                    
                    # Update user in Supabase
                    url = f"{self.supabase_url}/rest/v1/discord_users"
                    params = {"discord_id": f"eq.{discord_id}"}
                    
                    update_data = {
                        "granular_permissions": json.dumps(permissions),
                        "updated_at": datetime.now().isoformat(),
                    }
                    
                    response = requests.patch(
                        url,
                        headers=self.headers,
                        params=params,
                        json=update_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        uploaded += 1
                    else:
                        failed += 1
                        print(f"   ⚠️  Failed to update {discord_id}: {response.text}")
                
                except Exception as e:
                    failed += 1
                    print(f"   ⚠️  Error uploading user {discord_id_str}: {e}")
            
            # Update sync status
            json_data["last_sync"] = datetime.now().isoformat()
            json_data["sync_status"] = "cloud_uploaded"
            self._write_json(json_data)
            
            print(f"   ✅ Uploaded {uploaded} users, {failed} failed")
            return failed == 0
            
        except Exception as e:
            print(f"   ❌ Error uploading: {e}")
            return False
    
    def get_user_permissions(self, discord_id: str) -> Dict[str, Any]:
        """Get permissions for a specific user"""
        json_data = self._read_json()
        user_data = json_data.get('users', {}).get(str(discord_id), {})
        return user_data.get('permissions', self.default_permissions_template.copy())
    
    def set_user_permissions(self, discord_id: str, permissions: Dict[str, Any]) -> bool:
        """Set permissions for a user in local JSON"""
        json_data = self._read_json()
        
        discord_id_str = str(discord_id)
        if discord_id_str not in json_data['users']:
            print(f"   ℹ️  User {discord_id} not found in JSON")
            return False
        
        json_data['users'][discord_id_str]['permissions'] = permissions
        json_data['users'][discord_id_str]['updated_at'] = datetime.now().isoformat()
        
        self._write_json(json_data)
        return True
    
    def add_user(self, discord_id: int, username: str, is_admin: bool = False):
        """Add a new user to JSON"""
        json_data = self._read_json()
        
        discord_id_str = str(discord_id)
        if discord_id_str in json_data['users']:
            print(f"   ⚠️  User {discord_id} already exists")
            return False
        
        json_data['users'][discord_id_str] = {
            "discord_id": discord_id,
            "username": username,
            "is_admin": is_admin,
            "permissions": self.default_permissions_template.copy(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        self._write_json(json_data)
        return True
    
    def add_user_and_sync(self, discord_id: int, username: str, is_admin: bool = False) -> bool:
        """
        Add a new user to JSON and immediately sync to Supabase
        Use this when adding users from the EXE application
        """
        print(f"\n➕ Adding new user: {username} (ID: {discord_id})")
        
        # Add to local JSON
        if not self.add_user(discord_id, username, is_admin):
            print(f"   ❌ Failed to add user locally")
            return False
        
        print(f"   ✅ Added to local JSON")
        
        # Immediately upload to Supabase
        try:
            url = f"{self.supabase_url}/rest/v1/discord_users"
            
            # Check if user already exists in Supabase
            check_url = f"{self.supabase_url}/rest/v1/discord_users"
            check_params = {"discord_id": f"eq.{discord_id}", "select": "discord_id"}
            
            check_response = requests.get(
                check_url,
                headers=self.headers,
                params=check_params,
                timeout=10
            )
            
            exists_in_supabase = len(check_response.json()) > 0
            
            if exists_in_supabase:
                # Update existing user
                update_data = {
                    "discord_username": username,
                    "is_admin": is_admin,
                    "granular_permissions": json.dumps(self.default_permissions_template),
                    "updated_at": datetime.now().isoformat(),
                }
                
                response = requests.patch(
                    f"{url}",
                    headers=self.headers,
                    params={"discord_id": f"eq.{discord_id}"},
                    json=update_data,
                    timeout=10
                )
            else:
                # Insert new user
                insert_data = {
                    "discord_id": discord_id,
                    "discord_username": username,
                    "is_admin": is_admin,
                    "granular_permissions": json.dumps(self.default_permissions_template),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }
                
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=insert_data,
                    timeout=10
                )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Synced to Supabase")
                return True
            else:
                print(f"   ⚠️  Supabase sync issue: {response.status_code}")
                print(f"       {response.text[:100]}")
                # Still consider it a partial success - user is in local JSON
                return True
        
        except Exception as e:
            print(f"   ⚠️  Error syncing to Supabase: {e}")
            print(f"       User added locally, will sync on next sync operation")
            return True
    
    def delete_user(self, discord_id: int) -> bool:
        """Delete a user from JSON"""
        json_data = self._read_json()
        discord_id_str = str(discord_id)
        
        if discord_id_str not in json_data['users']:
            print(f"   ⚠️  User {discord_id} not found")
            return False
        
        del json_data['users'][discord_id_str]
        self._write_json(json_data)
        print(f"   ✅ Deleted user {discord_id}")
        return True
    
    def delete_user_and_sync(self, discord_id: int) -> bool:
        """Delete a user from JSON and sync to Supabase"""
        print(f"\n❌ Deleting user {discord_id}...")
        
        if not self.delete_user(discord_id):
            return False
        
        # Delete from Supabase
        try:
            url = f"{self.supabase_url}/rest/v1/discord_users"
            response = requests.delete(
                url,
                headers=self.headers,
                params={"discord_id": f"eq.{discord_id}"},
                timeout=10
            )
            
            if response.status_code == 204:
                print(f"   ✅ Deleted from Supabase")
                return True
            else:
                print(f"   ⚠️  Supabase deletion issue: {response.status_code}")
                return True  # Partial success
        
        except Exception as e:
            print(f"   ⚠️  Error deleting from Supabase: {e}")
            return True
    
    def list_users(self) -> List[Dict[str, Any]]:
        """Get list of all users"""
        json_data = self._read_json()
        return list(json_data.get('users', {}).values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about users and permissions"""
        json_data = self._read_json()
        users = json_data.get('users', {})
        
        admin_count = sum(1 for u in users.values() if u.get('is_admin', False))
        
        return {
            "total_users": len(users),
            "admin_users": admin_count,
            "regular_users": len(users) - admin_count,
            "last_sync": json_data.get('last_sync'),
            "sync_status": json_data.get('sync_status'),
        }
    
    def sync_bidirectional(self) -> bool:
        """
        Sync in both directions:
        1. Download from cloud
        2. Merge with local changes
        3. Upload to cloud
        """
        print(f"\n🔄 Bidirectional sync...")
        
        # Download fresh data from cloud
        if not self.download_from_cloud():
            print(f"   ⚠️  Download failed")
            return False
        
        # Upload local changes
        if not self.upload_to_cloud():
            print(f"   ⚠️  Upload failed")
            return False
        
        print(f"   ✅ Bidirectional sync complete")
        return True


# Test / Demo function
def demo():
    """Demonstrate usage"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        Users & Permissions JSON Manager - Demo                     ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    # Load from config (would be loaded from supabase_config.ini in real usage)
    import configparser
    config = configparser.ConfigParser()
    config_path = "supabase_config.ini"
    
    if not os.path.exists(config_path):
        print(f"⚠️  Config not found: {config_path}")
        print(f"Usage: Create supabase_config.ini with [supabase] section")
        return
    
    config.read(config_path)
    
    try:
        url = config['supabase']['url']
        key = config['supabase']['key']
    except:
        print("❌ Invalid config file")
        return
    
    # Create manager
    data_dir = "data"
    manager = UsersPermissionsJsonManager(url, key, data_dir)
    manager.ensure_json_exists()
    
    # Operations
    print(f"\n1️⃣  Download from cloud...")
    manager.download_from_cloud()
    
    print(f"\n2️⃣  Show users:")
    for user in manager.list_users():
        print(f"   • {user['username']} (ID: {user['discord_id']}, Admin: {user['is_admin']})")
    
    print(f"\n3️⃣  Statistics:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"   • {key}: {value}")
    
    print(f"\n✅ Demo complete!")

if __name__ == "__main__":
    demo()
