#!/usr/bin/env python3
"""
Build standalone Punctaj.exe distribution - FINAL VERSION
- Based on punctaj.py
- All modules included
- Config files included
- Ready to distribute
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys
import glob

def cleanup():
    """Remove old builds"""
    print("[*] Cleaning old builds...")
    for dirname in ['dist', 'build', 'build_spec']:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
            print(f"  Removed: {dirname}")

def find_all_modules():
    """Find all Python modules that should be included"""
    modules = set()
    skip = ('BUILD_', 'OPTIMIZE_', 'VERIFY_', 'TEST_', 'DEMO_', 
            'CREATE_', 'REBUILD_', '_', 'SETUP_', 'SET_', 'INSERT_',
            'DIAGNOSE_', 'DIAGNOSTIC_', 'REPAIR_', 'DEBUG_', 'CONFIG_FIX')
    
    for py_file in glob.glob('*.py'):
        basename = os.path.basename(py_file)
        if not any(basename.startswith(s) for s in skip):
            module = basename.replace('.py', '')
            if module != 'punctaj':  # Don't add main as hidden import
                modules.add(module)
    
    return sorted(modules)

def build_app():
    """Build standalone EXE using PyInstaller"""
    print("\n[*] Building standalone application...")
    
    modules = find_all_modules()
    print(f"[*] Found {len(modules)} local modules")
    
    # Base PyInstaller command
    cmd = [
        'pyinstaller',
        '--onedir',              # Creates _internal folder with libraries
        '--console',             # Show console output for debugging
        '--distpath=dist',
        '--specpath=build_spec',
        '--name=Punctaj',
        '--noconfirm',
        '--noupx',
    ]
    
    # Collect data files
    cmd.extend([
        '--collect-all=tkinter',
        '--collect-all=requests',
        '--collect-all=websockets',
    ])
    
    # Add config files to distribution
    for cfg_file in ['discord_config.ini', 'supabase_config.ini']:
        if os.path.exists(cfg_file):
            # Use absolute path so PyInstaller finds it
            abs_cfg = os.path.abspath(cfg_file)
            cmd.append(f'--add-data={abs_cfg}:.')
            print(f"  Including config: {cfg_file}")
    
    # Add all local modules as hidden imports
    for mod in modules:
        cmd.append(f'--hidden-import={mod}')
    
    # Main script
    cmd.append('punctaj.py')
    
    print(f"\n[*] Running PyInstaller with {len(modules)} hidden imports...")
    print(f"[*] Command: pyinstaller ... {' '.join(cmd[-3:])}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print("\n[ERROR] PyInstaller failed:")
        print(result.stderr[-1000:])
        return False
    
    # Verify build
    exe_path = 'dist/Punctaj/Punctaj.exe'
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024*1024)
        print(f"\n[OK] EXE built: {size_mb:.2f} MB")
        
        # Check _internal
        internal_path = 'dist/Punctaj/_internal'
        if os.path.exists(internal_path):
            file_count = len(os.listdir(internal_path))
            print(f"[OK] Libraries in _internal: {file_count} files")
        
        return True
    
    print("[ERROR] EXE not found after build")
    return False

def verify_distribution():
    """Verify all necessary files are in distribution"""
    print("\n[*] Verifying distribution...")
    
    dist_dir = 'dist/Punctaj'
    required_files = {
        'Punctaj.exe': 'Main executable',
        '_internal': 'Python runtime libraries',
        'supabase_config.ini': 'Supabase configuration',
        'discord_config.ini': 'Discord configuration',
    }
    
    # Check config in dist root
    root_configs = ['supabase_config.ini', 'discord_config.ini']
    for cfg in root_configs:
        src = cfg
        dst = os.path.join(dist_dir, cfg)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  Copied: {cfg} to distribution")
    
    # Check internal _internal
    internal_configs = ['supabase_config.ini', 'discord_config.ini']
    internal_dir = os.path.join(dist_dir, '_internal')
    for cfg in internal_configs:
        src = cfg
        dst = os.path.join(internal_dir, cfg)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  Copied: {cfg} to _internal")
    
    # Verify all required files
    all_ok = True
    for filename, desc in required_files.items():
        path = os.path.join(dist_dir, filename)
        if os.path.exists(path):
            if os.path.isdir(path):
                count = len(os.listdir(path))
                print(f"  [OK] {desc}: {filename}/ ({count} items)")
            else:
                size = os.path.getsize(path) / 1024
                print(f"  [OK] {desc}: {filename} ({size:.1f} KB)")
        else:
            print(f"  [ERROR] {desc}: {filename} - NOT FOUND")
            all_ok = False
    
    return all_ok

def create_zip():
    """Create distribution package"""
    print("\n[*] Creating distribution package...")
    
    zip_name = 'Punctaj_App_Distribution.zip'
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        dist_dir = 'dist/Punctaj'
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                fpath = os.path.join(root, f)
                arcname = os.path.relpath(fpath, 'dist')
                zf.write(fpath, arcname)
    
    size = os.path.getsize(zip_name) / (1024*1024)
    print(f"[OK] Package created: {zip_name} ({size:.2f} MB)")
    
    return zip_name

def main():
    print("=" * 70)
    print("BUILDING STANDALONE PUNCTAJ APPLICATION")
    print("=" * 70)
    
    try:
        cleanup()
        
        if not build_app():
            return False
        
        if not verify_distribution():
            print("\n[WARNING] Some files may be missing")
        
        zip_file = create_zip()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] STAND-ALONE APPLICATION READY!")
        print("=" * 70)
        print(f"\nDistribution folder: dist/Punctaj/")
        print(f"Package file: {zip_file}")
        print(f"\nTo run the application:")
        print(f"  1. Extract the ZIP file")
        print(f"  2. Run: .\\Punctaj.exe")
        print(f"\nThe application will connect automatically to:")
        print(f"  - Discord (for authentication)")
        print(f"  - Supabase (for database sync)")
        
        return True
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
