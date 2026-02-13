#!/usr/bin/env python3
"""
🔍 CHECK ALL TABLES - Verifica ce date sunt in fiecare tabel din Supabase
"""

import requests
import json
import configparser
from pathlib import Path

# Load config
config = configparser.ConfigParser()
config_path = Path(__file__).parent / "supabase_config.ini"
config.read(config_path)

SUPABASE_URL = config.get('supabase', 'url', fallback='')
SUPABASE_KEY = config.get('supabase', 'key', fallback='')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: supabase_config.ini not configured properly")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Map of tables to check
TABLES = {
    "police_data": "🏙️  Cities/Institutions (Orase si Institutii)",
    "users": "👥 Users & Permissions (Utilizatori si Drepturi)",
    "employees": "👨‍💼 Employees (Angajati)",
    "institutions": "🏢 Institutions (Institutii)",
    "weekly_reports": "📋 Weekly Reports (Rapoarte Saptamânale)"
}

def check_table(table_name, description):
    """Check if table exists and get row count"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"  Table: {table_name} (ID: ?)")
    print(f"{'='*70}")
    
    try:
        # Get count
        url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=count()"
        response = requests.head(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            count_header = response.headers.get('content-range', '0/0').split('/')[1]
            count = int(count_header) if count_header != '*' else '?'
            print(f"  ✅ Table EXISTS - Rows: {count}")
        elif response.status_code == 401:
            print(f"  ⚠️  Permission denied (RLS might be blocking)")
            return False
        elif response.status_code == 404:
            print(f"  ❌ Table MISSING")
            return False
        else:
            print(f"  ⚠️  Status {response.status_code}")
            return False
        
        # Get sample data
        url_data = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=3"
        response = requests.get(url_data, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"  📊 Sample records: {len(data)} shown")
                for i, record in enumerate(data[:2], 1):
                    print(f"\n     Record {i}:")
                    for key, value in list(record.items())[:5]:  # First 5 columns
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:47] + "..."
                        print(f"       {key}: {value}")
            else:
                print(f"  ⚠️  Table is EMPTY")
        else:
            print(f"  ⚠️  Cannot read data (status {response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  🔍 COMPLETE TABLE SYNC VERIFICATION")
    print("  Verifica ce date sunt sincronizate in fiecare tabel")
    print("="*70)
    
    results = {}
    
    for table, description in TABLES.items():
        success = check_table(table, description)
        results[table] = success
    
    # Summary
    print(f"\n\n" + "="*70)
    print("  📊 SUMMARY")
    print("="*70)
    
    for table, description in TABLES.items():
        status = "✅" if results[table] else "❌"
        print(f"  {status} {description}")
    
    # Findings
    print(f"\n\n" + "="*70)
    print("  📈 FINDINGS")
    print("="*70)
    
    has_issues = False
    
    # Check cities/institutions
    if results["police_data"]:
        print(f"\n  ✅ police_data table has records")
        print(f"     → Institutions and cities are being synced here as JSON")
    else:
        print(f"\n  ❌ police_data is empty or inaccessible")
        print(f"     → PROBLEM: Institution JSON data is not syncing!")
        has_issues = True
    
    # Check employees
    if results["employees"]:
        print(f"\n  ✅ employees table has records")
        print(f"     → Individual employee records are being synced")
    else:
        print(f"\n  ❌ employees table is empty or inaccessible")
        print(f"     → PROBLEM: Employee data is not syncing!")
        has_issues = True
    
    # Check institutions
    if results["institutions"]:
        print(f"\n  ✅ institutions table has records")
        print(f"     → Individual institution records are present")
    else:
        print(f"\n  ⚠️  institutions table is empty")
        print(f"     → INFO: Individual institution table not synced (optional)")
    
    # Check users
    if results["users"]:
        print(f"\n  ✅ users table has records")
        print(f"     → User permissions are stored")
    else:
        print(f"\n  ⚠️  users table is empty")
        print(f"     → INFO: User data not synced (optional)")
    
    # Check weekly reports
    if results["weekly_reports"]:
        print(f"\n  ✅ weekly_reports table has records")
        print(f"     → Weekly reports are being stored")
    else:
        print(f"\n  ⚠️  weekly_reports table is empty")
        print(f"     → INFO: No weekly reports synced yet")
    
    # Next steps
    print(f"\n\n" + "="*70)
    print("  📋 NEXT STEPS")
    print("="*70)
    
    if has_issues:
        print(f"\n  ⚠️  ISSUES FOUND:")
        if not results["police_data"]:
            print(f"     1. Fix police_data sync - institutions JSON")
            print(f"        Run: python disable_rls_for_testing.py")
            print(f"        Then: python punctaj.py & make a change")
        if not results["employees"]:
            print(f"     2. Fix employees sync")
            print(f"        Check SUPABASE_EMPLOYEE_MANAGER initialization")
            print(f"        Run: python debug_sync_connection.py")
    else:
        print(f"\n  ✅ All critical tables are syncing!")
        print(f"     Police data and employees are synchronizing correctly")
    
    print(f"\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
