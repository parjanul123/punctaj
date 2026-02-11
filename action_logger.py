# -*- coding: utf-8 -*-
"""
Action Logger for Audit Trail
Logs all user actions to Supabase table and local JSON files with encryption
"""

import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Import encryption module
try:
    from json_encryptor import get_encryptor, load_protected_json, save_protected_json
    ENCRYPTION_ENABLED = True
except ImportError:
    ENCRYPTION_ENABLED = False
    print("⚠️  JSON encryption module not available - logs will be saved unencrypted")

class ActionLogger:
    """Logs user actions to Supabase for audit trail and saves locally"""
    
    def __init__(self, supabase_sync, logs_dir: str = "logs"):
        """
        Initialize action logger
        
        Args:
            supabase_sync: SupabaseSync instance for database access
            logs_dir: Directory to save local log files
        """
        self.supabase_url = supabase_sync.url
        self.supabase_key = supabase_sync.key
        self.table_logs = supabase_sync.table_logs  # Use configured table name
        self.logs_dir = logs_dir
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for Supabase API"""
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
    
    def _save_local_log(self, log_entry: Dict[str, Any]) -> bool:
        """Save log entry to local JSON file organized by institution (encrypted)"""
        try:
            city = log_entry.get("city", "unknown")
            institution = log_entry.get("institution", "unknown")
            
            # Create directory structure: logs/{city}/{institution}.json
            city_dir = os.path.join(self.logs_dir, city)
            os.makedirs(city_dir, exist_ok=True)
            
            institution_file = os.path.join(city_dir, f"{institution}.json")
            
            # Load existing logs or create new array
            if ENCRYPTION_ENABLED:
                # Load encrypted if available, otherwise plain JSON
                logs = load_protected_json(institution_file, decrypt=True)
                if not isinstance(logs, list):
                    logs = []
            else:
                if os.path.exists(institution_file):
                    try:
                        with open(institution_file, 'r', encoding='utf-8') as f:
                            logs = json.load(f)
                    except:
                        logs = []
                else:
                    logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Save updated logs (encrypted if enabled)
            if ENCRYPTION_ENABLED:
                save_protected_json(institution_file, logs, encrypt=True)
            else:
                with open(institution_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, ensure_ascii=False, indent=2)
            
            enc_status = " (encrypted)" if ENCRYPTION_ENABLED else ""
            print(f"💾 Log saved locally{enc_status}: {institution_file}")
            
            # Update global summary
            self._update_global_summary(log_entry)
            
            return True
        except Exception as e:
            print(f"⚠️ Error saving local log: {e}")
            return False
    
    def _update_global_summary(self, log_entry: Dict[str, Any]) -> bool:
        """Update global summary JSON with the action (encrypted)"""
        try:
            global_summary_file = f"{self.logs_dir}/SUMMARY_global.json"
            
            # Load existing summary or create new (encrypted if available)
            if ENCRYPTION_ENABLED:
                summary = load_protected_json(global_summary_file, decrypt=True)
                if not isinstance(summary, dict):
                    summary = {}
            else:
                if os.path.exists(global_summary_file):
                    try:
                        with open(global_summary_file, 'r', encoding='utf-8') as f:
                            summary = json.load(f)
                    except:
                        summary = {}
                else:
                    summary = {}
            
            # Ensure required keys exist (for backward compatibility with old files)
            if "updated_at" not in summary:
                summary["updated_at"] = datetime.now().isoformat()
            if "users_connected" not in summary:
                summary["users_connected"] = []
            if "cities_modified" not in summary:
                summary["cities_modified"] = {}
            if "institutions_modified" not in summary:
                summary["institutions_modified"] = {}
            if "total_actions" not in summary:
                summary["total_actions"] = 0
            
            # Add user if not already there
            discord_id = log_entry.get("discord_id", "unknown")
            discord_username = log_entry.get("discord_username", discord_id)
            if discord_username not in summary.get("users_connected", []):
                summary["users_connected"].append(discord_username)
            
            # Add city modification (safe check)
            city = log_entry.get("city", "unknown")
            if city and city != "unknown":
                if city not in summary["cities_modified"]:
                    summary["cities_modified"][city] = {
                        "added": [],
                        "deleted": [],
                        "edited": []
                    }
            
            # Add institution modification (safe check)
            institution = log_entry.get("institution", "unknown")
            if city and city != "unknown" and institution and institution != "unknown":
                inst_key = f"{city}/{institution}"
                if inst_key not in summary["institutions_modified"]:
                    summary["institutions_modified"][inst_key] = {
                        "city": city,
                        "institution": institution,
                        "actions": []
                    }
                
                # Track action with Discord username for display
                action_type = log_entry.get("action_type", "unknown")
                details = log_entry.get("details", "")
                changes = log_entry.get("changes", "")
                timestamp = log_entry.get("timestamp", "")
                
                action_entry = {
                    "timestamp": timestamp,
                    "discord_id": discord_id,
                    "discord_username": discord_username,
                    "action": action_type,
                    "details": details,
                    "changes": changes
                }
                
                summary["institutions_modified"][inst_key]["actions"].append(action_entry)
            
            summary["total_actions"] = summary.get("total_actions", 0) + 1
            summary["updated_at"] = datetime.now().isoformat()
            
            # Save updated summary (encrypted if enabled)
            if ENCRYPTION_ENABLED:
                save_protected_json(global_summary_file, summary, encrypt=True)
            else:
                with open(global_summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"📊 Global summary updated: {global_summary_file}")
            return True
        except Exception as e:
            print(f"⚠️ Error updating global summary: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _log_action(self, 
                   discord_id: str,
                   action_type: str,
                   city: str,
                   institution_name: str,
                   details: str,
                   discord_username: str = "",
                   entity_name: str = "",
                   entity_id: str = "",
                   changes: str = "") -> bool:
        """
        Internal method to log action to Supabase and save locally
        
        Args:
            discord_id: User's Discord ID
            action_type: Type of action (add_employee, edit_points, delete_employee, etc.)
            city: City name
            institution_name: Name of institution affected
            details: Additional details (what was changed, amounts, etc.)
            discord_username: Discord username (for display)
            entity_name: Name of the entity being modified (e.g., employee name)
            entity_id: ID of the entity (e.g., NOME_IC)
            changes: Detailed change description (what specifically changed)
        
        Returns:
            bool: True if logged successfully
        """
        try:
            url = f"{self.supabase_url}/rest/v1/{self.table_logs}"
            
            # Create log entry with detailed information
            log_entry = {
                "discord_id": discord_id,
                "discord_username": discord_username or discord_id,  # Fallback to ID if no username
                "action_type": action_type,
                "city": city,
                "institution": institution_name,
                "entity_name": entity_name,  # Name of what was modified
                "entity_id": entity_id,      # ID of what was modified (e.g., NUME_IC)
                "details": details,
                "changes": changes,          # Detailed change description
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"📝 Logging: {action_type} | User: {discord_username or discord_id} | Entity: {entity_name} | Table: {self.table_logs}")
            
            # Save locally first
            self._save_local_log(log_entry)
            
            # Then send to Supabase
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=log_entry,
                timeout=5
            )
            
            if response.status_code in [201, 200]:
                print(f"✅ Log SUCCESS: {action_type} in {city}/{institution_name} ({details[:50]}...)")
                return True
            else:
                print(f"❌ Log FAILED (status {response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error logging action: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def log_add_employee(self, discord_id: str, city: str, institution_name: str, 
                        employee_name: str, employee_data: Dict[str, Any],
                        discord_username: str = "") -> bool:
        """Log employee addition"""
        details = f"Added employee: {employee_name}"
        entity_id = employee_data.get("NUME_IC", "")
        return self._log_action(
            discord_id,
            "add_employee",
            city,
            institution_name,
            details,
            discord_username=discord_username,
            entity_name=employee_name,
            entity_id=entity_id,
            changes=f"New employee added"
        )
    
    def log_edit_points(self, discord_id: str, city: str, institution_name: str,
                       employee_name: str, old_points: Any, new_points: Any, action: str = "",
                       discord_username: str = "", entity_id: str = "") -> bool:
        """Log points editing"""
        details = f"{employee_name}: {old_points} → {new_points}" + (f" ({action})" if action else "")
        changes_desc = f"Points: {old_points} → {new_points}" + (f" ({action})" if action else "")
        return self._log_action(
            discord_id,
            "edit_points",
            city,
            institution_name,
            details,
            discord_username=discord_username,
            entity_name=employee_name,
            entity_id=entity_id,
            changes=changes_desc
        )
    
    def log_delete_employee(self, discord_id: str, city: str, institution_name: str,
                          employee_name: str, employee_data: Dict[str, Any],
                          discord_username: str = "") -> bool:
        """Log employee deletion"""
        details = f"Deleted employee: {employee_name}"
        entity_id = employee_data.get("NUME_IC", "")
        return self._log_action(
            discord_id,
            "delete_employee",
            city,
            institution_name,
            details,
            discord_username=discord_username,
            entity_name=employee_name,
            entity_id=entity_id,
            changes="Employee permanently deleted"
        )
    
    def log_edit_employee(self, discord_id: str, city: str, institution_name: str,
                         employee_name: str, changed_fields: Dict[str, tuple]) -> bool:
        """Log employee data editing"""
        changes = "; ".join([f"{field}: {old_val} → {new_val}" 
                           for field, (old_val, new_val) in changed_fields.items()])
        details = f"{employee_name}: {changes}"
        
        return self._log_action(
            discord_id,
            "edit_employee",
            city,
            institution_name,
            details
        )
    
    def log_permission_change(self, discord_id: str, target_user: str, permission_changes: Dict[str, bool],
                             discord_username: str = "") -> bool:
        """Log permission changes - logs who gave what permissions to whom"""
        # Build description of what changed
        added_perms = [perm for perm, value in permission_changes.items() if value is True]
        removed_perms = [perm for perm, value in permission_changes.items() if value is False]
        
        changes_list = []
        if added_perms:
            changes_list.append(f"✓ Adăugate: {', '.join(added_perms)}")
        if removed_perms:
            changes_list.append(f"✗ Șterse: {', '.join(removed_perms)}")
        
        changes_desc = " | ".join(changes_list) if changes_list else "Permisiuni resetate"
        details = f"Utilizator {target_user}: {changes_desc}"
        
        # Log to main action log
        self._log_action(
            discord_id,
            "permission_change",
            "",  # No city/institution for global permissions
            "",
            details,
            discord_username=discord_username,
            entity_name=target_user,
            entity_id="",
            changes=changes_desc
        )
        
        # Also save to dedicated permission_changes table in Supabase
        try:
            url = f"{self.supabase_url}/rest/v1/permission_changes"
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
            
            permission_entry = {
                "discord_id": discord_id,
                "discord_username": discord_username or discord_id,
                "target_user": target_user,
                "permission_changes": json.dumps(permission_changes),
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(url, json=permission_entry, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                print(f"✅ Permission change saved to permission_changes table: {target_user}")
                return True
            else:
                print(f"⚠️ Failed to save to permission_changes table: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"⚠️ Error saving to permission_changes table: {e}")
            return False
    
    def log_edit_employee_safe(self, discord_id: str, city: str, institution_name: str,
                              employee_name: str, changes: str,
                              discord_username: str = "", entity_id: str = "") -> bool:
        """
        Log employee edit with safe schema
        Includes employee_name in details field for readability
        """
        details = f"{employee_name}: {changes}" if changes else f"Edited {employee_name}"
        return self._log_action(
            discord_id,
            "edit_employee",
            city,
            institution_name,
            details,
            discord_username=discord_username,
            entity_name=employee_name,
            entity_id=entity_id,
            changes=changes
        )
    
    def log_institution_field_edit(self, discord_id: str, city: str, institution_name: str,
                                   employee_name: str, field_name: str, old_value: str, new_value: str,
                                   discord_username: str = "", entity_id: str = "") -> bool:
        """
        Log detailed field-level institution edit
        
        Args:
            field_name: Which field changed (RANK, NAME, PUNCTAJ, PREZENTA, etc.)
            old_value: Previous value
            new_value: New value
        """
        # Determine action type based on field
        action_map = {
            "RANK": "edit_rank",
            "ROLE": "edit_role", 
            "PUNCTAJ": "edit_punctaj",
            "NUME IC": "edit_nume_ic",
            "DISCORD": "edit_discord",
            "SERIE DE BULETIN": "edit_serie_buletin"
        }
        
        action_type = action_map.get(field_name, "edit_field")
        changes = f"{field_name}: {old_value} → {new_value}"
        details = f"{employee_name}: {changes}"
        
        return self._log_action(
            discord_id,
            action_type,
            city,
            institution_name,
            details,
            discord_username=discord_username,
            entity_name=employee_name,
            entity_id=entity_id,
            changes=changes
        )
    
    def log_custom_action(self, discord_id: str, action_type: str,
                         institution_name: str, city: str = "", employee_name: str = "",
                         old_value: Any = "", new_value: Any = "",
                         details: str = "", discord_username: str = "") -> bool:
        """Log custom action type"""
        return self._log_action(
            discord_id,
            action_type,
            city,
            institution_name,
            details,
            discord_username=discord_username,
            entity_name=employee_name,
            entity_id="",
            changes=f"old: {old_value}, new: {new_value}" if old_value or new_value else ""
        )
