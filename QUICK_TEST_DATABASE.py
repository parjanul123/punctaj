#!/usr/bin/env python3
"""
Quick Test Script - Verifica rapid daca Punctaj poate conecta la Supabase
Ruleaza acest script IMEDIAT dupa instalare pe alt dispozitiv
"""

import os
import sys
from pathlib import Path

def quick_test():
    print("\n" + "="*70)
    print("⚡ QUICK TEST - Punctaj Database Connection")
    print("="*70 + "\n")
    
    # 1. Verifica config file
    print("🔍 Step 1: Gasind supabase_config.ini...")
    try:
        from config_resolver import ConfigResolver
        config_path = ConfigResolver.find_config_file()
        
        if os.path.exists(config_path):
            print(f"✓ Found: {config_path}")
        else:
            print(f"✗ NOT found: {config_path}")
            print("\n📝 SOLUTION: Run SETUP_SUPABASE_WIZARD.py to configure")
            return False
    except ImportError:
        print("⚠️  Config resolver not available - using fallback")
        config_path = "supabase_config.ini"
        if not os.path.exists(config_path):
            print(f"✗ File not found: {config_path}")
            return False
    
    # 2. Incarca configuratia
    print("\n📋 Step 2: Loading configuration...")
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        
        url = config.get('supabase', 'url', fallback=None)
        key = config.get('supabase', 'key', fallback=None)
        
        if not url or not key:
            print("✗ Configuration incomplete (missing URL or key)")
            return False
        
        print(f"✓ URL: {url[:30]}...")
        print(f"✓ Key: {key[:15]}...")
        
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False
    
    # 3. Testeaza conexiunea
    print("\n🌐 Step 3: Testing database connection...")
    try:
        import requests
        
        headers = {
            'apikey': key,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {key}'
        }
        
        test_url = f"{url}/rest/v1/users?limit=1&select=id"
        response = requests.get(test_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"✓ Connection successful (HTTP 200)")
            return True
        elif response.status_code == 401:
            print(f"✗ Unauthorized (HTTP 401) - API key invalid")
            return False
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  requests module not installed")
        print("   Installing: pip install requests")
        os.system("pip install requests")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def main():
    success = quick_test()
    
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED - Punctaj is ready!")
        print("   You can now run Punctaj.exe")
    else:
        print("❌ TEST FAILED - Fix issues above")
        print("\n📝 NEXT STEPS:")
        print("   1. Run: python SETUP_SUPABASE_WIZARD.py")
        print("   2. Enter your Supabase URL and API key")
        print("   3. Run this test again")
    print("="*70 + "\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        input("Press Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
