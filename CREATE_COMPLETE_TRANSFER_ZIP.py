#!/usr/bin/env python3
"""
Create a complete ZIP package with exe already installed
Transfer to another device, extract, and run
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_complete_zip_package():
    """Create a complete ZIP with exe and all required files"""
    
    base_dir = Path("d:/punctaj")
    dist_dir = base_dir / "dist"
    exe_file = dist_dir / "punctaj.exe"
    
    # Output location
    output_dir = base_dir.parent / "transfer"
    output_dir.mkdir(exist_ok=True)
    
    print("📦 Creating complete ZIP package for transfer...")
    print(f"📁 Source: {base_dir}")
    print(f"📁 Output: {output_dir}")
    
    # 1. Copy exe to root folder
    print("\n1️⃣  Copying exe to root folder...")
    if exe_file.exists():
        root_exe = base_dir / "punctaj.exe"
        shutil.copy2(exe_file, root_exe)
        print(f"   ✅ Copied: punctaj.exe")
    else:
        print(f"   ❌ ERROR: {exe_file} not found")
        return False
    
    # 2. Files and folders to include in ZIP
    print("\n2️⃣  Preparing files for compression...")
    
    files_to_include = [
        "punctaj.exe",              # Root exe
        "supabase_config.ini",      # Database config
        "discord_config.ini",       # Discord config
        "requirements.txt",         # Dependencies
        "config_loader_robust.py",  # Robust config loader
        "DIAGNOSE_SUPABASE.py",     # Diagnostic tool
        "FIX_SUPABASE_CONFIG.py",   # Fix script (if exists)
        "README_TRANSFER.txt",      # Instructions
    ]
    
    dirs_to_include = [
        "data",                     # Data folder
        "dist",                     # Dist with exe backup
    ]
    
    # Check which files exist
    existing_files = []
    for file_name in files_to_include:
        file_path = base_dir / file_name
        if file_path.exists():
            existing_files.append(file_path)
            print(f"   ✅ {file_name}")
        else:
            print(f"   ⚠️  {file_name} (optional)")
    
    existing_dirs = []
    for dir_name in dirs_to_include:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            existing_dirs.append(dir_path)
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ⚠️  {dir_name}/ (optional)")
    
    # 3. Create README for transfer
    print("\n3️⃣  Creating transfer instructions...")
    readme_transfer = """# Punctaj Manager - Transfer Package

## How to use on another device:

1. Extract this ZIP file to any location
   Example: C:\\Users\\YourName\\Punctaj

2. Run punctaj.exe directly
   - Double-click punctaj.exe
   - Or open Command Prompt and type: punctaj.exe

3. On first run:
   - Login with your Discord account
   - Allow Windows (SmartScreen might warn)
   - Wait for database to load

## What's included:

- punctaj.exe          - Ready to run (from dist/)
- supabase_config.ini  - Database connection config
- discord_config.ini   - Discord authentication setup
- data/                - Application data
- dist/                - Backup of exe and dependencies

## If database doesn't load:

Run diagnostic:
  py DIAGNOSE_SUPABASE.py

Run fix:
  py FIX_SUPABASE_CONFIG.py

## Multi-Device Sync:

All devices using same Discord account will:
✅ Share the same database
✅ Have same permissions
✅ Keep data in sync
✅ Fresh login each session (for security)

## Files to keep synchronized:

- supabase_config.ini  - Must be identical on all devices
- discord_config.ini   - Must be identical on all devices

If you change config on one device, copy updated files to other devices.

---
Transfer Date: {timestamp}
Package Size: Ready to extract anywhere
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    readme_path = base_dir / "README_TRANSFER.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_transfer)
    existing_files.append(readme_path)
    print(f"   ✅ Created README_TRANSFER.txt")
    
    # 4. Create ZIP file
    print("\n4️⃣  Creating ZIP file...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"Punctaj_Manager_Complete_{timestamp}.zip"
    zip_path = output_dir / zip_filename
    
    file_count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Add individual files
        print(f"   Adding files...")
        for file_path in existing_files:
            arcname = file_path.relative_to(base_dir)
            zipf.write(file_path, arcname)
            print(f"      ✅ {arcname}")
            file_count += 1
        
        # Add directories
        print(f"   Adding directories...")
        for dir_path in existing_dirs:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(base_dir)
                    zipf.write(file_path, arcname)
                    file_count += 1
            print(f"      ✅ {dir_path.name}/ ({len(list(dir_path.rglob('*')))} files)")
    
    # 5. Report
    print("\n" + "="*70)
    print("✅ ZIP PACKAGE CREATED SUCCESSFULLY!")
    print("="*70)
    
    size_mb = zip_path.stat().st_size / (1024*1024)
    print(f"\n📦 Package: {zip_filename}")
    print(f"   Location: {zip_path}")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Files: {file_count}")
    
    print("\n📋 How to transfer:")
    print("   1. Copy this ZIP file to USB drive or cloud storage")
    print("   2. Transfer to another device")
    print("   3. Extract anywhere (e.g., C:\\Punctaj)")
    print("   4. Run: punctaj.exe")
    
    print("\n✨ Everything needed is in this ZIP:")
    print("   ✅ punctaj.exe - ready to run")
    print("   ✅ supabase_config.ini - database config")
    print("   ✅ discord_config.ini - authentication config")
    print("   ✅ data/ - all application data")
    print("   ✅ Diagnostic & fix tools included")
    
    return True

def main():
    print("="*70)
    print("🚀 CREATE COMPLETE TRANSFER PACKAGE")
    print("="*70)
    print()
    
    success = create_complete_zip_package()
    
    if success:
        print("\n🎉 READY TO TRANSFER!")
        print("\nNext steps:")
        print("1. Find the ZIP file in: d:\\transfer\\")
        print("2. Copy to USB or upload to cloud")
        print("3. Transfer to another device")
        print("4. Extract and run punctaj.exe")
    else:
        print("\n❌ Failed to create package")

if __name__ == "__main__":
    main()
