# -*- coding: utf-8 -*-
"""
Granular Permission Management for Admin Panel
Allows admins to set detailed permissions for each user via checkboxes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from typing import Dict, List, Tuple
from global_hierarchy_permissions import GlobalHierarchyPermissionManager

class PermissionManager:
    """Manages granular permissions for users"""
    
    # Define all available permissions
    PERMISSIONS = {
        "Orașe": {
            "add_city": "➕ Adaugă oraş",
            "edit_city": "✏️ Editează oraş",
            "delete_city": "❌ Șterge oraş",
            "can_add_city": "✓ Permite adăugare oraş",
            "can_edit_city": "✓ Permite editare oraş",
            "can_delete_city": "✓ Permite ștergere oraş",
        },
        "Instituții": {
            "add_institution": "➕ Adaugă instituție",
            "edit_institution": "✏️ Editează instituție",
            "delete_institution": "❌ Șterge instituție",
            "can_add_institution": "✓ Permite adăugare instituție",
            "can_edit_institution": "✓ Permite editare instituție",
            "can_delete_institution": "✓ Permite ștergere instituție",
        },
        "Angajați": {
            "add_employee": "➕ Adaugă angajat",
            "edit_employee": "✏️ Editează angajat",
            "delete_employee": "❌ Șterge angajat",
            "can_add_employee": "✓ Permite adăugare angajat",
            "can_edit_employee": "✓ Permite editare angajat",
            "can_delete_employee": "✓ Permite ștergere angajat",
        },
        "Cloud": {
            "upload_cloud": "📤 Upload în cloud",
            "download_cloud": "📥 Download din cloud",
        },
        "Admin": {
            "view_logs": "📋 Vizualizare logs",
            "manage_users": "👥 Gestiune utilizatori",
            "manage_permissions": "🔐 Gestiune permisiuni",
        }
    }
    
    def __init__(self, supabase_sync):
        self.supabase_sync = supabase_sync
        self.supabase_url = supabase_sync.url
        self.supabase_key = supabase_sync.key
    
    def get_user_permissions(self, discord_id: str) -> Dict:
        """
        Fetch user's current permissions
        Priority:
        1. users_permissions.json (local encrypted cache - FAST)
        2. Supabase (fallback)
        """
        try:
            # FIRST: Try to load from users_permissions.json (LOCAL ENCRYPTED CACHE)
            import os
            
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
                    
                    users = json_data.get('users', {})
                    user_key = str(discord_id)
                    
                    if user_key in users:
                        user_perms = users[user_key]
                        perms_dict = user_perms.get('permissions', {})
                        
                        if isinstance(perms_dict, dict) and perms_dict:
                            return perms_dict
                except Exception as e:
                    print(f"[PermManager] Note: Could not read users_permissions.json: {e}")
            
            # FALLBACK: Fetch from Supabase
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.supabase_url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=permissions"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    perm_str = data[0].get('permissions', '{}')
                    try:
                        return json.loads(perm_str)
                    except:
                        return {}
            return {}
        except Exception as e:
            print(f"Error fetching permissions: {e}")
            return {}
    
    def save_user_permissions(self, discord_id: str, permissions: Dict) -> bool:
        """Save user's permissions to Supabase"""
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
                        "permissions": json.dumps(permissions)
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
            print(f"Error saving permissions: {e}")
            return False
    
    def has_permission(self, discord_id: str, permission_id: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(discord_id)
        return permissions.get(permission_id, False)
    
    def get_all_permissions_for_user(self, discord_id: str) -> Dict:
        """Get all permission checkboxes state for a user"""
        user_perms = self.get_user_permissions(discord_id)
        
        all_perms = {}
        for category, perms in self.PERMISSIONS.items():
            all_perms[category] = {}
            for perm_id, perm_name in perms.items():
                all_perms[category][perm_id] = user_perms.get(perm_id, False)
        
        return all_perms


class InstitutionPermissionManager:
    """Manages institution-based permissions for users (grouped by city)"""
    
    def __init__(self, supabase_sync, data_dir: str):
        self.supabase_sync = supabase_sync
        self.supabase_url = supabase_sync.url
        self.supabase_key = supabase_sync.key
        self.data_dir = data_dir
    
    def get_all_cities(self) -> List[str]:
        """Get all cities from data directory"""
        cities = []
        try:
            for city_folder in os.listdir(self.data_dir):
                city_path = os.path.join(self.data_dir, city_folder)
                if os.path.isdir(city_path):
                    cities.append(city_folder)
        except Exception as e:
            print(f"Error scanning cities: {e}")
        return sorted(cities)
    
    def get_all_institutions_for_city(self, city: str) -> List[str]:
        """Get all institutions for a specific city"""
        institutions = []
        try:
            city_path = os.path.join(self.data_dir, city)
            if os.path.isdir(city_path):
                for file in os.listdir(city_path):
                    if file.endswith('.json'):
                        institution = file.replace('.json', '')
                        institutions.append(institution)
        except Exception as e:
            print(f"Error scanning institutions for {city}: {e}")
        return sorted(institutions)
    
    def get_all_institutions_by_city(self) -> Dict[str, List[str]]:
        """Get all institutions grouped by city - structure: {city: [institution1, institution2, ...]}"""
        result = {}
        cities = self.get_all_cities()
        for city in cities:
            institutions = self.get_all_institutions_for_city(city)
            if institutions:
                result[city] = institutions
        return result
    
    def get_all_institutions(self) -> List[str]:
        """Get all institutions from data directory (legacy - returns flat list)"""
        institutions = []
        try:
            all_by_city = self.get_all_institutions_by_city()
            for city, insts in all_by_city.items():
                for inst in insts:
                    institutions.append(f"{city}/{inst}")
        except Exception as e:
            print(f"Error scanning institutions: {e}")
        
        return sorted(institutions)
    
    def get_user_institution_permissions(self, discord_id: str) -> Dict[str, Dict[str, Dict[str, bool]]]:
        """
        Fetch user's institution-based permissions (grouped by city)
        MERGES both structures:
        1. Top-level institutions key (preferred)
        2. Nested institutions within cities (fallback/compatibility)
        
        Priority:
        1. users_permissions.json (local encrypted cache - FAST)
        2. Supabase (fallback - with caching)
        """
        try:
            # FIRST: Try to load from users_permissions.json (LOCAL ENCRYPTED CACHE)
            import os
            import json
            from pathlib import Path
            
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
                    
                    users = json_data.get('users', {})
                    user_key = str(discord_id)
                    
                    if user_key in users:
                        user_perms = users[user_key]
                        perms_dict = user_perms.get('permissions', {})
                        
                        # Extract institution permissions (try both structures)
                        return self._merge_institution_permissions(perms_dict)
                except Exception as e:
                    print(f"[PermManager] Note: Could not read users_permissions.json: {e}")
            
            # FALLBACK: Fetch from Supabase (with caching)
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.supabase_url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=granular_permissions"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    perms_data = data[0].get('granular_permissions', {})
                    if isinstance(perms_data, str):
                        try:
                            perms_data = json.loads(perms_data)
                        except:
                            perms_data = {}
                    # Merge both institution structures
                    return self._merge_institution_permissions(perms_data)
            return {}
        except Exception as e:
            print(f"Error fetching institution permissions: {e}")
            return {}
    
    def _merge_institution_permissions(self, perms_dict: Dict) -> Dict:
        """
        Merge institution permissions from both possible structures:
        1. Top-level: institutions.{city}.{institution}
        2. Nested: cities.{city}.institutions.{institution}
        
        Top-level takes priority if both exist
        """
        if not isinstance(perms_dict, dict):
            return {}
        
        merged = {}
        
        # Add from top-level institutions key (preferred)
        if 'institutions' in perms_dict and isinstance(perms_dict['institutions'], dict):
            for city, insts in perms_dict['institutions'].items():
                if isinstance(insts, dict):
                    if city not in merged:
                        merged[city] = {}
                    merged[city].update(insts)
        
        # Add from nested institutions in cities (fallback/compatibility)
        if 'cities' in perms_dict and isinstance(perms_dict['cities'], dict):
            for city, city_perms in perms_dict['cities'].items():
                if isinstance(city_perms, dict) and 'institutions' in city_perms:
                    nested_insts = city_perms['institutions']
                    if isinstance(nested_insts, dict):
                        if city not in merged:
                            merged[city] = {}
                        # Only add if not already in top-level (top-level takes priority)
                        for inst_name, inst_perms in nested_insts.items():
                            if inst_name not in merged[city]:
                                merged[city][inst_name] = inst_perms
        
        return merged
    
    def save_user_institution_permissions(self, discord_id: str, permissions: Dict[str, Dict[str, Dict[str, bool]]]) -> bool:
        """Save institution permissions into user_server_permissions (table 44871)."""
        try:
            print(f"DEBUG save_user_institution_permissions: discord_id={discord_id}")
            print(f"DEBUG: Input permissions={permissions}")
            
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }

            permission_mapping = {
                'can_view': 'can_view_institution',
                'can_edit': 'can_edit_institution',
                'can_delete': 'can_delete_institution',
                'can_add_employee': 'can_add_employee',
                'can_edit_employee': 'can_edit_employee',
                'can_delete_employee': 'can_delete_employee',
                'can_add_score': 'can_add_score',
                'can_reset_scores': 'can_reset_score',
                'can_deduct_scores': 'can_remove_score',
            }
            managed_codes = set(permission_mapping.values())

            def _get_default_server_id():
                try:
                    settings_resp = requests.get(
                        f"{self.supabase_url}/rest/v1/app_runtime_settings",
                        headers=headers,
                        params={
                            "key": "eq.default_server_key",
                            "select": "value",
                            "limit": "1",
                        },
                        timeout=5,
                    )
                    if settings_resp.status_code == 200 and settings_resp.json():
                        server_key = str(settings_resp.json()[0].get("value") or "").strip()
                        if server_key:
                            srv_resp = requests.get(
                                f"{self.supabase_url}/rest/v1/app_servers",
                                headers=headers,
                                params={
                                    "server_key": f"eq.{server_key}",
                                    "select": "id",
                                    "limit": "1",
                                },
                                timeout=5,
                            )
                            if srv_resp.status_code == 200 and srv_resp.json():
                                return str(srv_resp.json()[0].get("id") or "").strip()
                except Exception as e:
                    print(f"DEBUG: default_server_key lookup failed: {e}")

                try:
                    fallback_resp = requests.get(
                        f"{self.supabase_url}/rest/v1/app_servers",
                        headers=headers,
                        params={
                            "is_active": "eq.true",
                            "select": "id",
                            "order": "server_name.asc",
                            "limit": "1",
                        },
                        timeout=5,
                    )
                    if fallback_resp.status_code == 200 and fallback_resp.json():
                        return str(fallback_resp.json()[0].get("id") or "").strip()
                except Exception as e:
                    print(f"DEBUG: fallback server lookup failed: {e}")

                return ""

            server_id = _get_default_server_id()
            if not server_id:
                print("DEBUG: No server_id found for institution permission save")
                return False

            cities_by_name = {}
            city_name_by_id = {}
            try:
                city_resp = requests.get(
                    f"{self.supabase_url}/rest/v1/cities",
                    headers=headers,
                    params={"select": "id,name"},
                    timeout=5,
                )
                if city_resp.status_code == 200:
                    for row in city_resp.json() or []:
                        city_id = row.get("id")
                        city_name = str(row.get("name") or "").strip()
                        if city_name:
                            cities_by_name[city_name.lower()] = city_id
                        if city_id is not None and city_name:
                            city_name_by_id[city_id] = city_name
            except Exception as e:
                print(f"DEBUG: city lookup failed: {e}")

            institutions_by_key = {}
            try:
                inst_resp = requests.get(
                    f"{self.supabase_url}/rest/v1/institutions",
                    headers=headers,
                    params={"select": "id,name,city_id"},
                    timeout=5,
                )
                if inst_resp.status_code == 200:
                    for row in inst_resp.json() or []:
                        inst_id = row.get("id")
                        inst_name = str(row.get("name") or "").strip()
                        city_id = row.get("city_id")
                        city_name = city_name_by_id.get(city_id, "")
                        key = (city_name.lower(), inst_name.lower())
                        if city_name and inst_name and inst_id is not None:
                            institutions_by_key[key] = inst_id
            except Exception as e:
                print(f"DEBUG: institution lookup failed: {e}")

            existing_resp = requests.get(
                f"{self.supabase_url}/rest/v1/user_server_permissions",
                headers=headers,
                params={
                    "server_id": f"eq.{server_id}",
                    "discord_id": f"eq.{discord_id}",
                    "select": "id,permission_code,institution_name",
                },
                timeout=5,
            )
            if existing_resp.status_code != 200:
                print(f"DEBUG: existing permissions fetch failed: {existing_resp.status_code} {existing_resp.text[:300]}")
                return False

            existing_rows = existing_resp.json() or []
            for row in existing_rows:
                code = str(row.get("permission_code") or "").strip()
                inst_name = str(row.get("institution_name") or "").strip()
                row_id = row.get("id")
                if code in managed_codes and inst_name and row_id:
                    delete_resp = requests.delete(
                        f"{self.supabase_url}/rest/v1/user_server_permissions?id=eq.{row_id}",
                        headers=headers,
                        timeout=5,
                    )
                    if delete_resp.status_code not in (200, 204):
                        print(f"DEBUG: delete existing row failed: {delete_resp.status_code} {delete_resp.text[:300]}")
                        return False

            rows_to_insert = []
            for city_name, institutions in (permissions or {}).items():
                city_label = str(city_name or "").strip()
                if not city_label:
                    continue

                city_id = cities_by_name.get(city_label.lower())
                for inst_name, perm_values in (institutions or {}).items():
                    institution_label = str(inst_name or "").strip()
                    if not institution_label:
                        continue

                    institution_id = institutions_by_key.get((city_label.lower(), institution_label.lower()))

                    for source_perm, enabled in (perm_values or {}).items():
                        if not enabled:
                            continue
                        mapped_code = permission_mapping.get(source_perm)
                        if not mapped_code:
                            continue

                        row = {
                            "server_id": server_id,
                            "discord_id": discord_id,
                            "permission_code": mapped_code,
                            "city_name": city_label,
                            "institution_name": institution_label,
                            "granted": True,
                        }
                        if city_id is not None:
                            row["city_id"] = city_id
                        if institution_id is not None:
                            row["institution_id"] = institution_id
                        rows_to_insert.append(row)

            for row in rows_to_insert:
                insert_resp = requests.post(
                    f"{self.supabase_url}/rest/v1/user_server_permissions",
                    headers=headers,
                    json=row,
                    timeout=5,
                )
                if insert_resp.status_code not in (200, 201):
                    print(f"DEBUG: insert permission row failed: {insert_resp.status_code} {insert_resp.text[:300]}")
                    return False

            print(f"DEBUG: Saved {len(rows_to_insert)} institution permission rows in user_server_permissions")
            return True
        except Exception as e:
            print(f"Error saving institution permissions: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def initialize_all_user_permissions(self) -> Tuple[int, int]:
        """Initialize granular permissions for all users who don't have them yet
        Returns: (users_initialized, total_users)
        """
        try:
            print("🔄 Initializing granular permissions for all users...")
            
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Fetch all users
            url = f"{self.supabase_url}/rest/v1/discord_users?select=id,discord_id,username,granular_permissions"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Error fetching users: {response.status_code} - {response.text}")
                return 0, 0
            
            all_users = response.json()
            total_users = len(all_users)
            users_initialized = 0
            
            # Get all available institutions
            all_institutions = self.get_all_institutions_by_city()
            print(f"Found {total_users} users, {len(all_institutions)} cities with institutions")
            
            # Create default permission structure
            default_permissions = {}
            for city, institutions in all_institutions.items():
                default_permissions[city] = {}
                for institution in institutions:
                    default_permissions[city][institution] = {
                        'can_view': False,
                        'can_edit': False,
                        'can_delete': False,
                        'can_add_employee': False,
                        'can_edit_employee': False,
                        'can_delete_employee': False,
                        'can_add_score': False,
                        'can_reset_scores': False,
                        'can_deduct_scores': False
                    }
            
            # Process each user
            for user in all_users:
                try:
                    user_id = user['id']
                    discord_id = user['discord_id']
                    username = user.get('username', 'Unknown')
                    perms_data = user.get('granular_permissions', {})
                    
                    # Parse if string
                    if isinstance(perms_data, str):
                        try:
                            perms_data = json.loads(perms_data)
                        except:
                            perms_data = {}
                    
                    # Check if user has institutions key or it's empty
                    institutions = perms_data.get('institutions', {})
                    
                    if not institutions or len(institutions) == 0:
                        print(f"  ⚙️ Initializing {username} (id:{discord_id})")
                        
                        # Initialize with default permissions
                        perms_data['institutions'] = default_permissions.copy()
                        
                        # Save back to database
                        update_url = f"{self.supabase_url}/rest/v1/discord_users?id=eq.{user_id}"
                        update_data = {"granular_permissions": json.dumps(perms_data)}
                        
                        update_response = requests.patch(
                            update_url,
                            headers=headers,
                            json=update_data,
                            timeout=5
                        )
                        
                        if update_response.status_code in [200, 204]:
                            users_initialized += 1
                            print(f"    ✅ Initialized successfully")
                        else:
                            print(f"    ❌ Failed to save: {update_response.status_code}")
                    else:
                        # User already has institutions, but check if missing any institutions
                        missing_count = 0
                        for city, insts in all_institutions.items():
                            if city not in institutions:
                                institutions[city] = {}
                                missing_count += 1
                            
                            for inst in insts:
                                if inst not in institutions[city]:
                                    institutions[city][inst] = {
                                        'can_view': False,
                                        'can_edit': False,
                                        'can_delete': False,
                                        'can_add_employee': False,
                                        'can_edit_employee': False,
                                        'can_delete_employee': False,
                                        'can_add_score': False,
                                        'can_reset_scores': False,
                                        'can_deduct_scores': False
                                    }
                                    missing_count += 1
                        
                        if missing_count > 0:
                            print(f"  ⚙️ Adding {missing_count} missing institutions for {username}")
                            perms_data['institutions'] = institutions
                            
                            update_url = f"{self.supabase_url}/rest/v1/discord_users?id=eq.{user_id}"
                            update_data = {"granular_permissions": json.dumps(perms_data)}
                            
                            update_response = requests.patch(
                                update_url,
                                headers=headers,
                                json=update_data,
                                timeout=5
                            )
                            
                            if update_response.status_code in [200, 204]:
                                users_initialized += 1
                                print(f"    ✅ Updated successfully")
                
                except Exception as e:
                    print(f"  ❌ Error processing user {username}: {e}")
                    continue
            
            print(f"\n✅ Initialization complete: {users_initialized}/{total_users} users initialized/updated")
            return users_initialized, total_users
            
        except Exception as e:
            print(f"Error initializing user permissions: {e}")
            import traceback
            traceback.print_exc()
            return 0, 0
    
    def check_user_institution_permission(self, discord_id: str, city: str, institution: str, permission: str) -> bool:
        """Check if user has specific permission for an institution
        
        Args:
            discord_id: User's Discord ID
            city: City name (e.g., 'BlackWater')
            institution: Institution name (e.g., 'Politie')
            permission: 'can_view', 'can_edit', 'can_delete', 'can_reset_scores', 'can_deduct_scores'
        
        Returns:
            True if user has permission, False otherwise
        """
        try:
            perms = self.get_user_institution_permissions(discord_id)
            
            # Navigate the structure: institutions -> city -> institution -> permission
            if city in perms and institution in perms[city]:
                return perms[city][institution].get(permission, False)
            
            return False
        except Exception as e:
            print(f"Error checking institution permission: {e}")
            return False
    
    def can_add_employee(self, discord_id: str, city: str, institution: str) -> bool:
        """Check if user can add employees to this institution"""
        return self.check_user_institution_permission(discord_id, city, institution, 'can_add_employee')
    
    def can_edit_employee(self, discord_id: str, city: str, institution: str) -> bool:
        """Check if user can edit employees in this institution"""
        return self.check_user_institution_permission(discord_id, city, institution, 'can_edit_employee')
    
    def can_delete_employee(self, discord_id: str, city: str, institution: str) -> bool:
        """Check if user can delete employees from this institution"""
        return self.check_user_institution_permission(discord_id, city, institution, 'can_delete_employee')
    
    def can_add_score(self, discord_id: str, city: str, institution: str) -> bool:
        """Check if user can add/edit scores (punctaj) in this institution"""
        return self.check_user_institution_permission(discord_id, city, institution, 'can_add_score')
    
    def can_add_city(self, discord_id: str) -> bool:
        """Check if user can add cities"""
        perms = self.get_user_permissions(discord_id)
        return perms.get('can_add_city', False)
    
    def can_edit_city(self, discord_id: str) -> bool:
        """Check if user can edit cities"""
        perms = self.get_user_permissions(discord_id)
        return perms.get('can_edit_city', False)
    
    def can_delete_city(self, discord_id: str) -> bool:
        """Check if user can delete cities"""
        perms = self.get_user_permissions(discord_id)
        return perms.get('can_delete_city', False)
    
    def get_user_permissions(self, discord_id: str) -> Dict:
        """
        Get global permissions for user (not institution-specific)
        Priority:
        1. users_permissions.json (local encrypted cache - FAST)
        2. Supabase (fallback)
        """
        try:
            # FIRST: Try to load from users_permissions.json (LOCAL ENCRYPTED CACHE)
            import os
            
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
                    
                    users = json_data.get('users', {})
                    user_key = str(discord_id)
                    
                    if user_key in users:
                        user_perms = users[user_key]
                        perms_dict = user_perms.get('permissions', {})
                        
                        if isinstance(perms_dict, dict) and perms_dict:
                            return perms_dict
                except Exception as e:
                    print(f"[PermManager] Note: Could not read users_permissions.json: {e}")
            
            # FALLBACK: Fetch from Supabase
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.supabase_url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=permissions"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    perm_str = data[0].get('permissions', '{}')
                    try:
                        return json.loads(perm_str)
                    except:
                        return {}
            return {}
        except Exception as e:
            print(f"Error fetching user permissions: {e}")
            return {}


class PermissionUIFrame:
    """UI Frame for managing user permissions with checkboxes"""
    
    def __init__(self, parent, user_data: Dict, permission_manager: PermissionManager, action_logger=None, discord_auth=None):
        self.parent = parent
        self.user_data = user_data
        self.permission_manager = permission_manager
        self.action_logger = action_logger
        self.discord_auth = discord_auth
        self.discord_id = user_data.get('discord_id', '')
        self.username = user_data.get('username', 'Unknown')
        
        print(f"DEBUG: PermissionUIFrame init - username: {self.username}, discord_id: {self.discord_id}")
        
        # Get current permissions
        self.current_permissions = permission_manager.get_all_permissions_for_user(self.discord_id)
        print(f"DEBUG: Current permissions loaded: {self.current_permissions}")
        
        self.checkbox_vars = {}
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create permission management UI"""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text=f"👤 {self.username}",
            font=("Segoe UI", 12, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame,
            text=f"ID: {self.discord_id[:10]}...",
            font=("Segoe UI", 9),
            foreground="gray"
        ).pack(side=tk.LEFT, padx=(20, 0))
        
        # Permissions notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each permission category
        for category, perms in self.permission_manager.PERMISSIONS.items():
            tab_frame = ttk.Frame(notebook)
            notebook.add(tab_frame, text=f"📋 {category}")
            
            # Create scrollable frame
            canvas = tk.Canvas(tab_frame)
            scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Add checkboxes for each permission
            for perm_id, perm_name in perms.items():
                var = tk.BooleanVar(
                    value=self.current_permissions[category].get(perm_id, False)
                )
                self.checkbox_vars[perm_id] = var
                
                check = ttk.Checkbutton(
                    scrollable_frame,
                    text=perm_name,
                    variable=var,
                    padding=10
                )
                check.pack(anchor=tk.W, fill=tk.X, padx=10, pady=5)
            
            # Pack scrollbar and canvas
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="💾 Salvează Permisiuni",
            command=self.save_permissions
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Resetează la Default",
            command=self.reset_permissions
        ).pack(side=tk.LEFT, padx=5)
    
    def save_permissions(self):
        """Save current permission selections"""
        permissions = {}
        for perm_id, var in self.checkbox_vars.items():
            permissions[perm_id] = var.get()
        
        if self.permission_manager.save_user_permissions(self.discord_id, permissions):
            messagebox.showinfo(
                "Succes",
                f"✅ Permisiuni salvate pentru {self.username}!"
            )
            
            # Log permission change
            if self.action_logger and self.discord_auth:
                try:
                    discord_id = self.discord_auth.get_discord_id() if self.discord_auth else ""
                    discord_username = self.discord_auth.user_info.get('username', discord_id) if self.discord_auth and self.discord_auth.user_info else discord_id
                    
                    self.action_logger.log_permission_change(
                        discord_id=discord_id,
                        target_user=self.username,
                        permission_changes=permissions,
                        discord_username=discord_username
                    )
                    print(f"✅ Permission change logged for {self.username}")
                except Exception as e:
                    print(f"⚠️ Error logging permission change: {e}")
        else:
            messagebox.showerror(
                "Eroare",
                f"❌ Eroare la salvarea permisiunilor!"
            )
    
    def reset_permissions(self):
        """Reset all permissions to default (none checked)"""
        if messagebox.askyesno(
            "Confirmare",
            f"Ștergi toate permisiunile pentru {self.username}?"
        ):
            for var in self.checkbox_vars.values():
                var.set(False)


def open_granular_permissions_panel(root, supabase_sync, discord_auth, data_dir: str = None, action_logger=None):
    """Open granular permissions management panel"""
    
    if not supabase_sync:
        messagebox.showerror("Eroare", "Supabase nu este configurat!")
        return
    
    # 🚨 SECURITY CHECK: Verifica dacă utilizatorul are permisiunea de a modifica permisiuni
    if not discord_auth:
        messagebox.showerror(
            "Eroare de Autentificare",
            "❌ Autentificare necesară pentru a accesa panoul de permisiuni!"
        )
        print(f"🚨 SECURITY ALERT: Attempt to access permissions panel without authentication!")
        return
    
    # Verifica permisiunea de management
    is_superuser = discord_auth.is_superuser() if hasattr(discord_auth, 'is_superuser') else False
    has_manage_permission = discord_auth.has_granular_permission('can_manage_user_permissions') if hasattr(discord_auth, 'has_granular_permission') else False
    
    if not (is_superuser or has_manage_permission):
        messagebox.showerror(
            "Acces Refuzat",
            "❌ NU AI PERMISIUNEA DE A MODIFICA PERMISIUNI!\n\n"
            "Doar Superadmini și utilizatori cu dreapta 'Poate DA PERMISIUNI'\n"
            "pot accesa acest panou.\n\n"
            "📞 Contactează un administrator pentru mai multe detalii."
        )
        
        # Log security incident
        current_user = discord_auth.get_username() if hasattr(discord_auth, 'get_username') else "Unknown"
        current_id = discord_auth.get_discord_id() if hasattr(discord_auth, 'get_discord_id') else "Unknown"
        print(f"🚨 SECURITY ALERT: User {current_user} (ID: {current_id}) tried to access permissions panel WITHOUT authorization!")
        
        # Log to action logger if available
        try:
            if action_logger and hasattr(action_logger, 'log_action'):
                action_logger.log_action(
                    action="UNAUTHORIZED_ACCESS_ATTEMPT",
                    details=f"Tried to access permissions panel without 'can_manage_user_permissions' permission",
                    status="BLOCKED"
                )
        except Exception as e:
            print(f"⚠️  Could not log security incident: {e}")
        
        return
    
    print(f"✅ SECURITY: User {discord_auth.get_username() if hasattr(discord_auth, 'get_username') else 'Unknown'} authorized to access permissions panel")
    
    # Create permission managers
    perm_manager = PermissionManager(supabase_sync)
    
    # Create hierarchy permission manager (for granular permissions)
    hierarchy_perm_manager = GlobalHierarchyPermissionManager(supabase_sync)
    
    # Create institution permission manager if data_dir provided
    institution_perm_manager = None
    if data_dir:
        institution_perm_manager = InstitutionPermissionManager(supabase_sync, data_dir)
    
    # Create main window - LARGER for better usability
    permissions_window = tk.Toplevel(root)
    permissions_window.title("🔐 Gestiune Permisiuni Granulare")
    
    # Responsive window sizing based on screen resolution
    screenwidth = permissions_window.winfo_screenwidth()
    screenheight = permissions_window.winfo_screenheight()
    
    # Calculate responsive size: 85% of screen but within bounds
    perm_width = max(1000, min(1600, int(screenwidth * 0.90)))
    perm_height = max(700, min(1000, int(screenheight * 0.85)))
    
    permissions_window.geometry(f"{perm_width}x{perm_height}")
    permissions_window.minsize(1000, 700)  # Minimum size
    permissions_window.grab_set()
    permissions_window.transient(root)
    
    # Center window
    permissions_window.update_idletasks()
    x = (screenwidth // 2) - (perm_width // 2)
    y = (screenheight // 2) - (perm_height // 2)
    permissions_window.geometry(f"+{x}+{y}")
    
    # ==================== TOP TOOLBAR ====================
    top_toolbar = ttk.Frame(permissions_window, relief=tk.RAISED, borderwidth=2)
    top_toolbar.pack(fill=tk.X, padx=0, pady=0)
    
    # Left side: Title
    left_title = ttk.Frame(top_toolbar)
    left_title.pack(side=tk.LEFT, padx=15, pady=10)
    
    ttk.Label(
        left_title,
        text="🔐 Gestiune Permisiuni Granulare",
        font=("Segoe UI", 14, "bold")
    ).pack(side=tk.LEFT)
    
    ttk.Label(
        left_title,
        text="│ Selectează și modifică permisiuni",
        font=("Segoe UI", 9),
        foreground="gray"
    ).pack(side=tk.LEFT, padx=(10, 0))
    
    # Right side: Quick actions
    right_actions = ttk.Frame(top_toolbar)
    right_actions.pack(side=tk.RIGHT, padx=15, pady=10)
    
    ttk.Button(
        right_actions,
        text="🔄 Reîncarcă",
        width=12
    ).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(
        right_actions,
        text="❌ Închide",
        width=12,
        command=permissions_window.destroy
    ).pack(side=tk.LEFT, padx=5)
    
    # ==================== USER SELECTION TOOLBAR ====================
    selection_toolbar = ttk.Frame(permissions_window, relief=tk.FLAT)
    selection_toolbar.pack(fill=tk.X, padx=15, pady=(10, 5))
    
    ttk.Label(selection_toolbar, text="👤 Selectează Utilizator:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
    
    # Get all users
    try:
        headers = {
            "apikey": supabase_sync.key,
            "Authorization": f"Bearer {supabase_sync.key}",
            "Content-Type": "application/json"
        }
        
        # Compat: încearcă surse multiple (schema veche + schema nouă)
        sources = [
            ("discord_users", "id,discord_id,username,is_superuser,is_admin,can_view,can_edit,can_delete"),
            ("discord_login_users", "id,discord_id,username"),
            ("v_permission_assignable_users", "discord_id,username")
        ]

        response = None
        users = []

        for table_name, select_fields in sources:
            url = f"{supabase_sync.url}/rest/v1/{table_name}?select={select_fields}"
            print(f"DEBUG: Fetching users from: {url}")
            response = requests.get(url, headers=headers, timeout=5)

            print(f"DEBUG: Response status ({table_name}): {response.status_code}")
            print(f"DEBUG: Response text ({table_name}): {response.text[:500]}")

            if response.status_code != 200:
                continue

            raw_users = response.json() or []
            if not raw_users:
                continue

            deduped = {}
            for row in raw_users:
                discord_id = str(row.get('discord_id', '')).strip()
                username = str(row.get('username', '')).strip()
                if not discord_id or not username:
                    continue
                deduped[discord_id] = {
                    'id': row.get('id'),
                    'discord_id': discord_id,
                    'username': username,
                    'is_superuser': bool(row.get('is_superuser', False)),
                    'is_admin': bool(row.get('is_admin', False)),
                    'can_view': bool(row.get('can_view', False)),
                    'can_edit': bool(row.get('can_edit', False)),
                    'can_delete': bool(row.get('can_delete', False)),
                }

            users = list(deduped.values())
            if users:
                print(f"DEBUG: Loaded {len(users)} users from {table_name}")
                break
        
        if response is not None and response.status_code == 200 and users:
            
            # Function to determine role from boolean columns
            def get_user_role(user_data):
                if user_data.get('is_superuser'):
                    return 'Superuser'
                elif user_data.get('is_admin'):
                    return 'Admin'
                elif user_data.get('can_view'):
                    return 'User'
                else:
                    return 'Viewer'
            
            # Users dropdown - show username and real role
            user_var = tk.StringVar()
            user_combo = ttk.Combobox(
                selection_toolbar,
                textvariable=user_var,
                values=[f"👤 {u['username']} ({get_user_role(u)})" for u in users],
                state="readonly",
                width=50
            )
            user_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            # Create tabbed interface - 4 NIVELURI DE PERMISIUNI
            main_notebook = ttk.Notebook(permissions_window)
            main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            def create_scrollable_tab_content(tab_parent):
                """Create a scrollable content frame for a notebook tab."""
                wrapper = ttk.Frame(tab_parent)
                wrapper.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                canvas = tk.Canvas(wrapper, bg="white", highlightthickness=0)
                scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)

                inner_frame = ttk.Frame(canvas)
                canvas_window_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

                def _on_inner_configure(_event):
                    canvas.configure(scrollregion=canvas.bbox("all"))

                def _on_canvas_configure(event):
                    try:
                        canvas.itemconfigure(canvas_window_id, width=event.width)
                    except Exception:
                        pass

                def _on_mousewheel(event):
                    try:
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    except Exception:
                        pass

                def _bind_mousewheel(_event=None):
                    try:
                        canvas.bind_all("<MouseWheel>", _on_mousewheel)
                    except Exception:
                        pass

                def _unbind_mousewheel(_event=None):
                    try:
                        canvas.unbind_all("<MouseWheel>")
                    except Exception:
                        pass

                inner_frame.bind("<Configure>", _on_inner_configure)
                canvas.bind("<Configure>", _on_canvas_configure)
                canvas.bind("<Enter>", _bind_mousewheel)
                canvas.bind("<Leave>", _unbind_mousewheel)
                inner_frame.bind("<Enter>", _bind_mousewheel)
                inner_frame.bind("<Leave>", _unbind_mousewheel)

                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                return inner_frame
            
            # TAB 1: Admin Permissions
            admin_tab = ttk.Frame(main_notebook)
            main_notebook.add(admin_tab, text="🔐 Admin")
            admin_content_frame = create_scrollable_tab_content(admin_tab)
            
            # TAB 2: Global Permissions
            global_tab = ttk.Frame(main_notebook)
            main_notebook.add(global_tab, text="🌍 Global")
            global_content_frame = create_scrollable_tab_content(global_tab)
            
            # TAB 3: City Level Permissions
            city_tab = ttk.Frame(main_notebook)
            main_notebook.add(city_tab, text="🏙️ Orașe")
            city_content_frame = create_scrollable_tab_content(city_tab)
            
            # TAB 4: Institution Permissions
            if institution_perm_manager:
                inst_tab = ttk.Frame(main_notebook)
                main_notebook.add(inst_tab, text="🏢 Instituții")

                inst_content_frame = create_scrollable_tab_content(inst_tab)
            else:
                inst_content_frame = None
            
            # Current UI frame references
            current_inst_ui = [None]
            current_ui = [None]
            current_inst_ui = [None]
            
            def show_institution_permissions(selected_user=None):
                """Show institution permissions for selected user"""
                print(f"DEBUG show_institution_permissions: selected_user={selected_user}")
                
                if selected_user is None:
                    selected = user_var.get()
                    if not selected:
                        print(f"DEBUG: No user selected, returning")
                        return
                    # Find selected user
                    username = selected.split(" (")[0].replace("👤 ", "").strip()
                    print(f"DEBUG: Looking for username: {username}")
                    selected_user = next(
                        (u for u in users if u['username'] == username),
                        None
                    )
                    print(f"DEBUG: Found user: {selected_user}")
                
                if not selected_user or not inst_content_frame:
                    print(f"DEBUG: Cannot show permissions - selected_user={selected_user}, inst_content_frame={inst_content_frame}")
                    return
                
                print(f"DEBUG: Clearing frame...")
                # Clear previous UI
                for widget in inst_content_frame.winfo_children():
                    widget.destroy()
                
                print(f"DEBUG: Creating institution permissions UI for {selected_user.get('username', 'Unknown')}")
                # Create institution permissions UI
                create_institution_permissions_ui(
                    inst_content_frame,
                    selected_user,
                    institution_perm_manager
                )
            
            def create_institution_permissions_ui(parent, user_data, inst_manager):
                """Create UI for institution permissions (grouped by city)"""
                print(f"DEBUG create_institution_permissions_ui: parent={parent}, user_data={user_data}")
                
                discord_id = user_data.get('discord_id', '')
                username = user_data.get('username', 'Unknown')
                
                print(f"DEBUG: Creating UI for {username} (discord_id={discord_id})")
                
                # Header
                header = ttk.Frame(parent)
                header.pack(fill=tk.X, pady=(0, 15))
                
                ttk.Label(
                    header,
                    text=f"👤 {username}",
                    font=("Segoe UI", 12, "bold")
                ).pack(side=tk.LEFT)
                
                # Get all institutions grouped by city
                institutions_by_city = inst_manager.get_all_institutions_by_city()
                print(f"DEBUG: institutions_by_city = {institutions_by_city}")
                
                current_perms = inst_manager.get_user_institution_permissions(discord_id)
                print(f"DEBUG: current_perms = {current_perms}")
                
                if not institutions_by_city:
                    ttk.Label(
                        parent,
                        text="❌ Nu au fost găsite instituții",
                        font=("Segoe UI", 10)
                    ).pack(pady=20)
                    print("DEBUG: No institutions found!")
                    return
                
                # Create city groups directly (no canvas - simpler approach)
                city_vars = {}
                
                for city in sorted(institutions_by_city.keys()):
                    print(f"DEBUG: Processing city: {city}")
                    institutions = institutions_by_city[city]
                    
                    # City header
                    city_frame = ttk.LabelFrame(parent, text=f"🏙️ {city}", padding=10)
                    city_frame.pack(fill=tk.X, padx=5, pady=5)
                    
                    city_vars[city] = {}
                    
                    # Initialize current permissions for this city if not exists
                    if city not in current_perms:
                        current_perms[city] = {}
                    
                    # Create institution groups for this city
                    for institution in institutions:
                        print(f"DEBUG: Processing institution: {institution}")
                        inst_frame = ttk.LabelFrame(city_frame, text=f"🏢 {institution}", padding=10)
                        inst_frame.pack(fill=tk.X, padx=5, pady=3)
                        
                        if institution not in current_perms[city]:
                            current_perms[city][institution] = {
                                'can_view': False,
                                'can_edit': False,
                                'can_delete': False,
                                'can_add_employee': False,
                                'can_edit_employee': False,
                                'can_delete_employee': False,
                                'can_add_score': False,
                                'can_reset_scores': False,
                                'can_deduct_scores': False
                            }
                        
                        city_vars[city][institution] = {}
                        perms_to_show = ['can_view', 'can_edit', 'can_delete', 'can_add_employee', 'can_delete_employee', 'can_add_score', 'can_reset_scores', 'can_deduct_scores']
                        perm_labels = {
                            'can_view': '👁️ Vizualizare',
                            'can_edit': '✏️ Editare',
                            'can_delete': '❌ Ștergere',
                            'can_add_employee': '➕ Adaugă Angajat',
                            'can_delete_employee': '❌ Șterge Angajat',
                            'can_add_score': '➕ Adaugă Puncte',
                            'can_reset_scores': '🔄 Reset Punctaj',
                            'can_deduct_scores': '📉 Scade Puncte'
                        }
                        
                        for perm in perms_to_show:
                            var = tk.BooleanVar(value=current_perms[city][institution].get(perm, False))
                            city_vars[city][institution][perm] = var
                            
                            check = ttk.Checkbutton(
                                inst_frame,
                                text=perm_labels[perm],
                                variable=var,
                                padding=5
                            )
                            check.pack(anchor=tk.W, fill=tk.X)
                
                print("DEBUG: All frames created!")
                
                # Buttons frame
                button_frame = ttk.Frame(parent)
                button_frame.pack(fill=tk.X, pady=(15, 0))
                
                def save_institution_permissions():
                    """Save institution permissions for all cities"""
                    try:
                        new_perms = {}
                        for city, institutions in city_vars.items():
                            new_perms[city] = {}
                            for institution, perms in institutions.items():
                                new_perms[city][institution] = {perm: var.get() for perm, var in perms.items()}
                        
                        print(f"\n{'='*80}")
                        print(f"📝 PERMISSION SAVE REQUEST")
                        print(f"{'='*80}")
                        print(f"Target User: {username} (ID: {discord_id})")
                        print(f"Total Cities: {len(new_perms)}")
                        
                        # Count changes
                        total_perms = 0
                        enabled_perms = 0
                        for city, institutions in new_perms.items():
                            for inst, perms in institutions.items():
                                for perm, value in perms.items():
                                    total_perms += 1
                                    if value:
                                        enabled_perms += 1
                        
                        print(f"Total Permissions: {total_perms}")
                        print(f"Enabled Permissions: {enabled_perms}")
                        print(f"Disabled Permissions: {total_perms - enabled_perms}")
                        print(f"\nDetailed Permissions:")
                        for city, institutions in new_perms.items():
                            print(f"  🏙️  {city}:")
                            for inst, perms in institutions.items():
                                print(f"      🏢 {inst}:")
                                for perm, value in perms.items():
                                    status = "✅" if value else "❌"
                                    print(f"         {status} {perm}: {value}")
                        print(f"{'='*80}\n")
                        
                        # Store institution vars for save_all_permissions
                        permissions_window.institution_vars = city_vars
                        
                        # 🔐 SECURITY: Log who is making this change
                        print(f"🔐 Change initiated by: {discord_auth.get_username() if hasattr(discord_auth, 'get_username') else 'Unknown'}")
                        
                        if inst_manager.save_user_institution_permissions(discord_id, new_perms):
                            print(f"✅ DATABASE SAVE: SUCCESS")
                            messagebox.showinfo("Succes", f"✅ Permisiuni salvate pentru {username}!\n\n📝 Orice noi instituții/orașe adăugate în viitor vor fi salvate automat.\n\n⏳ Clientul se va reîncărca automat la sigurii conexiuni...")
                            
                            # ✅ RELOAD PERMISSIONS FOR THE UPDATED USER (if cached in memory)
                            # This will force the client to reload from users_permissions.json on next startup
                            # or if the UsersPermissionsJsonManager is monitoring
                            print(f"✅ Permissions updated for {username} - they will reload on next sync")
                            
                            # Trigger a JSON file update/sync if available
                            try:
                                from users_permissions_json_manager import UsersPermissionsJsonManager
                                json_manager = UsersPermissionsJsonManager(data_dir)
                                # Force a quick sync to update users_permissions.json
                                if hasattr(json_manager, 'download_from_cloud'):
                                    json_manager.download_from_cloud()
                                    print(f"✅ Local users_permissions.json synchronized from Supabase")
                            except Exception as e:
                                print(f"⚠️  Could not sync users_permissions.json: {e}")
                        else:
                            print(f"❌ DATABASE SAVE: FAILED")
                            messagebox.showerror("Eroare", "❌ Eroare la salvare!\n\nVerificați conexiunea la baza de date și logurile de eroare.")
                    except Exception as e:
                        print(f"ERROR in save_institution_permissions: {e}")
                        import traceback
                        traceback.print_exc()
                        messagebox.showerror("Eroare", f"❌ Eroare la salvare: {str(e)}")
                
                ttk.Button(
                    button_frame,
                    text="💾 Salvează Permisiuni",
                    command=save_institution_permissions
                ).pack(side=tk.LEFT, padx=5)
                
                print(f"DEBUG: UI created successfully for {username}")
            
            def create_admin_tab_content(parent, user_data):
                """Create admin tab content"""
                discord_id = user_data.get('discord_id', '')
                var_manage = tk.BooleanVar()
                var_revoke = tk.BooleanVar()
                var_see_admin_button = tk.BooleanVar()
                var_see_admin_panel = tk.BooleanVar()
                var_see_permissions_button = tk.BooleanVar()

                def load_server_visibility_for_user(target_discord_id):
                    servers = []
                    visible_server_ids = set()
                    try:
                        servers_response = requests.get(
                            f"{supabase_sync.url}/rest/v1/app_servers?select=id,server_key,server_name,is_active&order=server_name.asc",
                            headers=headers,
                            timeout=5
                        )
                        if servers_response.status_code == 200:
                            servers = servers_response.json() or []
                        else:
                            print(f"DEBUG: app_servers fetch failed: {servers_response.status_code} {servers_response.text[:300]}")

                        visible_response = requests.get(
                            f"{supabase_sync.url}/rest/v1/user_server_permissions?select=server_id&discord_id=eq.{target_discord_id}&permission_code=eq.can_view_server&granted=eq.true",
                            headers=headers,
                            timeout=5
                        )
                        if visible_response.status_code == 200:
                            for row in (visible_response.json() or []):
                                server_id = str(row.get('server_id', '')).strip()
                                if server_id:
                                    visible_server_ids.add(server_id)
                        else:
                            print(f"DEBUG: user_server_permissions(can_view_server) fetch failed: {visible_response.status_code} {visible_response.text[:300]}")
                    except Exception as e:
                        print(f"DEBUG: Eroare load_server_visibility_for_user: {e}")

                    return servers, visible_server_ids
                
                # Citit permisiunile salvate din Supabase
                try:
                    headers = {
                        "apikey": supabase_sync.key,
                        "Authorization": f"Bearer {supabase_sync.key}",
                        "Content-Type": "application/json"
                    }
                    url = f"{supabase_sync.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=granular_permissions"
                    response = requests.get(url, headers=headers, timeout=5)
                    
                    if response.status_code == 200 and response.json():
                        data = response.json()[0]
                        perms_data = data.get('granular_permissions', {})
                        if isinstance(perms_data, str):
                            perms_data = json.loads(perms_data)
                        
                        global_perms = perms_data.get('global', {})
                        var_manage.set(global_perms.get('can_manage_user_permissions', False))
                        var_revoke.set(global_perms.get('can_revoke_user_permissions', False))
                        var_see_admin_button.set(global_perms.get('can_see_admin_button', False))
                        var_see_admin_panel.set(global_perms.get('can_see_admin_panel', False))
                        var_see_permissions_button.set(global_perms.get('can_see_user_permissions_button', False))
                except Exception as e:
                    print(f"DEBUG: Eroare citire admin perms: {e}")
                
                ttk.Label(parent, text="🔐 Admin Controls", font=("Segoe UI", 11, "bold")).pack(padx=10, pady=10)
                
                ttk.Checkbutton(
                    parent,
                    text="✅ Poate DA PERMISIUNI altor utilizatori",
                    variable=var_manage
                ).pack(anchor=tk.W, padx=20, pady=5)
                
                ttk.Checkbutton(
                    parent,
                    text="✅ Poate SCOATE DREPTURI altor utilizatori",
                    variable=var_revoke
                ).pack(anchor=tk.W, padx=20, pady=5)
                
                # Separator
                ttk.Separator(parent, orient="horizontal").pack(fill=tk.X, padx=20, pady=15)
                
                ttk.Label(parent, text="👁️ Vizibilitate Butoane Admin", font=("Segoe UI", 10, "bold")).pack(padx=10, pady=(10, 5))
                
                ttk.Checkbutton(
                    parent,
                    text="👁️ Poate VEDEA Butonul ⚙️ Admin (din Sidebar)",
                    variable=var_see_admin_button
                ).pack(anchor=tk.W, padx=20, pady=3)
                
                ttk.Checkbutton(
                    parent,
                    text="👁️ Poate VEDEA 🛡️ Admin Panel",
                    variable=var_see_admin_panel
                ).pack(anchor=tk.W, padx=20, pady=3)
                
                ttk.Checkbutton(
                    parent,
                    text="👁️ Poate VEDEA 🔐 Permisiuni Utilizatori",
                    variable=var_see_permissions_button
                ).pack(anchor=tk.W, padx=20, pady=3)

                ttk.Separator(parent, orient="horizontal").pack(fill=tk.X, padx=20, pady=15)
                ttk.Label(parent, text="🖥️ Poate vizualiza server", font=("Segoe UI", 10, "bold")).pack(padx=10, pady=(10, 5))

                server_visibility_vars = {}
                servers, visible_server_ids = load_server_visibility_for_user(discord_id)

                if servers:
                    servers_frame = ttk.Frame(parent)
                    servers_frame.pack(fill=tk.X, padx=20, pady=(0, 6))

                    for server in servers:
                        server_id = str(server.get('id', '')).strip()
                        server_key = str(server.get('server_key', '')).strip() or 'unknown'
                        server_name = str(server.get('server_name', '')).strip() or server_key
                        is_active = bool(server.get('is_active', True))

                        if not server_id:
                            continue

                        label = f"{server_name} ({server_key})"
                        if not is_active:
                            label = f"{label} [INACTIV]"

                        var_visible = tk.BooleanVar(value=(server_id in visible_server_ids))
                        server_visibility_vars[server_id] = {
                            'var': var_visible,
                            'server_key': server_key,
                            'server_name': server_name
                        }

                        ttk.Checkbutton(
                            servers_frame,
                            text=f"👁️ {label}",
                            variable=var_visible
                        ).pack(anchor=tk.W, padx=5, pady=2)
                else:
                    ttk.Label(
                        parent,
                        text="⚠️ Nu există servere înregistrate în app_servers",
                        foreground="gray"
                    ).pack(anchor=tk.W, padx=20, pady=4)
                
                return {
                    'can_manage_user_permissions': var_manage, 
                    'can_revoke_user_permissions': var_revoke,
                    'can_see_admin_button': var_see_admin_button,
                    'can_see_admin_panel': var_see_admin_panel,
                    'can_see_user_permissions_button': var_see_permissions_button,
                    '__server_visibility__': server_visibility_vars
                }
            
            def create_global_tab_content(parent, user_data):
                """Create global tab content"""
                discord_id = user_data.get('discord_id', '')
                var_cities = tk.BooleanVar()
                var_edit_cities = tk.BooleanVar()
                var_delete_cities = tk.BooleanVar()
                
                # Citit permisiunile salvate din Supabase
                try:
                    headers = {
                        "apikey": supabase_sync.key,
                        "Authorization": f"Bearer {supabase_sync.key}",
                        "Content-Type": "application/json"
                    }
                    url = f"{supabase_sync.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=granular_permissions"
                    response = requests.get(url, headers=headers, timeout=5)
                    
                    if response.status_code == 200 and response.json():
                        data = response.json()[0]
                        perms_data = data.get('granular_permissions', {})
                        if isinstance(perms_data, str):
                            perms_data = json.loads(perms_data)
                        
                        global_perms = perms_data.get('global', {})
                        var_cities.set(global_perms.get('can_add_city', False))
                        var_edit_cities.set(global_perms.get('can_edit_city', False))
                        var_delete_cities.set(global_perms.get('can_delete_city', False))
                except Exception as e:
                    print(f"DEBUG: Eroare citire global perms: {e}")
                
                ttk.Label(parent, text="🌍 Global Permissions", font=("Segoe UI", 11, "bold")).pack(padx=10, pady=10)
                
                ttk.Checkbutton(
                    parent,
                    text="✅ Poate ADAUGĂ ORAȘE noi",
                    variable=var_cities
                ).pack(anchor=tk.W, padx=20, pady=5)
                
                ttk.Checkbutton(
                    parent,
                    text="✅ Poate EDITEAZĂ ORAȘE existente",
                    variable=var_edit_cities
                ).pack(anchor=tk.W, padx=20, pady=5)
                
                ttk.Checkbutton(
                    parent,
                    text="✅ Poate ȘTERGE ORAȘE",
                    variable=var_delete_cities
                ).pack(anchor=tk.W, padx=20, pady=5)
                
                return {'can_add_city': var_cities, 'can_edit_city': var_edit_cities, 'can_delete_city': var_delete_cities}
            
            def create_city_tab_content(parent, user_data):
                """Create city level tab content"""
                discord_id = user_data.get('discord_id', '')
                city_vars_dict = {}
                
                # Citit permisiunile salvate din Supabase
                saved_city_perms = {}
                try:
                    headers = {
                        "apikey": supabase_sync.key,
                        "Authorization": f"Bearer {supabase_sync.key}",
                        "Content-Type": "application/json"
                    }
                    url = f"{supabase_sync.url}/rest/v1/discord_users?discord_id=eq.{discord_id}&select=granular_permissions"
                    response = requests.get(url, headers=headers, timeout=5)
                    
                    if response.status_code == 200 and response.json():
                        data = response.json()[0]
                        perms_data = data.get('granular_permissions', {})
                        if isinstance(perms_data, str):
                            perms_data = json.loads(perms_data)
                        saved_city_perms = perms_data.get('cities', {})
                except Exception as e:
                    print(f"DEBUG: Eroare citire city perms: {e}")
                
                ttk.Label(parent, text="🏙️ City Level - Permisiuni pe Instituții", font=("Segoe UI", 11, "bold")).pack(padx=10, pady=10)
                
                # Get all cities
                try:
                    cities_response = requests.get(
                        f"{supabase_sync.url}/rest/v1/cities?select=name",
                        headers={
                            "apikey": supabase_sync.key,
                            "Authorization": f"Bearer {supabase_sync.key}"
                        },
                        timeout=5
                    )
                    if cities_response.status_code == 200:
                        cities = [row['name'] for row in cities_response.json()]
                        for city in sorted(cities):
                            city_vars_dict[city] = {}
                            
                            # Frame pentru fiecare oraș
                            city_frame = ttk.LabelFrame(parent, text=f"🏙️ {city}", padding=10)
                            city_frame.pack(fill=tk.X, padx=10, pady=5)
                            
                            # Get saved permissions for this city
                            city_saved_perms = saved_city_perms.get(city, {})
                            
                            # Adaugă instituții
                            var_add = tk.BooleanVar(value=city_saved_perms.get('can_add_institutions', False))
                            city_vars_dict[city]['add'] = var_add
                            ttk.Checkbutton(
                                city_frame,
                                text="➕ Poate ADAUGĂ INSTITUȚII",
                                variable=var_add
                            ).pack(anchor=tk.W, padx=10, pady=2)
                            
                            # Editează instituții
                            var_edit = tk.BooleanVar(value=city_saved_perms.get('can_edit_institutions', False))
                            city_vars_dict[city]['edit'] = var_edit
                            ttk.Checkbutton(
                                city_frame,
                                text="✏️ Poate EDITEAZĂ INSTITUȚII",
                                variable=var_edit
                            ).pack(anchor=tk.W, padx=10, pady=2)
                            
                            # Șterge instituții
                            var_delete = tk.BooleanVar(value=city_saved_perms.get('can_delete_institutions', False))
                            city_vars_dict[city]['delete'] = var_delete
                            ttk.Checkbutton(
                                city_frame,
                                text="❌ Poate ȘTERGE INSTITUȚII",
                                variable=var_delete
                            ).pack(anchor=tk.W, padx=10, pady=2)
                except Exception as e:
                    print(f"Error loading cities: {e}")
                
                return city_vars_dict
            
            def show_user_permissions(*args):
                """Show permissions for selected user"""
                selected = user_var.get()
                print(f"DEBUG: Selected user: {selected}")
                if not selected:
                    return
                
                # Find selected user - extract username from "👤 username (role)" format
                try:
                    # Format: "👤 username (Role)"
                    parts = selected.split(" (")
                    username_part = parts[0].replace("👤 ", "").strip()
                    print(f"DEBUG: Extracted username: {username_part}")
                    
                    selected_user = next(
                        (u for u in users if u['username'] == username_part),
                        None
                    )
                    
                    print(f"DEBUG: Found user: {selected_user}")
                    
                    if selected_user:
                        # Clear all tabs
                        for widget in admin_content_frame.winfo_children():
                            widget.destroy()
                        for widget in global_content_frame.winfo_children():
                            widget.destroy()
                        for widget in city_content_frame.winfo_children():
                            widget.destroy()
                        
                        # Create content for all tabs
                        admin_vars = create_admin_tab_content(admin_content_frame, selected_user)
                        global_vars = create_global_tab_content(global_content_frame, selected_user)
                        city_vars_dict = create_city_tab_content(city_content_frame, selected_user)
                        
                        # Update institution permissions with the selected user
                        show_institution_permissions(selected_user)
                        
                        # Store vars for save operation
                        permissions_window.admin_vars = admin_vars
                        permissions_window.global_vars = global_vars
                        permissions_window.city_vars = city_vars_dict
                        permissions_window.selected_user = selected_user
                    else:
                        print(f"ERROR: Could not find user with username: {username_part}")
                except Exception as e:
                    print(f"ERROR in show_user_permissions: {e}")
                    import traceback
                    traceback.print_exc()
            
            def save_all_permissions():
                """Salvează TOATE permisiunile: Admin, Global, City, Institution"""
                if not hasattr(permissions_window, 'selected_user') or not permissions_window.selected_user:
                    messagebox.showwarning("Avertisment", "Te rog selectează un utilizator mai întâi!")
                    return
                
                discord_id = permissions_window.selected_user.get('discord_id', '')
                username = permissions_window.selected_user.get('username', 'Unknown')
                
                try:
                    def save_server_visibility_permissions(target_discord_id, server_visibility):
                        if not isinstance(server_visibility, dict):
                            return

                        try:
                            current_rows_response = requests.get(
                                f"{supabase_sync.url}/rest/v1/user_server_permissions?select=id,server_id&discord_id=eq.{target_discord_id}&permission_code=eq.can_view_server",
                                headers=headers,
                                timeout=5
                            )
                            if current_rows_response.status_code != 200:
                                print(f"DEBUG: cannot load existing can_view_server rows: {current_rows_response.status_code} {current_rows_response.text[:300]}")
                                return

                            current_rows = current_rows_response.json() or []
                            existing_by_server = {}
                            for row in current_rows:
                                row_id = row.get('id')
                                server_id = str(row.get('server_id', '')).strip()
                                if row_id and server_id:
                                    existing_by_server.setdefault(server_id, []).append(row_id)

                            selected_server_ids = {
                                server_id
                                for server_id, meta in server_visibility.items()
                                if meta.get('var') is not None and bool(meta['var'].get())
                            }

                            actor_discord_id = None
                            try:
                                actor_discord_id = discord_auth.get_discord_id() if discord_auth else None
                            except Exception:
                                actor_discord_id = None

                            for server_id in selected_server_ids:
                                if server_id in existing_by_server:
                                    continue

                                payload = {
                                    "server_id": server_id,
                                    "discord_id": target_discord_id,
                                    "permission_code": "can_view_server",
                                    "granted": True,
                                    "granted_by": actor_discord_id,
                                }
                                ins = requests.post(
                                    f"{supabase_sync.url}/rest/v1/user_server_permissions",
                                    headers=headers,
                                    json=payload,
                                    timeout=5
                                )
                                if ins.status_code not in (200, 201):
                                    print(f"DEBUG: insert can_view_server failed for {server_id}: {ins.status_code} {ins.text[:300]}")

                            for server_id, row_ids in existing_by_server.items():
                                if server_id in selected_server_ids:
                                    continue
                                for row_id in row_ids:
                                    dele = requests.delete(
                                        f"{supabase_sync.url}/rest/v1/user_server_permissions?id=eq.{row_id}",
                                        headers=headers,
                                        timeout=5
                                    )
                                    if dele.status_code not in (200, 204):
                                        print(f"DEBUG: delete can_view_server failed for row {row_id}: {dele.status_code} {dele.text[:300]}")
                        except Exception as e:
                            print(f"DEBUG: save_server_visibility_permissions error: {e}")

                    # 1. Salvează Admin permissions
                    if hasattr(permissions_window, 'admin_vars'):
                        for perm_key, var in permissions_window.admin_vars.items():
                            if str(perm_key).startswith('__'):
                                continue
                            hierarchy_perm_manager.set_global_permission(
                                discord_id, perm_key, var.get()
                            )

                        server_visibility = permissions_window.admin_vars.get('__server_visibility__', {})
                        save_server_visibility_permissions(discord_id, server_visibility)
                    
                    # 2. Salvează Global permissions
                    if hasattr(permissions_window, 'global_vars'):
                        for perm_key, var in permissions_window.global_vars.items():
                            hierarchy_perm_manager.set_global_permission(
                                discord_id, perm_key, var.get()
                            )
                    
                    # 3. Salvează City Level permissions
                    if hasattr(permissions_window, 'city_vars'):
                        for city, city_perms in permissions_window.city_vars.items():
                            # Pentru fiecare permisiune din fiecare oraș
                            for perm_key in ['add', 'edit', 'delete']:
                                if perm_key in city_perms:
                                    var = city_perms[perm_key]
                                    # Salvează în supabase
                                    perm_mapping = {
                                        'add': 'can_add_institutions',
                                        'edit': 'can_edit_institutions',
                                        'delete': 'can_delete_institutions'
                                    }
                                    hierarchy_perm_manager.set_city_permission(
                                        discord_id, city, perm_mapping[perm_key], var.get()
                                    )
                    
                    # 4. Salvează Institution Level permissions
                    if hasattr(permissions_window, 'institution_vars') and institution_perm_manager:
                        inst_perms = {}
                        for city, institutions in permissions_window.institution_vars.items():
                            inst_perms[city] = {}
                            for institution, perms in institutions.items():
                                inst_perms[city][institution] = {perm: var.get() for perm, var in perms.items()}
                        
                        if inst_perms:
                            institution_perm_manager.save_user_institution_permissions(discord_id, inst_perms)
                    
                    messagebox.showinfo("Succes", f"✅ TOATE permisiunile salvate pentru {username}!")
                    
                    # Log permission change
                    if action_logger and discord_auth:
                        disc_id = discord_auth.get_discord_id() if discord_auth else ""
                        disc_username = discord_auth.user_info.get('username', disc_id) if discord_auth and discord_auth.user_info else disc_id
                        
                        # Collect all permission changes
                        all_perms_changed = {}
                        if hasattr(permissions_window, 'admin_vars'):
                            for k, v in permissions_window.admin_vars.items():
                                if str(k).startswith('__'):
                                    continue
                                all_perms_changed[k] = v.get()

                            server_visibility = permissions_window.admin_vars.get('__server_visibility__', {})
                            if isinstance(server_visibility, dict):
                                all_perms_changed['can_view_server'] = [
                                    meta.get('server_key')
                                    for _server_id, meta in server_visibility.items()
                                    if meta.get('var') is not None and bool(meta['var'].get())
                                ]
                        if hasattr(permissions_window, 'global_vars'):
                            all_perms_changed.update({k: v.get() for k, v in permissions_window.global_vars.items()})
                        if hasattr(permissions_window, 'city_vars'):
                            for city_dict in permissions_window.city_vars.values():
                                all_perms_changed.update({k: v.get() for k, v in city_dict.items()})
                        
                        action_logger.log_permission_change(
                            discord_id=disc_id,
                            target_user=username,
                            permission_changes=all_perms_changed,
                            discord_username=disc_username
                        )
                    
                except Exception as e:
                    print(f"ERROR in save_all_permissions: {e}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("Eroare", f"Eroare la salvare: {str(e)}")
            
            user_combo.bind("<<ComboboxSelected>>", show_user_permissions)
            
            # ==================== BOTTOM TOOLBAR ====================
            bottom_toolbar = ttk.Frame(permissions_window, relief=tk.RAISED, borderwidth=2)
            bottom_toolbar.pack(fill=tk.X, padx=0, pady=0, side=tk.BOTTOM)
            
            # Left side: Info
            left_info = ttk.Frame(bottom_toolbar)
            left_info.pack(side=tk.LEFT, padx=15, pady=10)
            
            ttk.Label(
                left_info,
                text="💡 Modifică checkboxuri și apasă 'Salvează'",
                font=("Segoe UI", 9),
                foreground="gray"
            ).pack(side=tk.LEFT)
            
            # Right side: Action buttons
            right_buttons = ttk.Frame(bottom_toolbar)
            right_buttons.pack(side=tk.RIGHT, padx=15, pady=10)
            
            ttk.Button(
                right_buttons,
                text="🔄 Reîncarcă Permisiuni",
                width=18,
                command=show_user_permissions
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                right_buttons,
                text="💾 Salvează TOATE",
                width=16,
                command=save_all_permissions
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                right_buttons,
                text="❌ Închide",
                width=10,
                command=permissions_window.destroy
            ).pack(side=tk.LEFT, padx=5)
            
            # Set first user as default
            if users:
                user_combo.current(0)
                # Force window update before calling show_user_permissions
                permissions_window.update_idletasks()
                show_user_permissions()
        
        else:
            print(f"ERROR: Status code {response.status_code}")
            print(f"ERROR: Response: {response.text}")
            messagebox.showerror("Eroare", f"Nu se pot încărca utilizatorii! Status: {response.status_code}")
    
    except Exception as e:
        import traceback
        print(f"ERROR in open_granular_permissions_panel: {e}")
        traceback.print_exc()
        messagebox.showerror("Eroare", f"Eroare: {str(e)}")
