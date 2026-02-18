#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUICK BUILD - Construieste punctaj.exe rapid cu PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Fix Unicode encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.chdir(r"d:\punctaj")

print("🔨 Building punctaj.exe...\n")

# Clean
for d in ["build", "dist", "__pycache__"]:
    if Path(d).exists():
        shutil.rmtree(d)

# Build
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile", "--windowed", "--console",
    "--name=punctaj",
    "--distpath=dist",
    "--workpath=build",
    "--specpath=.",
    "punctaj.py"
]

result = subprocess.run(cmd)

if result.returncode == 0:
    exe = Path("dist/punctaj.exe")
    if exe.exists():
        size = exe.stat().st_size / (1024*1024)
        print(f"\n✅ SUCCESS: {exe} ({size:.1f} MB)\n")
    else:
        print("\n❌ EXE not found\n")
        sys.exit(1)
else:
    print("\n❌ Build failed\n")
    sys.exit(1)

# Copy configs
for f in ["supabase_config.ini", "discord_config.ini"]:
    if Path(f).exists():
        shutil.copy2(f, f"dist/{f}")

print("✅ Ready to use: dist/punctaj.exe\n")
