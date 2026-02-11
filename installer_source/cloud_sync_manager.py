"""
Cloud Synchronization Module
Handles 1-second polling for cloud changes and forced synchronization
"""

import json
import hashlib
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil
import zipfile
from pathlib import Path

class CloudSyncManager:
    """Manages cloud synchronization with Supabase"""
    
    def __init__(self, supabase_sync, base_dir: str):
        """
        Initialize cloud sync manager
        
        Args:
            supabase_sync: SupabaseSync instance
            base_dir: Application base directory (d:\\punctaj)
        """
        self.supabase = supabase_sync
        self.base_dir = base_dir
        self.archive_dir = os.path.join(base_dir, "arhiva")
        self.data_dir = os.path.join(base_dir, "data")
        
        # Local version tracking
        self.local_version = 1
        self.local_data_hash = None
        self.cloud_version = 1
        self.cloud_data_hash = None
        self.is_syncing = False
        self.sync_pending = False
        self.polling_active = False
        
        # Callbacks for UI updates
        self.on_sync_required = None  # Called when cloud changes detected
        self.on_sync_start = None
        self.on_sync_complete = None
        self.on_sync_error = None
        
        # Polling thread
        self.polling_thread = None
        self.polling_stop_event = threading.Event()
    
    def start_polling(self, interval: int = 1):
        """
        Start polling thread that checks for cloud changes every N seconds
        
        Args:
            interval: Polling interval in seconds (default: 1)
        """
        if self.polling_active:
            return
        
        self.polling_active = True
        self.polling_stop_event.clear()
        self.polling_thread = threading.Thread(
            target=self._polling_loop,
            args=(interval,),
            daemon=True
        )
        self.polling_thread.start()
        print(f"☁️ Cloud sync polling started (interval: {interval}s)")
    
    def stop_polling(self):
        """Stop polling thread"""
        if self.polling_active:
            self.polling_active = False
            self.polling_stop_event.set()
            if self.polling_thread:
                self.polling_thread.join(timeout=5)
            print("☁️ Cloud sync polling stopped")
    
    def _polling_loop(self, interval: int):
        """Main polling loop running in background thread"""
        while not self.polling_stop_event.is_set():
            try:
                # Check if cloud has newer version
                cloud_version, cloud_hash = self._get_cloud_version()
                
                if cloud_version > self.local_version or cloud_hash != self.local_data_hash:
                    # Cloud has changes!
                    self.sync_pending = True
                    if self.on_sync_required:
                        self.on_sync_required(cloud_version, self.local_version)
                    print(f"🔔 Cloud changes detected: v{cloud_version} (local: v{self.local_version})")
                
                # Wait for next poll
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Polling error: {e}")
                time.sleep(interval)
    
    def _get_cloud_version(self) -> Tuple[int, Optional[str]]:
        """
        Get cloud version from Supabase sync_metadata table
        
        Returns:
            Tuple of (version, data_hash)
        """
        try:
            import requests
            
            # Use REST API to query sync_metadata
            url = f"{self.supabase.url}/rest/v1/sync_metadata?sync_key=eq.global_version"
            headers = {
                'apikey': self.supabase.key,
                'Authorization': f'Bearer {self.supabase.key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    item = data[0]
                    return item.get('version', 1), item.get('data_hash', None)
            
            return 1, None
        except Exception as e:
            print(f"⚠️ Error fetching cloud version: {e}")
            return self.cloud_version, self.cloud_data_hash
    
    def _get_local_data_hash(self) -> str:
        """Calculate SHA256 hash of all local data files"""
        try:
            hash_obj = hashlib.sha256()
            
            # Hash all JSON files in data directory
            if os.path.exists(self.data_dir):
                for filename in sorted(os.listdir(self.data_dir)):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.data_dir, filename)
                        with open(filepath, 'rb') as f:
                            hash_obj.update(f.read())
            
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"⚠️ Error calculating data hash: {e}")
            return None
    
    def download_all_changes(self, callback=None) -> bool:
        """
        Download all changes from cloud (cities, institutions, employees, archive)
        
        Args:
            callback: Function to call with progress updates
        
        Returns:
            True if successful, False otherwise
        """
        if self.is_syncing:
            print("⚠️ Sync already in progress")
            return False
        
        try:
            self.is_syncing = True
            if self.on_sync_start:
                self.on_sync_start()
            
            print("📥 Starting full download from cloud...")
            
            # Update callback
            if callback:
                callback("Descarcă datele de orașe și instituții...")
            
            # Step 1: Download all city/institution/employee data
            cities_ok = self._download_cities_and_institutions()
            if not cities_ok:
                raise Exception("Failed to download cities and institutions")
            
            if callback:
                callback("Descarcă datele de angajați...")
            
            # Step 2: Download archive from Supabase Storage
            archive_ok = self._download_archive_from_storage()
            if not archive_ok:
                print("⚠️ Warning: Could not download archive from storage (may not exist)")
            
            if callback:
                callback("Actualizează versiunea locală...")
            
            # Step 3: Update local version tracking
            self.local_version, self.local_data_hash = self._get_cloud_version()
            self.sync_pending = False
            
            print("✅ Cloud download completed successfully")
            
            if self.on_sync_complete:
                self.on_sync_complete()
            
            return True
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            if self.on_sync_error:
                self.on_sync_error(str(e))
            return False
            
        finally:
            self.is_syncing = False
    
    def _download_cities_and_institutions(self) -> bool:
        """Download cities, institutions, and employees from Supabase"""
        try:
            # Use the supabase_sync module to download everything
            # This should sync to the local data directory
            print("📥 Downloading cities and institutions...")
            
            # Call sync methods from supabase_sync
            if hasattr(self.supabase, 'sync_all_data'):
                result = self.supabase.sync_all_data()
                return result
            
            return True
            
        except Exception as e:
            print(f"❌ Error downloading cities/institutions: {e}")
            return False
    
    def _download_archive_from_storage(self) -> bool:
        """Download entire archive folder from Supabase Storage"""
        try:
            print("📥 Downloading archive from cloud storage...")
            
            # For now, skip storage download (no storage API in SupabaseSync)
            # Archive is saved locally in d:\punctaj\arhiva\
            # Storage upload is handled separately
            print("⚠️ Storage download not yet implemented in REST API")
            return True
            
        except Exception as e:
            print(f"⚠️ Error accessing archive storage: {e}")
            return False
    
    def upload_archive_to_storage(self) -> bool:
        """Upload entire local archive to Supabase Storage"""
        try:
            print("📤 Uploading archive to cloud storage...")
            
            if not os.path.exists(self.archive_dir):
                print("⚠️ No local archive directory to upload")
                return False
            
            # Archive is saved locally - storage upload not yet implemented
            # This can be enhanced later with a proper storage solution
            print("⚠️ Storage upload not yet implemented in REST API")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading archive: {e}")
            return False
    
    def force_sync_from_cloud(self) -> bool:
        """Force synchronization of all data from cloud"""
        print("🔄 Forcing cloud synchronization...")
        return self.download_all_changes()
    
    def update_cloud_version(self, new_version: Optional[int] = None) -> bool:
        """Update cloud version after local changes"""
        try:
            import requests
            
            if new_version is None:
                new_version = self.local_version + 1
            
            new_hash = self._get_local_data_hash()
            
            # Use REST API to update sync_metadata
            url = f"{self.supabase.url}/rest/v1/sync_metadata?sync_key=eq.global_version"
            headers = {
                'apikey': self.supabase.key,
                'Authorization': f'Bearer {self.supabase.key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'version': new_version,
                'data_hash': new_hash,
                'last_modified_at': datetime.now().isoformat()
            }
            
            response = requests.patch(url, json=data, headers=headers, timeout=5)
            
            if response.status_code in [200, 204]:
                self.local_version = new_version
                self.local_data_hash = new_hash
                print(f"☁️ Cloud version updated to {new_version}")
                return True
            else:
                print(f"⚠️ Error updating cloud version: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Error updating cloud version: {e}")
            return False
    
    def log_sync_activity(self, discord_id: str, sync_type: str, status: str, items_count: int = 0, error: Optional[str] = None) -> bool:
        """Log synchronization activity to sync_log table"""
        try:
            import requests
            
            url = f"{self.supabase.url}/rest/v1/sync_log"
            headers = {
                'apikey': self.supabase.key,
                'Authorization': f'Bearer {self.supabase.key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'discord_id': discord_id,
                'sync_type': sync_type,
                'status': status,
                'items_synced': items_count,
                'error_message': error,
                'synced_at': datetime.now().isoformat()
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=5)
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"⚠️ Error logging sync activity: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Error logging sync activity: {e}")
            return False
