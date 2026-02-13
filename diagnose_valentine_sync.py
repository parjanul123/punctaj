#!/usr/bin/env python3
"""
🔍 DIAGNOSE VALENTINE SYNC - De ce nu apare Valentine in Supabase
"""

import os
import json
import requests
import configparser
from pathlib import Path

# Load config
config = configparser.ConfigParser()
config.read("supabase_config.ini")

SUPABASE_URL = config.get('supabase', 'url', fallback='')
SUPABASE_KEY = config.get('supabase', 'key', fallback='')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def check_valentine_local():
    """Check if Valentine exists locally"""
    print("\n" + "="*70)
    print("  📁 STEP 1: Check Local")
    print("="*70 + "\n")
    
    valentine_path = "data/Valentine"
    
    if os.path.exists(valentine_path):
        print(f"  ✅ Valentine folder EXISTS at: {valentine_path}")
        
        # List institutions
        institutions = []
        for file in os.listdir(valentine_path):
            if file.endswith('.json'):
                inst_name = file[:-5]
                institutions.append(inst_name)
                print(f"     🏢 Institution: {inst_name}")
                
                # Show employee count
                try:
                    with open(os.path.join(valentine_path, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        emp_count = len(data.get('rows', []))
                        print(f"        👥 Employees: {emp_count}")
                except:
                    pass
        
        return True, institutions
    else:
        print(f"  ❌ Valentine folder MISSING")
        return False, []

def check_valentine_in_cities():
    """Check if Valentine is in Supabase cities table"""
    print("\n" + "="*70)
    print("  🏙️  STEP 2: Check Supabase cities Table")
    print("="*70 + "\n")
    
    url = f"{SUPABASE_URL}/rest/v1/cities?select=*&order=name.asc"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            cities = response.json()
            print(f"  ✅ cities table accessible")
            print(f"     Total cities: {len(cities)}\n")
            
            for city in cities:
                print(f"     🏙️  {city.get('name')} (ID: {city.get('id')})")
            
            # Check if Valentine in list
            valentine_exists = any(c.get('name') == 'Valentine' for c in cities)
            
            if valentine_exists:
                print(f"\n  ✅ Valentine FOUND in cities table")
                return True
            else:
                print(f"\n  ❌ Valentine NOT in cities table")
                return False
        
        elif response.status_code == 404:
            print(f"  ❌ cities table NOT FOUND")
            return False
        else:
            print(f"  ⚠️  Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_valentine_institutions():
    """Check if Valentine institutions are in Supabase"""
    print("\n" + "="*70)
    print("  🏢 STEP 3: Check Supabase institutions Table")
    print("="*70 + "\n")
    
    url = f"{SUPABASE_URL}/rest/v1/institutions?select=*&order=name.asc"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            institutions = response.json()
            print(f"  ✅ institutions table accessible")
            print(f"     Total institutions: {len(institutions)}\n")
            
            valentine_insts = [i for i in institutions if i.get('city_id')]
            
            if valentine_insts:
                print(f"     Found {len(valentine_insts)} institutions:")
                for inst in valentine_insts[:5]:  # Show first 5
                    print(f"     🏢 {inst.get('name')} (City ID: {inst.get('city_id')})")
            
            return len(institutions) > 0
        
        else:
            print(f"  ⚠️  Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_valentine_police_data():
    """Check if Valentine data is in police_data"""
    print("\n" + "="*70)
    print("  📄 STEP 4: Check Supabase police_data Table")
    print("="*70 + "\n")
    
    url = f"{SUPABASE_URL}/rest/v1/police_data?select=*&order=updated_at.desc"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            records = response.json()
            print(f"  ✅ police_data table accessible")
            print(f"     Total records: {len(records)}\n")
            
            valentine_records = [r for r in records if r.get('city') == 'Valentine']
            
            if valentine_records:
                print(f"  ✅ Valentine FOUND in police_data")
                print(f"     Records: {len(valentine_records)}\n")
                
                for record in valentine_records:
                    print(f"     City: {record.get('city')}")
                    print(f"     Institution: {record.get('institution')}")
                    print(f"     Updated: {record.get('updated_at')}")
                    print()
                
                return True
            else:
                print(f"  ❌ Valentine NOT in police_data")
                print(f"\n     Latest records in table:")
                for record in records[:3]:
                    print(f"     - {record.get('city')}/{record.get('institution')}")
                
                return False
        
        elif response.status_code == 404:
            print(f"  ❌ police_data table NOT FOUND")
            print(f"     Solution: python initialize_supabase_tables.py")
            return False
        else:
            print(f"  ⚠️  Status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def sync_valentine_now():
    """Try to sync Valentine to Supabase"""
    print("\n" + "="*70)
    print("  🔄 STEP 5: Sync Valentine NOW")
    print("="*70 + "\n")
    
    print("  Attempting manual sync...")
    
    try:
        # Import sync manager
        from supabase_sync import SupabaseSync
        
        sync = SupabaseSync()
        
        if not sync.enabled:
            print("  ⚠️  Supabase sync is DISABLED in config")
            return False
        
        # Load Valentine data
        valentine_path = "data/Valentine"
        
        if not os.path.exists(valentine_path):
            print("  ❌ Valentine folder not found")
            return False
        
        synced = 0
        failed = 0
        
        for file in os.listdir(valentine_path):
            if not file.endswith('.json'):
                continue
            
            institution = file[:-5]
            
            try:
                with open(os.path.join(valentine_path, file), 'r', encoding='utf-8') as f:
                    inst_data = json.load(f)
                
                print(f"  Syncing: {institution}...", end=' ')
                
                result = sync.sync_data("Valentine", institution, inst_data)
                
                if result:
                    print("✅")
                    synced += 1
                else:
                    print("❌")
                    failed += 1
            
            except Exception as e:
                print(f"❌ ({e})")
                failed += 1
        
        print(f"\n  Results: {synced} synced, {failed} failed")
        
        return synced > 0
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("  🔍 VALENTINE SYNC DIAGNOSTIC")
    print("  De ce nu apare Valentine in Supabase?")
    print("="*70)
    
    # Step 1
    local_ok, institutions = check_valentine_local()
    
    if not local_ok:
        print("\n❌ ISSUE: Valentine not found locally!")
        return
    
    # Step 2
    cities_ok = check_valentine_in_cities()
    
    # Step 3
    insts_ok = check_valentine_institutions()
    
    # Step 4
    police_ok = check_valentine_police_data()
    
    # Summary
    print("\n" + "="*70)
    print("  📊 DIAGNOSIS SUMMARY")
    print("="*70 + "\n")
    
    print(f"  ✅ Local: Valentine found with {len(institutions)} institutions")
    print(f"  {'✅' if cities_ok else '❌'} Supabase cities: {'Valentine present' if cities_ok else 'Valentine MISSING'}")
    print(f"  {'✅' if insts_ok else '❌'} Supabase institutions: {'Has records' if insts_ok else 'No records'}")
    print(f"  {'✅' if police_ok else '❌'} Supabase police_data: {'Valentine data present' if police_ok else 'Valentine data MISSING'}")
    
    # Recommendations
    print("\n" + "="*70)
    print("  🔧 RECOMMENDED FIXES")
    print("="*70 + "\n")
    
    if not cities_ok or not police_ok:
        print("  1️⃣  CREATE MISSING TABLES")
        print("     python initialize_supabase_tables.py\n")
        
        print("  2️⃣  MANUAL SYNC Valentine")
        print("     Running sync now...\n")
        
        if sync_valentine_now():
            print("\n  ✅ SYNC SUCCESSFUL!")
            print("     Valentine should now appear in Supabase")
        else:
            print("\n  ⚠️  Sync failed - may need to fix RLS")
            print("     python disable_rls_for_testing.py")
    
    elif not cities_ok and not police_ok:
        print("  ❌ Valentine exists locally but NOT in Supabase")
        print("\n  Solutions (in order):")
        print("  1. python initialize_supabase_tables.py  (create tables)")
        print("  2. python disable_rls_for_testing.py    (disable RLS)")
        print("  3. python punctaj.py                    (restart app)")
        print("  4. The app will auto-sync Valentine on startup")
    
    else:
        print("  ✅ Valentine is ALREADY synced in Supabase!")
        print("     No action needed")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
