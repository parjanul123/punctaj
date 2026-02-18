#!/usr/bin/env python3
"""
Build distribution with --onedir to preserve module structure
This ensures all local modules are properly accessible from the EXE
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
    for d in ['d:\\punctaj\\dist_onedir', 'd:\\punctaj\\build_dir', 'd:\\punctaj\\build_spec', 'd:\\punctaj\\PUNCTAJ_DIST_NEW']:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"    [OK] Removed {d}")

def build_exe_with_modules():
    """Build EXE with --onedir to preserve module structure"""
    print("\n[*] Building with directory structure for proper imports...")
    
    os.makedirs('d:\\punctaj\\build_spec', exist_ok=True)
    
    # Use --onedir instead of --onefile - this preserves module structure
    cmd = [
        'pyinstaller',
        '--onedir',  # ← KEY: Keep directory structure!
        '--windowed',
        '--distpath=d:\\punctaj\\dist_onedir',
        '--specpath=d:\\punctaj\\build_spec',
        '--name=Punctaj',
        '--noconfirm',
        '--collect-all=tkinter',
        '--collect-all=requests',
        # All critical modules
        '--hidden-import=discord_auth',
        '--hidden-import=supabase_sync',
        '--hidden-import=supabase_employee_manager',
        '--hidden-import=supabase_realtime_ws',
        '--hidden-import=config_loader_robust',
        '--hidden-import=config_resolver',
        '--hidden-import=action_logger',
        '--hidden-import=admin_panel',
        '--hidden-import=admin_permissions',
        '--hidden-import=admin_ui',
        '--hidden-import=multi_device_sync_manager',
        '--hidden-import=cloud_sync_manager',
        '--hidden-import=users_permissions_json_manager',
        '--hidden-import=permission_decorators',
        '--hidden-import=realtime_sync',
        '--hidden-import=backup_manager',
        # Include data files
        '--add-data=d:\\punctaj\\discord_config.ini:.',
        '--add-data=d:\\punctaj\\supabase_config.ini:.',
        'd:\\punctaj\\punctaj.py'
    ]
    
    print("[*] Running PyInstaller with onedir mode...")
    print("[*] This preserves module directory structure")
    
    result = subprocess.run(cmd, cwd='d:\\punctaj', capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"[ERROR] Build failed:")
        print(result.stderr[-500:])
        return False
    
    exe_path = 'd:\\punctaj\\dist_onedir\\Punctaj\\Punctaj.exe'
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024*1024)
        
        # Check for _internal directory (contains modules)
        internal_path = 'd:\\punctaj\\dist_onedir\\Punctaj\\_internal'
        lib_count = 0
        if os.path.exists(internal_path):
            lib_count = len([f for f in os.listdir(internal_path) if os.path.isfile(os.path.join(internal_path, f))])
        
        print(f"[OK] EXE built: {exe_size:.2f} MB")
        print(f"[OK] Modules directory: {internal_path}")
        print(f"[OK] Internal files: {lib_count}")
        return True
    else:
        print(f"[ERROR] EXE not found at {exe_path}")
        return False

def create_distribution_from_onedir():
    """Create distribution from --onedir build"""
    print("\n[*] Preparing distribution...")
    
    src_app_dir = 'd:\\punctaj\\dist_onedir\\Punctaj'
    dist_dir = 'd:\\punctaj\\PUNCTAJ_DIST_FINAL'
    
    if not os.path.exists(src_app_dir):
        print(f"[ERROR] Built app not found at {src_app_dir}")
        return None
    
    # Copy entire app folder (including _internal with all libraries)
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    print("[*] Copying app folder with all modules...")
    shutil.copytree(src_app_dir, dist_dir)
    
    exe_size = os.path.getsize(os.path.join(dist_dir, 'Punctaj.exe')) / (1024*1024)
    print(f"[OK] EXE: {exe_size:.2f} MB")
    
    # Copy configs
    for cfg in ['discord_config.ini', 'supabase_config.ini']:
        src_cfg = os.path.join('d:\\punctaj', cfg)
        if os.path.exists(src_cfg):
            dst_cfg = os.path.join(dist_dir, cfg)
            shutil.copy2(src_cfg, dst_cfg)
            print(f"[OK] Config: {cfg}")
    
    # Copy critical module files as fallback
    for mod in ['supabase_sync.py', 'supabase_employee_manager.py', 'discord_auth.py', 'config_loader_robust.py']:
        src = os.path.join('d:\\punctaj', mod)
        if os.path.exists(src):
            dst = os.path.join(dist_dir, mod)
            shutil.copy2(src, dst)
    
    return dist_dir

def create_zip_distrib(dist_dir):
    """Create final ZIP distribution"""
    print("\n[*] Creating ZIP archive...")
    
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
    
    if size <= 500:
        print(f"[SUCCESS] Size within limits: {size:.2f}MB <= 500MB")
    else:
        print(f"[WARNING] Archive large: {size:.2f}MB")
    
    return output

def main():
    print("="*60)
    print("BUILD DISTRIBUTION - --onedir FOR FULL COMPATIBILITY")
    print("="*60)
    
    try:
        cleanup_builds()
        
        if not build_exe_with_modules():
            print("[FAILED] Build error")
            return False
        
        dist_dir = create_distribution_from_onedir()
        if not dist_dir:
            print("[FAILED] Distribution prep error")
            return False
        
        zip_file = create_zip_distrib(dist_dir)
        
        print("\n" + "="*60)
        print("[SUCCESS] FINAL DISTRIBUTION READY!")
        print("="*60)
        print(f"\nFile: Punctaj_App_Distribution.zip")
        print(f"\nContains:")
        print(f"  - Punctaj.exe (with all modules)")
        print(f"  - _internal/ (PyInstaller libraries)")
        print(f"  - supabase_config.ini")
        print(f"  - discord_config.ini")
        print(f"  - Supporting Python modules")
        print(f"\nThis version is IDENTICAL to punctaj.py execution!")
        
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
