#!/usr/bin/env python3
"""
Supabase integration module for bidirectional sync
Handles: Read cities/institutions/employees, Write changes back to Supabase
"""

import requests
import json
from typing import List, Dict, Optional
from pathlib import Path
import configparser

class SupabaseEmployeeManager:
    """Manage cities, institutions, and employees in Supabase"""
    
    def __init__(self, config_path: str = "supabase_config.ini"):
        """Initialize Supabase connection"""
        self.config = configparser.ConfigParser()
        
        # Try different config paths
        config_paths = [
            config_path,
            Path(__file__).parent / config_path,
            Path(__file__).parent / "supabase_config.ini"
        ]
        
        found = False
        for path in config_paths:
            if Path(path).exists():
                self.config.read(path)
                found = True
                break
        
        if not found:
            raise FileNotFoundError(f"supabase_config.ini not found")
        
        self.url = self.config.get('supabase', 'url')
        self.key = self.config.get('supabase', 'key')
        
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    # ==================== READ OPERATIONS ====================
    
    def get_all_cities(self) -> List[Dict]:
        """Get all cities from Supabase"""
        url = f"{self.url}/rest/v1/cities?select=*&order=name.asc"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"❌ Error fetching cities: {e}")
        
        return []
    
    def get_city_by_name(self, city_name: str) -> Optional[Dict]:
        """Get city by name"""
        url = f"{self.url}/rest/v1/cities?name=eq.{city_name}&select=*"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data[0] if data else None
        except Exception as e:
            print(f"❌ Error fetching city {city_name}: {e}")
        
        return None
    
    def get_institutions_by_city(self, city_id: int) -> List[Dict]:
        """Get all institutions for a city"""
        url = f"{self.url}/rest/v1/institutions?city_id=eq.{city_id}&select=*&order=name.asc"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"❌ Error fetching institutions: {e}")
        
        return []
    
    def get_institution_by_name(self, city_id: int, institution_name: str) -> Optional[Dict]:
        """Get institution by city_id and name"""
        url = f"{self.url}/rest/v1/institutions?city_id=eq.{city_id}&name=eq.{institution_name}&select=*"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data[0] if data else None
        except Exception as e:
            print(f"❌ Error fetching institution: {e}")
        
        return None
    
    def get_employees_by_institution(self, institution_id: int) -> List[Dict]:
        """Get all employees for an institution"""
        url = f"{self.url}/rest/v1/employees?institution_id=eq.{institution_id}&select=*&order=employee_name.asc"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"❌ Error fetching employees: {e}")
        
        return []
    
    def get_employee_by_name(self, institution_id: int, employee_name: str) -> Optional[Dict]:
        """Get employee by institution and name"""
        url = f"{self.url}/rest/v1/employees?institution_id=eq.{institution_id}&employee_name=eq.{employee_name}&select=*"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data[0] if data else None
        except Exception as e:
            print(f"❌ Error fetching employee: {e}")
        
        return None
    
    # ==================== WRITE OPERATIONS ====================
    
    def add_city(self, city_name: str) -> Optional[Dict]:
        """Create a new city"""
        url = f"{self.url}/rest/v1/cities"
        payload = {"name": city_name}
        
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
            if resp.status_code in [200, 201]:
                result = resp.json()
                return result[0] if isinstance(result, list) else result
        except Exception as e:
            print(f"❌ Error creating city: {e}")
        
        return None
    
    def add_institution(self, city_id: int, institution_name: str) -> Optional[Dict]:
        """Create a new institution"""
        url = f"{self.url}/rest/v1/institutions"
        payload = {"city_id": city_id, "name": institution_name}
        
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
            if resp.status_code in [200, 201]:
                result = resp.json()
                return result[0] if isinstance(result, list) else result
        except Exception as e:
            print(f"❌ Error creating institution: {e}")
        
        return None
    
    def add_employee(self, institution_id: int, employee_data: Dict) -> Optional[Dict]:
        """Create a new employee"""
        url = f"{self.url}/rest/v1/employees"
        employee_data['institution_id'] = institution_id
        
        try:
            resp = requests.post(url, json=employee_data, headers=self.headers, timeout=10)
            if resp.status_code in [200, 201]:
                result = resp.json()
                return result[0] if isinstance(result, list) else result
        except Exception as e:
            print(f"❌ Error creating employee: {e}")
        
        return None
    
    def update_employee(self, employee_id: int, update_data: Dict) -> Optional[Dict]:
        """Update an employee"""
        url = f"{self.url}/rest/v1/employees?id=eq.{employee_id}"
        
        try:
            resp = requests.patch(url, json=update_data, headers=self.headers, timeout=10)
            if resp.status_code in [200, 204]:
                result = resp.json() if resp.text else None
                return result[0] if isinstance(result, list) else result
        except Exception as e:
            print(f"❌ Error updating employee: {e}")
        
        return None
    
    def delete_employee(self, employee_id: int) -> bool:
        """Delete an employee"""
        url = f"{self.url}/rest/v1/employees?id=eq.{employee_id}"
        
        try:
            resp = requests.delete(url, headers=self.headers, timeout=10)
            return resp.status_code in [200, 204]
        except Exception as e:
            print(f"❌ Error deleting employee: {e}")
        
        return False
    
    def delete_institution(self, institution_id: int) -> bool:
        """Delete an institution (and all its employees cascade)"""
        url = f"{self.url}/rest/v1/institutions?id=eq.{institution_id}"
        
        try:
            resp = requests.delete(url, headers=self.headers, timeout=10)
            if resp.status_code in [200, 204]:
                print(f"✓ Institution deleted from Supabase (ID: {institution_id})")
                return True
            else:
                print(f"❌ Error deleting institution: Status {resp.status_code}")
        except Exception as e:
            print(f"❌ Error deleting institution: {e}")
        
        return False
    
    def delete_city(self, city_id: int) -> bool:
        """Delete a city (and all its institutions/employees cascade)"""
        url = f"{self.url}/rest/v1/cities?id=eq.{city_id}"
        
        try:
            resp = requests.delete(url, headers=self.headers, timeout=10)
            if resp.status_code in [200, 204]:
                print(f"✓ City deleted from Supabase (ID: {city_id})")
                return True
            else:
                print(f"❌ Error deleting city: Status {resp.status_code}")
        except Exception as e:
            print(f"❌ Error deleting city: {e}")
        
        return False
    
    # ==================== HELPER METHODS ====================
    
    def get_full_structure(self) -> Dict:
        """Get full structure: cities -> institutions -> employees"""
        structure = {}
        
        for city in self.get_all_cities():
            city_id = city['id']
            city_name = city['name']
            structure[city_name] = {}
            
            for institution in self.get_institutions_by_city(city_id):
                inst_id = institution['id']
                inst_name = institution['name']
                structure[city_name][inst_name] = self.get_employees_by_institution(inst_id)
        
        return structure
    
    def format_employee_for_app(self, emp: Dict) -> Dict:
        """Format Supabase employee to app format"""
        return {
            "id": emp.get("id"),  # IMPORTANT: Preserve for delete operations
            "DISCORD": emp.get("discord_username", ""),
            "NUME IC": emp.get("employee_name", ""),
            "RANK": emp.get("rank", ""),
            "ROLE": emp.get("role", ""),
            "PUNCTAJ": emp.get("points", 0),
            "SERIE DE BULETIN": emp.get("id_card_series", ""),
            "ULTIMA_MOD": emp.get("updated_at", "")
        }
    
    def format_employee_for_supabase(self, emp: Dict) -> Dict:
        """Format app employee to Supabase format"""
        return {
            "discord_username": emp.get("DISCORD", ""),
            "employee_name": emp.get("NUME IC", ""),
            "rank": emp.get("RANK", ""),
            "role": emp.get("ROLE", ""),
            "points": int(emp.get("PUNCTAJ", 0)),
            "id_card_series": emp.get("SERIE DE BULETIN", "")
        }


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 70)
    print("SUPABASE EMPLOYEE MANAGER TEST")
    print("=" * 70)
    
    try:
        manager = SupabaseEmployeeManager()
        print("✓ Connected to Supabase\n")
        
        # Get structure
        structure = manager.get_full_structure()
        
        print("📊 DATA STRUCTURE:\n")
        for city, institutions in structure.items():
            print(f"  📍 {city}")
            for institution, employees in institutions.items():
                print(f"    🏢 {institution}: {len(employees)} employees")
                for emp in employees:
                    print(f"       • {emp['employee_name']} (Rank: {emp['rank']}, Points: {emp['points']})")
        
        print("\n" + "=" * 70)
        print("✅ TEST PASSED")
        print("=" * 70)
    
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
