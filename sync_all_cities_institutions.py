#!/usr/bin/env python3
"""
📍 SYNC ALL CITIES & INSTITUTIONS TO SUPABASE
Sincronizează toate orașul și instituții din folderul local data/ la Supabase
"""

import os
import json
import configparser
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ ERROR: requests library not found. Install with: pip install requests")
    exit(1)

# Load config
config = configparser.ConfigParser()
config_path = Path(__file__).parent / "supabase_config.ini"
config.read(config_path)

SUPABASE_URL = config.get('supabase', 'url', fallback='')
SUPABASE_KEY = config.get('supabase', 'key', fallback='')
DATA_DIR = "data"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: supabase_config.ini not configured")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def city_exists(city_name: str) -> bool:
    """Check if city exists in Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/cities?name=eq.{city_name}&select=id"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return len(response.json()) > 0
    except Exception as e:
        print(f"   ⚠️  Error checking city: {e}")
    return False

def create_city(city_name: str) -> dict:
    """Create city in Supabase and return it"""
    url = f"{SUPABASE_URL}/rest/v1/cities"
    payload = {"name": city_name}
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if response.status_code in [200, 201]:
            result = response.json()
            city = result[0] if isinstance(result, list) else result
            print(f"   ✅ City created: {city_name} (ID: {city.get('id')})")
            return city
    except Exception as e:
        print(f"   ❌ Error creating city: {e}")
    
    return None

def get_city_by_name(city_name: str) -> dict:
    """Get city from Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/cities?name=eq.{city_name}&select=*"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]
    except Exception as e:
        print(f"   ⚠️  Error fetching city: {e}")
    
    return None

def institution_exists(city_id: int, institution_name: str) -> bool:
    """Check if institution exists"""
    url = f"{SUPABASE_URL}/rest/v1/institutions?city_id=eq.{city_id}&name=eq.{institution_name}&select=id"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return len(response.json()) > 0
    except Exception as e:
        print(f"   ⚠️  Error checking institution: {e}")
    return False

def create_institution(city_id: int, institution_name: str) -> dict:
    """Create institution in Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/institutions"
    payload = {"city_id": city_id, "name": institution_name}
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if response.status_code in [200, 201]:
            result = response.json()
            institution = result[0] if isinstance(result, list) else result
            print(f"   ✅ Institution created: {institution_name} (ID: {institution.get('id')})")
            return institution
    except Exception as e:
        print(f"   ❌ Error creating institution: {e}")
    
    return None

def sync_police_data(city_name: str, institution_name: str, institution_id: int):
    """Also sync the police_data (institution JSON) for this institution"""
    # Try to load the institution JSON
    institution_path = os.path.join(DATA_DIR, city_name, f"{institution_name}.json")
    
    if not os.path.exists(institution_path):
        return
    
    try:
        with open(institution_path, 'r', encoding='utf-8') as f:
            inst_data = json.load(f)
        
        # Upload to police_data table
        url = f"{SUPABASE_URL}/rest/v1/police_data"
        sync_record = {
            'city': city_name,
            'institution': institution_name,
            'data_json': json.dumps(inst_data),
            'updated_at': Path(institution_path).stat().st_mtime
        }
        
        # Check if record exists
        check_url = f"{url}?city=eq.{city_name}&institution=eq.{institution_name}"
        response = requests.get(check_url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            existing = response.json()
            if existing:
                # Update
                requests.patch(check_url, json=sync_record, headers=HEADERS, timeout=10)
                print(f"      ↔️  Updated police_data for {institution_name}")
            else:
                # Insert
                requests.post(url, json=sync_record, headers=HEADERS, timeout=10)
                print(f"      ✅ Synced police_data for {institution_name}")
    except Exception as e:
        print(f"      ⚠️  Error syncing police_data: {e}")

def main():
    print("\n" + "="*70)
    print("  📍 SYNC ALL CITIES & INSTITUTIONS TO SUPABASE")
    print("="*70)
    
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ ERROR: {DATA_DIR} folder not found")
        return
    
    cities_created = 0
    institutions_created = 0
    police_data_synced = 0
    
    # Scan all cities
    for city_dir_name in sorted(os.listdir(DATA_DIR)):
        city_path = os.path.join(DATA_DIR, city_dir_name)
        
        # Skip files, only process directories
        if not os.path.isdir(city_path):
            continue
        
        print(f"\n📍 Processing city: {city_dir_name}")
        
        # Check if city exists, create if not
        if not city_exists(city_dir_name):
            print(f"   Não existe em Supabase, criando...")
            city_obj = create_city(city_dir_name)
            if not city_obj:
                print(f"   ❌ Failed to create city")
                continue
            cities_created += 1
        else:
            print(f"   ✓ City already exists")
            city_obj = get_city_by_name(city_dir_name)
        
        if not city_obj or 'id' not in city_obj:
            print(f"   ❌ Cannot get city ID")
            continue
        
        city_id = city_obj['id']
        
        # Scan institutions in this city
        for json_file in sorted(os.listdir(city_path)):
            if not json_file.endswith('.json'):
                continue
            
            institution_name = json_file[:-5]  # Remove .json
            
            # Check if institution exists, create if not
            if not institution_exists(city_id, institution_name):
                print(f"   🏢 Não existe: {institution_name}, criando...")
                inst_obj = create_institution(city_id, institution_name)
                if inst_obj:
                    institutions_created += 1
                    sync_police_data(city_dir_name, institution_name, inst_obj.get('id'))
                    police_data_synced += 1
            else:
                print(f"   ✓ Institution exists: {institution_name}")
                # Still try to sync police_data
                sync_police_data(city_dir_name, institution_name, city_id)
                police_data_synced += 1
    
    # Summary
    print(f"\n\n" + "="*70)
    print("  📊 SYNC COMPLETED")
    print("="*70)
    print(f"\n  📍 Cities created: {cities_created}")
    print(f"  🏢 Institutions created: {institutions_created}")
    print(f"  📄 Police data synced: {police_data_synced}")
    
    if cities_created == 0 and institutions_created == 0:
        print(f"\n  ✅ All cities and institutions already in sync!")
    else:
        print(f"\n  ✅ Sync completed successfully!")
    
    print(f"\n  Next step: Verify all data appears in Supabase:")
    print(f"     - Check cities table at https://supabase.com/dashboard/.../cities")
    print(f"     - Check institutions at https://supabase.com/dashboard/.../institutions")
    print(f"     - Check police_data at https://supabase.com/dashboard/.../police_data")
    
    print(f"\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
