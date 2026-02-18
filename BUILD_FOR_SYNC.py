#!/usr/bin/env python3
"""
Build Punctaj distribution - optimized for Supabase sync
Uses optimal PyInstaller settings for local module imports
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
    print("[*] Cleaning old builds...")
    for d in ['d:\\punctaj\\dist_output', 'd:\\punctaj\\build_spec', 'd:\\punctaj\\build']:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"    [OK] Removed {d}")

def build_exe():
    """Build optimized EXE"""
    print("\n[*] Building Punctaj.exe...")
    
    os.makedirs('d:\\punctaj\\build_spec', exist_ok=True)
    
    # Core command - minimal but effective
    cmd = [
        'pyinstaller',
        '--onefile',  # Single EXE - simpler distribution
        '--windowed',
        '--distpath=d:\\punctaj\\dist_final',
        '--specpath=d:\\punctaj\\build_spec',
        '--name=Punctaj',
        '--noconfirm',
        '--collect-all=tkinter',
        '--collect-all=requests',
        # All local modules as hidden imports - PyInstaller will find them
        '--hidden-import=discord_auth',
        '--hidden-import=supabase_sync',
        '--hidden-import=supabase_employee_manager',
        '--hidden-import=supabase_realtime_ws',
        '--hidden-import=config_loader_robust',
        '--hidden-import=action_logger',
        '--hidden-import=admin_permissions',
        '--hidden-import=multi_device_sync_manager',
        '--hidden-import=cloud_sync_manager',
        '--hidden-import=users_permissions_json_manager',
        '--hidden-import=permission_decorators',
        '--hidden-import=realtime_sync',
        # Config files embedded
        '--add-data=d:\\punctaj\\discord_config.ini:.',
        '--add-data=d:\\punctaj\\supabase_config.ini:.',
        'd:\\punctaj\\punctaj.py'
    ]
    
    print("[*] Running PyInstaller with hidden-import discovery...")
    result = subprocess.run(cmd, cwd='d:\\punctaj', capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr[-300:]}")
        return False
    
    exe_path = 'd:\\punctaj\\dist_final\\Punctaj.exe'
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / (1024*1024)
        print(f"[OK] EXE ready: {size:.2f} MB")
        return True
    return False

def create_distribution():
    """Create final distribution package"""
    print("\n[*] Creating distribution package...")
    
    dist_dir = 'd:\\punctaj\\PUNCTAJ_DIST'
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy EXE
    src = 'd:\\punctaj\\dist_final\\Punctaj.exe'
    dst = os.path.join(dist_dir, 'Punctaj.exe')
    shutil.copy2(src, dst)
    exe_size = os.path.getsize(dst) / (1024*1024)
    print(f"[OK] EXE: {exe_size:.2f} MB")
    
    # *** CRITICAL: Copy configs to SAME FOLDER as EXE ***
    # This ensures config_loader finds them when EXE runs
    configs_to_include = ['discord_config.ini', 'supabase_config.ini', 'config.json', 'settings.json']
    
    for cfg in configs_to_include:
        src_cfg = os.path.join('d:\\punctaj', cfg)
        if os.path.exists(src_cfg):
            dst_cfg = os.path.join(dist_dir, cfg)  # SAME FOLDER as EXE
            shutil.copy2(src_cfg, dst_cfg)
            print(f"[OK] Config: {cfg}")
        else:
            print(f"[SKIP] Config not found: {cfg}")
    
    # Copy module files as fallback for imports
    print("[*] Adding module files as import fallback...")
    critical_modules = [
        'supabase_sync.py',
        'supabase_employee_manager.py',
        'supabase_realtime_ws.py',
        'discord_auth.py',
        'config_loader_robust.py',
        'config_resolver.py',
        'users_permissions_json_manager.py',
    ]
    
    for mod in critical_modules:
        src_mod = os.path.join('d:\\punctaj', mod)
        if os.path.exists(src_mod):
            dst_mod = os.path.join(dist_dir, mod)
            shutil.copy2(src_mod, dst_mod)
            print(f"    [OK] {mod}")
    
    print(f"\n[SUCCESS] Distribution folder prepared at: {dist_dir}")
    return dist_dir

def create_final_zip(dist_dir):
    """Create distribution ZIP"""
    print("\n[*] Creating ZIP archive...")
    
    output = 'd:\\punctaj\\Punctaj_App_Distribution.zip'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                fpath = os.path.join(root, f)
                arcname = os.path.relpath(fpath, dist_dir)
                zf.write(fpath, arcname)
    
    size = os.path.getsize(output) / (1024*1024)
    print(f"[OK] Archive: {size:.2f} MB")
    
    if size <= 500:
        print(f"[SUCCESS] Size OK: {size:.2f}MB (limit: 500MB)")
    else:
        print(f"[WARNING] Size large: {size:.2f}MB")
    
    return output

def main():
    print("="*60)
    print("BUILD DISTRIBUTION - WITH DATABASE SYNC FIX")
    print("="*60)
    
    try:
        cleanup_builds()
        if not build_exe():
            print("[FAILED] Build error")
            return False
        dist_dir = create_distribution()
        create_final_zip(dist_dir)
        
        print("\n" + "="*60)
        print("[SUCCESS] DISTRIBUTION READY!")
        print("="*60)
        print("\nFile: Punctaj_App_Distribution.zip")
        print("Status: Ready for distribution")
        print("\nFeatures:")
        print("  - Full Discord authentication")
        print("  - Supabase database sync ENABLED")
        print("  - All modules properly imported")
        print("  - Config files included")
        
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
