#!/usr/bin/env python3
"""
Diagnostic Tool - Check why Supabase is not loading on other devices
"""

import os
import sys
import configparser
from pathlib import Path

def diagnose_supabase_issue():
    """Diagnose Supabase config and database issues"""
    
    print("\n" + "="*70)
    print("🔍 SUPABASE DATABASE DIAGNOSTIC")
    print("="*70)
    print(f"Device: {os.environ.get('COMPUTERNAME', 'Unknown')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working dir: {os.getcwd()}")
    
    # Step 1: Check if supabase_config.ini exists
    print("\n📁 STEP 1: Looking for supabase_config.ini")
    print("-" * 70)
    
    config_locations = [
        Path.cwd() / "supabase_config.ini",
        Path(__file__).parent / "supabase_config.ini",
        Path.home() / "Documents" / "supabase_config.ini",
        Path("D:\\punctaj\\supabase_config.ini") if os.name == 'nt' else Path("/opt/punctaj/supabase_config.ini"),
        Path(os.path.dirname(sys.executable)) / "supabase_config.ini",
    ]
    
    found_files = []
    for loc in config_locations:
        exists = "✅" if loc.exists() else "❌"
        print(f"  {exists} {loc}")
        if loc.exists():
            found_files.append(loc)
    
    if not found_files:
        print("\n⚠️  PROBLEM: supabase_config.ini not found in any location!")
        print("\n💡 SOLUTION:")
        print("  1. Copy supabase_config.ini from source to application folder")
        print("  2. Run FIX_SUPABASE_CONFIG.py to fix it")
        return False
    
    # Step 2: Read and validate config
    print("\n📋 STEP 2: Reading configuration")
    print("-" * 70)
    
    config = configparser.ConfigParser()
    config_path = found_files[0]
    
    try:
        config.read(config_path)
        print(f"✅ Reading from: {config_path}")
        
        if 'supabase' not in config.sections():
            print("❌ [supabase] section not found in config!")
            return False
        
        url = config.get('supabase', 'URL', fallback=None)
        anon_key = config.get('supabase', 'ANON_KEY', fallback=None)
        
        print(f"  URL: {url[:50] + '...' if url else '❌ NOT SET'}")
        print(f"  ANON_KEY: {anon_key[:20] + '...' if anon_key else '❌ NOT SET'}")
        
        if not (url and anon_key):
            print("\n❌ PROBLEM: URL or ANON_KEY not configured!")
            return False
        
        print("\n✅ Config is valid")
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False
    
    # Step 3: Test Supabase connection
    print("\n🔌 STEP 3: Testing Supabase connection")
    print("-" * 70)
    
    try:
        import requests
        
        headers = {
            "apikey": anon_key,
            "Content-Type": "application/json"
        }
        
        # Try to fetch from Supabase
        response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        
        if response.status_code in [200, 204, 400]:  # 400 is okay, means API is reachable
            print(f"✅ Supabase API is reachable (status: {response.status_code})")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        
    except requests.exceptions.ConnectionError:
        print("❌ PROBLEM: Cannot connect to Supabase URL (network error)")
        print(f"   Check if {url} is reachable")
        return False
    except Exception as e:
        print(f"⚠️  Connection test error: {e}")
    
    # Step 4: Test SupabaseSync module
    print("\n🔄 STEP 4: Testing SupabaseSync module")
    print("-" * 70)
    
    try:
        from supabase_sync import SupabaseSync
        
        # Create instance
        sync = SupabaseSync(str(config_path))
        
        print(f"✅ SupabaseSync initialized successfully")
        print(f"   Connected to: {sync.supabase_url[:50]}...")
        
    except Exception as e:
        print(f"❌ PROBLEM: SupabaseSync error: {e}")
        print("\n💡 SOLUTION:")
        print("  1. Check if requirements are installed: pip install supabase requests")
        print("  2. Verify config file is in correct format")
        return False
    
    # Step 5: Summary
    print("\n" + "="*70)
    print("✅ DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\n✅ Everything looks good! Supabase should be working.")
    
    return True

def create_fix_script():
    """Create a fix script if needed"""
    
    fix_script = '''#!/usr/bin/env python3
"""Fix Supabase config on this device"""

import shutil
from pathlib import Path

print("🔧 FIXING SUPABASE CONFIG...")

# Copy from source if available
source_locations = [
    Path("D:\\\\punctaj\\\\supabase_config.ini"),  # Main source
    Path("..\\\\supabase_config.ini"),  # Parent
    Path("supabase_config.ini"),  # Current
]

for source in source_locations:
    if source.exists():
        dest = Path.cwd() / "supabase_config.ini"
        shutil.copy2(source, dest)
        print(f"✅ Copied from {source} to {dest}")
        print("✨ Fix complete! Try running the app again.")
        break
else:
    print("❌ Could not find source supabase_config.ini")
    print("💡 Please manually copy supabase_config.ini to this folder")
'''
    
    return fix_script

if __name__ == "__main__":
    success = diagnose_supabase_issue()
    
    if not success:
        print("\n📝 Creating FIX_SUPABASE_CONFIG.py...")
        fix_code = create_fix_script()
        with open("FIX_SUPABASE_CONFIG.py", "w") as f:
            f.write(fix_code)
        print("✅ Run: python FIX_SUPABASE_CONFIG.py")
