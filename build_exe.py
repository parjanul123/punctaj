# Python build script for Punctaj Manager
# Creates EXE without PyInstaller dependency

import os
import shutil
import sys

SOURCE_DIR = r"D:\punctaj"
DIST_DIR = r"D:\punctaj\setup_output\dist"
EXE_OUTPUT = os.path.join(DIST_DIR, "exe_output")

print("\n" + "="*60)
print("  PUNCTAJ MANAGER v2.5 - EXE BUILDER")
print("="*60 + "\n")

# Check if source files exist
print("Checking source files...")
required_files = [
    "punctaj.py",
    "admin_permissions.py",
    "discord_auth.py",
    "supabase_sync.py",
    "realtime_sync.py",
    "permission_sync_fix.py",
    "permission_check_helpers.py",
]

for file in required_files:
    path = os.path.join(SOURCE_DIR, file)
    if not os.path.exists(path):
        print(f"❌ MISSING: {file}")
    else:
        print(f"✓ {file}")

print()

# Check for PyInstaller
print("Checking for PyInstaller...")
try:
    import PyInstaller
    print("✓ PyInstaller is installed")
except ImportError:
    print("⚠️  PyInstaller not found, attempting to install...")
    os.system(f"{sys.executable} -m pip install pyinstaller -q")
    try:
        import PyInstaller
        print("✓ PyInstaller installed successfully")
    except:
        print("❌ Failed to install PyInstaller")
        print("\nTry running as Administrator:")
        print(f"  {sys.executable} -m pip install pyinstaller")
        sys.exit(1)

print()
print("Building EXE...")
print()

# Create output directory
os.makedirs(EXE_OUTPUT, exist_ok=True)

# Run PyInstaller
try:
    from PyInstaller.__main__ import run
    
    args = [
        '--onefile',
        '--windowed',
        '--name', 'PunctajManager',
        '--add-data', f'{os.path.join(SOURCE_DIR, "discord_config.ini")};.',
        '--add-data', f'{os.path.join(SOURCE_DIR, "supabase_config.ini")};.',
        '--distpath', EXE_OUTPUT,
        '--workpath', os.path.join(SOURCE_DIR, 'build_temp'),
        '--specpath', os.path.join(SOURCE_DIR, 'build_temp'),
        '--noconfirm',
        '--clean',
        os.path.join(SOURCE_DIR, 'punctaj.py')
    ]
    
    run(args)
    
    exe_path = os.path.join(EXE_OUTPUT, "PunctajManager.exe")
    
    if os.path.exists(exe_path):
        print()
        print("="*60)
        print("  BUILD SUCCESSFUL! ✓")
        print("="*60)
        print()
        print(f"EXE created: {exe_path}")
        print()
        print("File size:", f"{os.path.getsize(exe_path) / (1024*1024):.1f} MB")
        print()
        print("To run:")
        print(f"  Double-click: {exe_path}")
        print()
        print("Configuration files required:")
        print("  - discord_config.ini")
        print("  - supabase_config.ini")
        print()
    else:
        print("❌ Build failed - EXE not created")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Cleanup
print("Cleaning up temporary files...")
build_dir = os.path.join(SOURCE_DIR, 'build_temp')
if os.path.exists(build_dir):
    shutil.rmtree(build_dir, ignore_errors=True)
    print("✓ Cleanup complete")

print()
print("✅ All done!")
