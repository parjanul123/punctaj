#!/usr/bin/env python3
"""
Create a portable ZIP package with the exe and all required files
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_portable_package():
    """Create a portable ZIP package with exe and required files"""
    
    # Define paths
    base_dir = Path("d:/punctaj")
    dist_dir = base_dir / "dist"
    exe_file = dist_dir / "punctaj.exe"
    output_dir = base_dir  # ZIP goes directly in punctaj folder
    
    # Files that should be included in the package
    required_files = [
        "supabase_config.ini",  # Configuration file
        "requirements.txt",      # Dependencies reference
        "discord_config.ini",    # Discord config
    ]
    
    # Directories to include
    required_dirs = [
        "data",  # Data directory if exists
    ]
    
    # Create temporary package directory
    package_dir = output_dir / "Punctaj_Manager_Portable"
    
    # Clean if exists
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)
    
    print("📦 Creating portable package...")
    print(f"📁 Package directory: {package_dir}")
    
    # Copy exe file
    if exe_file.exists():
        print(f"✅ Copying executable: {exe_file.name}")
        shutil.copy2(exe_file, package_dir / exe_file.name)
    else:
        print(f"❌ ERROR: Executable not found at {exe_file}")
        return False
    
    # Copy required files
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            print(f"✅ Copying: {file_name}")
            shutil.copy2(file_path, package_dir / file_name)
        else:
            print(f"⚠️  Optional file not found: {file_name}")
    
    # Copy required directories
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ Copying directory: {dir_name}")
            dest_dir = package_dir / dir_name
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            shutil.copytree(dir_path, dest_dir)
        else:
            print(f"⚠️  Optional directory not found: {dir_name}")
    
    # Create README
    readme_content = """# Punctaj Manager - Portable Package

## How to Run

1. Extract this ZIP file to any location
2. Run **punctaj.exe**
3. The application will start with all required files

## Contents

- **punctaj.exe** - Main application executable
- **supabase_config.ini** - Database configuration
- **discord_config.ini** - Discord authentication setup
- **data/** - Application data directory

## System Requirements

- Windows 7 or later
- ~100 MB free disk space
- Internet connection (for cloud sync)

## First Run

On first launch:
1. You may see Windows Defender warning (it's safe)
2. Click "More info" → "Run anyway"
3. Login with your Discord account

## Support

For issues or updates, check the main application folder.

---
Generated: {timestamp}
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    readme_path = package_dir / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ Created README.txt")
    
    # Create ZIP file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"Punctaj_Manager_Portable_{timestamp}.zip"
    zip_path = output_dir / zip_filename
    
    print(f"\n📦 Creating ZIP file: {zip_filename}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir.parent)
                print(f"   Adding: {arcname}")
                zipf.write(file_path, arcname)
    
    print(f"\n✅ SUCCESS! Portable package created:")
    print(f"   Location: {zip_path}")
    print(f"   Size: {zip_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Clean up extracted folder (optional)
    print(f"\n🧹 Cleaning up temporary files...")
    shutil.rmtree(package_dir)
    
    return True

if __name__ == "__main__":
    try:
        success = create_portable_package()
        if success:
            print("\n✨ Package creation completed successfully!")
        else:
            print("\n❌ Package creation failed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
