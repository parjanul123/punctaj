#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Device Cloud Sync Manager
Sincronizează TOT din cloud la orice dispozitiv
- Datele politienilor (police_data)
- Permisiunile utilizatorilor
- Logs și audit trail
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import threading
import time

class MultiDeviceSyncManager:
    """Sincronizează toate datele din cloud pentru multi-device support"""
    
    def __init__(self, supabase_sync, data_dir: str):
        """
        Initialize multi-device sync manager
        
        Args:
            supabase_sync: SupabaseSync instance
            data_dir: Local data directory
        """
        self.supabase_sync = supabase_sync
        self.data_dir = Path(data_dir)
        self.supabase_url = supabase_sync.url
        self.supabase_key = supabase_sync.key
        
        self.headers = {
            "apikey": supabase_sync.key,
            "Authorization": f"Bearer {supabase_sync.key}",
            "Content-Type": "application/json"
        }
        
        # Sync status
        self.is_syncing = False
        self.last_sync_time = None
        self.sync_thread = None
        
        print(f"🔄 Multi-Device Sync Manager initialized")
        print(f"   Data directory: {data_dir}")
    
    def full_cloud_sync_on_startup(self) -> Dict:
        """
        Sincronizează COMPLET din cloud la startup
        - Descarcă toți policiile
        - Descarcă permisiunile utilizatorilor
        - Descarcă logs
        - Verifica integritatea datelor
        
        Returns:
            Dict cu status al sincronizării
        """
        print(f"\n{'='*80}")
        print(f"🌐 Starting Full Cloud Sync (Multi-Device)")
        print(f"{'='*80}")
        
        self.is_syncing = True
        start_time = time.time()
        
        results = {
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "police_data": {"status": "pending", "count": 0},
            "user_permissions": {"status": "pending", "count": 0},
            "logs": {"status": "pending", "count": 0},
            "total_time": 0,
            "message": ""
        }
        
        try:
            # Step 1: Sincronizare datele policienilor
            print(f"\n📥 Step 1: Syncing police data...")
            police_result = self._sync_police_data()
            results["police_data"] = police_result
            
            # Step 2: Sincronizare permisiunile utilizatorilor
            print(f"\n📥 Step 2: Syncing user permissions...")
            perms_result = self._sync_user_permissions()
            results["user_permissions"] = perms_result
            
            # Step 3: Sincronizare logs
            print(f"\n📥 Step 3: Syncing audit logs...")
            logs_result = self._sync_audit_logs()
            results["logs"] = logs_result
            
            # Step 4: Verifica integritatea
            print(f"\n✔️  Step 4: Verifying data integrity...")
            integrity_check = self._verify_data_integrity()
            results["integrity"] = integrity_check
            
            # Status overall
            if (results["police_data"]["status"] == "success" and 
                results["user_permissions"]["status"] == "success"):
                results["status"] = "success"
                results["message"] = "✅ Full sync completed successfully!"
            else:
                results["status"] = "partial"
                results["message"] = "⚠️  Partial sync - some data may be incomplete"
            
            # Time
            results["total_time"] = time.time() - start_time
            
            # Status report
            print(f"\n{'='*80}")
            print(f"SYNC REPORT")
            print(f"{'='*80}")
            print(f"Status: {results['status'].upper()}")
            print(f"Police Data: {results['police_data']['status'].upper()} ({results['police_data'].get('count', 0)} cities)")
            print(f"User Permissions: {results['user_permissions']['status'].upper()} ({results['user_permissions'].get('count', 0)} users)")
            print(f"Audit Logs: {results['logs']['status'].upper()} ({results['logs'].get('count', 0)} logs)")
            print(f"Integrity Check: {results['integrity']['status'].upper()}")
            print(f"Total Time: {results['total_time']:.2f}s")
            print(f"{'='*80}\n")
            
            self.last_sync_time = datetime.now()
            return results
            
        except Exception as e:
            print(f"❌ ERROR During sync: {e}")
            import traceback
            traceback.print_exc()
            
            results["status"] = "error"
            results["message"] = f"Error: {str(e)}"
            results["total_time"] = time.time() - start_time
            return results
        
        finally:
            self.is_syncing = False
    
    def _sync_police_data(self) -> Dict:
        """Sincronizează datele politienilor din cloud"""
        try:
            # Fetch all police data
            print(f"  📊 Fetching police data...")
            
            # Query: Get all police data grouped by city
            url = f"{self.supabase_url}/rest/v1/police_data"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                print(f"     ⚠️  HTTP {response.status_code}: {response.text[:100]}")
                return {"status": "failed", "count": 0, "error": response.text[:100]}
            
            data = response.json()
            if not isinstance(data, list):
                print(f"     ⚠️  Unexpected format: {type(data)}")
                return {"status": "failed", "count": 0}
            
            print(f"     Found {len(data)} police records")
            
            # Group by city and save locally
            cities_data = {}
            for record in data:
                city = record.get('city', 'Unknown')
                if city not in cities_data:
                    cities_data[city] = []
                cities_data[city].append(record)
            
            # Save to local files
            synced_count = 0
            for city, records in cities_data.items():
                city_path = self.data_dir / city
                city_path.mkdir(parents=True, exist_ok=True)
                
                # Save as JSON files organized by institution
                for record in records:
                    institution = record.get('institution', 'Unknown')
                    file_path = city_path / f"{institution}.json"
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(record, f, ensure_ascii=False, indent=2)
                    
                    synced_count += 1
            
            print(f"     ✅ Synced {synced_count} police records across {len(cities_data)} cities")
            
            return {
                "status": "success",
                "count": len(cities_data),
                "records": synced_count
            }
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
            return {"status": "error", "count": 0, "error": str(e)}
    
    def _sync_user_permissions(self) -> Dict:
        """Sincronizează permisiunile utilizatorilor din cloud"""
        try:
            print(f"  👤 Fetching user permissions...")
            
            # Query: Get all users with permissions
            url = f"{self.supabase_url}/rest/v1/discord_users"
            params = {
                "select": "discord_id,username,is_superuser,is_admin,granular_permissions,created_at,updated_at"
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"     ⚠️  HTTP {response.status_code}")
                return {"status": "failed", "count": 0}
            
            data = response.json()
            print(f"     Found {len(data)} users")
            
            # Save to users_permissions.json
            perms_file = self.data_dir / "users_permissions.json"
            
            json_data = {
                "users": {},
                "last_sync": datetime.now().isoformat(),
                "sync_status": "cloud_synced",
                "version": "2.0"
            }
            
            for user in data:
                discord_id = str(user.get('discord_id', ''))
                if not discord_id:
                    continue
                
                # Parse permissions
                perms_str = user.get('granular_permissions', '{}')
                if isinstance(perms_str, str):
                    try:
                        perms = json.loads(perms_str) if perms_str else {}
                    except:
                        perms = {}
                else:
                    perms = perms_str if isinstance(perms_str, dict) else {}
                
                json_data["users"][discord_id] = {
                    "discord_id": user.get('discord_id'),
                    "username": user.get('username', 'Unknown'),
                    "is_superuser": user.get('is_superuser', False),
                    "is_admin": user.get('is_admin', False),
                    "permissions": perms,
                    "created_at": user.get('created_at'),
                    "updated_at": user.get('updated_at'),
                }
            
            # Write file
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(perms_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print(f"     ✅ Synced {len(json_data['users'])} users to users_permissions.json")
            
            return {
                "status": "success",
                "count": len(json_data['users']),
                "file": str(perms_file)
            }
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
            return {"status": "error", "count": 0, "error": str(e)}
    
    def _sync_audit_logs(self) -> Dict:
        """Sincronizează audit logs din cloud"""
        try:
            print(f"  📋 Fetching audit logs...")
            
            # Query: Get recent logs (last 1000)
            url = f"{self.supabase_url}/rest/v1/audit_logs"
            params = {
                "select": "*",
                "order": "created_at.desc",
                "limit": 1000
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code not in [200, 206]:
                print(f"     ⚠️  HTTP {response.status_code} - logs may not be available")
                return {"status": "warning", "count": 0}
            
            data = response.json()
            if not data:
                print(f"     ℹ️  No logs found")
                return {"status": "success", "count": 0}
            
            print(f"     Found {len(data)} log entries")
            
            # Save to logs file
            logs_file = self.data_dir / "audit_logs.json"
            logs_data = {
                "logs": data[:1000],  # Keep last 1000
                "last_sync": datetime.now().isoformat(),
                "total_count": len(data)
            }
            
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(logs_file, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, ensure_ascii=False, indent=2)
            
            print(f"     ✅ Synced {len(data)} logs")
            
            return {
                "status": "success",
                "count": len(data)
            }
            
        except Exception as e:
            print(f"     ⚠️  Warning: {e} (logs optional)")
            return {"status": "warning", "count": 0}
    
    def _verify_data_integrity(self) -> Dict:
        """Verifica integritatea datelor descărcate"""
        try:
            print(f"  🔍 Checking data...")
            
            issues = []
            
            # Check police data
            data_dir = self.data_dir
            if not data_dir.exists():
                issues.append("Data directory doesn't exist")
            else:
                cities = [d for d in data_dir.iterdir() if d.is_dir()]
                print(f"     Found {len(cities)} cities in local data")
                if len(cities) == 0:
                    issues.append("No cities found in local data")
            
            # Check permissions file
            perms_file = self.data_dir / "users_permissions.json"
            if not perms_file.exists():
                issues.append("users_permissions.json not found")
            else:
                with open(perms_file, 'r') as f:
                    perms_data = json.load(f)
                    user_count = len(perms_data.get('users', {}))
                    print(f"     Found {user_count} users in permissions")
                    if user_count == 0:
                        issues.append("No users in permissions file")
            
            if issues:
                return {
                    "status": "warning",
                    "issues": issues
                }
            
            print(f"     ✅ All checks passed")
            return {
                "status": "success",
                "issues": []
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def start_background_sync(self, interval: int = 300):
        """
        Pornește sync-ul în background (la 5 minute)
        
        Args:
            interval: Interval în secunde (default 300 = 5 min)
        """
        if self.sync_thread and self.sync_thread.is_alive():
            print("⚠️  Sync thread already running")
            return
        
        def sync_worker():
            while True:
                try:
                    time.sleep(interval)
                    print(f"\n🔄 Background sync check...")
                    result = self.full_cloud_sync_on_startup()
                    if result["status"] != "success":
                        print(f"  ⚠️  Sync warning: {result['message']}")
                except Exception as e:
                    print(f"  ❌ Background sync error: {e}")
        
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
        print(f"✅ Background sync started (interval: {interval}s)")
    
    def get_last_sync_time(self) -> str:
        """Retorna time-ul ultimei sincronizări"""
        if self.last_sync_time:
            return self.last_sync_time.isoformat()
        return "Never"
    
    def get_sync_status(self) -> Dict:
        """Retorna status-ul actual de sincronizare"""
        return {
            "is_syncing": self.is_syncing,
            "last_sync_time": self.get_last_sync_time(),
            "data_dir": str(self.data_dir)
        }


# ================== EXEMPLU DE UTILIZARE ==================

if __name__ == "__main__":
    from supabase_sync import SupabaseSync
    
    # Initialize
    supabase = SupabaseSync("supabase_config.ini")
    sync_manager = MultiDeviceSyncManager(supabase, "data")
    
    # Sync all data
    result = sync_manager.full_cloud_sync_on_startup()
    print(f"\nSync result: {result}")
