#!/usr/bin/env python3
"""
Build distribution with enhanced debugging
Includes console output and detailed module verification
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys
import glob

def cleanup_builds():
    """Clean old builds"""
    print("[*] Cleaning...")
    for d in ['d:\\punctaj\\dist_debug', 'd:\\punctaj\\build_debug', 'd:\\punctaj\\build_spec']:
        if os.path.exists(d):
            shutil.rmtree(d)

def find_all_local_modules():
    """Find ALL Python modules in root directory"""
    modules = []
    for py_file in glob.glob('d:\\punctaj\\*.py'):
        basename = os.path.basename(py_file)
        # Skip build scripts
        skip_prefixes = ('BUILD_', 'OPTIMIZE_', '_', 'VERIFY_', 'TEST_', 'DEMO_', 
                        'CREATE_', 'REBUILD_', 'SETUP_INSTALLER', 'SET_', 'INSERT_',
                        'DIAGNOSE_', 'DIAGNOSTIC_', 'REPAIR_')
        if not any(basename.startswith(p) for p in skip_prefixes):
            modules.append(basename)
    return sorted(modules)

def build_exe_debug():
    """Build EXE with console for debugging"""
    print("\n[*] Building with debug support...")
    print("[*] This build includes console output for troubleshooting")
    
    os.makedirs('d:\\punctaj\\build_spec', exist_ok=True)
    
    # Find ALL local modules
    all_modules = find_all_local_modules()
    print(f"[*] Found {len(all_modules)} local modules to include")
    
    # Base command
    cmd = [
        'pyinstaller',
        '--onedir',
        # --console instead of --windowed for debug output
        '--console',
        '--distpath=d:\\punctaj\\dist_debug',
        '--specpath=d:\\punctaj\\build_spec',
        '--name=Punctaj',
        '--noconfirm',
        '--collect-all=tkinter',
        '--collect-all=requests',
    ]
    
    # Add EVERY local module as hidden-import
    for mod in all_modules:
        mod_name = mod.replace('.py', '')
        cmd.append(f'--hidden-import={mod_name}')
    
    # Add config files
    for cfg in ['discord_config.ini', 'supabase_config.ini']:
        cfg_path = f'd:\\punctaj\\{cfg}'
        if os.path.exists(cfg_path):
            cmd.append(f'--add-data={cfg_path}:.')
    
    cmd.append('d:\\punctaj\\punctaj.py')
    
    print(f"[*] PyInstaller command: pyinstaller [OPTIONS] with {len(all_modules)} hidden-imports")
    
    result = subprocess.run(cmd, cwd='d:\\punctaj', capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"[ERROR] Build failed:")
        print(result.stderr[-800:])
        return False
    
    exe_path = 'd:\\punctaj\\dist_debug\\Punctaj\\Punctaj.exe'
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024*1024)
        print(f"[OK] EXE built: {exe_size:.2f} MB")
        
        internal_path = 'd:\\punctaj\\dist_debug\\Punctaj\\_internal'
        if os.path.exists(internal_path):
            lib_count = len(os.listdir(internal_path))
            print(f"[OK] _internal libraries: {lib_count}")
        
        return True
    return False

def create_distribution():
    """Create distribution from debug build"""
    print("\n[*] Preparing distribution...")
    
    src_app_dir = 'd:\\punctaj\\dist_debug\\Punctaj'
    dist_dir = 'd:\\punctaj\\PUNCTAJ_DIST_FINAL'
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    shutil.copytree(src_app_dir, dist_dir)
    exe_size = os.path.getsize(os.path.join(dist_dir, 'Punctaj.exe')) / (1024*1024)
    print(f"[OK] Distribution prepared: {exe_size:.2f} MB EXE")
    
    # Ensure configs are present
    for cfg in ['discord_config.ini', 'supabase_config.ini']:
        src = os.path.join('d:\\punctaj', cfg)
        if os.path.exists(src):
            dst = os.path.join(dist_dir, cfg)
            shutil.copy2(src, dst)
    
    return dist_dir

def create_zip(dist_dir):
    """Create ZIP distribution"""
    print("\n[*] Creating ZIP...")
    
    output = 'd:\\punctaj\\Punctaj_App_Distribution.zip'
    if os.path.exists(output):
        os.remove(output)
    
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                fpath = os.path.join(root, f)
                arcname = os.path.relpath(fpath, dist_dir)
                zf.write(fpath, arcname)
    
    size = os.path.getsize(output) / (1024*1024)
    print(f"[OK] Archive: {size:.2f} MB")
    return output

def main():
    print("="*60)
    print("BUILD WITH ENHANCED DEBUGGING")
    print("="*60)
    
    try:
        cleanup_builds()
        
        if not build_exe_debug():
            return False
        
        dist_dir = create_distribution()
        create_zip(dist_dir)
        
        print("\n" + "="*60)
        print("[SUCCESS] DISTRIBUTION READY")
        print("="*60)
        print(f"\nTo test:")
        print(f"  cd PUNCTAJ_DIST_FINAL")
        print(f"  .\\Punctaj.exe")
        print(f"\nYou'll see console output for debugging!")
        
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
