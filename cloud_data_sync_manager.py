#!/usr/bin/env python3
"""
Cloud Data Sync Manager
Automatically downloads and manages data in Punctaj/Data folder
"""

import os
import json
from pathlib import Path
from datetime import datetime

class CloudDataSyncManager:
    """Manages cloud-to-local data synchronization in Punctaj/Data"""
    
    def __init__(self, data_manager, supabase_sync=None):
        """
        Initialize cloud sync manager
        
        Args:
            data_manager: DataDirectoryManager instance
            supabase_sync: SupabaseSync instance for cloud operations
        """
        self.data_manager = data_manager
        self.supabase_sync = supabase_sync
        self.sync_log = []
    
    def sync_city_from_cloud(self, city_name, city_id):
        """
        Download city data from cloud to Punctaj/Data/CityName
        
        Args:
            city_name: City name (e.g., "BlackWater")
            city_id: City ID in Supabase
            
        Returns:
            True if successful, False otherwise
        """
        
        if not self.supabase_sync:
            print(f"⚠️  Supabase sync not available, skipping cloud sync for {city_name}")
            return False
        
        try:
            print(f"\n☁️  Syncing {city_name} from cloud...")
            
            # Fetch from cloud
            response = self.supabase_sync.supabase.table("employee_data")\
                .select("*")\
                .eq("city_id", city_id)\
                .execute()
            
            if response.data:
                # Prepare data
                cloud_data = {
                    "columns": ["DISCORD", "NUME IC", "SERIE DE BULETIN", "RANK", "ROLE", "PUNCTAJ", "ULTIMA_MOD"],
                    "rows": response.data,
                    "version": 2,
                    "source": "supabase",
                    "city_id": city_id,
                    "institution_id": 1,
                    "synced_at": datetime.now().isoformat()
                }
                
                # Save to local Punctaj/Data
                self.data_manager.download_from_cloud(city_name, cloud_data)
                self.sync_log.append(f"✅ {city_name}: {len(response.data)} records")
                return True
            else:
                print(f"   ⚠️  No data in cloud for {city_name}")
                self.sync_log.append(f"⚠️  {city_name}: No cloud data")
                return False
        
        except Exception as e:
            print(f"   ❌ Error syncing {city_name}: {e}")
            self.sync_log.append(f"❌ {city_name}: {str(e)}")
            return False
    
    def sync_city_to_cloud(self, city_name, city_id):
        """
        Upload city data from Punctaj/Data to cloud
        
        Args:
            city_name: City name
            city_id: City ID in Supabase
            
        Returns:
            True if successful
        """
        
        if not self.supabase_sync:
            print(f"⚠️  Supabase sync not available")
            return False
        
        try:
            print(f"\n☁️  Uploading {city_name} to cloud...")
            
            # Load from local
            local_data = self.data_manager.upload_to_cloud(city_name)
            
            if not local_data or "rows" not in local_data:
                print(f"   ⚠️  No local data for {city_name}")
                return False
            
            # Upload each row
            for row in local_data["rows"]:
                row["city_id"] = city_id
                row["institution_id"] = 1
            
            response = self.supabase_sync.supabase.table("employee_data")\
                .upsert(local_data["rows"])\
                .execute()
            
            print(f"   ✅ Uploaded {len(local_data['rows'])} records")
            self.sync_log.append(f"✅ {city_name}: Uploaded to cloud")
            return True
        
        except Exception as e:
            print(f"   ❌ Error uploading {city_name}: {e}")
            self.sync_log.append(f"❌ {city_name}: Upload failed")
            return False
    
    def sync_all_cities(self, cities_config):
        """
        Sync all cities from cloud
        
        Args:
            cities_config: Dict with city names and IDs
                Example: {"BlackWater": 5, "Saint_Denis": 6}
        """
        
        print("\n" + "="*70)
        print("☁️  CLOUD DATA SYNCHRONIZATION")
        print("="*70)
        
        self.sync_log = []
        
        for city_name, city_id in cities_config.items():
            self.sync_city_from_cloud(city_name, city_id)
        
        # Print summary
        print("\n" + "="*70)
        print("📊 SYNC SUMMARY")
        print("="*70)
        for log_entry in self.sync_log:
            print(log_entry)
        
        return True
    
    def ensure_local_data(self):
        """Ensure all cities have local data files"""
        
        print("\n🔧 Ensuring local data files...")
        
        for city_name in self.data_manager.get_all_cities():
            self.data_manager.ensure_city_data(city_name)
        
        print("✅ Local data ensured")
    
    def get_sync_status(self):
        """Get current sync status"""
        
        status = {
            "base_directory": str(self.data_manager.base_dir),
            "data_directory": str(self.data_manager.get_data_dir()),
            "cities": self.data_manager.get_all_cities(),
            "last_sync": datetime.now().isoformat(),
            "logs": self.sync_log
        }
        
        return status

def startup_cloud_sync(data_manager, supabase_sync):
    """
    Run on app startup to sync cloud data to Punctaj/Data
    
    Args:
        data_manager: DataDirectoryManager instance
        supabase_sync: SupabaseSync instance
    """
    
    print("\n" + "="*70)
    print("🚀 STARTUP CLOUD DATA SYNC")
    print("="*70)
    
    try:
        sync_manager = CloudDataSyncManager(data_manager, supabase_sync)
        
        # Ensure local structure
        sync_manager.ensure_local_data()
        
        # Cities to sync
        cities_config = {
            "BlackWater": 5,
            "Saint_Denis": 6
        }
        
        # Sync all cities from cloud
        sync_manager.sync_all_cities(cities_config)
        
        print("\n✅ Startup sync complete!")
        print(f"📁 Data location: {data_manager.get_data_dir()}")
        
        return sync_manager
    
    except Exception as e:
        print(f"\n⚠️  Startup sync error: {e}")
        return None

if __name__ == "__main__":
    # For testing
    from data_directory_manager import DataDirectoryManager
    
    print("Testing Cloud Data Sync Manager...")
    manager = DataDirectoryManager()
    sync = CloudDataSyncManager(manager)
    sync.ensure_local_data()
