#!/usr/bin/env python3
"""
🔐 CHECK RLS STATUS - Verifica care tabele au RLS enabled/disabled
"""

import requests
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read("supabase_config.ini")

SUPABASE_URL = config.get('supabase', 'url', fallback='')
SUPABASE_KEY = config.get('supabase', 'key', fallback='')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Tables to check
TABLES_TO_CHECK = [
    "police_data",
    "employees", 
    "cities",
    "institutions",
    "discord_users",
    "audit_logs"
]

def check_table_rls(table_name):
    """Check if RLS is enabled on a table"""
    print(f"\n📊 Checking {table_name}...")
    
    # Try simple SELECT
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=count()&limit=1"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ SELECT allowed (status 200)")
            
            # Try INSERT with test record
            insert_url = f"{SUPABASE_URL}/rest/v1/{table_name}"
            test_record = {"test_field": "test_value"}
            
            insert_response = requests.post(insert_url, json=test_record, headers=HEADERS, timeout=5)
            
            if insert_response.status_code in [200, 201]:
                print(f"  ✅ INSERT allowed - RLS likely DISABLED or user has access")
                
                # Try to delete the test record
                try:
                    requests.delete(f"{insert_url}?test_field=eq.test_value", headers=HEADERS, timeout=5)
                except:
                    pass
                
                return "DISABLED"
            
            elif insert_response.status_code == 403:
                print(f"  ❌ INSERT denied (403) - RLS is BLOCKING")
                return "ENABLED"
            
            else:
                print(f"  ⚠️  INSERT status {insert_response.status_code}")
                print(f"     Response: {insert_response.text[:100]}")
                return "UNKNOWN"
        
        elif response.status_code == 404:
            print(f"  ❌ Table not found (404)")
            return "MISSING"
        
        elif response.status_code == 403:
            print(f"  ❌ SELECT denied (403) - RLS might be blocking all access")
            return "ENABLED"
        
        elif response.status_code == 401:
            print(f"  ⚠️  Unauthorized (401) - API key might be invalid")
            return "UNKNOWN"
        
        else:
            print(f"  ⚠️  Status {response.status_code}")
            return "UNKNOWN"
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return "ERROR"

def main():
    print("\n" + "="*70)
    print("  🔐 RLS STATUS CHECK")
    print("  Verifica care tabele au Row Level Security enabled/disabled")
    print("="*70)
    
    results = {}
    
    for table in TABLES_TO_CHECK:
        status = check_table_rls(table)
        results[table] = status
    
    # Summary
    print("\n" + "="*70)
    print("  📊 SUMMARY")
    print("="*70)
    
    for table, status in results.items():
        if status == "DISABLED":
            icon = "✅"
        elif status == "ENABLED":
            icon = "🔒"
        else:
            icon = "⚠️"
        
        print(f"  {icon} {table:20} → {status}")
    
    # Recommendations
    print("\n" + "="*70)
    print("  🔧 RECOMMENDATIONS")
    print("="*70)
    
    enabled_tables = [t for t, s in results.items() if s == "ENABLED"]
    
    if enabled_tables:
        print(f"\n  ⚠️  RLS IS ENABLED on these tables:")
        for table in enabled_tables:
            print(f"     - {table}")
        
        print(f"\n  This might block INSERT/UPDATE/DELETE operations.")
        print(f"  To disable RLS for testing:")
        print(f"\n  Option 1: Run disable script")
        print(f"     python disable_rls_for_testing.py")
        
        print(f"\n  Option 2: SQL manually in Supabase")
        for table in enabled_tables:
            print(f"     ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
    
    else:
        print(f"\n  ✅ All tables have RLS DISABLED")
        print(f"     INSERT/UPDATE/DELETE should work")
    
    # Check sync status
    print("\n" + "="*70)
    print("  🔄 NEXT: Test Real-Time Sync")
    print("="*70)
    
    print(f"""
  1. Open another terminal
  2. Run: python monitor_realtime_sync.py
  3. In app, make a change (add/edit employee)
  4. Monitor should show change within 2 seconds
    """)
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
