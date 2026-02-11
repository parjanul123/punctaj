#!/usr/bin/env python3
"""
Standardized Data Directory Manager
Ensures all devices use Punctaj/Data folder for storing and syncing data
"""

import os
import sys
from pathlib import Path
import shutil
import json

class DataDirectoryManager:
    """Manages data directories across all devices with standard structure"""
    
    # Standard folder structure on ANY device
    STANDARD_STRUCTURE = [
        "data",              # Local cached data
        "data/BlackWater",   # City 1
        "data/Saint_Denis",  # City 2
        "arhiva",            # Archive
        "logs",              # Application logs
        ".config",           # Hidden config folder
    ]
    
    def __init__(self, base_path=None):
        """
        Initialize data manager
        
        Args:
            base_path: Custom base path (defaults to Punctaj/Data)
        """
        
        if base_path:
            self.base_dir = Path(base_path)
        else:
            # Determine installation directory
            if getattr(sys, 'frozen', False):
                # Running as EXE
                exe_dir = Path(os.path.dirname(sys.executable))
            else:
                # Running as script
                exe_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            
            # Check if in a folder named something like Punctaj_DeviceX or Punctaj
            parent_dir = exe_dir.parent
            
            # Use parent/data if exe is in root, otherwise use exe_dir/data
            if exe_dir.name.startswith('Punctaj'):
                self.base_dir = exe_dir
            else:
                self.base_dir = exe_dir
        
        print(f"📁 Data Directory: {self.base_dir}")
        self.ensure_structure()
    
    def ensure_structure(self):
        """Create standard folder structure if missing"""
        
        print("\n🔧 Ensuring standard data structure...")
        
        for folder in self.STANDARD_STRUCTURE:
            folder_path = self.base_dir / folder
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created: {folder}")
            else:
                print(f"   ✓ Exists: {folder}")
        
        print("✅ Data structure ready")
    
    def get_data_dir(self):
        """Get path to data directory"""
        return self.base_dir / "data"
    
    def get_city_dir(self, city_name):
        """Get path to city-specific data"""
        city_dir = self.base_dir / "data" / city_name
        city_dir.mkdir(parents=True, exist_ok=True)
        return city_dir
    
    def get_archive_dir(self):
        """Get path to archive directory"""
        return self.base_dir / "arhiva"
    
    def get_logs_dir(self):
        """Get path to logs directory"""
        return self.base_dir / "logs"
    
    def get_config_dir(self):
        """Get path to config directory"""
        return self.base_dir / ".config"
    
    def get_file_in_city(self, city_name, filename):
        """Get full path to a file in a city folder"""
        city_dir = self.get_city_dir(city_name)
        return city_dir / filename
    
    def ensure_city_data(self, city_name, data_template=None):
        """
        Ensure a city has basic data file
        
        Args:
            city_name: Name of the city
            data_template: Optional template data
        """
        
        city_dir = self.get_city_dir(city_name)
        data_file = city_dir / "Politie.json"
        
        if not data_file.exists():
            print(f"\n📝 Creating data file for {city_name}...")
            
            if data_template is None:
                data_template = {
                    "columns": [
                        "DISCORD", "NUME IC", "SERIE DE BULETIN",
                        "RANK", "ROLE", "PUNCTAJ", "ULTIMA_MOD"
                    ],
                    "ranks": {
                        "1": "Officer",
                        "2": "Corporal",
                        "3": "Sergeant",
                        "4": "Plutonian",
                        "5": "Lieutenant Instructor",
                        "6": "Sheriff Adjunct",
                        "7": "Sheriff"
                    },
                    "rows": [],
                    "version": 2,
                    "source": "local",
                    "city_id": None,
                    "institution_id": None
                }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data_template, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Created: {data_file}")
        else:
            print(f"   ✓ Exists: {city_name}/Politie.json")
    
    def download_from_cloud(self, city_name, data_from_cloud):
        """
        Save cloud-downloaded data to local file
        
        Args:
            city_name: City name
            data_from_cloud: Data from Supabase
        """
        
        city_dir = self.get_city_dir(city_name)
        data_file = city_dir / "Politie.json"
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data_from_cloud, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Downloaded {city_name} data to {data_file}")
    
    def upload_to_cloud(self, city_name):
        """
        Load local data for upload to cloud
        
        Args:
            city_name: City name
            
        Returns:
            Data dictionary or None if file doesn't exist
        """
        
        data_file = self.get_file_in_city(city_name, "Politie.json")
        
        if not data_file.exists():
            print(f"⚠️  Data file not found: {data_file}")
            return None
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ Error loading {city_name} data: {e}")
            return None
    
    def get_all_cities(self):
        """Get list of all cities with data"""
        
        data_dir = self.get_data_dir()
        cities = []
        
        if data_dir.exists():
            for item in data_dir.iterdir():
                if item.is_dir():
                    cities.append(item.name)
        
        return sorted(cities)
    
    def print_status(self):
        """Print detailed status of data directories"""
        
        print("\n" + "="*70)
        print("📊 DATA DIRECTORY STATUS")
        print("="*70)
        
        print(f"\nBase Directory: {self.base_dir}")
        
        # Check each standard folder
        for folder in self.STANDARD_STRUCTURE:
            folder_path = self.base_dir / folder
            exists = "✅" if folder_path.exists() else "❌"
            
            if folder_path.exists() and folder_path.is_dir():
                # Count files in directory
                file_count = len(list(folder_path.rglob('*')))
                print(f"{exists} {folder:<20} ({file_count} items)")
            else:
                print(f"{exists} {folder:<20}")
        
        # List cities
        print(f"\nCities:")
        cities = self.get_all_cities()
        if cities:
            for city in cities:
                city_dir = self.get_city_dir(city)
                files = list(city_dir.glob("*.json"))
                print(f"  ✅ {city:<20} ({len(files)} files)")
        else:
            print("  ⚠️  No cities found")
        
        print("=" * 70)

def setup_data_directories():
    """Setup data directories for first-time use"""
    
    print("\n" + "="*70)
    print("🚀 SETTING UP DATA DIRECTORIES")
    print("="*70)
    
    manager = DataDirectoryManager()
    
    # Create standard cities
    print("\n📝 Creating city data files...")
    
    cities_templates = {
        "BlackWater": {
            "columns": ["DISCORD", "NUME IC", "SERIE DE BULETIN", "RANK", "ROLE", "PUNCTAJ", "ULTIMA_MOD"],
            "ranks": {
                "1": "Officer",
                "2": "Corporal", 
                "3": "Sergeant",
                "4": "Plutonian",
                "5": "Lieutenant Instructor",
                "6": "Sheriff Adjunct",
                "7": "Sheriff"
            },
            "rows": [],
            "version": 2,
            "source": "local",
            "city_id": 5,
            "institution_id": 1
        },
        "Saint_Denis": {
            "columns": ["DISCORD", "NUME IC", "SERIE DE BULETIN", "RANK", "ROLE", "PUNCTAJ", "ULTIMA_MOD"],
            "ranks": {
                "1": "Officer",
                "2": "Corporal",
                "3": "Sergeant", 
                "4": "Plutonian",
                "5": "Lieutenant Instructor",
                "6": "Sheriff Adjunct",
                "7": "Sheriff"
            },
            "rows": [],
            "version": 2,
            "source": "local",
            "city_id": 6,
            "institution_id": 1
        }
    }
    
    for city_name, template in cities_templates.items():
        manager.ensure_city_data(city_name, template)
    
    # Print status
    manager.print_status()
    
    print("\n✅ Data directories setup complete!")
    return manager

if __name__ == "__main__":
    manager = setup_data_directories()
