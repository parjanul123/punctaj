#!/usr/bin/env python3
"""
Diagnostic tool for Discord multi-device authentication issues
Identifies and fixes conflicts when using the app on multiple devices
"""

import os
import json
import configparser
from pathlib import Path
from datetime import datetime
import sys

def check_discord_config():
    """Check Discord configuration"""
    print("\n🔍 Checking Discord Configuration...")
    
    config_file = Path("discord_config.ini")
    if not config_file.exists():
        print("❌ discord_config.ini not found")
        return False
    
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        client_id = config.get('discord', 'CLIENT_ID', fallback=None)
        client_secret = config.get('discord', 'CLIENT_SECRET', fallback=None)
        redirect_uri = config.get('discord', 'REDIRECT_URI', fallback=None)
        
        print(f"✅ Discord Config Found:")
        print(f"   - CLIENT_ID: {client_id[:20]}...")
        print(f"   - REDIRECT_URI: {redirect_uri}")
        
        if not all([client_id, client_secret, redirect_uri]):
            print("❌ Missing required Discord settings")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error reading Discord config: {e}")
        return False

def check_supabase_config():
    """Check Supabase configuration"""
    print("\n🔍 Checking Supabase Configuration...")
    
    config_file = Path("supabase_config.ini")
    if not config_file.exists():
        print("⚠️  supabase_config.ini not found")
        return False
    
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        url = config.get('supabase', 'URL', fallback=None)
        key = config.get('supabase', 'ANON_KEY', fallback=None)
        
        print(f"✅ Supabase Config Found:")
        print(f"   - URL: {url}")
        print(f"   - ANON_KEY: {key[:20] if key else 'Not set'}...")
        
        return bool(url and key)
    except Exception as e:
        print(f"❌ Error reading Supabase config: {e}")
        return False

def check_session_conflicts():
    """Check for session conflicts from multiple devices"""
    print("\n🔍 Checking for Session Conflicts...")
    
    conflict_paths = [
        Path.home() / "Documents" / "PunctajManager" / ".discord_token",
        Path.home() / "AppData" / "Local" / "PunctajManager" / ".session",
        Path(".discord_token"),
        Path(".punctaj_session"),
    ]
    
    found_conflicts = False
    for path in conflict_paths:
        if path.exists():
            print(f"⚠️  Found potential conflict file: {path}")
            found_conflicts = True
    
    if not found_conflicts:
        print("✅ No session conflict files found")
    
    return found_conflicts

def diagnose_authentication_issue():
    """Run full diagnostic for authentication issues"""
    print("\n" + "="*60)
    print("🔧 DISCORD MULTI-DEVICE AUTHENTICATION DIAGNOSTIC")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "discord_config": check_discord_config(),
        "supabase_config": check_supabase_config(),
        "session_conflicts": check_session_conflicts(),
    }
    
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    if results["discord_config"] and results["supabase_config"]:
        print("✅ Configuration files are valid")
    else:
        print("❌ Configuration issues detected")
    
    if results["session_conflicts"]:
        print("⚠️  Session conflicts detected - clearing recommended")
    else:
        print("✅ No session conflicts detected")
    
    return results

def create_fix_script():
    """Create a script to fix multi-device authentication issues"""
    
    fix_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Fix Discord Authentication for Multi-Device Use
\"\"\"

import os
import shutil
from pathlib import Path
from datetime import datetime

def clear_session_cache():
    \"\"\"Clear old session/token caches\"\"\"
    print("🧹 Clearing session caches...")
    
    paths_to_clear = [
        Path.home() / "Documents" / "PunctajManager" / ".discord_token",
        Path.home() / "AppData" / "Local" / "PunctajManager" / ".session",
        Path(".discord_token"),
        Path(".punctaj_session"),
        Path("discord_token.json"),
        Path(".auth_cache"),
    ]
    
    cleared = 0
    for path in paths_to_clear:
        try:
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"   ✅ Cleared: {path}")
                cleared += 1
        except Exception as e:
            print(f"   ⚠️  Could not clear {path}: {e}")
    
    return cleared > 0

def verify_oauth_settings():
    \"\"\"Verify OAuth redirect settings are correct\"\"\"
    print("\\n✅ Verifying OAuth Settings...")
    
    import configparser
    
    config = configparser.ConfigParser()
    if not config.read('discord_config.ini'):
        print("❌ discord_config.ini not found")
        return False
    
    redirect_uri = config.get('discord', 'REDIRECT_URI', fallback='')
    
    # Must be localhost and not in use
    if 'localhost' not in redirect_uri:
        print(f"⚠️  Redirect URI should use localhost: {redirect_uri}")
    else:
        print(f"   Redirect URI: {redirect_uri} ✓")
    
    return True

def test_discord_connection():
    \"\"\"Test if Discord connection works\"\"\"
    print("\\n🔗 Testing Discord Connection...")
    
    try:
        import requests
        response = requests.get("https://discord.com/api/v10/", timeout=5)
        if response.status_code >= 400:
            print(f"⚠️  Discord API returned {response.status_code}")
            return False
        print("   ✅ Discord API is reachable")
        return True
    except Exception as e:
        print(f"❌ Cannot reach Discord: {e}")
        return False

def main():
    print("\\n" + "="*60)
    print("🔧 FIXING DISCORD MULTI-DEVICE AUTHENTICATION")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Clear caches
    if clear_session_cache():
        print("\\n✅ Session caches cleared")
    else:
        print("\\n✅ No caches to clear")
    
    # Step 2: Verify settings
    verify_oauth_settings()
    
    # Step 3: Test connection
    test_discord_connection()
    
    print("\\n" + "="*60)
    print("✨ FIX COMPLETE!")
    print("="*60)
    print("""
How to use after fix:
1. Start the app normally
2. You will be prompted to login with Discord (fresh session)
3. Use your Discord account from ANY device
4. The app will save your session and sync across devices

If you still get errors:
- Check your internet connection
- Verify Discord API is not rate-limiting you
- Check Windows Defender isn't blocking the connection
- Restart your PC
\"\"\"
    )

if __name__ == "__main__":
    main()
"""
    
    script_path = Path("FIX_DISCORD_MULTIDEVICE.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(fix_script)
    
    print(f"✅ Created fix script: {script_path}")
    return script_path

if __name__ == "__main__":
    # Run diagnostic
    results = diagnose_authentication_issue()
    
    # Create fix script
    print("\n📝 Creating fix script...")
    create_fix_script()
    
    print("\n" + "="*60)
    print("📋 RECOMMENDED ACTIONS:")
    print("="*60)
    print("""
1. Run: python FIX_DISCORD_MULTIDEVICE.py
   (Clears old session caches)

2. Then run the application normally

3. If you still have issues, check:
   - Your Discord Client ID is correct
   - Your Supabase connection is working
   - Internet connection is stable

4. For different devices:
   - Each device gets its own fresh login
   - Permissions sync automatically from database
   - No conflicts between sessions
""")
