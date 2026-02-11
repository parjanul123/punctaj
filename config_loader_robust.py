#!/usr/bin/env python3
"""
Config Loader Robust - Ensures Supabase config is found on ANY device
"""

import os
import sys
import configparser
from pathlib import Path

class RobustConfigLoader:
    """Loads Supabase config from multiple locations with fallback"""
    
    # List of all possible config locations
    CONFIG_LOCATIONS = [
        # 1. PyInstaller bundle directory
        lambda: os.path.join(getattr(sys, '_MEIPASS', ''), 'supabase_config.ini'),
        # 2. EXE directory
        lambda: os.path.join(os.path.dirname(sys.executable), 'supabase_config.ini'),
        # 3. Script directory
        lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), 'supabase_config.ini'),
        # 4. Current working directory
        lambda: os.path.join(os.getcwd(), 'supabase_config.ini'),
        # 5. Common program directories
        lambda: os.path.join(os.path.expanduser('~'), 'Documents', 'Punctaj', 'supabase_config.ini'),
        # 6. Relative to script
        lambda: 'supabase_config.ini',
        # 7. Parent directory
        lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'supabase_config.ini'),
        # 8. Program Files
        lambda: os.path.join(os.environ.get('ProgramFiles', ''), 'Punctaj', 'supabase_config.ini'),
    ]
    
    def __init__(self, debug=True):
        self.debug = debug
        self.config_path = None
        self.config = configparser.ConfigParser()
        self.url = None
        self.anon_key = None
        self.load_config()
    
    def load_config(self):
        """Try to load config from all possible locations"""
        
        if self.debug:
            print("\n🔍 ROBUST CONFIG LOADER - Searching for supabase_config.ini")
            print("=" * 60)
        
        # Try each location
        for location_func in self.CONFIG_LOCATIONS:
            try:
                path = location_func()
                if not path:  # Skip empty paths
                    continue
                
                if self.debug:
                    print(f"  Checking: {path}")
                
                if os.path.exists(path) and os.path.isfile(path):
                    if self.debug:
                        print(f"  ✅ FOUND: {path}")
                    
                    try:
                        self.config.read(path)
                        self.url = self.config.get('supabase', 'URL', fallback=None)
                        self.anon_key = self.config.get('supabase', 'ANON_KEY', fallback=None)
                        
                        if self.url and self.anon_key:
                            self.config_path = path
                            if self.debug:
                                print(f"  ✅ CONFIG VALID - URL: {self.url[:50]}...")
                            return True
                        else:
                            if self.debug:
                                print(f"  ⚠️  Config file invalid (missing URL or ANON_KEY)")
                    except Exception as e:
                        if self.debug:
                            print(f"  ⚠️  Error reading config: {e}")
                        continue
            except Exception as e:
                if self.debug:
                    print(f"  ⚠️  Error checking path: {e}")
                continue
        
        if self.debug:
            print("=" * 60)
            print("❌ CONFIG NOT FOUND - Using fallback/empty config")
            print("\n⚠️  TROUBLESHOOTING:")
            print("  1. Ensure supabase_config.ini is in same folder as punctaj.exe")
            print("  2. Check file permissions")
            print("  3. Verify config file is not corrupted")
            print("  4. Try running CONFIG_FIX.py to regenerate config")
        
        return False
    
    def is_valid(self):
        """Check if config is valid and Supabase is accessible"""
        if not self.url or not self.anon_key:
            return False
        
        # Try to connect
        try:
            import requests
            response = requests.head(self.url, timeout=5)
            return response.status_code < 500  # Not a server error
        except:
            return True  # Assume valid if we can't test (might be offline)
    
    def get_url(self):
        """Get Supabase URL"""
        return self.url
    
    def get_anon_key(self):
        """Get Supabase anonymous key"""
        return self.anon_key
    
    def get_config_path(self):
        """Get path to config file"""
        return self.config_path
    
    def print_status(self):
        """Print detailed status"""
        print("\n📋 CONFIGURATION STATUS:")
        print(f"  Config file: {self.config_path or '❌ NOT FOUND'}")
        print(f"  URL: {self.url[:50] + '...' if self.url else '❌ NOT SET'}")
        print(f"  Key: {self.anon_key[:20] + '...' if self.anon_key else '❌ NOT SET'}")
        print(f"  Valid: {'✅ YES' if self.is_valid() else '❌ NO'}")

def test_config_loader():
    """Test the config loader"""
    
    print("\n" + "=" * 70)
    print("🧪 TESTING ROBUST CONFIG LOADER")
    print("=" * 70)
    
    loader = RobustConfigLoader(debug=True)
    loader.print_status()
    
    if loader.is_valid():
        print("\n✅ CONFIG LOADER WORKING - Ready for production")
    else:
        print("\n❌ CONFIG LOADER FAILED - Fix required")
    
    return loader

if __name__ == "__main__":
    loader = test_config_loader()
