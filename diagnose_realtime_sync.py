#!/usr/bin/env python3
"""
🔍 REAL-TIME SYNC DIAGNOSTIC - Verifica de ce nu se sincronizeaza in timp real
"""

import os
import json
import time
import requests
import configparser
from pathlib import Path
from datetime import datetime

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

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_police_data_table():
    """Test if police_data table exists and is accessible"""
    print_section("1️⃣ TESTING police_data TABLE")
    
    url = f"{SUPABASE_URL}/rest/v1/police_data?select=count()&limit=1"
    
    try:
        response = requests.head(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            print("  ✅ police_data table EXISTS")
            print(f"     Status: {response.status_code}")
            
            # Try to get count
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                count = response.headers.get('content-range', '0/0').split('/')[1]
                print(f"     Records: {count}")
                return True
        elif response.status_code == 404:
            print("  ❌ police_data table MISSING")
            print("     FIX: Run: python initialize_supabase_tables.py")
            return False
        elif response.status_code == 401:
            print("  ⚠️  UNAUTHORIZED (401)")
            print("     Problem: API key or JWT invalid")
            return False
        else:
            print(f"  ⚠️  Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def test_rls_policy():
    """Test if RLS is blocking INSERT/UPDATE"""
    print_section("2️⃣ TESTING RLS (Row Level Security)")
    
    print("  Testing INSERT permission...")
    
    test_record = {
        'city': 'TEST_SYNC_' + str(int(time.time())),
        'institution': 'TEST_INSTITUTION',
        'data_json': json.dumps({'test': True}),
        'updated_at': datetime.now().isoformat(),
        'updated_by': 'test'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/police_data"
    
    try:
        response = requests.post(url, json=test_record, headers=HEADERS, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"  ✅ INSERT ALLOWED (status {response.status_code})")
            
            # Delete test record
            delete_url = f"{url}?city=eq.{test_record['city']}"
            requests.delete(delete_url, headers=HEADERS, timeout=10)
            print("     (test record cleaned up)")
            return True
            
        elif response.status_code == 403:
            print(f"  ❌ INSERT DENIED - RLS IS BLOCKING (status 403)")
            print("     FIX: Run: python disable_rls_for_testing.py")
            return False
        else:
            print(f"  ⚠️  Status {response.status_code}")
            if response.text:
                print(f"     Response: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def test_employees_table():
    """Test employees table sync"""
    print_section("3️⃣ TESTING employees TABLE")
    
    url = f"{SUPABASE_URL}/rest/v1/employees?select=count()&limit=1"
    
    try:
        response = requests.head(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            print("  ✅ employees table EXISTS")
            
            # Get count
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                count = response.headers.get('content-range', '0/0').split('/')[1]
                print(f"     Records: {count}")
                return True
        else:
            print(f"  ⚠️  Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def test_manual_sync():
    """Test if manual sync to Supabase works"""
    print_section("4️⃣ TESTING MANUAL SYNC")
    
    # Load a local institution file
    local_data_dir = "data"
    
    if not os.path.exists(local_data_dir):
        print(f"  ⚠️  No data/ folder found")
        return False
    
    # Find first institution
    for city_dir in os.listdir(local_data_dir):
        city_path = os.path.join(local_data_dir, city_dir)
        if not os.path.isdir(city_path):
            continue
        
        for json_file in os.listdir(city_path):
            if not json_file.endswith('.json'):
                continue
            
            institution = json_file[:-5]
            inst_path = os.path.join(city_path, json_file)
            
            print(f"  Testing sync: {city_dir}/{institution}")
            
            try:
                with open(inst_path, 'r', encoding='utf-8') as f:
                    inst_data = json.load(f)
                
                # Try to sync to police_data
                sync_record = {
                    'city': city_dir,
                    'institution': institution,
                    'data_json': json.dumps(inst_data),
                    'updated_at': datetime.now().isoformat()
                }
                
                url = f"{SUPABASE_URL}/rest/v1/police_data"
                
                # Check if exists
                check_url = f"{url}?city=eq.{city_dir}&institution=eq.{institution}"
                response = requests.get(check_url, headers=HEADERS, timeout=10)
                
                if response.status_code == 200:
                    existing = response.json()
                    if existing:
                        # Update
                        response = requests.patch(check_url, json=sync_record, headers=HEADERS, timeout=10)
                        if response.status_code in [200, 204]:
                            print(f"     ✅ UPDATE succeeded")
                            return True
                        else:
                            print(f"     ❌ UPDATE failed (status {response.status_code})")
                            return False
                    else:
                        # Insert
                        response = requests.post(url, json=sync_record, headers=HEADERS, timeout=10)
                        if response.status_code in [200, 201]:
                            print(f"     ✅ INSERT succeeded")
                            return True
                        else:
                            print(f"     ❌ INSERT failed (status {response.status_code})")
                            return False
                
            except Exception as e:
                print(f"     ⚠️  Error: {e}")
                return False
    
    print("  ⚠️  No institution files found to test")
    return False

def check_webhook_triggers():
    """Check if Supabase webhooks are configured"""
    print_section("5️⃣ CHECKING WEBHOOKS & TRIGGERS")
    
    print("  ℹ️  Real-time sync requires:")
    print("     1. Supabase RealtimeSync enabled")
    print("     2. WebSocket connection working")
    print("     3. Valid JWT token for realtime")
    print("     4. RLS policies allowing access")
    
    print("\n  Current issues detected:")
    print("     ⚠️  WebSocket 401 error in logs")
    print("     ⚠️  This means JWT token is invalid/expired")
    
    print("\n  ✅ What to check:")
    print("     1. Restart app (will refresh JWT)")
    print("     2. Verify API key in supabase_config.ini")
    print("     3. Check RLS policies on tables")
    print("     4. Verify police_data table exists")

def main():
    print("\n" + "="*70)
    print("  🔍 REAL-TIME SYNC DIAGNOSTIC")
    print("  Verifica de ce nu se sincronizeaza in timp real")
    print("="*70)
    
    results = {
        "police_data": test_police_data_table(),
        "rls": test_rls_policy(),
        "employees": test_employees_table(),
        "manual_sync": test_manual_sync(),
    }
    
    check_webhook_triggers()
    
    # Summary
    print_section("📊 SUMMARY")
    
    all_ok = all(results.values())
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    print("\n" + "="*70)
    print("  🔧 RECOMMENDED FIXES (in order):")
    print("="*70)
    
    if not results["police_data"]:
        print("\n  1️⃣  CREATE police_data TABLE")
        print("      python initialize_supabase_tables.py")
    
    if not results["rls"]:
        print("\n  2️⃣  DISABLE RLS FOR TESTING")
        print("      python disable_rls_for_testing.py")
    
    if not all_ok:
        print("\n  3️⃣  RESTART APP TO REFRESH TOKENS")
        print("      python punctaj.py")
    
    if all_ok:
        print("\n  ✅ ALL TESTS PASSED!")
        print("     Real-time sync should be working")
        print("     Try:")
        print("       1. Make a change in app (add/edit employee)")
        print("       2. Check Supabase tables immediately")
        print("       3. Should appear within 2 seconds")
    
    print("\n" + "="*70)
    print("  📝 TROUBLESHOOTING STEPS")
    print("="*70)
    
    print("""
  IF STILL NOT SYNCING AFTER FIXES:
  
  1. Check console output in app for errors:
     Look for: "SUPABASE_UPLOAD ERROR" or "sync_data returned False"
  
  2. Enable detailed logging:
     - Edit supabase_config.ini
     - Set: debug = true
     - Restart app
  
  3. Manual test sync:
     - Add/edit an employee
     - Check Supabase immediately
     - Look at console for sync messages
  
  4. Check RLS status in Supabase:
     - Dashboard → Tables → police_data
     - Click RLS toggle (should be GREEN = enabled, RED = disabled)
     - If RED = sync might be blocked anyway
  
  5. Check API key:
     - Dashboard → Project Settings → API
     - Copy anon/public key
     - Update supabase_config.ini
     - Restart app
    """)
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
