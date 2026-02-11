#!/usr/bin/env python3
"""
🚀 BUILD SCRIPT - Punctaj Manager Installer v2.5
Creates professional installer with all latest features:
- Permission Sync (auto-update permisiuni)
- Auto-Registration (creare user automat)
- All dependencies bundled
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================================
# ⚙️ CONFIGURARE
# ============================================================================

PROJECT_ROOT = Path(r"d:\punctaj")
INSTALLER_SOURCE = PROJECT_ROOT / "installer_source"
OUTPUT_DIR = PROJECT_ROOT / "installer_output"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
VERSION = "2.5"

# ============================================================================
# 🔍 VERIFICARE PREREQUISITE
# ============================================================================

print("\n" + "=" * 80)
print("🚀 PUNCTAJ MANAGER INSTALLER BUILD v" + VERSION)
print("=" * 80)
print(f"📅 Build date: {BUILD_DATE}")
print(f"📁 Project root: {PROJECT_ROOT}")
print(f"📦 Output directory: {OUTPUT_DIR}")

# Check if PyInstaller installed
try:
    import PyInstaller
    print("✅ PyInstaller: OK")
except ImportError:
    print("❌ PyInstaller: NOT INSTALLED")
    print("   Install with: pip install pyinstaller")
    sys.exit(1)

# Check if main file exists
if not (PROJECT_ROOT / "punctaj.py").exists():
    print("❌ punctaj.py not found!")
    sys.exit(1)

if not INSTALLER_SOURCE.exists():
    print("❌ installer_source folder not found!")
    print("   Create with BUILD_PROFESSIONAL_EXE_INSTALLER.py first")
    sys.exit(1)

# ============================================================================
# 📋 LISTA FISIERE VERIFICARE
# ============================================================================

print("\n" + "-" * 80)
print("📋 Verificare fișiere...")
print("-" * 80)

REQUIRED_FILES = [
    "punctaj.py",
    "discord_auth.py",
    "supabase_sync.py",
    "admin_panel.py",
    "admin_permissions.py",
    "admin_ui.py",
    "permission_sync_fix.py",  # ← NEW: Permission sync
    "action_logger.py",
    "cloud_sync_manager.py",
    "discord_config.ini",
    "supabase_config.ini",
    "requirements.txt",
]

missing_files = []
for file in REQUIRED_FILES:
    file_path = INSTALLER_SOURCE / file
    if file_path.exists():
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - MISSING!")
        missing_files.append(file)

if missing_files:
    print(f"\n⚠️  {len(missing_files)} file(s) missing!")
    print("   Try running BUILD_PROFESSIONAL_EXE_INSTALLER.py first")
    sys.exit(1)

print("\n✅ All files present!")

# ============================================================================
# 🔨 BUILD PROCES
# ============================================================================

print("\n" + "=" * 80)
print("🔨 INCEPE BUILD PROCES...")
print("=" * 80)

# Creeaza output dir
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# PyInstaller command
print("\n⏳ Running PyInstaller...")
print("   (This may take 2-3 minutes...)")

pyinstaller_cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--icon=" + str(PROJECT_ROOT / "icon.ico") if (PROJECT_ROOT / "icon.ico").exists() else "",
    "--name=PunctajManager",
    "--dist=" + str(OUTPUT_DIR / "dist"),
    "--build=" + str(OUTPUT_DIR / "build"),
    "--specpath=" + str(OUTPUT_DIR),
    str(INSTALLER_SOURCE / "punctaj.py")
]

# Remove empty icon parameter if file doesn't exist
pyinstaller_cmd = [x for x in pyinstaller_cmd if x]

try:
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ PyInstaller: SUCCESS")
    else:
        print("❌ PyInstaller: FAILED")
        print("   Error output:")
        print(result.stderr)
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error running PyInstaller: {e}")
    sys.exit(1)

# ============================================================================
# 📦 VERIFICA OUTPUT EXE
# ============================================================================

print("\n" + "-" * 80)
print("📦 Verificare EXE output...")
print("-" * 80)

exe_path = OUTPUT_DIR / "dist" / "PunctajManager.exe"

if exe_path.exists():
    exe_size = exe_path.stat().st_size / (1024 * 1024)  # Convert to MB
    print(f"✅ EXE created: {exe_path}")
    print(f"   Size: {exe_size:.1f} MB")
else:
    print(f"❌ EXE not found at: {exe_path}")
    sys.exit(1)

# ============================================================================
# 📝 GENEREAZA MANIFEST
# ============================================================================

print("\n" + "-" * 80)
print("📝 Genereaza manifest...")
print("-" * 80)

manifest = {
    "version": VERSION,
    "build_date": BUILD_DATE,
    "features": [
        "✅ Discord OAuth2 Authentication",
        "✅ Supabase Cloud Sync",
        "✅ Admin Panel & Permissions",
        "✅ Permission Auto-Sync (new!)",
        "✅ Auto-Registration Discord Users (new!)",
        "✅ Real-time Data Sync",
        "✅ Cloud Backup & Archive",
    ],
    "improvements": [
        "🔄 Permission sync every 5 seconds",
        "👥 Auto-create users from Discord",
        "🔧 Improved error handling",
        "📊 Better logging & debugging",
    ],
    "exe": {
        "path": str(exe_path),
        "size_mb": f"{exe_size:.1f}",
    },
    "requirements": {
        "os": "Windows 7+",
        "python": "Bundled (no install needed)",
        "ram": "512 MB minimum",
        "disk": "200 MB free",
    }
}

import json
manifest_file = OUTPUT_DIR / "MANIFEST.json"
with open(manifest_file, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"✅ Manifest created: {manifest_file}")

# ============================================================================
# ✅ BUILD COMPLET
# ============================================================================

print("\n" + "=" * 80)
print("✅ BUILD COMPLET!")
print("=" * 80)

print(f"\n📦 Installer EXE ready at:")
print(f"   {exe_path}")
print(f"\n📦 Size: {exe_size:.1f} MB")
print(f"\n📋 Features included:")
for feature in manifest["features"]:
    print(f"   {feature}")

print(f"\n🚀 NEXT STEPS:")
print(f"   1. Copy PunctajManager.exe to distribution folder")
print(f"   2. Share with users")
print(f"   3. Users can run directly (no install needed)")
print(f"\n📞 Support:")
print(f"   For issues, check: PERMISSION_SYNC_FIX.md & AUTO_REGISTRATION_DISCORD.md")

print("\n" + "=" * 80)
print("Done! ✨")
print("=" * 80)
