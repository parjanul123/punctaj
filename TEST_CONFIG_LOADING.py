#!/usr/bin/env python3
"""Test config loading directly"""
import os
import sys
import configparser

# Test reading config like the loader does
config_path = 'd:\\punctaj\\PUNCTAJ_DIST_FINAL\\supabase_config.ini'

print(f"Testing config loading from: {config_path}")
print(f"File exists: {os.path.exists(config_path)}\n")

if os.path.exists(config_path):
    config = configparser.ConfigParser()
    result = config.read(config_path)
    
    print(f"Config.read() result: {result}")
    print(f"Sections: {config.sections()}")
    
    if 'supabase' in config:
        print("\n[supabase] section found!")
        print(f"Keys in section: {list(config['supabase'].keys())}")
        
        # Try to read values
        print(f"\nTrying to read 'url':")
        url = config.get('supabase', 'url', fallback='NOT_FOUND')
        print(f"  Result: {url}")
        
        print(f"\nTrying to read 'URL' (uppercase):")
        url_upper = config.get('supabase', 'URL', fallback='NOT_FOUND')
        print(f"  Result: {url_upper}")
        
        print(f"\nTrying to read 'key':")
        key = config.get('supabase', 'key', fallback='NOT_FOUND')
        print(f"  Result: {key[:30]}..." if key != 'NOT_FOUND' else f"  Result: {key}")
        
        print(f"\nTrying to read 'ANON_KEY' (uppercase):")
        key_upper = config.get('supabase', 'ANON_KEY', fallback='NOT_FOUND')
        print(f"  Result: {key_upper}")
        
        # Show raw file content
        print(f"\n=== RAW FILE CONTENT ===")
        with open(config_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:15], 1):
                print(f"{i:2d}: {repr(line)}")
    else:
        print("ERROR: [supabase] section NOT found!")
else:
    print("ERROR: Config file not found!")
