#!/usr/bin/env python3
"""
Clean duplicate employees from Supabase
Keeps the most recent version of each employee (by updated_at or id)
"""

import requests
import json
from pathlib import Path
import configparser
from collections import defaultdict

class SupabaseCleanup:
    def __init__(self, config_path: str = "supabase_config.ini"):
        """Initialize Supabase connection"""
        self.config = configparser.ConfigParser()
        
        config_paths = [
            config_path,
            Path(__file__).parent / config_path,
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
    
    def get_all_employees(self):
        """Get all employees from Supabase"""
        url = f"{self.url}/rest/v1/employees?select=*&order=id.asc"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"❌ Error fetching employees: {e}")
        
        return []
    
    def find_duplicates(self):
        """Find duplicate employees by discord_id"""
        employees = self.get_all_employees()
        print(f"📊 Total employees in Supabase: {len(employees)}")
        
        # Group by discord_id
        groups = defaultdict(list)
        for emp in employees:
            discord_id = emp.get('discord_id')
            if discord_id:
                groups[discord_id].append(emp)
        
        # Find duplicates
        duplicates = {k: v for k, v in groups.items() if len(v) > 1}
        
        print(f"\n🔍 Found {len(duplicates)} duplicate Discord IDs:")
        print(f"   ({sum(len(v)-1 for v in duplicates.values())} total duplicate records to delete)\n")
        
        if not duplicates:
            print("✅ No duplicates found!")
            return []
        
        # Show duplicates and mark which ones to keep
        to_delete = []
        for discord_id, group in sorted(duplicates.items()):
            print(f"   Discord ID: {discord_id}")
            
            # Sort by id (ascending) and keep the latest, delete earlier ones
            group_sorted = sorted(group, key=lambda x: x.get('id', 0))
            
            for i, emp in enumerate(group_sorted):
                status = "✅ KEEP" if i == len(group_sorted) - 1 else "❌ DELETE"
                print(f"      ID: {emp['id']:4d} | Name: {emp.get('employee_name', 'N/A'):20s} | {status}")
                
                if i < len(group_sorted) - 1:
                    to_delete.append(emp['id'])
            print()
        
        return to_delete
    
    def delete_employee(self, employee_id: int) -> bool:
        """Delete an employee by ID"""
        url = f"{self.url}/rest/v1/employees?id=eq.{employee_id}"
        
        try:
            resp = requests.delete(url, headers=self.headers, timeout=10)
            return resp.status_code in [200, 204]
        except Exception as e:
            print(f"❌ Error deleting employee {employee_id}: {e}")
        
        return False
    
    def clean_duplicates(self, to_delete: list, dry_run: bool = True):
        """Delete duplicate employees"""
        if not to_delete:
            print("✅ No duplicates to clean")
            return
        
        if dry_run:
            print(f"🔍 DRY RUN MODE: Would delete {len(to_delete)} records")
            print(f"   Records to delete: {to_delete}")
            return
        
        print(f"\n🗑️  Deleting {len(to_delete)} duplicate records...")
        
        deleted = 0
        failed = 0
        
        for emp_id in to_delete:
            if self.delete_employee(emp_id):
                deleted += 1
                print(f"   ✅ Deleted ID {emp_id}")
            else:
                failed += 1
                print(f"   ❌ Failed to delete ID {emp_id}")
        
        print(f"\n📊 Results: Deleted {deleted}, Failed {failed}")

def main():
    print("=" * 60)
    print("🧹 SUPABASE DUPLICATE CLEANUP")
    print("=" * 60)
    
    cleanup = SupabaseCleanup()
    
    # Find duplicates
    to_delete = cleanup.find_duplicates()
    
    if not to_delete:
        print("✅ Database is clean!")
        return
    
    # Ask user confirmation
    print("\n" + "=" * 60)
    confirm = input("❓ Delete these records? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        cleanup.clean_duplicates(to_delete, dry_run=False)
        print("\n✅ Cleanup complete!")
    else:
        print("❌ Cleanup cancelled")

if __name__ == "__main__":
    main()
