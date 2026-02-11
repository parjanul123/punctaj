#!/usr/bin/env python3
"""
Simple EXE Builder for Punctaj Manager
Creates a single executable file for distribution
"""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    project_root = Path(__file__).parent
    
    print("\n" + "=" * 80)
    print("BUILDING EXECUTABLE FOR DISTRIBUTION")
    print("=" * 80)
    
    # Check PyInstaller
    print("\n[1] Checking PyInstaller...")
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True)
    if "pyinstaller" not in result.stdout:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"],
                      check=True)
    
    print("✓ PyInstaller ready")
    
    # Build command
    print("\n[2] Building EXE...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--distpath", "dist",
        "--workpath", "build",
        "punctaj.py"
    ]
    
    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    # Check result
    exe_file = project_root / "dist" / "punctaj.exe"
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"✓ EXE created: {exe_file}")
        print(f"  Size: {size_mb:.1f} MB")
        return True
    else:
        print("✗ EXE not created")
        return False

if __name__ == "__main__":
    if build_exe():
        print("\n" + "=" * 80)
        print("SUCCESS! Your EXE is ready at: d:\\punctaj\\dist\\punctaj.exe")
        print("=" * 80)
        print("\nYou can now:")
        print("  1. Test it on this PC")
        print("  2. Copy it to other PCs and run directly")
        print("  3. Or use INSTALL_SIMPLE.bat to create a proper installer")
    else:
        print("\nBuild failed. Check error messages above.")
        sys.exit(1)
