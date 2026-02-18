#!/usr/bin/env python3
"""
Build complete distribution with ALL local modules
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys
import glob

def find_all_local_modules():
    """Find all .py files in root that need to be included"""
    print("[*] Scanning for local modules...")
    
    modules = []
    for py_file in glob.glob('d:\\punctaj\\*.py'):
        basename = os.path.basename(py_file)
        # Skip build/setup scripts
        if not basename.startswith('_') and basename not in ['BUILD_DISTRIBUTION_PACKAGE.py', 'OPTIMIZE_FOR_DISTRIBUTION.py']:
            modules.append(basename)
            print(f"    Found: {basename}")
    
    return sorted(modules)

def cleanup_old_builds():
    """Clean old build folders"""
    print("[*] Cleaning old build folders...")
    
    dirs = [
        'd:\\punctaj\\dist_output',
        'd:\\punctaj\\build_spec',
        'd:\\punctaj\\punctaj_app_build',
    ]
    
    for d in dirs:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"    [OK] Removed {d}")
            except:
                pass

def build_exe():
    """Build EXE with PyInstaller (--onedir for proper module import)"""
    print("\n[*] Building EXE with PyInstaller...")
    
    # Create necessary directories
    build_dir = 'd:\\punctaj\\punctaj_app_build'
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs('d:\\punctaj\\build_spec', exist_ok=True)
    
    # Stage all modules in build directory FIRST
    print("[*] Staging all modules in build directory...")
    
    staged_modules = []
    for py_file in glob.glob('d:\\punctaj\\*.py'):
        basename = os.path.basename(py_file)
        if not basename.startswith(('BUILD_', 'OPTIMIZE_', '_', 'VERIFY_', 'TEST_', 'DEMO_', 'CREATE_', 'REBUILD_', 'SETUP_INSTALLER', 'SET_', 'INSERT_', 'DEBUG_', 'DIAGNOSTIC_', 'REPAIR_', 'initialize', 'delete_', 'disable_', 'check_', 'clean_', 'populate_', 'list_', 'monitor_', 'sync_', 'test_', 'update_', 'upload_', 'add_', 'install', 'FINAL_', 'FIX_', 'INTEGRATION_', 'MULTIDEVICE_', 'PACKAGE_', 'QUICK_', 'RUN_', 'RESET_', 'DEPLOY_', 'DIAGNOSE_', 'revolut_', 'CAPTURE_')):
            try:
                dst = os.path.join(build_dir, basename)
                shutil.copy2(py_file, dst)
                staged_modules.append(basename)
                print(f"    [OK] {basename}")
            except Exception as e:
                pass
    
    # Stage config files
    for cfg in ['discord_config.ini', 'supabase_config.ini', 'config.json', 'settings.json']:
        src = os.path.join('d:\\punctaj', cfg)
        if os.path.exists(src):
            dst = os.path.join(build_dir, cfg)
            shutil.copy2(src, dst)
            print(f"    [OK] {cfg}")
    
    # Build command - use --onedir instead of --onefile for proper imports
    cmd = [
        'pyinstaller',
        '--onedir',  # IMPORTANT: Keep directory structure for module imports
        '--windowed',
        '--distpath=d:\\punctaj\\dist_output',
        '--specpath=d:\\punctaj\\build_spec',
        '--name=Punctaj',
        '--noconfirm',
        # Add build directory (with all modules) to path during build
        f'--workpath={build_dir}',
        # Hidden imports
        '--hidden-import=discord_auth',
        '--hidden-import=supabase_sync',
        '--hidden-import=supabase_employee_manager',
        '--hidden-import=supabase_realtime_ws',
        '--hidden-import=requests',
        '--hidden-import=tkinter',
        '--hidden-import=json',
        '--hidden-import=configparser',
        '--hidden-import=schedule',
        '--hidden-import=threading',
        '--hidden-import=csv',
    ]
    
    # Add all staged modules as data
    for mod in staged_modules:
        mod_path = os.path.join(build_dir, mod)
        cmd.append(f'--add-data={mod_path}:.')
    
    # Add main file
    cmd.append('d:\\punctaj\\punctaj.py')
    
    print(f"\n[*] Building with {len(staged_modules)} modules...")
    result = subprocess.run(cmd, cwd='d:\\punctaj', capture_output=True, text=True, timeout=600)
    
    if result.returncode != 0:
        print(f"[ERROR] Build failed:")
        print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
        return False
    
    exe_path = 'd:\\punctaj\\dist_output\\Punctaj\\Punctaj.exe'
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024*1024)
        print(f"[OK] EXE built: {size_mb:.2f} MB")
        print(f"[OK] Directory structure maintained for module access")
        return True
    else:
        print("[ERROR] EXE not found after build")
        return False

def prepare_distribution():
    """Prepare distribution files from --onedir build"""
    print("\n[*] Preparing distribution files...")
    
    # The built folder structure with --onedir
    built_app_dir = 'd:\\punctaj\\dist_output\\Punctaj'
    dist_dir = 'd:\\punctaj\\PUNCTAJ_DIST'
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    # Copy entire Punctaj folder (with all dependencies, libraries, and modules)
    if os.path.exists(built_app_dir):
        shutil.copytree(built_app_dir, dist_dir)
        exe_size = os.path.getsize(os.path.join(dist_dir, 'Punctaj.exe')) / (1024*1024)
        print(f"[OK] Copied app folder: {exe_size:.2f} MB (main exe)")
        print(f"[OK] All dependencies and modules included in folder structure")
    else:
        print(f"[ERROR] Built app folder not found: {built_app_dir}")
        return dist_dir
    
    # Add essential config files to main folder
    config_files = ['config.json', 'settings.json', 'discord_config.ini', 'supabase_config.ini', 'README.txt']
    
    for cfg in config_files:
        src = os.path.join('d:\\punctaj', cfg)
        if os.path.exists(src):
            dst = os.path.join(dist_dir, cfg)
            shutil.copy2(src, dst)
            print(f"[OK] Added config: {cfg}")
    
    return dist_dir

def create_zip(dist_dir):
    """Create compressed archive"""
    print("\n[*] Creating compressed archive...")
    
    output = 'd:\\punctaj\\Punctaj_App_Distribution.zip'
    
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                fpath = os.path.join(root, f)
                arcname = os.path.relpath(fpath, dist_dir)
                zf.write(fpath, arcname)
    
    size_mb = os.path.getsize(output) / (1024*1024)
    print(f"[OK] Archive created: {size_mb:.2f} MB")
    
    if size_mb <= 500:
        print(f"[SUCCESS] SIZE OK: {size_mb:.2f} MB (limit: 500 MB)")
    else:
        print(f"[WARNING] SIZE LARGE: {size_mb:.2f} MB (limit: 500 MB)")
    
    return output

def main():
    print("=" * 60)
    print("BUILD COMPLETE DISTRIBUTION WITH ALL MODULES")
    print("=" * 60)
    
    try:
        cleanup_old_builds()
        
        if not build_exe():
            print("\n[FAILED] Could not build EXE")
            return False
        
        dist_dir = prepare_distribution()
        
        zip_file = create_zip(dist_dir)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] COMPLETE DISTRIBUTION PACKAGE READY!")
        print("=" * 60)
        print(f"\nFile: Punctaj_App_Distribution.zip")
        print(f"Location: d:\\punctaj\\")
        print(f"\nIncludes:")
        print(f"  - Complete EXE with all modules")
        print(f"  - Discord authentication")
        print(f"  - Supabase database sync")
        print(f"  - All local Python modules")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
