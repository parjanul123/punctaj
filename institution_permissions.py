# -*- coding: utf-8 -*-
"""
Institution-Based Permissions Manager
Manages granular permissions per institution for each user
"""

import json
import os
import requests
from typing import Dict, List, Optional

class InstitutionPermissionManager:
    """Manages permissions per institution for each user"""
    
    def __init__(self, supabase_sync, data_dir: str):
        """
        Initialize permission manager
        
        Args:
            supabase_sync: SupabaseSync instance
            data_dir: Path to data directory with institution JSON files
        """
        self.supabase_sync = supabase_sync
        self.data_dir = data_dir
        self.supabase_url = supabase_sync.url
        self.supabase_key = supabase_sync.key
    
    def get_all_institutions(self) -> List[str]:
        """Get all institutions from data directory"""
        institutions = []
        try:
            # Scan data directory for institution JSON files
            for city_folder in os.listdir(self.data_dir):
                city_path = os.path.join(self.data_dir, city_folder)
                if os.path.isdir(city_path):
                    # Look for JSON files (e.g., Politie.json)
                    for file in os.listdir(city_path):
                        if file.endswith('.json'):
                            institution = file.replace('.json', '')
                            key = f"{city_folder}/{institution}"
                            institutions.append(key)
        except Exception as e:
            print(f"Error scanning institutions: {e}")
        
        return sorted(institutions)
    
    def get_user_institution_permissions(self, discord_id: str) -> Dict[str, Dict[str, bool]]:
        """Fetch user's institution-based permissions from Supabase"""
        try:
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.supabase_url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=institution_permissions"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    perms_str = data[0].get('institution_permissions', '{}')
                    try:
                        return json.loads(perms_str) if isinstance(perms_str, str) else perms_str
                    except:
                        return {}
            return {}
        except Exception as e:
            print(f"Error fetching institution permissions: {e}")
            return {}
    
    def save_user_institution_permissions(self, discord_id: str, permissions: Dict[str, Dict[str, bool]]) -> bool:
        """Save user's institution permissions to Supabase"""
        try:
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Get user ID first
            url = f"{self.supabase_url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=id"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    user_id = data[0]['id']
                    
                    # Update permissions
                    update_url = f"{self.supabase_url}/rest/v1/discord_users?id=eq.{user_id}"
                    update_data = {
                        "institution_permissions": json.dumps(permissions)
                    }
                    
                    update_response = requests.patch(
                        update_url,
                        headers=headers,
                        json=update_data,
                        timeout=5
                    )
                    
                    return update_response.status_code in [200, 204]
            return False
        except Exception as e:
            print(f"Error saving institution permissions: {e}")
            return False
    
    def has_permission_for_institution(self, discord_id: str, institution_key: str, permission: str) -> bool:
        """Check if user has specific permission for an institution"""
        permissions = self.get_user_institution_permissions(discord_id)
        
        if institution_key in permissions:
            return permissions[institution_key].get(permission, False)
        
        return False
    
    def get_user_accessible_institutions(self, discord_id: str, permission: str = 'can_view') -> List[str]:
        """Get list of institutions user can access with given permission"""
        permissions = self.get_user_institution_permissions(discord_id)
        accessible = []
        
        for institution_key, perms in permissions.items():
            if perms.get(permission, False):
                accessible.append(institution_key)
        
        return accessible
