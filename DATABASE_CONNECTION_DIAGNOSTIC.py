#!/usr/bin/env python3
"""
Database Connection Diagnostic Tool
Verifica si diagnostica probleme de conectare la Supabase
"""

import os
import sys
import configparser
import json
from pathlib import Path
from datetime import datetime

def check_config_file():
    """Verifica daca exista fisierul de configurare Supabase"""
    print("\n" + "="*70)
    print("🔍 DIAGNOSTIC: DATABASE CONNECTION")
    print("="*70)
    
    # Locatii posibile pentru supabase_config.ini
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "supabase_config.ini"),
        os.path.expandvars(r"%ProgramFiles%\Punctaj\supabase_config.ini"),
        os.path.expandvars(r"%APPDATA%\Punctaj\supabase_config.ini"),
        os.path.expandvars(r"%LOCALAPPDATA%\Punctaj\supabase_config.ini"),
        r"C:\Punctaj\supabase_config.ini",
        r"d:\punctaj\supabase_config.ini",
        os.path.expandvars(r"%USERPROFILE%\Punctaj\supabase_config.ini"),
        "supabase_config.ini"
    ]
    
    print("\n📁 FOLDER STRUCTURE:")
    print("-" * 70)
    
    # Verifica directorul curent
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")
    
    if os.path.exists("supabase_config.ini"):
        print("  ✓ supabase_config.ini found in current directory")
    else:
        print("  ✗ supabase_config.ini NOT found in current directory")
    
    # Lista fisiere .ini in directorul curent
    ini_files = [f for f in os.listdir(cwd) if f.endswith('.ini')]
    if ini_files:
        print(f"  Found .ini files: {', '.join(ini_files)}")
    
    print("\n🔎 SEARCHING FOR supabase_config.ini:")
    print("-" * 70)
    
    found_path = None
    for path in possible_paths:
        exists = os.path.exists(path)
        status = "✓ FOUND" if exists else "✗ NOT found"
        print(f"{status}: {path}")
        if exists and not found_path:
            found_path = path
    
    return found_path

def validate_config(config_path):
    """Valideaza continutul fisierului de configurare"""
    print("\n📋 CONFIG FILE VALIDATION:")
    print("-" * 70)
    
    config = configparser.ConfigParser()
    
    try:
        config.read(config_path)
        print(f"✓ Config file successfully loaded")
        print(f"  File: {config_path}")
        
        # Check supabase section
        if 'supabase' not in config:
            print("✗ ERROR: [supabase] section not found in config")
            return False
        
        # Validate required fields
        required_fields = ['url', 'key']
        for field in required_fields:
            if field not in config['supabase']:
                print(f"✗ ERROR: Missing required field: {field}")
                return False
            
            value = config.get('supabase', field)
            if not value or value.strip() == '':
                print(f"✗ ERROR: {field} is empty")
                return False
            
            # Mask sensitive data
            masked_value = value[:10] + "***" + value[-5:] if len(value) > 20 else "***"
            print(f"✓ {field}: {masked_value}")
        
        # Optional fields
        optional_fields = ['table_sync', 'table_logs', 'table_users']
        for field in optional_fields:
            if field in config['supabase']:
                value = config.get('supabase', field)
                print(f"✓ {field}: {value}")
        
        print("\n✓ Config validation PASSED")
        return True
        
    except configparser.Error as e:
        print(f"✗ ERROR: Invalid config file format: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_connection(config_path):
    """Testeaza conexiunea la Supabase"""
    print("\n🌐 CONNECTION TEST:")
    print("-" * 70)
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    url = config.get('supabase', 'url')
    key = config.get('supabase', 'key')
    
    try:
        import requests
        
        # Test simple request
        headers = {
            'apikey': key,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {key}'
        }
        
        # Try to fetch users table (simple health check)
        test_url = f"{url}/rest/v1/users?limit=1&select=id"
        
        print(f"Testing: {url}")
        response = requests.get(test_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print("✓ Connection successful (HTTP 200)")
            print(f"  Response time: {response.elapsed.total_seconds():.2f}s")
            return True
        elif response.status_code == 401:
            print("✗ ERROR: Unauthorized - API key is invalid")
            return False
        elif response.status_code == 403:
            print("✗ ERROR: Forbidden - Check API key permissions")
            return False
        else:
            print(f"✗ ERROR: HTTP {response.status_code}")
            print(f"  Response: {response.text[:100]}")
            return False
            
    except ImportError:
        print("⚠️  requests module not installed - cannot test connection")
        print("  Install with: pip install requests")
        return False
    except requests.exceptions.Timeout:
        print("✗ ERROR: Connection timeout - check internet connection")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to server - check URL and internet")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def generate_report(config_found, config_valid, connection_ok):
    """Genereaza raport diagnostic"""
    print("\n" + "="*70)
    print("📊 DIAGNOSTIC REPORT")
    print("="*70)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'config_file_found': config_found,
        'config_valid': config_valid,
        'database_connection': connection_ok,
        'status': 'OK' if all([config_found, config_valid, connection_ok]) else 'ISSUES FOUND'
    }
    
    print(f"\n✓ Config file found: {'YES' if config_found else 'NO'}")
    print(f"✓ Config valid: {'YES' if config_valid else 'NO'}")
    print(f"✓ Database connection: {'OK' if connection_ok else 'FAILED'}")
    
    print(f"\nOVERALL STATUS: {report['status']}")
    
    if report['status'] != 'OK':
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("-" * 70)
        
        if not config_found:
            print("1. supabase_config.ini not found")
            print("   → Copy supabase_config.ini to the application folder")
            print("   → Or create it with your Supabase credentials:")
            print("""
[supabase]
url = https://your-project.supabase.co
key = your-api-key
table_sync = police_data
table_logs = audit_logs
table_users = users

[sync]
enabled = true
auto_sync = true
sync_interval = 30
conflict_resolution = latest_timestamp
sync_on_startup = true
""")
        
        if config_found and not config_valid:
            print("2. Config file format is invalid")
            print("   → Verify the INI file syntax")
            print("   → Ensure [supabase] section exists")
            print("   → Verify URL and key are not empty")
        
        if config_found and config_valid and not connection_ok:
            print("3. Cannot connect to Supabase")
            print("   → Check internet connection")
            print("   → Verify Supabase URL is correct")
            print("   → Verify API key is valid")
            print("   → Check firewall/proxy settings")
    
    # Save report to file
    report_path = os.path.join(os.getcwd(), "connection_diagnostic_report.json")
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Report saved to: {report_path}")
    except:
        pass
    
    print("\n" + "="*70 + "\n")
    
    return report['status'] == 'OK'

def main():
    """Main diagnostic function"""
    print("\n🚀 Punctaj - Database Connection Diagnostic Tool")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"OS: {sys.platform}")
    
    # Step 1: Find config file
    config_path = check_config_file()
    config_found = config_path is not None
    
    # Step 2: Validate config
    config_valid = False
    connection_ok = False
    
    if config_found:
        config_valid = validate_config(config_path)
        
        # Step 3: Test connection
        if config_valid:
            connection_ok = test_connection(config_path)
    
    # Step 4: Generate report
    success = generate_report(config_found, config_valid, connection_ok)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
