#!/usr/bin/env python3
"""
Optimizeaza aplicatia pentru distributie - max 500MB comprimat
Curata build directories, remove venv din distribution, si face arhiva lean
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys

def cleanup_build_dirs():
    """Sterge toate directoarele de build vechi"""
    print("🧹 Curatat old build directories...")
    
    dirs_to_remove = [
        'd:\\punctaj\\app_build',
        'd:\\punctaj\\build',
        'd:\\punctaj\\installer_build',
        'd:\\punctaj\\installer_output',
        'd:\\punctaj\\Punctaj_Manager_Professional_Installer',
        'd:\\punctaj\\Punctaj_Manager_Setup',
        'd:\\punctaj\\setup_output',
        'd:\\punctaj\\dist',
        'd:\\punctaj\\installer_dist',
        'd:\\punctaj\\installer_outputs',
    ]
    
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"  ✓ Removed: {dir_path}")
            except Exception as e:
                print(f"  ⚠ Could not remove {dir_path}: {e}")

def get_unnecessary_files():
    """Lista fissiere care nu trebuie in distributie"""
    unnecessary = [
        # Documentation files (optional, keep if needed)
        # '__pycache__',
        '*.pyc',
        '.git',
        '.gitignore',
        '.pytest_cache',
        '__pycache__',
        '.vscode',
        '.env',
        'venv',
        'env',
        # Test files (optional)
        'test_*.py',
        '*_test.py',
        'tests',
        # Old documentation
        '00_*.txt',
        '00_*.md',
        '01_QUICK_START_BUILD_DISTRIBUTE.md',
        '02_ARCHITECTURE_COMPLETE.md',
        'ACTION_ITEMS_*.md',
        'ACTIONABLE_*.md',
        'ADMIN_*.md',
        'ARCHITECTURE_*.md',
        'AUTO_REGISTRATION_*.md',
        'BANK_*.md',
        'BANK_*.py',
        'BEFORE_AFTER_*.md',
        'BIDIRECTIONAL_*.md',
        'BUGFIX_*.md',
        'BUGFIXES_*.md',
        'BUILD_*.md',
        'BUILD_*.py',
        'BUILD_*.bat',
        'BUILD_*.ps1',
        'build_*.py',
        'build_*.bat',
        'build_*.ps1',
        '_backup_*.py',
        '_setup*.py',
        'arhiva',
        '*.md',  # Remove all markdown docs for distribution
    ]
    return unnecessary

def build_lean_exe():
    """Construieste EXE optimizat cu PyInstaller"""
    print("\n🔨 Building optimized EXE with PyInstaller...")
    
    # PyInstaller command for minimal size
    cmd = [
        'pyinstaller',
        '--onefile',  # Single executable
        '--windowed',  # No console window
        '--optimize=2',  # Optimize bytecode
        '--noupx',  # Don't use UPX (may cause issues)
        '--distpath=d:\\punctaj\\dist_lean',
        '--build-temp=d:\\punctaj\\build_temp',
        '--specpath=d:\\punctaj\\build_spec',
        '--name=Punctaj',
        # Strip debug info
        '--strip',
        # Minimize dependencies
        '--collect-all=tkinter',
        '--collect-all=requests',
        'd:\\punctaj\\punctaj.py'
    ]
    
    try:
        result = subprocess.run(cmd, cwd='d:\\punctaj', capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ EXE built successfully")
            return True
        else:
            print(f"  ✗ Build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Error building: {e}")
        return False

def copy_essential_files():
    """Copie doarfissierele essentiale in output folder"""
    print("\n📁 Preparing distribution files...")
    
    dist_dir = 'd:\\punctaj\\APPLICATION_DIST'
    exe_source = 'd:\\punctaj\\dist_lean\\Punctaj.exe'
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir, exist_ok=True)
    
    # Copy main executable
    if os.path.exists(exe_source):
        shutil.copy(exe_source, os.path.join(dist_dir, 'Punctaj.exe'))
        size_mb = os.path.getsize(exe_source) / (1024 * 1024)
        print(f"  ✓ Copied EXE ({size_mb:.2f} MB)")
    
    # Copy only essential config/data files
    essential_files = [
        'config.json',
        'settings.json',
        'README.txt',  # If exists
    ]
    
    for file in essential_files:
        src = os.path.join('d:\\punctaj', file)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(dist_dir, file))
            print(f"  ✓ Copied {file}")
    
    return dist_dir

def compress_for_distribution(dist_dir):
    """Compresa aplicatia intr-un ZIP de maxim 500MB"""
    print("\n📦 Creating compressed archive...")
    
    output_zip = 'd:\\punctaj\\Punctaj_Application_FINAL.zip'
    
    # Use maximum compression
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
    
    zip_size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"  ✓ Archive created: {output_zip}")
    print(f"  📊 Archive size: {zip_size_mb:.2f} MB")
    
    if zip_size_mb > 500:
        print(f"  ⚠ WARNING: Archive is {zip_size_mb:.2f}MB, exceeds 500MB limit!")
    else:
        print(f"  ✅ EXCELLENT: Archive is {zip_size_mb:.2f}MB (within 500MB limit)")
    
    return output_zip

def get_directory_size_mb(path):
    """Calculeaza size-ul unui director"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            total += os.path.getsize(os.path.join(dirpath, filename))
    return total / (1024 * 1024)

def main():
    print("=" * 60)
    print("🎯 OPTIMIZE PUNCTAJ APPLICATION FOR DISTRIBUTION")
    print("=" * 60)
    
    try:
        # Step 1: Cleanup
        cleanup_build_dirs()
        
        # Step 2: Build lean EXE
        if not build_lean_exe():
            print("\n❌ Failed to build EXE. Exiting.")
            sys.exit(1)
        
        # Step 3: Copy essential files
        dist_dir = copy_essential_files()
        
        dist_size = get_directory_size_mb(dist_dir)
        print(f"\n📊 Distribution folder size: {dist_size:.2f} MB")
        
        # Step 4: Compress
        final_archive = compress_for_distribution(dist_dir)
        
        print("\n" + "=" * 60)
        print("✅ OPTIMIZATION COMPLETE!")
        print("=" * 60)
        print(f"\n📦 Final package: Punctaj_Application_FINAL.zip")
        print(f"📍 Location: d:\\punctaj\\")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
