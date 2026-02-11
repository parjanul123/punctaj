#!/usr/bin/env python3
"""
Rebuild EXE in punctaj/dist with latest modifications
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

root = Path(r"d:\punctaj")

print("\n" + "=" * 80)
print("🔨 REBUILD EXE FOR DISTRIBUTION")
print("=" * 80)

# Verify PyInstaller
try:
    import PyInstaller
    print("✅ PyInstaller available")
except ImportError:
    print("❌ PyInstaller not installed")
    sys.exit(1)

# Verify required files exist
required_files = [
    "installer_source/punctaj.py",
    "installer_source/backup_manager.py",
    "installer_source/permission_sync_fix.py",
    "installer_source/discord_auth.py",
]

print("\n📋 Checking files:")
for file in required_files:
    path = root / file
    if path.exists():
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} MISSING")
        sys.exit(1)

# Clean old dist if possible
dist_dir = root / "dist"
if dist_dir.exists():
    try:
        print(f"\n🗑️  Removing old dist folder...")
        shutil.rmtree(dist_dir)
        print("  ✅ Old dist removed")
    except Exception as e:
        print(f"  ⚠️  Could not remove dist: {e}")

# Build EXE
print("\n⏳ Building PunctajManager.exe...")
print("   (This may take 2-3 minutes...)\n")

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name=PunctajManager",
    f"--distpath={root}/dist",
    f"--workpath={root}/build",
    f"--specpath={root}",
    str(root / "installer_source" / "punctaj.py")
]

result = subprocess.run(cmd, cwd=root)

if result.returncode == 0:
    exe_path = root / "dist" / "PunctajManager.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ BUILD SUCCESSFUL!")
        print(f"   📦 {exe_path}")
        print(f"   📊 Size: {size_mb:.2f} MB")
        
        # Copy to original .exe name for compatibility
        original_exe = root / "dist" / "punctaj.exe"
        shutil.copy2(exe_path, original_exe)
        print(f"\n✅ Also copied as: {original_exe}")
        
        print("\n🎉 Ready for distribution!")
    else:
        print(f"❌ EXE not found at {exe_path}")
        sys.exit(1)
else:
    print("\n❌ BUILD FAILED")
    sys.exit(1)
