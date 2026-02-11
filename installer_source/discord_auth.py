# -*- coding: utf-8 -*-
"""
Discord OAuth2 Authentication Module
Manages Discord login with webhook support for data synchronization
"""

import os
import json
import requests
from typing import Optional, Dict, Any
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
        
        # State for CSRF protection
        self.state = None
        
        # Permission sync manager (optional)
        self.permission_sync_manager = None
        
        # Cached granular permissions
        self._cached_granular_permissions = {}
        
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
        try:
            # Try to import and use SupabaseSync if available
            try:
                from supabase_sync import SupabaseSync
                import configparser
                import os
                import sys
                
                # Find supabase config - includes installation directory
                meipass = getattr(sys, '_MEIPASS', None)
                exe_dir = os.path.dirname(sys.executable) if hasattr(sys, 'executable') else None
                
                config_paths = [
                    os.path.join(meipass, "supabase_config.ini") if meipass else None,
                    os.path.join(exe_dir, "supabase_config.ini") if exe_dir else None,
                    os.path.dirname(sys.executable),  # Installation directory where EXE is
                    os.path.join(os.path.dirname(__file__), "supabase_config.ini"),
                    os.path.join(os.getcwd(), "supabase_config.ini"),  # Current working directory
                    os.path.join(os.path.expanduser("~"), "Documents/PunctajManager/supabase_config.ini"),
                    "supabase_config.ini"
                ]
                
                # Remove None entries
                config_paths = [p for p in config_paths if p is not None]
                
                config_found = None
                for path in config_paths:
                    if os.path.exists(path):
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
                    
            except ImportError:
                print("[WARNING] SupabaseSync module not available - user not saved to Supabase")
        
        except Exception as e:
            print(f"[WARNING] Failed to save user to Supabase: {e}")
    
    def _fetch_user_role_from_supabase(self, user_id: str, supabase=None):
        """Fetch user role and admin status from Supabase discord_users table"""
        _log_auth_debug(f"[DEBUG] _fetch_user_role_from_supabase called with user_id={user_id}, supabase={supabase}")
        try:
            if supabase is None:
                _log_auth_debug(f"[DEBUG] Supabase is None, initializing...")
                try:
                    from supabase_sync import SupabaseSync
                    import configparser
                    import os
                    import sys
                    
                    # Find supabase config - includes installation directory
                    meipass = getattr(sys, '_MEIPASS', None)
                    exe_dir = os.path.dirname(sys.executable) if hasattr(sys, 'executable') else None
                    
                    config_paths = [
                        os.path.join(meipass, "supabase_config.ini") if meipass else None,
                        os.path.join(exe_dir, "supabase_config.ini") if exe_dir else None,
                        os.path.dirname(sys.executable),  # Installation directory where EXE is
                        os.path.join(os.path.dirname(__file__), "supabase_config.ini"),
                        os.path.join(os.getcwd(), "supabase_config.ini"),  # Current working directory
                        os.path.join(os.path.expanduser("~"), "Documents/PunctajManager/supabase_config.ini"),
                        "supabase_config.ini"
                    ]
                    
                    # Remove None entries
                    config_paths = [p for p in config_paths if p is not None]
                    
                    for path in config_paths:
                        if os.path.exists(path):
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
                        _log_auth_debug(f"[DEBUG] No data returned from API")
                        # User not found - default to viewer (no permissions)
                        self.user_role = "viewer"
                        self._is_superuser = False
                        self._is_admin = False
                        _log_auth_debug(f"👁️  User role: VIEWER (default - no permissions yet)")
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
    
    def get_username(self) -> str:
        """Get current user's username"""
        if self.user_info:
            return self.user_info.get('username', 'Unknown')
        return None
    
    def get_discord_id(self) -> str:
        """Get current user's Discord ID"""
        if self.user_info:
            return self.user_info.get('id', '')
        return None
    
    def get_user_role(self) -> str:
        """Get current user's role: admin, user, or viewer"""
        return self.user_role
    
    def get_accessible_institutions(self) -> list:
        """Fetch institutions that the user has access to from Supabase"""
        try:
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
        """Check if user is admin or superuser"""
        if not self.is_authenticated():
            return False
        
        # Superuser and admin both have admin privileges
        return self._is_superuser or self._is_admin or self.user_role.lower() in ['admin', 'superuser']
    
    def is_superuser(self) -> bool:
        """Check if user is superuser"""
        if not self.is_authenticated():
            return False
        
        return self._is_superuser or self.user_role.lower() == 'superuser'
    
    def can_view(self) -> bool:
        """Check if user can view data - all authenticated users"""
        if not self.is_authenticated():
            return False
        
        # viewers, users, and admins can view
        return self.user_role.lower() in ['viewer', 'user', 'admin']
    
    def can_view_city(self, city_name: str) -> bool:
        """Check if user can view specific city - checks granular permissions"""
        if not self.is_authenticated():
            return False
        
        # Superuser always can view
        if self._is_superuser:
            print(f"[DEBUG] {self.get_username()} is superuser - can view {city_name}")
            return True
        
        # Check granular permission for this specific city
        permission_key = f"cities.{city_name}.can_view"
        if self.has_granular_permission(permission_key):
            return True
        
        # Fallback: viewers, users, and admins can view (if granular not set)
        return self.user_role.lower() in ['viewer', 'user', 'admin']
    
    def can_edit_city_granular(self, city_name: str) -> bool:
        """Check if user can edit specific city - checks granular permissions"""
        if not self.is_authenticated():
            return False
        
        # Superuser always can edit
        if self._is_superuser:
            return True
        
        # Check granular permission for this specific city
        permission_key = f"cities.{city_name}.can_edit"
        if self.has_granular_permission(permission_key):
            return True
        
        # Fallback: users and admins can edit (if granular not set)
        return self.user_role.lower() in ['user', 'admin']
    
    def can_perform_action(self, action_id: str, city_name: str = None) -> bool:
        """Check if user can perform a specific action - users, admins, and superusers"""
        if not self.is_authenticated():
            return False
        
        # Actions: add_institution, edit_institution, delete_institution, add_employee, etc.
        # Users, admins, and superusers can perform modifications
        return self.user_role.lower() in ['user', 'admin', 'superuser']
    
    def can_manage_institution_employees(self, city: str, institution: str) -> bool:
        """Check if user can manage employees - only users and admins"""
        if not self.is_authenticated():
            return False
        
        # Only users and admins can manage employees
        return self.user_role.lower() in ['user', 'admin']
    
    def can_manage_granular_permissions(self) -> bool:
        """Check if user can manage granular permissions - only superusers and admins"""
        if not self.is_authenticated():
            return False
        
        # Only superusers and admins can manage granular permissions
        return self._is_superuser or self._is_admin
    
    def reload_granular_permissions_from_json(self):
        """
        Reload granular permissions from users_permissions.json
        Called after downloading new permissions from cloud
        ALSO RESTORE is_superuser and is_admin from JSON!
        """
        try:
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
        """
        Check if user has a specific granular permission
        Priority: 
        1. users_permissions.json (local encrypted cache)
        2. Permission sync manager cache
        3. Supabase (fallback with caching)
        """
        if not self.is_authenticated():
            return False
        
        # Superuser always has all permissions
        if self._is_superuser:
            return True
        
        user_id = self.get_discord_id()
        if not user_id:
            return False
        
        # Check local cache first
        if permission_key in self._cached_granular_permissions:
            return self._cached_granular_permissions[permission_key]
        
        # Try to load from users_permissions.json (LOCAL ENCRYPTED CACHE)
        try:
            import os
            import json
            from pathlib import Path
            
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
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Get user's permissions from JSON
                    users = json_data.get('users', {})
                    user_key = str(user_id)
                    
                    if user_key in users:
                        user_perms = users[user_key]
                        perms_dict = user_perms.get('permissions', {})
                        
                        # Parse permission_key (e.g., "cities.BlackWater.can_view")
                        keys = permission_key.split('.')
                        current = perms_dict
                        
                        for key in keys:
                            if isinstance(current, dict) and key in current:
                                current = current[key]
                            else:
                                break
                        
                        # If we found a value, cache and return it
                        if isinstance(current, bool):
                            self._cached_granular_permissions[permission_key] = current
                            return current
                except Exception as e:
                    print(f"[DiscordAuth] Warning: Could not read users_permissions.json: {e}")
        except:
            pass
        
        # Try to use permission sync manager cache
        if self.permission_sync_manager:
            try:
                cached_value = self.permission_sync_manager.get_cached_permission(permission_key)
                if permission_key in self.permission_sync_manager.last_global_permissions:
                    return cached_value
            except:
                pass
        
        # Fallback: Check granular permissions from Supabase (with caching)
        try:
            import requests
            
            # Try to get granular permissions from supabase
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
                
                if supabase:
                    headers = {
                        "apikey": supabase.key,
                        "Authorization": f"Bearer {supabase.key}",
                        "Content-Type": "application/json"
                    }
                    
                    url = f"{supabase.url}/rest/v1/discord_users?discord_id=eq.{user_id}&select=granular_permissions"
                    response = requests.get(url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            perms_data = data[0].get('granular_permissions', {})
                            if isinstance(perms_data, str):
                                perms_data = json.loads(perms_data)
                            
                            # Cache all global permissions
                            global_perms = perms_data.get('global', {})
                            self._cached_granular_permissions = global_perms
                            
                            # Check in global permissions
                            if permission_key in global_perms:
                                return global_perms.get(permission_key, False)
            except:
                pass
        except Exception as e:
            print(f"[DiscordAuth] Error checking granular permission {permission_key}: {e}")
        
        return False
    
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
