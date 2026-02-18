#!/usr/bin/env python3
"""
Construieste pachetul final de distributie - max 500MB comprimat
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys

def cleanup_old_builds():
    """Sterge build folders ramase"""
    print("[*] Cleaning old build folders...")
    
    dirs = [
        'd:\\punctaj\\dist_lean',
        'd:\\punctaj\\build_spec',
    ]
    
    for d in dirs:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"    [OK] Removed {d}")
            except:
                pass

def build_exe():
    """Construieste EXE cu PyInstaller"""
    print("\n[*] Building EXE with PyInstaller...")
    
    # Ensure directories exist
    os.makedirs('d:\\punctaj\\dist_lean', exist_ok=True)
    os.makedirs('d:\\punctaj\\build_spec', exist_ok=True)
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--distpath=d:\\punctaj\\dist_lean',
        '--specpath=d:\\punctaj\\build_spec',
        '--name=Punctaj',
        # Include Discord and database modules
        '--hidden-import=discord_auth',
        '--hidden-import=supabase_sync',
        '--hidden-import=supabase_employee_manager',
        '--hidden-import=supabase_realtime_ws',
        '--hidden-import=requests',
        '--hidden-import=tkinter',
        '--hidden-import=json',
        '--hidden-import=configparser',
        # Include data files and configs
        '--add-data=d:\\punctaj\\discord_config.ini:.',
        '--add-data=d:\\punctaj\\supabase_config.ini:.',
        '--add-data=d:\\punctaj\\discord_auth.py:.',
        '--add-data=d:\\punctaj\\supabase_sync.py:.',
        '--add-data=d:\\punctaj\\supabase_employee_manager.py:.',
        '--add-data=d:\\punctaj\\supabase_realtime_ws.py:.',
        'd:\\punctaj\\punctaj.py'
    ]
    
    print("[*] Running: " + " ".join(cmd))
    result = subprocess.run(cmd, cwd='d:\\punctaj', capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Build failed:")
        print(result.stderr)
        return False
    
    exe_path = 'd:\\punctaj\\dist_lean\\Punctaj.exe'
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024*1024)
        print(f"[OK] EXE built: {size_mb:.2f} MB")
        return True
    else:
        print("[ERROR] EXE not found after build")
        return False

def prepare_distribution():
    """Pregateste fisierele pentru distributie"""
    print("\n[*] Preparing distribution files...")
    
    dist_dir = 'd:\\punctaj\\PUNCTAJ_DIST'
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir, exist_ok=True)
    
    # Copy EXE
    src_exe = 'd:\\punctaj\\dist_lean\\Punctaj.exe'
    if os.path.exists(src_exe):
        dst_exe = os.path.join(dist_dir, 'Punctaj.exe')
        shutil.copy2(src_exe, dst_exe)
        size = os.path.getsize(dst_exe) / (1024*1024)
        print(f"[OK] Copied EXE: {size:.2f} MB")
    
    # Copy essential config/data files
    essential_files = [
        ('config.json', 'config.json'),
        ('settings.json', 'settings.json'),
        ('discord_config.ini', 'discord_config.ini'),
        ('supabase_config.ini', 'supabase_config.ini'),  # CRITICAL for DB
        ('discord_auth.py', 'discord_auth.py'),  # CRITICAL for Discord
        ('supabase_sync.py', 'supabase_sync.py'),  # CRITICAL for Database
        ('supabase_employee_manager.py', 'supabase_employee_manager.py'),
        ('supabase_realtime_ws.py', 'supabase_realtime_ws.py'),
        ('README.txt', 'README.txt'),
    ]
    
    for src_name, dst_name in essential_files:
        src = os.path.join('d:\\punctaj', src_name)
        if os.path.exists(src):
            dst = os.path.join(dist_dir, dst_name)
            shutil.copy2(src, dst)
            size = os.path.getsize(src) / (1024*1024)
            if size > 0.1:
                print(f"[OK] Copied {src_name}: {size:.2f} MB")
            else:
                print(f"[OK] Copied {src_name}")
    
    return dist_dir

def create_zip(dist_dir):
    """Comprima distributia in ZIP"""
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
    print(f"[*] File: {output}")
    
    if size_mb <= 500:
        print(f"[SUCCESS] SIZE OK: {size_mb:.2f} MB (limit: 500 MB)")
    else:
        print(f"[WARNING] SIZE TOO LARGE: {size_mb:.2f} MB (limit: 500 MB)")
    
    return output

def main():
    print("=" * 60)
    print("BUILD FINAL DISTRIBUTION PACKAGE")
    print("=" * 60)
    
    try:
        cleanup_old_builds()
        
        if not build_exe():
            print("\n[FAILED] Could not build EXE")
            return False
        
        dist_dir = prepare_distribution()
        
        zip_file = create_zip(dist_dir)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] DISTRIBUTION PACKAGE READY!")
        print("=" * 60)
        print(f"\nFile: Punctaj_App_Distribution.zip")
        print(f"Ready to distribute from: d:\\punctaj\\")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
