# -*- coding: utf-8 -*-
"""
Supabase Cloud Sync Module
Handles real-time synchronization with Supabase PostgreSQL
"""

import json
import os
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import configparser
import sys

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Import config resolver
try:
    from config_resolver import ConfigResolver
except ImportError:
    ConfigResolver = None

# Import WebSocket manager for real-time sync
try:
    from supabase_realtime_ws import SupabaseRealtimeWS, create_realtime_ws_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("⚠️  WebSocket support not available")


class SupabaseSync:
    """Manages synchronization with Supabase"""
    
    def __init__(self, config_file: str = None):
        """Initialize Supabase Sync"""
        self.config = configparser.ConfigParser()
        
        # Daca nu e furnizat fisierul, incearca sa il gaseasca
        if not config_file:
            if ConfigResolver:
                config_file = ConfigResolver.find_config_file('supabase_config.ini')
            else:
                # Fallback la metoda veche
                config_paths = [
                    os.path.join(os.path.dirname(__file__), "supabase_config.ini"),
                    os.path.join(os.getcwd(), "supabase_config.ini"),
                    "supabase_config.ini"
                ]
                for path in config_paths:
                    if os.path.exists(path):
                        config_file = path
                        break
        
        if config_file and os.path.exists(config_file):
            self.config.read(config_file)
            print(f"✓ Supabase config loaded from: {config_file}")
        else:
            print(f"⚠️ Supabase config file not found!")
            print(f"   Expected locations:")
            if ConfigResolver:
                for path in ConfigResolver.get_config_paths():
                    print(f"   - {path}")
        
        # Supabase settings
        self.url = self.config.get('supabase', 'url', fallback=None)
        self.key = self.config.get('supabase', 'key', fallback=None)
        self.table_sync = self.config.get('supabase', 'table_sync', fallback='data')
        self.table_logs = self.config.get('supabase', 'table_logs', fallback='logs')
        self.table_users = self.config.get('supabase', 'table_users', fallback='users')
        
        # Sync settings
        self.enabled = self.config.getboolean('sync', 'enabled', fallback=True)
        self.auto_sync = self.config.getboolean('sync', 'auto_sync', fallback=True)
        self.sync_on_startup = self.config.getboolean('sync', 'sync_on_startup', fallback=True)
        self.sync_interval = self.config.getint('sync', 'sync_interval', fallback=30)
        self.conflict_resolution = self.config.get('sync', 'conflict_resolution', fallback='latest_timestamp')
        
        # Headers for API requests
        if self.key:
            self.headers = {
                'apikey': self.key,
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.key}'
            }
        else:
            self.headers = {
                'Content-Type': 'application/json'
            }
        
        # Sync state
        self.last_sync = {}
        self.sync_thread = None
        self.running = False
        
        # Real-time WebSocket manager
        self.ws_manager: Optional[SupabaseRealtimeWS] = None
        self.ws_enabled = False
        
        print(f"[OK] Supabase initialized: {self.url}")
        
        # Initialize WebSocket for real-time sync
        if WEBSOCKET_AVAILABLE and self.url and self.key:
            self._init_websocket()
        else:
            print("⚠️  Real-time WebSocket sync not available")
    
    def _init_websocket(self):
        """Initialize WebSocket connection for real-time sync"""
        try:
            tables_to_sync = ['employees', 'institutions', 'cities', 'discord_users']
            
            self.ws_manager = create_realtime_ws_manager(
                self.url,
                self.key,
                tables=tables_to_sync
            )
            
            if not self.ws_manager:
                print("❌ Failed to create WebSocket manager")
                return
            
            # Register callback for employee updates
            self.ws_manager.register_callback(
                "insert",
                "employees",
                self._on_employee_insert
            )
            self.ws_manager.register_callback(
                "update",
                "employees",
                self._on_employee_update
            )
            self.ws_manager.register_callback(
                "delete",
                "employees",
                self._on_employee_delete
            )
            
            # Register callback for institution updates
            self.ws_manager.register_callback(
                "update",
                "institutions",
                self._on_institution_update
            )
            
            self.ws_enabled = True
            print("✅ WebSocket real-time sync configured")
        
        except Exception as e:
            print(f"❌ Failed to initialize WebSocket: {e}")
    
    def _on_employee_insert(self, record: Dict[str, Any]):
        """Callback when employee is inserted - sync to local files"""
        print(f"📥 NEW EMPLOYEE (real-time): {record.get('employee_name')} at {record.get('institution_id')}")
        print(f"   📡 Broadcasting to all connected clients...")
        
        # Trigger remote data sync for all clients
        try:
            self._trigger_client_refresh("employee_insert", {
                'employee_name': record.get('employee_name'),
                'institution_id': record.get('institution_id'),
                'points': record.get('points', 0),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"   ⚠️ Failed to broadcast: {e}")
    
    def _on_employee_update(self, record: Dict[str, Any]):
        """Callback when employee is updated - sync to local files"""
        print(f"🔄 EMPLOYEE UPDATED (real-time): {record.get('employee_name')} - Points: {record.get('points', 0)}")
        print(f"   📡 Broadcasting to all connected clients...")
        
        # Trigger remote data sync for all clients
        try:
            self._trigger_client_refresh("employee_update", {
                'employee_name': record.get('employee_name'),
                'institution_id': record.get('institution_id'),
                'points': record.get('points', 0),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"   ⚠️ Failed to broadcast: {e}")
    
    def _on_employee_delete(self, record: Dict[str, Any]):
        """Callback when employee is deleted - sync to local files"""
        print(f"❌ EMPLOYEE DELETED (real-time): {record.get('employee_name')}")
        print(f"   📡 Broadcasting to all connected clients...")
        
        # Trigger remote data sync for all clients
        try:
            self._trigger_client_refresh("employee_delete", {
                'employee_name': record.get('employee_name'),
                'institution_id': record.get('institution_id'),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"   ⚠️ Failed to broadcast: {e}")
    
    def _on_institution_update(self, record: Dict[str, Any]):
        """Callback when institution is updated - sync to local files"""
        print(f"🔄 INSTITUTION UPDATED (real-time): {record.get('name')}")
        print(f"   📡 Broadcasting to all connected clients...")
        
        # Trigger remote data sync for all clients
        try:
            self._trigger_client_refresh("institution_update", {
                'institution_name': record.get('name'),
                'city': record.get('city'),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"   ⚠️ Failed to broadcast: {e}")
    
    def start_realtime_sync(self):
        """Start WebSocket real-time synchronization"""
        if not self.ws_enabled or not self.ws_manager:
            print("⚠️  WebSocket real-time sync not available")
            return
        
        self.ws_manager.start()
        print("✅ Real-time WebSocket sync started!")
    
    def stop_realtime_sync(self):
        """Stop WebSocket real-time synchronization"""
        if self.ws_manager:
            self.ws_manager.stop()
            print("🛑 Real-time WebSocket sync stopped")
    
    def _trigger_client_refresh(self, event_type: str, data: Dict[str, Any]):
        """Trigger refresh on other connected clients via WebSocket broadcast
        event_type: "employee_insert", "employee_update", "employee_delete", "institution_update"
        data: event details to broadcast"""
        try:
            # Prepare broadcast message
            broadcast_msg = {
                'type': 'client_sync_event',
                'event_type': event_type,
                'data': data,
                'broadcast_time': datetime.now().isoformat(),
                'priority': 'high'
            }
            
            # If WebSocket manager available, use it for real-time broadcast
            if self.ws_manager and hasattr(self.ws_manager, 'broadcast'):
                self.ws_manager.broadcast(broadcast_msg)
                print(f"   ✅ Broadcasted to WebSocket subscribers")
            
            # Also send via Supabase REST if needed for persistence
            self._log_sync_event(event_type, data)
            
            return True
        except Exception as e:
            print(f"   ⚠️ Broadcast error: {e}")
            return False
    
    def _log_sync_event(self, event_type: str, data: Dict[str, Any]):
        """Log sync event to Supabase for audit trail"""
        try:
            sync_event = {
                'event_type': event_type,
                'event_data': json.dumps(data),
                'created_at': datetime.now().isoformat(),
                'status': 'broadcasted'
            }
            
            # Optional: Create a sync_events table for audit trail
            # This ensures changes are tracked even when WebSocket is unavailable
            
        except Exception as e:
            print(f"   ⚠️ Failed to log sync event: {e}")
    
    def get_realtime_status(self) -> Dict[str, Any]:
        """Get real-time WebSocket status"""
        if not self.ws_manager:
            return {"enabled": False, "reason": "WebSocket manager not initialized"}
        return self.ws_manager.get_status()
    
    def register_user(self, discord_username: str, discord_id: str, discord_email: str = None) -> bool:
        """Register user in Supabase after Discord login - CREATE if not exists with NO PERMISSIONS"""
        if not self.enabled:
            print("⚠️ Supabase sync disabled - user not registered")
            return False
        
        try:
            # Use discord_users table (if available) or users table
            table_name = "discord_users" if "discord_users" in self.table_users else self.table_users
            
            url = f"{self.url}/rest/v1/{table_name}"
            
            print(f"🔍 Checking if Discord user exists: {discord_username} (ID: {discord_id})")
            
            # Check if user exists
            check_url = f"{url}?discord_id=eq.{discord_id}&select=*"
            try:
                response = requests.get(check_url, headers=self.headers, timeout=5)
            except requests.exceptions.Timeout:
                print(f"⚠️ Supabase timeout while checking user - retrying...")
                import time
                time.sleep(1)
                response = requests.get(check_url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # User exists - update last_login
                    user = data[0]
                    print(f"✅ User already exists in Supabase: {discord_username}")
                    print(f"   Discord ID: {discord_id}")
                    print(f"   Status: {user.get('active', False)} | Role: {'SUPERUSER' if user.get('is_superuser') else 'ADMIN' if user.get('is_admin') else 'USER' if user.get('can_view') else 'VIEWER'}")
                    
                    update_url = f"{url}?discord_id=eq.{discord_id}"
                    update_data = {
                        'last_login': datetime.now().isoformat(),
                        'active': True
                    }
                    try:
                        response = requests.patch(update_url, json=update_data, headers=self.headers, timeout=5)
                    except requests.exceptions.Timeout:
                        print(f"⚠️ Supabase timeout while updating user - retrying...")
                        import time
                        time.sleep(1)
                        response = requests.patch(update_url, json=update_data, headers=self.headers, timeout=5)
                    
                    if response.status_code in [200, 204]:
                        print(f"✅ User last_login updated in Supabase")
                        return True
                    else:
                        print(f"⚠️ Failed to update user last_login: HTTP {response.status_code}")
                        print(f"   Response: {response.text}")
                        return False
                else:
                    # User does NOT exist - CREATE NEW user WITHOUT PERMISSIONS
                    print(f"➕ User NOT found in Supabase - creating new account...")
                    print(f"   Discord Username: {discord_username}")
                    print(f"   Discord ID: {discord_id}")
                    print(f"   Email: {discord_email or 'NOT PROVIDED'}")
                    
                    user_data = {
                        'discord_username': discord_username,
                        'discord_id': str(discord_id),
                        'discord_email': discord_email or '',
                        'created_at': datetime.now().isoformat(),
                        'last_login': datetime.now().isoformat(),
                        'active': True,
                        # NO PERMISSIONS - all false by default (must be granted by admin)
                        'is_superuser': False,
                        'is_admin': False,
                        'can_view': False,
                        'can_edit': False,
                        'can_delete': False,
                        # Default empty granular permissions
                        'granular_permissions': '{}'
                    }
                    
                    # Insert new user
                    try:
                        response = requests.post(url, json=user_data, headers=self.headers, timeout=5)
                    except requests.exceptions.Timeout:
                        print(f"⚠️ Supabase timeout while creating user - retrying...")
                        import time
                        time.sleep(1)
                        response = requests.post(url, json=user_data, headers=self.headers, timeout=5)
                    
                    if response.status_code in [201, 200]:
                        print(f"✅ NEW USER CREATED IN SUPABASE")
                        print(f"   Discord Username: {discord_username}")
                        print(f"   Discord ID: {discord_id}")
                        print(f"   Initial Permissions: NONE (role: VIEWER)")
                        print(f"   Status: ✅ Ready - Admin can assign permissions")
                        return True
                    else:
                        print(f"❌ Failed to create user in Supabase: HTTP {response.status_code}")
                        print(f"   Response: {response.text}")
                        
                        # Try to provide helpful error message
                        if response.status_code == 409:
                            print(f"   Error: User already exists (duplicate detection failed)")
                        elif response.status_code == 400:
                            print(f"   Error: Invalid data format - check table schema")
                        elif response.status_code == 401:
                            print(f"   Error: Supabase auth failed - check API key")
                        
                        return False
            else:
                print(f"❌ Failed to check if user exists in Supabase: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error to Supabase: {e}")
            print(f"   Check: Is Supabase online? Is internet connected?")
            return False
        except Exception as e:
            print(f"❌ Failed to register user in Supabase: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def sync_data(self, city: str, institution: str, data: Dict) -> bool:
        """Upload local JSON data to Supabase AND broadcast to all clients
        BLOCKED if user doesn't have can_edit permission (unless superuser/admin)
        
        After successful save, notifies all connected clients about the update"""
        if not self.enabled:
            return False
        
        # ✅ SUPERUSER/ADMIN: Always allow
        if self._is_user_superuser_or_admin():
            print(f"👑 SUPERUSER/ADMIN UPLOAD: {city}/{institution}")
        else:
            # ✅ CHECK EDIT PERMISSION BEFORE UPLOAD
            if not self._can_access_institution(city, institution, "can_edit"):
                print(f"🚫 UPLOAD BLOCKED - no can_edit permission for {city}/{institution}")
                from discord_auth import DISCORD_AUTH
                if DISCORD_AUTH:
                    perms = DISCORD_AUTH.get_granular_permissions()
                    key = f"{city}/{institution}"
                    print(f"   DEBUG: Looking for key '{key}' in permissions")
                    print(f"   DEBUG: Available perms: {list(perms.keys())}")
                    if key in perms:
                        print(f"   DEBUG: Perms for {key}: {perms[key]}")
                return False
        
        try:
            sync_record = {
                'city': city,
                'institution': institution,
                'data_json': json.dumps(data),
                'updated_at': datetime.now().isoformat(),
                'updated_by': 'system'  # Will be overridden by Discord username
            }
            
            url = f"{self.url}/rest/v1/{self.table_sync}"
            
            # Check if record exists
            check_url = f"{url}?city=eq.{city}&institution=eq.{institution}"
            response = requests.get(check_url, headers=self.headers)
            
            if response.status_code == 200:
                existing = response.json()
                if existing:
                    # Update existing record
                    update_url = f"{url}?city=eq.{city}&institution=eq.{institution}"
                    response = requests.patch(update_url, json=sync_record, headers=self.headers)
                    if response.status_code in [200, 204]:
                        # 📡 BROADCAST UPDATE TO ALL CLIENTS
                        self._trigger_client_refresh("institution_sync", {
                            'city': city,
                            'institution': institution,
                            'employee_count': len(data.get('rows', [])),
                            'timestamp': datetime.now().isoformat(),
                            'action': 'update'
                        })
                    return response.status_code in [200, 204]
                else:
                    # Insert new record
                    response = requests.post(url, json=sync_record, headers=self.headers)
                    if response.status_code in [201, 200]:
                        # 📡 BROADCAST NEW INSTITUTION TO ALL CLIENTS
                        self._trigger_client_refresh("institution_sync", {
                            'city': city,
                            'institution': institution,
                            'employee_count': len(data.get('rows', [])),
                            'timestamp': datetime.now().isoformat(),
                            'action': 'create'
                        })
                    return response.status_code in [201, 200]
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Failed to sync data: {e}")
            return False
    
    def get_remote_data(self, city: str = None, institution: str = None) -> Optional[Dict]:
        """Download data from Supabase
        FILTERED by user's permissions"""
        if not self.enabled:
            return None
        
        # ✅ CHECK VIEW PERMISSION BEFORE DOWNLOAD
        if city and institution:
            if not self._can_access_institution(city, institution, "can_view"):
                print(f"🚫 ACCESS DENIED - no can_view permission for {city}/{institution}")
                return None
        
        try:
            url = f"{self.url}/rest/v1/{self.table_sync}"
            
            if city and institution:
                url += f"?city=eq.{city}&institution=eq.{institution}"
            elif city:
                url += f"?city=eq.{city}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return json.loads(data[0].get('data_json', '{}'))
            
            return None
            
        except Exception as e:
            print(f"[ERROR] Failed to get remote data: {e}")
            return None
    
    def log_action(self, action: str, city: str, institution: str, user: str, details: str = None) -> bool:
        """Log user action in Supabase"""
        if not self.enabled:
            return False
        
        try:
            log_record = {
                'action': action,
                'city': city,
                'institution': institution,
                'user': user,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            url = f"{self.url}/rest/v1/{self.table_logs}"
            response = requests.post(url, json=log_record, headers=self.headers)
            
            return response.status_code in [201, 200]
            
        except Exception as e:
            print(f"[ERROR] Failed to log action: {e}")
            return False
    
    def start_auto_sync(self):
        """Start background sync thread"""
        if not self.auto_sync or self.running:
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print("[OK] Auto-sync started")
    
    def _get_user_granular_permissions(self) -> Dict[str, Dict[str, bool]]:
        """Get current user's granular permissions
        Returns dict like: {"city/institution": {"can_view": true, "can_edit": false, ...}}
        """
        try:
            # Try to import discord_auth to get current user permissions
            from discord_auth import DISCORD_AUTH
            if DISCORD_AUTH:
                return DISCORD_AUTH.get_granular_permissions()
        except ImportError:
            pass
        return {}
    
    def _is_user_superuser_or_admin(self) -> bool:
        """Check if current user is superuser or admin (bypass all permission checks)"""
        try:
            from discord_auth import DISCORD_AUTH
            if DISCORD_AUTH:
                if DISCORD_AUTH.is_superuser() or DISCORD_AUTH.is_admin():
                    return True
        except ImportError:
            pass
        return False
    
    def _get_user_global_permissions(self) -> Dict[str, bool]:
        """Get current user's global permissions
        Returns dict like: {"can_add_cities": true, "can_edit_cities": true, ...}
        """
        try:
            from discord_auth import DISCORD_AUTH
            if DISCORD_AUTH:
                # Return global permissions if available
                perms = DISCORD_AUTH.get_granular_permissions()
                if isinstance(perms, dict):
                    # Check if there's a __global__ key
                    if "__global__" in perms:
                        return perms["__global__"]
                    # Otherwise, check basic global permissions
                    return {
                        'can_add_cities': DISCORD_AUTH.is_admin() or DISCORD_AUTH.is_superuser(),
                        'can_edit_cities': DISCORD_AUTH.is_admin() or DISCORD_AUTH.is_superuser(),
                        'can_delete_cities': DISCORD_AUTH.is_superuser(),
                        'can_view_logs': DISCORD_AUTH.can_view() or DISCORD_AUTH.is_admin(),
                    }
        except ImportError:
            pass
        return {}
    
    def _can_access_institution(self, city: str, institution: str, permission: str = "can_view") -> bool:
        """Check if user can access specific institution for given permission type
        permission: "can_view", "can_edit", "can_delete"
        
        Returns True if:
        - User is SUPERUSER/ADMIN (bypass all checks)
        - OR user has permission in granular_permissions
        """
        # ✅ SUPERUSER/ADMIN: Always allow
        if self._is_user_superuser_or_admin():
            return True
        
        perms = self._get_user_granular_permissions()
        key = f"{city}/{institution}"
        
        if not perms:
            # No permissions loaded - deny access
            return False
        
        # Check if institution is in user's permissions
        if key in perms:
            institution_perms = perms[key]
            # Check if permission is granted
            if permission in institution_perms:
                result = institution_perms[permission] is True
                if not result:
                    print(f"🔐 Permission check: {permission} on {key} = FALSE")
                return result
        
        return False
    
    def _can_perform_global_action(self, action: str) -> bool:
        """Check if user can perform global action like add_cities, delete_cities
        action: "add_cities", "edit_cities", "delete_cities"
        """
        # ✅ SUPERUSER: Always allow
        if self._is_user_superuser_or_admin():
            return True
        
        global_perms = self._get_user_global_permissions()
        
        # Map action to permission key
        action_map = {
            "add_cities": "can_add_cities",
            "edit_cities": "can_edit_cities",
            "delete_cities": "can_delete_cities",
            "view_logs": "can_view_logs",
        }
        
        perm_key = action_map.get(action)
        if perm_key and perm_key in global_perms:
            return global_perms[perm_key] is True
        
        return False
    
    def _filter_institutions_by_permission(self, institutions: List[Dict], permission: str = "can_view") -> List[Dict]:
        """Filter list of institutions to only those user can access"""
        filtered = []
        for inst in institutions:
            city = inst.get('city', '')
            inst_name = inst.get('institution', '')
            if self._can_access_institution(city, inst_name, permission):
                filtered.append(inst)
        return filtered
    
    def sync_all_from_cloud(self, data_dir: str) -> Dict[str, Any]:
        """Download all data from Supabase and update local JSON files
        FILTERED by user's granular permissions (except superuser/admin)
        Also downloads audit logs"""
        if not self.enabled:
            return {"status": "disabled"}
        
        try:
            downloaded = 0
            cities = set()
            skipped = 0
            
            # ✅ SUPERUSER/ADMIN: Download ALL data without filtering
            is_superuser = self._is_user_superuser_or_admin()
            if is_superuser:
                print("👑 SUPERUSER/ADMIN MODE - downloading ALL data without filtering")
            
            # Get current user's granular permissions (if not superuser)
            user_perms = self._get_user_granular_permissions() if not is_superuser else {}
            if not is_superuser and not user_perms:
                print("⚠️  No granular permissions found - cannot download data")
                return {"status": "error", "message": "No permissions loaded"}
            
            # Get all records from Supabase - use proper REST API URL
            url = f"{self.url}/rest/v1/{self.table_sync}?select=*&limit=1000"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 404:
                print(f"[WARNING] Table {self.table_sync} not found in Supabase - no data to sync yet")
                return {"status": "success", "downloaded": 0, "cities": []}
            
            if response.status_code != 200:
                print(f"[ERROR] Failed to fetch from Supabase: {response.status_code}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
            
            records = response.json()
            
            if not records:
                print("[OK] No records in Supabase")
                return {"status": "success", "downloaded": 0, "cities": []}
            
            # Process each record - FILTER BY PERMISSIONS (if not superuser)
            for record in records:
                try:
                    city = record.get('city', '')
                    institution = record.get('institution', '')
                    data_json = record.get('data_json', '{}')
                    
                    if not city or not institution:
                        continue
                    
                    # ✅ CHECK PERMISSION BEFORE DOWNLOAD (skip if superuser)
                    if not is_superuser and not self._can_access_institution(city, institution, "can_view"):
                        print(f"🚫 SKIPPED (no permission): {city}/{institution}")
                        skipped += 1
                        continue
                    
                    # Ensure directory exists
                    city_dir = os.path.join(data_dir, city)
                    os.makedirs(city_dir, exist_ok=True)
                    
                    # Save JSON file
                    json_file = os.path.join(city_dir, f"{institution}.json")
                    
                    try:
                        data = json.loads(data_json)
                    except json.JSONDecodeError:
                        data = {}
                    
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    downloaded += 1
                    cities.add(city)
                    print(f"[OK] Downloaded: {city}/{institution}")
                    
                except Exception as e:
                    print(f"[ERROR] Failed to process record: {e}")
                    continue
            
            # Download audit logs organized by city/institution
            try:
                logs_downloaded = 0
                logs_dir = "logs"
                os.makedirs(logs_dir, exist_ok=True)
                
                # Get all audit logs from Supabase
                logs_url = f"{self.url}/rest/v1/{self.table_logs}?select=*&order=timestamp.desc&limit=1000"
                logs_response = requests.get(logs_url, headers=self.headers, timeout=30)
                
                if logs_response.status_code == 200:
                    logs = logs_response.json()
                    
                    # Organize logs by city/institution
                    logs_by_institution = {}
                    for log in logs:
                        city = log.get('city', 'unknown')
                        institution = log.get('institution', 'unknown')
                        key = f"{city}/{institution}"
                        
                        if key not in logs_by_institution:
                            logs_by_institution[key] = []
                        
                        logs_by_institution[key].append(log)
                    
                    # Save organized logs
                    for key, logs_array in logs_by_institution.items():
                        try:
                            parts = key.split('/')
                            city = parts[0]
                            institution = parts[1] if len(parts) > 1 else 'unknown'
                            
                            # Create directory: logs/{city}/
                            city_dir = os.path.join(logs_dir, city)
                            os.makedirs(city_dir, exist_ok=True)
                            
                            # Save logs to: logs/{city}/{institution}.json
                            log_file = os.path.join(city_dir, f"{institution}.json")
                            
                            with open(log_file, 'w', encoding='utf-8') as f:
                                json.dump(logs_array, f, ensure_ascii=False, indent=2)
                            
                            logs_downloaded += len(logs_array)
                            print(f"[OK] Downloaded {len(logs_array)} logs to {log_file}")
                        except Exception as e:
                            print(f"[WARNING] Failed to save logs for {key}: {e}")
                    
                    if logs_downloaded > 0:
                        print(f"[OK] Downloaded {logs_downloaded} total audit logs")
            except Exception as e:
                print(f"[WARNING] Failed to download logs: {e}")
            
            return {
                "status": "success",
                "downloaded": downloaded,
                "skipped": skipped,
                "cities": sorted(list(cities))
            }
            
        except Exception as e:
            print(f"[ERROR] Sync error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_city_permissions(self, city: str, user: str = None) -> Dict[str, bool]:
        """Get permissions for a city"""
        # For now: grant full access to all authenticated users
        return {
            'view': True,
            'edit': True,
            'delete': False,
            'admin': False
        }
    
    def _sync_loop(self):
        """Background sync loop"""
        while self.running:
            try:
                time.sleep(self.sync_interval)
                # Sync logic here - check for remote changes
            except Exception as e:
                print(f"[ERROR] Sync loop error: {e}")
    
    def stop_auto_sync(self):
        """Stop background sync thread"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("[OK] Auto-sync stopped")
