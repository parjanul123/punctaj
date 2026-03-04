# -*- coding: utf-8 -*-
"""
Discord OAuth2 Authentication Module
Manages Discord login with webhook support for data synchronization
"""

import os
import json
import requests
from typing import Optional, Dict, Any, Set, Tuple
from urllib.parse import urlencode, unquote
from datetime import datetime, timedelta
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import base64
import hashlib

# Multi-device authentication lock to prevent concurrent auth attempts
_DISCORD_AUTH_LOCK = threading.Lock()
_AUTH_IN_PROGRESS = False

# File logging helper
def _log_auth_debug(message: str):
    """Log authentication debug info to both console and file"""
    print(message)  # Console output
    try:
        # Write to auth debug log file
        log_dir = os.path.join(os.path.expanduser("~"), "Documents/PunctajManager")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "discord_auth_debug.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"[WARNING] Could not write to auth log: {e}")

class DiscordAuth:
    """Manages Discord OAuth2 authentication"""
    
    # Discord OAuth2 endpoints
    DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
    DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
    DISCORD_USER_URL = "https://discord.com/api/users/@me"
    DISCORD_GUILD_URL = "https://discord.com/api/users/@me/guilds"

    @staticmethod
    def _env_force_all_superusers() -> bool:
        """Return True when app runs in force-all-superusers mode."""
        return os.getenv("PUNCTAJ_FORCE_ALL_SUPERUSERS", "0").strip().lower() in {
            "1", "true", "yes", "on"
        }

    @staticmethod
    def _env_no_cloud_db() -> bool:
        """Return True when cloud DB/Supabase integration must be disabled."""
        return os.getenv("PUNCTAJ_NO_CLOUD_DB", "0").strip().lower() in {
            "1", "true", "yes", "on"
        }
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8888/callback"):
        """
        Initialize Discord Auth
        
        Args:
            client_id: Discord Application ID
            client_secret: Discord Application Secret
            redirect_uri: Redirect URL after login
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = ["identify", "email", "guilds"]
        
        # Token storage
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.user_info = None
        self.user_role = "viewer"  # Default role: viewer
        self._is_superuser = False
        self._is_admin = False
        self._force_all_superusers = self._env_force_all_superusers()
        self._no_cloud_db = self._env_no_cloud_db()
        
        # State for CSRF protection
        self.state = None
        
        # Permission sync manager (optional)
        self.permission_sync_manager = None
        
        # Cached granular permissions
        self._cached_granular_permissions = {}
        self._server_key = os.getenv("PUNCTAJ_SERVER_KEY", "default").strip() or "default"
        self._scoped_permissions_loaded = False
        self._global_permissions: Set[str] = set()
        self._city_permissions: Dict[str, Set[str]] = {}
        self._institution_permissions: Dict[Tuple[str, str], Set[str]] = {}
        self._cached_accessible_servers = []
        
        # Multi-device auth tracking
        self._auth_start_time = None
        self._device_id = base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8')
        
        # Token file path - NOT USED (force fresh login every session)
        # self.token_file = os.path.join(
        #     os.path.expanduser("~"),
        #     "Documents",
        #     "PunctajManager",
        #     ".discord_token"
        # )
        
        # NOTE: Discord token is NOT cached
        # User must authenticate fresh every time app starts
        # This ensures always fresh permission check and role verification
        if self._force_all_superusers:
            self._is_superuser = True
            self._is_admin = True
            self.user_role = "superuser"
            _log_auth_debug("👑 FORCE MODE ACTIVE: all authenticated users are SUPERUSER")

    def _apply_force_superuser_mode(self) -> bool:
        """Apply force mode flags and return True when enabled."""
        if self._force_all_superusers:
            self._is_superuser = True
            self._is_admin = True
            self.user_role = "superuser"
            return True
        return False
    
    def get_auth_url(self) -> str:
        """Generates the Discord OAuth2 authorization URL"""
        # Generate state for CSRF protection
        self.state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": self.state,
            "prompt": "consent"  # Force authorization screen
        }
        
        query_string = urlencode(params)
        return f"{self.DISCORD_AUTH_URL}?{query_string}"
    
    def handle_callback(self, code: str, state: str) -> bool:
        """
        Handles OAuth2 callback
        
        Args:
            code: Authorization code from Discord
            state: State for CSRF validation
            
        Returns:
            True if authentication successful
        """
        # Verify state
        if state != self.state:
            print("CSRF State validation failed")
            return False
        
        # Exchange code for token
        return self._exchange_code_for_token(code)
    
    def _exchange_code_for_token(self, code: str) -> bool:
        """Exchanges authorization code for access token - THREAD SAFE for multi-device"""
        global _AUTH_IN_PROGRESS
        
        # Acquire lock to prevent concurrent auth from multiple devices
        with _DISCORD_AUTH_LOCK:
            if _AUTH_IN_PROGRESS:
                print("⚠️  Another device is authenticating, waiting...")
                time.sleep(1)
        
        try:
            self._auth_start_time = datetime.now()
            
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "scope": " ".join(self.scopes)
            }
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            response = requests.post(
                self.DISCORD_TOKEN_URL,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"Token exchange failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            
            # Calculate token expiry
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            # Fetch user info
            if self._fetch_user_info():
                # Token is NOT saved - fresh login required every session
                print(f"Discord auth successful for {self.user_info.get('username')} (Device: {self._device_id[:8]}) - fresh login")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error exchanging code: {e}")
            return False
    
    def _fetch_user_info(self) -> bool:
        """Fetches authenticated user's info"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(self.DISCORD_USER_URL, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch user info: {response.status_code}")
                return False
            
            self.user_info = response.json()
            
            # Save user to Supabase after successful authentication
            self._save_to_supabase()
            
            return True
        
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return False
    
    def _save_to_supabase(self):
        """Save Discord user info to Supabase users table and fetch role"""
        if self._no_cloud_db:
            _log_auth_debug("ℹ️ NO-CLOUD mode: skipping Supabase user save/role fetch")
            return

        try:
            # Try to import and use SupabaseSync if available
            try:
                from supabase_sync import SupabaseSync
                import configparser
                import os
                import sys
                
                # Find supabase config - PRIORITY ORDER MATTERS! (same as supabase_sync.py)
                # ✅ Check script directory FIRST (most reliable)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                cwd = os.getcwd()
                
                config_paths = [
                    # ✅ FIRST: Script directory (most reliable)
                    os.path.join(script_dir, "supabase_config.ini"),
                    # ✅ SECOND: Current working directory  
                    os.path.join(cwd, "supabase_config.ini"),
                    # ✅ THIRD: Parent directory
                    os.path.join(os.path.dirname(script_dir), "supabase_config.ini"),
                    # Last resort: just the filename
                    "supabase_config.ini"
                ]
                
                # Remove duplicates while preserving order
                seen = set()
                config_paths = [p for p in config_paths if not (p in seen or seen.add(p))]
                
                config_found = None
                for path in config_paths:
                    if path and os.path.exists(path):
                        config_found = path
                        print(f"[DEBUG] Found config at: {path}")
                        break
                
                if config_found:
                    supabase = SupabaseSync(config_found)
                    username = self.user_info.get('username', 'Unknown')
                    user_id = self.user_info.get('id', '')
                    email = self.user_info.get('email', '')
                    
                    if supabase.register_user(username, user_id, email):
                        print(f"[OK] Discord user saved to Supabase: {username}#{self.user_info.get('discriminator', '0000')}")
                    
                    # Fetch user role from Supabase
                    self._fetch_user_role_from_supabase(user_id, supabase)
                    # Load scoped permissions (server/city/institution) from new tables
                    self._load_scoped_permissions_from_supabase(user_id, supabase)
                    
            except ImportError:
                print("[WARNING] SupabaseSync module not available - user not saved to Supabase")
        
        except Exception as e:
            print(f"[WARNING] Failed to save user to Supabase: {e}")
    
    def _fetch_user_role_from_supabase(self, user_id: str, supabase=None):
        """Fetch user role and admin status from Supabase discord_users table"""
        _log_auth_debug(f"[DEBUG] _fetch_user_role_from_supabase called with user_id={user_id}, supabase={supabase}")
        if self._no_cloud_db:
            _log_auth_debug("ℹ️ NO-CLOUD mode: skipped Supabase role fetch")
            return

        if self._apply_force_superuser_mode():
            _log_auth_debug("👑 Force mode: skipped role fetch from Supabase")
            return
        try:
            if supabase is None:
                _log_auth_debug(f"[DEBUG] Supabase is None, initializing...")
                try:
                    from supabase_sync import SupabaseSync
                    import configparser
                    import os
                    import sys
                    
                    # Find supabase config - PRIORITY ORDER MATTERS!
                    # ✅ Check script directory FIRST (same as supabase_sync.py)
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    cwd = os.getcwd()
                    
                    config_paths = [
                        # ✅ FIRST: Script directory (most reliable)
                        os.path.join(script_dir, "supabase_config.ini"),
                        # ✅ SECOND: Current working directory  
                        os.path.join(cwd, "supabase_config.ini"),
                        # ✅ THIRD: Parent directory
                        os.path.join(os.path.dirname(script_dir), "supabase_config.ini"),
                        # Last resort: just the filename
                        "supabase_config.ini"
                    ]
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    config_paths = [p for p in config_paths if not (p in seen or seen.add(p))]
                    
                    for path in config_paths:
                        if path and os.path.exists(path):
                            supabase = SupabaseSync(path)
                            _log_auth_debug(f"[DEBUG] Initialized supabase from {path}")
                            break
                except Exception as e:
                    _log_auth_debug(f"[DEBUG] Error initializing supabase: {e}")
                    return
            
            if supabase:
                _log_auth_debug(f"[DEBUG] Supabase object exists, URL={supabase.url}")
                # Query discord_users table for this user
                headers = {
                    "apikey": supabase.key,
                    "Authorization": f"Bearer {supabase.key}",
                    "Content-Type": "application/json"
                }
                
                url = f"{supabase.url}/rest/v1/discord_users?discord_id=eq.{user_id}&select=username,is_superuser,is_admin,can_view,can_edit,can_delete"
                _log_auth_debug(f"[DEBUG] Requesting: {url}")
                
                try:
                    import requests
                    response = requests.get(url, headers=headers, timeout=5)
                    _log_auth_debug(f"[DEBUG] Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        _log_auth_debug(f"[DEBUG] Response data: {data}")
                        if data and len(data) > 0:
                            user_data = data[0]
                            # Explicit boolean conversion - handle both boolean and string values
                            raw_is_superuser = user_data.get('is_superuser', False)
                            raw_is_admin = user_data.get('is_admin', False)
                            
                            # Convert to proper boolean
                            if isinstance(raw_is_superuser, str):
                                self._is_superuser = raw_is_superuser.lower() in ['true', '1', 'yes']
                            else:
                                self._is_superuser = bool(raw_is_superuser)
                            
                            if isinstance(raw_is_admin, str):
                                self._is_admin = raw_is_admin.lower() in ['true', '1', 'yes']
                            else:
                                self._is_admin = bool(raw_is_admin)
                        
                            _log_auth_debug(f"[DEBUG] Raw data from Supabase: is_superuser={raw_is_superuser} (type={type(raw_is_superuser).__name__}), is_admin={raw_is_admin} (type={type(raw_is_admin).__name__})")
                            _log_auth_debug(f"[DEBUG] Converted: self._is_superuser={self._is_superuser} (type={type(self._is_superuser).__name__}), self._is_admin={self._is_admin} (type={type(self._is_admin).__name__})")
                        
                            # Set role based on superuser/admin status
                            if self._is_superuser:
                                self.user_role = "superuser"
                                _log_auth_debug(f"👑 User role: SUPERUSER")
                            elif self._is_admin:
                                self.user_role = "admin"
                                _log_auth_debug(f"🛡️  User role: ADMIN")
                            else:
                                # Check can_view permission to determine if user or viewer
                                raw_can_view = user_data.get('can_view', False)
                                if isinstance(raw_can_view, str):
                                    can_view = raw_can_view.lower() in ['true', '1', 'yes']
                                else:
                                    can_view = bool(raw_can_view)
                                
                                if can_view:
                                    self.user_role = "user"
                                    _log_auth_debug(f"👤 User role: USER (can view)")
                                else:
                                    self.user_role = "viewer"
                                    _log_auth_debug(f"👁️  User role: VIEWER (read-only)")
                        else:
                            _log_auth_debug("[DEBUG] No rows in discord_users; role will be resolved from scoped/global permissions")
                    else:
                        _log_auth_debug(
                            f"[DEBUG] discord_users lookup unavailable (HTTP {response.status_code}); "
                            f"role will be resolved from scoped/global permissions"
                        )
                except Exception as req_error:
                    _log_auth_debug(f"[DEBUG] Request error: {req_error}")
                    import traceback
                    traceback.print_exc()
            else:
                _log_auth_debug(f"[DEBUG] Supabase object is None/invalid")
        except Exception as e:
            _log_auth_debug(f"[DEBUG] Exception in _fetch_user_role_from_supabase: {e}")
            import traceback
            traceback.print_exc()

    def _normalize_permission_code(self, permission_code: str) -> str:
        aliases = {
            "can_add_city": "can_add_cities",
            "can_edit_city": "can_edit_cities",
            "can_delete_city": "can_delete_cities",
            "add_cities": "can_add_cities",
            "edit_cities": "can_edit_cities",
            "delete_cities": "can_delete_cities",
        }
        return aliases.get(permission_code, permission_code)

    def _ensure_scoped_permissions_loaded(self):
        if self._scoped_permissions_loaded:
            return
        user_id = self.get_discord_id()
        if user_id:
            self._load_scoped_permissions_from_supabase(user_id)

    def _has_scoped_permission(self, permission_code: str, city_name: str = None, institution_name: str = None) -> bool:
        permission_code = self._normalize_permission_code(permission_code)

        if self._apply_force_superuser_mode():
            return True

        if self._is_superuser:
            return True

        self._ensure_scoped_permissions_loaded()

        if permission_code in self._global_permissions:
            return True

        if city_name and permission_code in self._city_permissions.get(city_name, set()):
            return True

        if city_name and institution_name and permission_code in self._institution_permissions.get((city_name, institution_name), set()):
            return True

        return False

    def _load_scoped_permissions_from_supabase(self, user_id: str, supabase=None) -> bool:
        """Load permissions from app_servers + user_server_permissions (multi-server model)."""
        if self._no_cloud_db or not user_id:
            return False

        # Reset cache before reload
        self._global_permissions = set()
        self._city_permissions = {}
        self._institution_permissions = {}
        self._cached_granular_permissions = {}
        self._scoped_permissions_loaded = False

        try:
            if supabase is None:
                try:
                    from supabase_sync import SupabaseSync
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    cwd = os.getcwd()
                    config_paths = [
                        os.path.join(script_dir, "supabase_config.ini"),
                        os.path.join(cwd, "supabase_config.ini"),
                        os.path.join(os.path.dirname(script_dir), "supabase_config.ini"),
                        "supabase_config.ini"
                    ]
                    seen = set()
                    config_paths = [p for p in config_paths if not (p in seen or seen.add(p))]
                    for path in config_paths:
                        if path and os.path.exists(path):
                            supabase = SupabaseSync(path)
                            break
                except Exception as e:
                    _log_auth_debug(f"[DEBUG] Could not init Supabase for scoped permissions: {e}")
                    return False

            if not supabase:
                return False

            try:
                self._server_key = supabase.config.get('supabase', 'server_key', fallback=self._server_key).strip() or self._server_key
            except Exception:
                pass

            headers = {
                "apikey": supabase.key,
                "Authorization": f"Bearer {supabase.key}",
                "Content-Type": "application/json"
            }

            # Global superuser check (independent of server)
            global_superuser_url = (
                f"{supabase.url}/rest/v1/global_superusers"
                f"?discord_id=eq.{user_id}&select=discord_id&limit=1"
            )
            global_superuser_response = requests.get(global_superuser_url, headers=headers, timeout=5)
            if global_superuser_response.status_code == 200 and (global_superuser_response.json() or []):
                self._is_superuser = True
                self._is_admin = True
                self.user_role = "superuser"
                self._scoped_permissions_loaded = True
                _log_auth_debug("👑 Global superuser detected (server-independent)")
                return True

            server_id = None

            # 1) Try configured server_key
            server_url = f"{supabase.url}/rest/v1/app_servers?server_key=eq.{self._server_key}&select=id,server_key&limit=1"
            server_response = requests.get(server_url, headers=headers, timeout=5)
            if server_response.status_code == 200:
                server_rows = server_response.json() or []
                if server_rows:
                    server_id = server_rows[0].get('id')
                    self._server_key = (server_rows[0].get('server_key') or self._server_key).strip() or self._server_key

            # 2) Fallback to app_runtime_settings.default_server_key
            if not server_id:
                runtime_url = (
                    f"{supabase.url}/rest/v1/app_runtime_settings"
                    f"?key=eq.default_server_key&select=value&limit=1"
                )
                runtime_response = requests.get(runtime_url, headers=headers, timeout=5)
                if runtime_response.status_code == 200:
                    runtime_rows = runtime_response.json() or []
                    if runtime_rows and runtime_rows[0].get('value'):
                        runtime_key = str(runtime_rows[0].get('value')).strip()
                        runtime_server_url = (
                            f"{supabase.url}/rest/v1/app_servers"
                            f"?server_key=eq.{runtime_key}&select=id,server_key&limit=1"
                        )
                        runtime_server_response = requests.get(runtime_server_url, headers=headers, timeout=5)
                        if runtime_server_response.status_code == 200:
                            runtime_server_rows = runtime_server_response.json() or []
                            if runtime_server_rows:
                                server_id = runtime_server_rows[0].get('id')
                                self._server_key = (runtime_server_rows[0].get('server_key') or runtime_key).strip() or runtime_key

            # 3) Last fallback: first active server
            if not server_id:
                any_server_url = (
                    f"{supabase.url}/rest/v1/app_servers"
                    f"?is_active=eq.true&select=id,server_key&order=created_at.asc&limit=1"
                )
                any_server_response = requests.get(any_server_url, headers=headers, timeout=5)
                if any_server_response.status_code == 200:
                    any_server_rows = any_server_response.json() or []
                    if any_server_rows:
                        server_id = any_server_rows[0].get('id')
                        self._server_key = (any_server_rows[0].get('server_key') or self._server_key).strip() or self._server_key

            if not server_id:
                _log_auth_debug(
                    f"[DEBUG] Could not resolve server context. "
                    f"configured='{self._server_key}', runtime default and active fallback missing"
                )
                return False

            if not server_id:
                return False

            # Superuser check in new model (server_superusers)
            superuser_url = (
                f"{supabase.url}/rest/v1/server_superusers"
                f"?server_id=eq.{server_id}&discord_id=eq.{user_id}&select=discord_id&limit=1"
            )
            superuser_response = requests.get(superuser_url, headers=headers, timeout=5)
            if superuser_response.status_code == 200 and (superuser_response.json() or []):
                self._is_superuser = True
                self._is_admin = True
                self.user_role = "superuser"
                self._scoped_permissions_loaded = True
                _log_auth_debug(f"👑 Superuser detected from server_superusers for server '{self._server_key}'")
                return True

            perms_url = (
                f"{supabase.url}/rest/v1/user_server_permissions"
                f"?server_id=eq.{server_id}&discord_id=eq.{user_id}&granted=eq.true"
                f"&select=permission_code,city_name,institution_name"
            )
            perms_response = requests.get(perms_url, headers=headers, timeout=5)
            if perms_response.status_code != 200:
                _log_auth_debug(f"[DEBUG] user_server_permissions lookup failed: HTTP {perms_response.status_code}")
                return False

            rows = perms_response.json() or []
            for row in rows:
                code = self._normalize_permission_code((row.get('permission_code') or '').strip())
                if not code:
                    continue

                city_name = row.get('city_name')
                institution_name = row.get('institution_name')

                if city_name and institution_name:
                    key = (city_name, institution_name)
                    self._institution_permissions.setdefault(key, set()).add(code)
                    self._cached_granular_permissions[f"institutions.{city_name}.{institution_name}.{code}"] = True
                    self._cached_granular_permissions[f"cities.{city_name}.institutions.{institution_name}.{code}"] = True
                elif city_name:
                    self._city_permissions.setdefault(city_name, set()).add(code)
                    self._cached_granular_permissions[f"cities.{city_name}.{code}"] = True
                else:
                    self._global_permissions.add(code)
                    self._cached_granular_permissions[code] = True

            # Standard user role in scoped model
            self._is_admin = False
            self._is_superuser = False
            has_any_permission = bool(rows)
            self.user_role = "user" if has_any_permission else "viewer"
            self._scoped_permissions_loaded = True

            _log_auth_debug(
                f"[DEBUG] Scoped permissions loaded for server '{self._server_key}': "
                f"global={len(self._global_permissions)}, city={len(self._city_permissions)}, institution={len(self._institution_permissions)}"
            )
            return True
        except Exception as e:
            _log_auth_debug(f"[DEBUG] Error loading scoped permissions: {e}")
            return False

    def get_accessible_servers(self) -> list:
        """Return list of servers visible to current user in format [{server_key, server_name}]."""
        if self._no_cloud_db:
            return []

        if not self.is_authenticated():
            return []

        user_id = self.get_discord_id()
        if not user_id:
            return []

        try:
            from supabase_sync import SupabaseSync

            script_dir = os.path.dirname(os.path.abspath(__file__))
            cwd = os.getcwd()
            config_paths = [
                os.path.join(script_dir, "supabase_config.ini"),
                os.path.join(cwd, "supabase_config.ini"),
                os.path.join(os.path.dirname(script_dir), "supabase_config.ini"),
                "supabase_config.ini"
            ]

            seen = set()
            config_paths = [p for p in config_paths if not (p in seen or seen.add(p))]

            supabase = None
            for path in config_paths:
                if path and os.path.exists(path):
                    supabase = SupabaseSync(path)
                    break

            if not supabase:
                return []

            headers = {
                "apikey": supabase.key,
                "Authorization": f"Bearer {supabase.key}",
                "Content-Type": "application/json"
            }

            is_global_superuser = False
            gs_url = (
                f"{supabase.url}/rest/v1/global_superusers"
                f"?discord_id=eq.{user_id}&select=discord_id&limit=1"
            )
            gs_resp = requests.get(gs_url, headers=headers, timeout=5)
            if gs_resp.status_code == 200 and (gs_resp.json() or []):
                is_global_superuser = True

            if self._apply_force_superuser_mode() or self._is_superuser or is_global_superuser:
                all_servers_url = (
                    f"{supabase.url}/rest/v1/app_servers"
                    f"?is_active=eq.true&select=server_key,server_name&order=server_name.asc"
                )
                all_servers_resp = requests.get(all_servers_url, headers=headers, timeout=5)
                if all_servers_resp.status_code == 200:
                    self._cached_accessible_servers = all_servers_resp.json() or []
                    return self._cached_accessible_servers
                return []

            server_ids = set()

            memberships_url = (
                f"{supabase.url}/rest/v1/server_users"
                f"?discord_id=eq.{user_id}&is_active=eq.true&select=server_id"
            )
            memberships_resp = requests.get(memberships_url, headers=headers, timeout=5)
            if memberships_resp.status_code == 200:
                for row in memberships_resp.json() or []:
                    sid = (row or {}).get('server_id')
                    if sid:
                        server_ids.add(str(sid))

            # Explicit server-visibility permission (new model)
            view_server_perms_url = (
                f"{supabase.url}/rest/v1/user_server_permissions"
                f"?discord_id=eq.{user_id}&granted=eq.true&permission_code=eq.can_view_server&select=server_id"
            )
            view_server_perms_resp = requests.get(view_server_perms_url, headers=headers, timeout=5)
            if view_server_perms_resp.status_code == 200:
                for row in view_server_perms_resp.json() or []:
                    sid = (row or {}).get('server_id')
                    if sid:
                        server_ids.add(str(sid))

            # Backward compatibility: any granted scoped permission implies server visibility
            direct_perms_url = (
                f"{supabase.url}/rest/v1/user_server_permissions"
                f"?discord_id=eq.{user_id}&granted=eq.true&select=server_id"
            )
            direct_perms_resp = requests.get(direct_perms_url, headers=headers, timeout=5)
            if direct_perms_resp.status_code == 200:
                for row in direct_perms_resp.json() or []:
                    sid = (row or {}).get('server_id')
                    if sid:
                        server_ids.add(str(sid))

            if not server_ids:
                self._cached_accessible_servers = []
                return []

            in_filter = ",".join(server_ids)
            servers_url = (
                f"{supabase.url}/rest/v1/app_servers"
                f"?id=in.({in_filter})&is_active=eq.true&select=server_key,server_name&order=server_name.asc"
            )
            servers_resp = requests.get(servers_url, headers=headers, timeout=5)
            if servers_resp.status_code == 200:
                self._cached_accessible_servers = servers_resp.json() or []
                return self._cached_accessible_servers

            return []
        except Exception as e:
            _log_auth_debug(f"[DEBUG] Error loading accessible servers: {e}")
            return []
    
    def get_username(self) -> str:
        """Get current user's username"""
        if self.user_info:
            return self.user_info.get('username', 'Unknown')
        return None
    
    def get_discord_id(self) -> str:
        """Get current user's Discord ID"""
        if self.user_info:
            discord_id = self.user_info.get('id') or self.user_info.get('discord_id') or ''
            return str(discord_id)
        return None
    
    def get_user_role(self) -> str:
        """Get current user's role: admin, user, or viewer"""
        if self._apply_force_superuser_mode():
            return "superuser"
        return self.user_role
    
    def get_accessible_institutions(self) -> list:
        """Fetch institutions that the user has access to from Supabase"""
        try:
            if self._apply_force_superuser_mode():
                return []  # Empty means "all institutions"

            user_id = self.get_discord_id()
            if not user_id:
                return []
            
            # If superuser or admin, return empty list (has access to all)
            if self._is_superuser or self._is_admin:
                return []  # Empty means "all institutions"
            
            # Try to get from SupabaseSync
            try:
                from supabase_sync import SupabaseSync
                import configparser
                
                config_paths = [
                    os.path.join(os.path.dirname(__file__), "supabase_config.ini"),
                    os.path.join(os.path.expanduser("~"), "Documents/PunctajManager/supabase_config.ini"),
                    "supabase_config.ini"
                ]
                
                supabase = None
                for path in config_paths:
                    if os.path.exists(path):
                        supabase = SupabaseSync(path)
                        break
                
                if not supabase:
                    return []
                
                # Query institution_permissions table for this user
                headers = {
                    "apikey": supabase.key,
                    "Authorization": f"Bearer {supabase.key}",
                    "Content-Type": "application/json"
                }
                
                # Get all institutions where user has at least can_view permission
                url = f"{supabase.url}/rest/v1/institution_permissions?discord_id=eq.{user_id}&can_view=eq.true&select=city,institution"
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    institutions = response.json()
                    print(f"✅ Found {len(institutions)} accessible institutions for user {user_id}")
                    return institutions
                else:
                    print(f"⚠️ Could not fetch institutions: HTTP {response.status_code}")
                    return []
            except ImportError:
                print("⚠️ SupabaseSync module not available")
                return []
        except Exception as e:
            print(f"⚠️ Error fetching accessible institutions: {e}")
            return []
    
    def refresh_access_token(self) -> bool:
        """Refreshes the access token if expired"""
        if not self.refresh_token:
            return False
        
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
            
            response = requests.post(
                self.DISCORD_TOKEN_URL,
                data=data,
                timeout=10
            )
            
            if response.status_code != 200:
                print("Token refresh failed")
                return False
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            self._save_token()
            print("Token refreshed successfully")
            return True
            
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """Checks if current token is valid and not expired"""
        if not self.access_token or not self.token_expiry:
            return False
        
        # Refresh if expiring soon (within 5 minutes)
        if datetime.now() > self.token_expiry - timedelta(minutes=5):
            return self.refresh_access_token()
        
        return True
    
    def is_authenticated(self) -> bool:
        """Returns True if user is authenticated"""
        return self.access_token is not None and self.user_info is not None
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Returns authenticated user's info"""
        if self.is_token_valid():
            return self.user_info
        return None
    
    def logout(self):
        """Logs out and removes stored token"""
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.user_info = None
        
        # Remove token file
        if os.path.exists(self.token_file):
            try:
                os.remove(self.token_file)
                print("Token removed")
            except Exception as e:
                print(f"Error removing token: {e}")
    
    def _save_token(self):
        """
        DISABLED - Token caching disabled for security
        Users must authenticate fresh every session
        This ensures always fresh permission check and role verification
        """
        pass  # Token is NOT saved - fresh login required every session
    
    def _load_stored_token(self):
        """
        DISABLED - Token caching disabled for security
        Users must authenticate fresh every session
        This ensures always fresh permission check and role verification
        """
        # Token is NOT loaded - fresh login required every session
        print("[INFO] Discord token caching DISABLED - fresh login required every session")
        return
    
    def start_oauth_server(self, port: int = 8888) -> bool:
        """
        Starts a local HTTP server to handle OAuth2 callback
        
        Returns:
            True if callback was successful
        """
        # Log to file for debugging
        log_file = os.path.join(os.path.expanduser("~"), "punctaj_discord_debug.log")
        
        def log_debug(msg):
            print(msg)  # Console
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(msg + "\n")
            except:
                pass
        
        log_debug(f"[{datetime.now()}] start_oauth_server called with port={port}")
        
        callback_received = {"success": False}
        server = None
        auth_instance = self  # Capture outer instance
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    print(f"Callback received: {self.path}")
                    
                    # Parse callback parameters
                    if "?" in self.path:
                        query_string = self.path.split('?')[1]
                        params = query_string.split('&')
                        params_dict = {}
                        for param in params:
                            if '=' in param:
                                key, value = param.split('=', 1)
                                # URL decode the value
                                params_dict[key] = unquote(value)
                        
                        code = params_dict.get('code')
                        state = params_dict.get('state')
                        error = params_dict.get('error')
                        error_desc = params_dict.get('error_description')
                        
                        print(f"Raw query: {query_string}")
                        print(f"Parsed params: {params_dict}")
                        print(f"Callback params: code={code}, state={state}, error={error}, desc={error_desc}")
                        
                        if error:
                            print(f"Discord error: {error}")
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html; charset=utf-8')
                            self.end_headers()
                            html = f"<html><body><h1>Error: {error}</h1></body></html>"
                            self.wfile.write(html.encode('utf-8'))
                            return
                        
                        if code and state:
                            if auth_instance.handle_callback(code, state):
                                callback_received["success"] = True
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html; charset=utf-8')
                                self.end_headers()
                                html = "<html><head><title>Discord Auth</title></head>"
                                html += "<body><h1>Authentication Successful!</h1>"
                                html += "<p>You can close this window.</p></body></html>"
                                self.wfile.write(html.encode('utf-8'))
                            else:
                                print("handle_callback returned False")
                                self.send_response(401)
                                self.send_header('Content-type', 'text/html; charset=utf-8')
                                self.end_headers()
                                html = "<html><body><h1>Authentication Failed</h1></body></html>"
                                self.wfile.write(html.encode('utf-8'))
                        else:
                            print(f"Missing code or state")
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html; charset=utf-8')
                            self.end_headers()
                            html = "<html><body><h1>Missing code or state</h1></body></html>"
                            self.wfile.write(html.encode('utf-8'))
                    else:
                        print("No query parameters in callback")
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        html = "<html><body><h1>No query parameters</h1></body></html>"
                        self.wfile.write(html.encode('utf-8'))
                except Exception as e:
                    print(f"Callback handler error: {e}")
                    self.send_response(500)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress server logging
        
        try:
            # Start server in background
            server = HTTPServer(('localhost', port), CallbackHandler)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            log_debug(f"[{datetime.now()}] OAuth2 server started on port {port}")
            
            # Open browser
            auth_url = self.get_auth_url()
            log_debug(f"[{datetime.now()}] Opening Discord auth URL: {auth_url}")
            webbrowser.open(auth_url)
            log_debug(f"[{datetime.now()}] Browser opened")
            
            # Wait for callback (30 second timeout)
            start_time = time.time()
            while time.time() - start_time < 30:
                if callback_received["success"]:
                    log_debug(f"[{datetime.now()}] Callback received successfully!")
                    return True
                time.sleep(0.5)
            
            log_debug(f"[{datetime.now()}] OAuth2 callback timeout")
            return False
            
        except Exception as e:
            print(f"OAuth2 server error: {e}")
            return False
        finally:
            if server:
                try:
                    server.shutdown()
                except:
                    pass
    
    def is_admin(self) -> bool:
        """Return True when authenticated user is admin/superuser or force mode is active."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True

        return bool(self._is_admin or self._is_superuser)
    
    def is_superuser(self) -> bool:
        """Return True when authenticated user is superuser or force mode is active."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True

        return bool(self._is_superuser)
    
    def can_view(self) -> bool:
        """Check if user can view data based on explicit permission."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True

        return self._has_scoped_permission('can_view')
    
    def can_view_city(self, city_name: str) -> bool:
        """Check if user can view specific city based on scoped permissions."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True
        
        return self._has_scoped_permission('can_view', city_name=city_name)
    
    def can_edit_city_granular(self, city_name: str) -> bool:
        """Check if user can edit specific city based on scoped permissions."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True
        
        return self._has_scoped_permission('can_edit', city_name=city_name) or self._has_scoped_permission('can_edit_cities', city_name=city_name)
    
    def can_perform_action(self, action_id: str, city_name: str = None) -> bool:
        """Check if user can perform action based on explicit permission mapping."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True
        
        action_map = {
            'add_institution': 'can_edit',
            'edit_institution': 'can_edit',
            'delete_institution': 'can_delete',
            'add_employee': 'can_edit_employee',
            'edit_employee': 'can_edit_employee',
            'delete_employee': 'can_delete_employee',
            'add_city': 'can_add_cities',
            'edit_city': 'can_edit_cities',
            'delete_city': 'can_delete_cities',
            'view_logs': 'can_view_logs',
        }
        permission_code = action_map.get(action_id, 'can_edit')
        return self._has_scoped_permission(permission_code, city_name=city_name)
    
    def can_manage_institution_employees(self, city: str, institution: str) -> bool:
        """Check if user can manage institution employees based on explicit permissions."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True
        
        return (
            self._has_scoped_permission('can_edit_employee', city_name=city, institution_name=institution)
            or self._has_scoped_permission('can_edit', city_name=city, institution_name=institution)
        )
    
    def can_manage_granular_permissions(self) -> bool:
        """Check if user can manage permissions based on explicit rights."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True
        
        return (
            self._has_scoped_permission('can_manage_user_permissions')
            or self._has_scoped_permission('can_see_user_permissions_button')
        )
    
    def reload_granular_permissions_from_json(self):
        """
        Reload granular permissions from users_permissions.json
        Called after downloading new permissions from cloud
        ALSO RESTORE is_superuser and is_admin from JSON!
        """
        try:
            if self._apply_force_superuser_mode():
                return True

            import os
            import json
            
            user_id = self.get_discord_id()
            if not user_id:
                return False
            
            # Find data directory
            data_dirs = [
                os.path.join(os.path.dirname(__file__), "data"),
                "data",
                os.path.join(os.path.expanduser("~"), "Documents/PunctajManager/data"),
            ]
            
            json_file = None
            for data_dir in data_dirs:
                potential_file = os.path.join(data_dir, "users_permissions.json")
                if os.path.exists(potential_file):
                    json_file = potential_file
                    break
            
            if json_file:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                users = json_data.get('users', {})
                user_key = str(user_id)
                
                if user_key in users:
                    user_perms = users[user_key]
                    perms_dict = user_perms.get('permissions', {})
                    
                    # 🔥 RESTORE is_superuser and is_admin from JSON!
                    raw_is_superuser = user_perms.get('is_superuser', False)
                    raw_is_admin = user_perms.get('is_admin', False)
                    
                    # Convert to proper boolean
                    if isinstance(raw_is_superuser, str):
                        self._is_superuser = raw_is_superuser.lower() in ['true', '1', 'yes']
                    else:
                        self._is_superuser = bool(raw_is_superuser)
                    
                    if isinstance(raw_is_admin, str):
                        self._is_admin = raw_is_admin.lower() in ['true', '1', 'yes']
                    else:
                        self._is_admin = bool(raw_is_admin)
                    
                    # Update role based on restored superuser/admin status
                    if self._is_superuser:
                        self.user_role = "superuser"
                        print(f"👑 Restored from JSON: user_role = SUPERUSER")
                    elif self._is_admin:
                        self.user_role = "admin"
                        print(f"🛡️  Restored from JSON: user_role = ADMIN")
                    
                    # Flatten and cache all permissions
                    def flatten_perms(d, prefix=''):
                        flat = {}
                        for k, v in d.items():
                            new_key = f"{prefix}.{k}" if prefix else k
                            if isinstance(v, dict):
                                flat.update(flatten_perms(v, new_key))
                            else:
                                flat[new_key] = v
                        return flat
                    
                    self._cached_granular_permissions = flatten_perms(perms_dict)
                    print(f"✅ Reloaded {len(self._cached_granular_permissions)} granular permissions from JSON")
                    print(f"✅ Restored: is_superuser={self._is_superuser}, is_admin={self._is_admin}")
                    return True
        except Exception as e:
            print(f"⚠️ Error reloading permissions from JSON: {e}")
        
        return False
    
    def has_granular_permission(self, permission_key: str) -> bool:
        """Permission-only mode: evaluate permission from user_server_permissions scopes."""
        if not self.is_authenticated():
            return False

        if self._apply_force_superuser_mode():
            return True

        self._ensure_scoped_permissions_loaded()

        if permission_key in self._cached_granular_permissions:
            return bool(self._cached_granular_permissions[permission_key])

        parts = permission_key.split('.')
        if len(parts) >= 3 and parts[0] == 'cities':
            city_name = parts[1]
            if len(parts) >= 5 and parts[2] == 'institutions':
                institution_name = parts[3]
                permission_code = self._normalize_permission_code(parts[4])
                return self._has_scoped_permission(permission_code, city_name=city_name, institution_name=institution_name)
            permission_code = self._normalize_permission_code(parts[2])
            return self._has_scoped_permission(permission_code, city_name=city_name)

        if len(parts) >= 4 and parts[0] == 'institutions':
            city_name = parts[1]
            institution_name = parts[2]
            permission_code = self._normalize_permission_code(parts[3])
            return self._has_scoped_permission(permission_code, city_name=city_name, institution_name=institution_name)

        return self._has_scoped_permission(self._normalize_permission_code(permission_key))
    
    def set_permission_sync_manager(self, sync_manager):
        """Set the permission sync manager for cached permission checks"""
        self.permission_sync_manager = sync_manager
        print("✅ Permission sync manager attached to Discord auth")


class DiscordWebhook:
    """Sends notifications to Discord webhook"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_message(self, message: str, title: str = "Punctaj Manager") -> bool:
        """Sends a message to Discord channel"""
        try:
            payload = {
                "content": f"**{title}**\n{message}"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error sending webhook: {e}")
            return False
    
    def send_embed(self, embed_dict: Dict) -> bool:
        """Sends an embed message"""
        try:
            payload = {"embeds": [embed_dict]}
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error sending embed: {e}")
            return False
