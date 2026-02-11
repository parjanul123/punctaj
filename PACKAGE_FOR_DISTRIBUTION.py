#!/usr/bin/env python3
"""
Create distributable installer package with EXE
Packages everything needed to install on other PCs
"""

import shutil
from pathlib import Path
import os

def create_installer_package():
    project_root = Path("d:\\punctaj")
    
    # Create package directory
    package_dir = project_root / "Punctaj_Manager_Setup"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print("\n" + "="*80)
    print("CREATING INSTALLER PACKAGE FOR DISTRIBUTION")
    print("="*80 + "\n")
    
    # Copy EXE
    exe_file = project_root / "dist" / "punctaj.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, package_dir / "punctaj.exe")
        size_mb = exe_file.stat().st_size / (1024*1024)
        print(f"✓ Copied punctaj.exe ({size_mb:.1f} MB)")
    
    # Copy installer script
    installer = project_root / "INSTALL_FOR_OTHER_PCs.bat"
    if installer.exists():
        shutil.copy2(installer, package_dir / "INSTALL_FOR_OTHER_PCs.bat")
        print(f"✓ Copied INSTALL_FOR_OTHER_PCs.bat")
    
    # Copy configuration files
    for config_file in ["supabase_config.ini", "discord_config.ini"]:
        src = project_root / config_file
        if src.exists():
            shutil.copy2(src, package_dir / config_file)
            print(f"✓ Copied {config_file}")
    
    # Copy documentation
    for doc in ["INSTALLATION_GUIDE.txt", "DISTRIBUTION_GUIDE_FOR_INSTALLERS.txt"]:
        src = project_root / doc
        if src.exists():
            shutil.copy2(src, package_dir / doc)
            print(f"✓ Copied {doc}")
    
    # Copy requirements.txt
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        shutil.copy2(req_file, package_dir / "requirements.txt")
        print(f"✓ Copied requirements.txt")
    
    print(f"\n✓ Package directory created: {package_dir}")
    print(f"\n📦 Contents of installer package:")
    
    total_size = 0
    for file in sorted(package_dir.iterdir()):
        size_mb = file.stat().st_size / (1024*1024)
        total_size += file.stat().st_size
        print(f"   • {file.name} ({size_mb:.1f} MB)")
    
    print(f"\n   Total size: {total_size / (1024*1024):.1f} MB")
    
    # Create ZIP
    print(f"\n📦 Creating ZIP package...")
    zip_path = project_root / "Punctaj_Manager_Setup"
    shutil.make_archive(str(zip_path), 'zip', project_root, "Punctaj_Manager_Setup")
    
    zip_file = project_root / "Punctaj_Manager_Setup.zip"
    if zip_file.exists():
        zip_size = zip_file.stat().st_size / (1024*1024)
        print(f"✓ Created ZIP: Punctaj_Manager_Setup.zip ({zip_size:.1f} MB)")
    
    # Create README for package
    readme = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          PUNCTAJ MANAGER v2.0.0 - READY FOR DISTRIBUTION                  ║
║                                                                            ║
║                  Install on Any Windows PC with One Click!                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 WHAT'S IN THIS PACKAGE:
─────────────────────────────────────────────────────────────────────────────

✓ EXE application (doesn't require Python!)
✓ Automatic installer script
✓ Cloud configuration (Supabase)
✓ Complete documentation
✓ Everything needed for other PCs


🚀 QUICK START (3 STEPS):
─────────────────────────────────────────────────────────────────────────────

1. Copy this folder to the target PC (USB or file transfer)

2. Right-click "INSTALL_FOR_OTHER_PCs.bat"
   Select "Run as administrator"

3. Wait for "Installation successful!" message

That's it! Punctaj Manager is ready to use with cloud sync enabled!


📋 SYSTEM REQUIREMENTS:
─────────────────────────────────────────────────────────────────────────────

✓ Windows 7 or later (64-bit recommended)
✓ 500 MB free disk space
✓ Internet connection (for cloud sync)
✓ Administrator privileges for installation


☁️  CLOUD SYNCHRONIZATION - INCLUDED!
─────────────────────────────────────────────────────────────────────────────

This installation automatically:
• Configures Supabase cloud sync
• Downloads existing data from cloud
• Syncs all changes automatically
• Works with multiple PCs simultaneously


📖 NEED HELP?
─────────────────────────────────────────────────────────────────────────────

See the included documentation files:
• INSTALLATION_GUIDE.txt - Step-by-step installation
• DISTRIBUTION_GUIDE_FOR_INSTALLERS.txt - Detailed instructions


═════════════════════════════════════════════════════════════════════════════

READY? Run the installer now!

Right-click: INSTALL_FOR_OTHER_PCs.bat
Select: Run as administrator

═════════════════════════════════════════════════════════════════════════════
"""
    
    readme_file = package_dir / "README_FIRST.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"✓ Created README_FIRST.txt")
    
    print("\n" + "="*80)
    print("✓ INSTALLER PACKAGE READY FOR DISTRIBUTION!")
    print("="*80)
    print(f"\n📂 Location: {package_dir}")
    print(f"\n📝 How to distribute:")
    print(f"   Option 1: Copy the entire 'Punctaj_Manager_Setup' folder to USB")
    print(f"   Option 2: Send 'Punctaj_Manager_Setup.zip' via email/cloud")
    print(f"   Option 3: Share the folder on network")
    print(f"\n💬 To install on another PC:")
    print(f"   1. Copy the package to target PC")
    print(f"   2. Run: INSTALL_FOR_OTHER_PCs.bat (as Administrator)")
    print(f"   3. Done! Cloud sync works automatically!")
    print()

if __name__ == "__main__":
    create_installer_package()
