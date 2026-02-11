"""
Global Hierarchy Permissions System
=====================================
Gestionează permisiuni pe 3 niveluri:
1. GLOBAL - cine poate adaugă ORAȘE/JUDEȚE
2. CITY LEVEL - cine poate adaugă INSTITUȚII în acel oraș
3. INSTITUTION LEVEL - cine poate vedea/edita/șterge în acea instituție
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any


class GlobalHierarchyPermissionManager:
    """
    Manager pentru permisiuni pe 3 niveluri de ierarhie
    """
    
    def __init__(self, supabase_client, cache_dir: str = "d:/punctaj/data"):
        """
        Inițializează manager-ul
        
        Args:
            supabase_client: Client Supabase
            cache_dir: Directory pentru cache local
        """
        self.supabase = supabase_client
        self.cache_dir = cache_dir
        self.table_name = "discord_users"
        self.column_name = "granular_permissions"
    
    # ==================== NIVEL GLOBAL ====================
    
    def can_add_cities(self, discord_id: str) -> bool:
        """
        Verifică dacă user-ul poate adaugă ORAȘE/JUDEȚE
        
        Args:
            discord_id: Discord ID al user-ului
            
        Returns:
            True dacă poate adaugă orașe
        """
        try:
            perms = self._get_user_permissions(discord_id)
            
            if not perms:
                return False
            
            # Verifică permisiunea globală
            global_perms = perms.get("global", {})
            return global_perms.get("can_add_cities", False)
            
        except Exception as e:
            print(f"❌ Eroare verificare can_add_cities: {e}")
            return False
    
    def can_add_states(self, discord_id: str) -> bool:
        """
        Verifică dacă user-ul poate adaugă JUDEȚE
        
        Args:
            discord_id: Discord ID al user-ului
            
        Returns:
            True dacă poate adaugă județe
        """
        try:
            perms = self._get_user_permissions(discord_id)
            
            if not perms:
                return False
            
            # Verifică permisiunea globală
            global_perms = perms.get("global", {})
            return global_perms.get("can_add_states", False)
            
        except Exception as e:
            print(f"❌ Eroare verificare can_add_states: {e}")
            return False
    
    def set_global_permission(self, discord_id: str, permission: str, value: bool) -> bool:
        """
        Setează permisiune globală (can_add_cities, can_add_states)
        
        Args:
            discord_id: Discord ID
            permission: Tipul permisiunii (can_add_cities, can_add_states)
            value: True/False
            
        Returns:
            True dacă successful
        """
        try:
            perms = self._get_user_permissions(discord_id)
            if not perms:
                perms = {}
            
            # Inițializează global dict
            if "global" not in perms:
                perms["global"] = {}
            
            # Setează permisiunea
            perms["global"][permission] = value
            
            # Salvează în Supabase
            return self._save_permissions(discord_id, perms)
            
        except Exception as e:
            print(f"❌ Eroare setare global permission: {e}")
            return False
    
    # ==================== NIVEL CITY ====================
    
    def can_add_institutions(self, discord_id: str, city: str) -> bool:
        """
        Verifică dacă user-ul poate adaugă INSTITUȚII în acel ORAȘ
        
        Args:
            discord_id: Discord ID
            city: Numele orașului
            
        Returns:
            True dacă poate adaugă instituții în acest oraș
        """
        try:
            perms = self._get_user_permissions(discord_id)
            
            if not perms:
                return False
            
            # Verifică permisiunea la nivel city
            cities_perms = perms.get("cities", {})
            city_perms = cities_perms.get(city, {})
            return city_perms.get("can_add_institutions", False)
            
        except Exception as e:
            print(f"❌ Eroare verificare can_add_institutions: {e}")
            return False
    
    def set_city_permission(self, discord_id: str, city: str, permission: str, value: bool) -> bool:
        """
        Setează permisiune la nivel CITY (can_add_institutions)
        
        Args:
            discord_id: Discord ID
            city: Numele orașului
            permission: Tipul permisiunii
            value: True/False
            
        Returns:
            True dacă successful
        """
        try:
            perms = self._get_user_permissions(discord_id)
            if not perms:
                perms = {}
            
            # Inițializează cities dict
            if "cities" not in perms:
                perms["cities"] = {}
            
            if city not in perms["cities"]:
                perms["cities"][city] = {}
            
            # Setează permisiunea
            perms["cities"][city][permission] = value
            
            # Salvează în Supabase
            return self._save_permissions(discord_id, perms)
            
        except Exception as e:
            print(f"❌ Eroare setare city permission: {e}")
            return False
    
    # ==================== NIVEL INSTITUTION ====================
    
    def check_institution_permission(
        self, discord_id: str, city: str, institution: str, permission: str
    ) -> bool:
        """
        Verifică permisiune la nivel INSTITUTION (can_view, can_edit, etc)
        
        Args:
            discord_id: Discord ID
            city: Orașul
            institution: Instituția
            permission: Tipul permisiunii (can_view, can_edit, can_delete, etc)
            
        Returns:
            True dacă are permisiune
        """
        try:
            perms = self._get_user_permissions(discord_id)
            
            if not perms:
                return False
            
            # Verifică permisiunea la nivel institution
            inst_perms = perms.get("institutions", {})
            city_perms = inst_perms.get(city, {})
            inst_perm = city_perms.get(institution, {})
            return inst_perm.get(permission, False)
            
        except Exception as e:
            print(f"❌ Eroare verificare institution permission: {e}")
            return False
    
    def set_institution_permission(
        self, discord_id: str, city: str, institution: str, permission: str, value: bool
    ) -> bool:
        """
        Setează permisiune la nivel INSTITUTION
        
        Args:
            discord_id: Discord ID
            city: Orașul
            institution: Instituția
            permission: Tipul permisiunii
            value: True/False
            
        Returns:
            True dacă successful
        """
        try:
            perms = self._get_user_permissions(discord_id)
            if not perms:
                perms = {}
            
            # Inițializează institutions dict
            if "institutions" not in perms:
                perms["institutions"] = {}
            
            if city not in perms["institutions"]:
                perms["institutions"][city] = {}
            
            if institution not in perms["institutions"][city]:
                perms["institutions"][city][institution] = {}
            
            # Setează permisiunea
            perms["institutions"][city][institution][permission] = value
            
            # Salvează în Supabase
            return self._save_permissions(discord_id, perms)
            
        except Exception as e:
            print(f"❌ Eroare setare institution permission: {e}")
            return False
    
    # ==================== HELPER METHODS ====================
    
    def _get_user_permissions(self, discord_id: str) -> Optional[Dict]:
        """Obține permisiunile user-ului din Supabase"""
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
                    perm_data = data[0].get('granular_permissions')
                    if perm_data:
                        if isinstance(perm_data, str):
                            return json.loads(perm_data)
                        return perm_data
            
            return None
            
        except Exception as e:
            print(f"❌ Eroare citire permissions: {e}")
            return None
    
    def _save_permissions(self, discord_id: str, permissions: Dict) -> bool:
        """Salvează permisiunile în Supabase"""
        try:
            headers = {
                "apikey": self.supabase.key,
                "Authorization": f"Bearer {self.supabase.key}",
                "Content-Type": "application/json"
            }
            
            # Convertește la JSON string
            perm_json = json.dumps(permissions, ensure_ascii=False, indent=2)
            
            # Salvează în Supabase
            url = f"{self.supabase.url}/rest/v1/discord_users?discord_id=eq.{discord_id}"
            response = requests.patch(
                url,
                headers=headers,
                json={"granular_permissions": perm_json},
                timeout=5
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ Permisiuni salvate pentru {discord_id}")
                return True
            else:
                print(f"❌ Eroare salvare permissions: Status {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Eroare salvare permissions: {e}")
            return False
    
    def get_all_permissions(self, discord_id: str) -> Dict:
        """Obține TOATE permisiunile user-ului"""
        return self._get_user_permissions(discord_id) or {}
    
    def get_summary(self, discord_id: str) -> str:
        """Obține sumar permisiuni în format citibil"""
        perms = self.get_all_permissions(discord_id)
        
        summary = f"\n📋 PERMISIUNI PENTRU {discord_id}:\n"
        summary += "=" * 50 + "\n"
        
        # Global permissions
        global_perms = perms.get("global", {})
        if global_perms:
            summary += "\n🌍 GLOBAL:\n"
            summary += f"  • Adaugă Orașe: {'✅' if global_perms.get('can_add_cities') else '❌'}\n"
            summary += f"  • Adaugă Județe: {'✅' if global_perms.get('can_add_states') else '❌'}\n"
        
        # City permissions
        cities_perms = perms.get("cities", {})
        if cities_perms:
            summary += "\n🏙️ ORAȘE:\n"
            for city, city_perm in cities_perms.items():
                can_add = city_perm.get("can_add_institutions", False)
                summary += f"  • {city}: {'✅' if can_add else '❌'} Adaugă Instituții\n"
        
        # Institution permissions
        inst_perms = perms.get("institutions", {})
        if inst_perms:
            summary += "\n🏢 INSTITUȚII:\n"
            for city, city_inst in inst_perms.items():
                summary += f"  [{city}]\n"
                for institution, perm in city_inst.items():
                    view = perm.get("can_view", False)
                    edit = perm.get("can_edit", False)
                    delete = perm.get("can_delete", False)
                    reset = perm.get("can_reset_scores", False)
                    deduct = perm.get("can_deduct_scores", False)
                    
                    status = f"V{'✅' if view else '❌'} E{'✅' if edit else '❌'} D{'✅' if delete else '❌'} R{'✅' if reset else '❌'} Sc{'✅' if deduct else '❌'}"
                    summary += f"    • {institution}: {status}\n"
        
        return summary


# ==================== QUICK CHECKS ====================

class QuickPermissionChecks:
    """Utilități rapide pentru verificări permisiuni"""
    
    @staticmethod
    def can_add_anything(manager: GlobalHierarchyPermissionManager, discord_id: str) -> bool:
        """Verifică dacă user poate adaugă ceva (orașe, județe, instituții)"""
        return (
            manager.can_add_cities(discord_id) or
            manager.can_add_states(discord_id)
        )
    
    @staticmethod
    def what_can_add(manager: GlobalHierarchyPermissionManager, discord_id: str) -> List[str]:
        """Returnează lista ce poate adaugă user-ul"""
        can_add = []
        
        if manager.can_add_cities(discord_id):
            can_add.append("ORAȘE")
        
        if manager.can_add_states(discord_id):
            can_add.append("JUDEȚE")
        
        # Check city level
        perms = manager.get_all_permissions(discord_id)
        cities_perms = perms.get("cities", {})
        for city in cities_perms.keys():
            if cities_perms[city].get("can_add_institutions"):
                can_add.append(f"INSTITUȚII în {city}")
        
        return can_add


# ==================== INTEGRATION POINTS ====================

def integrate_add_city_button(manager: GlobalHierarchyPermissionManager, discord_id: str) -> bool:
    """
    Check before showing "Add City" button
    
    Usage:
        if integrate_add_city_button(manager, user_id):
            # Show button
        else:
            # Hide button
    """
    return manager.can_add_cities(discord_id)


def integrate_add_institution_button(
    manager: GlobalHierarchyPermissionManager, discord_id: str, city: str
) -> bool:
    """
    Check before showing "Add Institution" button for a city
    
    Usage:
        if integrate_add_institution_button(manager, user_id, "Blackwater"):
            # Show button
        else:
            # Hide button
    """
    return manager.can_add_institutions(discord_id, city)


def integrate_institution_actions(
    manager: GlobalHierarchyPermissionManager, 
    discord_id: str, 
    city: str, 
    institution: str
) -> Dict[str, bool]:
    """
    Get all permissions for a user in an institution
    
    Returns dict with:
        - can_view
        - can_edit
        - can_delete
        - can_reset_scores
        - can_deduct_scores
    
    Usage:
        perms = integrate_institution_actions(manager, user_id, "Blackwater", "Politie")
        self.add_button.config(state=tk.NORMAL if perms['can_edit'] else tk.DISABLED)
    """
    return {
        "can_view": manager.check_institution_permission(discord_id, city, institution, "can_view"),
        "can_edit": manager.check_institution_permission(discord_id, city, institution, "can_edit"),
        "can_delete": manager.check_institution_permission(discord_id, city, institution, "can_delete"),
        "can_reset_scores": manager.check_institution_permission(discord_id, city, institution, "can_reset_scores"),
        "can_deduct_scores": manager.check_institution_permission(discord_id, city, institution, "can_deduct_scores"),
    }
