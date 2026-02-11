# -*- coding: utf-8 -*-
"""
Admin Panel & Logging System for Punctaj Manager
Handles user permissions and action logging
"""

import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from supabase_sync import SupabaseSync


class ActionLogger:
    """Logs all user actions to Supabase"""
    
    def __init__(self, supabase: SupabaseSync):
        """Initialize action logger"""
        self.supabase = supabase
        self.queue = []
        self.lock = threading.Lock()
    
    def log_action(self, action: str, user: str, city: str = None, institution: str = None, 
                   details: str = None, status: str = "success"):
        """Log an action"""
        try:
            log_entry = {
                'action': action,
                'user': user,
                'city': city,
                'institution': institution,
                'details': details,
                'timestamp': datetime.now().isoformat(),
                'status': status
            }
            
            # Queue the log entry
            with self.lock:
                self.queue.append(log_entry)
            
            # Try to send immediately in background
            threading.Thread(target=self._send_log, args=(log_entry,), daemon=True).start()
            
        except Exception as e:
            print(f"[ERROR] Failed to queue action: {e}")
    
    def _send_log(self, log_entry: Dict):
        """Send log entry to Supabase"""
        try:
            if not self.supabase or not self.supabase.enabled:
                return
            
            url = f"{self.supabase.url}/rest/v1/action_log"
            response = requests.post(url, json=log_entry, headers=self.supabase.headers, timeout=10)
            
            if response.status_code in [201, 200]:
                print(f"[OK] Action logged: {log_entry['action']} by {log_entry['user']}")
                with self.lock:
                    if log_entry in self.queue:
                        self.queue.remove(log_entry)
        
        except Exception as e:
            print(f"[WARNING] Failed to send log: {e}")
    
    def flush_queue(self):
        """Send all queued logs"""
        with self.lock:
            queue_copy = self.queue.copy()
        
        for log_entry in queue_copy:
            self._send_log(log_entry)


class AdminPanel:
    """Admin panel for managing users and permissions"""
    
    def __init__(self, supabase: SupabaseSync):
        """Initialize admin panel"""
        self.supabase = supabase
    
    def get_all_users(self) -> list:
        """Get all registered Discord users"""
        try:
            if not self.supabase or not self.supabase.enabled:
                return []
            
            url = f"{self.supabase.url}/rest/v1/discord_users?select=*"
            response = requests.get(url, headers=self.supabase.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        
        except Exception as e:
            print(f"[ERROR] Failed to get users: {e}")
            return []
    
    def update_user_role(self, discord_id: str, role: str) -> bool:
        """Update user role (admin, user, viewer)"""
        try:
            if not self.supabase or not self.supabase.enabled:
                return False
            
            data = {
                'role': role,
                'updated_at': datetime.now().isoformat()
            }
            
            url = f"{self.supabase.url}/rest/v1/discord_users?discord_id=eq.{discord_id}"
            response = requests.patch(url, json=data, headers=self.supabase.headers, timeout=10)
            
            return response.status_code in [200, 204]
        
        except Exception as e:
            print(f"[ERROR] Failed to update user: {e}")
            return False
    
    def set_user_permissions(self, discord_id: str, permissions: Dict[str, Any]) -> bool:
        """Set specific permissions for user"""
        try:
            if not self.supabase or not self.supabase.enabled:
                return False
            
            data = {
                'permissions': json.dumps(permissions),
                'updated_at': datetime.now().isoformat()
            }
            
            url = f"{self.supabase.url}/rest/v1/discord_users?discord_id=eq.{discord_id}"
            response = requests.patch(url, json=data, headers=self.supabase.headers, timeout=10)
            
            return response.status_code in [200, 204]
        
        except Exception as e:
            print(f"[ERROR] Failed to set permissions: {e}")
            return False
    
    def get_action_logs(self, user: str = None, limit: int = 100) -> list:
        """Get action logs"""
        try:
            if not self.supabase or not self.supabase.enabled:
                return []
            
            if user:
                url = f"{self.supabase.url}/rest/v1/action_log?user=eq.{user}&limit={limit}&order=timestamp.desc"
            else:
                url = f"{self.supabase.url}/rest/v1/action_log?limit={limit}&order=timestamp.desc"
            
            response = requests.get(url, headers=self.supabase.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        
        except Exception as e:
            print(f"[ERROR] Failed to get logs: {e}")
            return []


# Import requests here
try:
    import requests
except ImportError:
    pass
