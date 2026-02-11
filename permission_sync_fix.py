# -*- coding: utf-8 -*-
"""
Fix pentru sincronizarea permisiunilor - reîncarcă permisiunile din Supabase periodic
"""

import threading
import time
import json
import requests
from datetime import datetime


class PermissionSyncManager:
    """Manages periodic sync of permissions from Supabase"""
    
    def __init__(self, supabase_sync, discord_auth, users_perms_json_manager=None, sync_interval: int = 5):
        """
        Initialize permission sync manager
        
        Args:
            supabase_sync: SupabaseSync instance
            discord_auth: DiscordAuth instance
            users_perms_json_manager: UsersPermissionsJsonManager for local JSON sync
            sync_interval: How often to sync permissions (seconds)
        """
        self.supabase = supabase_sync
        self.discord_auth = discord_auth
        self.users_perms_json_manager = users_perms_json_manager
        self.sync_interval = sync_interval
        
        # Thread control
        self.sync_thread = None
        self.stop_event = threading.Event()
        self.is_syncing = False
        
        # Cache
        self.last_global_permissions = {}
        self.last_institution_permissions = {}
        self.last_sync_time = None
        self.last_sync_hash = None  # Track if permissions actually changed
        
        # Callbacks for UI updates
        self.on_permissions_changed = None
        self.on_sync_error = None
    
    def start(self):
        """Start the permission sync thread"""
        if self.sync_thread and self.sync_thread.is_alive():
            print("⚠️ Permission sync already running")
            return
        
        self.stop_event.clear()
        self.sync_thread = threading.Thread(
            target=self._sync_loop,
            daemon=True
        )
        self.sync_thread.start()
        print("✅ Permission sync started (every 5 seconds)")
    
    def stop(self):
        """Stop the permission sync thread"""
        self.stop_event.set()
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("⏹️ Permission sync stopped")
    
    def _sync_loop(self):
        """Main sync loop running in background"""
        while not self.stop_event.is_set():
            try:
                self.sync_permissions()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"❌ Error in permission sync loop: {e}")
                if self.on_sync_error:
                    self.on_sync_error(str(e))
                time.sleep(self.sync_interval)
    
    def sync_permissions(self):
        """Sync permissions from Supabase to local JSON"""
        if self.is_syncing:
            return
        
        self.is_syncing = True
        try:
            discord_id = self.discord_auth.get_discord_id()
            if not discord_id:
                self.is_syncing = False
                return
            
            # ⭐ Download from cloud to local JSON
            if self.users_perms_json_manager:
                try:
                    success = self.users_perms_json_manager.download_from_cloud()
                    if success:
                        # ⭐ Reload cache from JSON after download
                        self.discord_auth.reload_granular_permissions_from_json()
                        print(f"🔄 Permissions synced from cloud (user: {discord_id})")
                    else:
                        print(f"⚠️ Failed to sync permissions from cloud")
                except Exception as e:
                    print(f"⚠️ Error downloading permissions from cloud: {e}")
            else:
                # Fallback: Fetch granular permissions directly from Supabase
                global_perms = self._fetch_global_permissions(discord_id)
                
                # Check if permissions changed
                import hashlib
                current_hash = hashlib.md5(json.dumps(global_perms, sort_keys=True).encode()).hexdigest()
                
                if current_hash != self.last_sync_hash:
                    print(f"🔄 Permissions changed for {discord_id}")
                    self.last_global_permissions = global_perms
                    self.last_sync_hash = current_hash
                    
                    if self.on_permissions_changed:
                        self.on_permissions_changed(global_perms)
            
            self.last_sync_time = datetime.now()
        
        except Exception as e:
            print(f"❌ Error syncing permissions: {e}")
        
        finally:
            self.is_syncing = False
    
    def _fetch_global_permissions(self, discord_id: str) -> dict:
        """Fetch global granular permissions from Supabase"""
        try:
            headers = {
                "apikey": self.supabase.key,
                "Authorization": f"Bearer {self.supabase.key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.supabase.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=granular_permissions"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    perms_data = data[0].get('granular_permissions', {})
                    if isinstance(perms_data, str):
                        perms_data = json.loads(perms_data)
                    
                    return perms_data.get('global', {})
            
            return {}
        
        except Exception as e:
            print(f"❌ Error fetching global permissions: {e}")
            return {}
    
    def get_cached_permission(self, permission_key: str) -> bool:
        """Get cached permission value"""
        return self.last_global_permissions.get(permission_key, False)
    
    def force_sync_now(self):
        """Force an immediate sync"""
        print("🔄 Forcing immediate permission sync...")
        self.sync_permissions()


def integrate_permission_sync(punctaj_root, discord_auth, supabase_sync, users_perms_json_manager=None):
    """
    Integrate permission sync into the application
    
    Usage in punctaj.py after Discord auth:
        
        # After DISCORD_AUTH is initialized
        permission_sync_manager = integrate_permission_sync(
            punctaj_root,
            DISCORD_AUTH,
            SUPABASE_SYNC,
            USERS_PERMS_JSON_MANAGER
        )
        
        # When closing app
        permission_sync_manager.stop()
    """
    
    # Create sync manager
    sync_manager = PermissionSyncManager(
        supabase_sync=supabase_sync,
        discord_auth=discord_auth,
        users_perms_json_manager=users_perms_json_manager,
        sync_interval=5  # Sync every 5 seconds
    )
    
    # Start syncing
    sync_manager.start()
    
    return sync_manager
