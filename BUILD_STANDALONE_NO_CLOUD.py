#!/usr/bin/env python3
"""
Build standalone distribution (NO CLOUD DB + ALL PERMISSIONS)
- Uses punctaj_standalone_no_cloud.py launcher
- Produces separate dist folder: dist_no_cloud
- Keeps same local data behavior as normal app
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys
import glob


def cleanup():
    """Remove old offline build artifacts"""
    print("[*] Cleaning old offline builds...")
    for dirname in ["dist_no_cloud", "build_no_cloud", "build_spec_no_cloud"]:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
            print(f"  Removed: {dirname}")


def find_all_modules():
    """Find local Python modules that should be bundled"""
    modules = set()
    skip = (
        "BUILD_", "OPTIMIZE_", "VERIFY_", "TEST_", "DEMO_",
        "CREATE_", "REBUILD_", "_", "SETUP_", "SET_", "INSERT_",
        "DIAGNOSE_", "DIAGNOSTIC_", "REPAIR_", "DEBUG_", "CONFIG_FIX"
    )

    for py_file in glob.glob("*.py"):
        basename = os.path.basename(py_file)
        if not any(basename.startswith(s) for s in skip):
            module = basename.replace(".py", "")
            if module != "punctaj_standalone_no_cloud":
                modules.add(module)

    return sorted(modules)


def build_app():
    """Build no-cloud EXE using PyInstaller"""
    print("\n[*] Building standalone no-cloud application...")

    modules = find_all_modules()
    print(f"[*] Found {len(modules)} local modules")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onedir",
        "--console",
        "--distpath=dist_no_cloud",
        "--workpath=build_no_cloud",
        "--specpath=build_spec_no_cloud",
        "--name=Punctaj_NoCloud",
        "--noconfirm",
        "--noupx",
        "--collect-all=tkinter",
        "--collect-all=requests",
        "--collect-all=websockets",
    ]

    if os.path.exists("discord_config.ini"):
        abs_cfg = os.path.abspath("discord_config.ini")
        cmd.append(f"--add-data={abs_cfg}:.")
        print("  Including config: discord_config.ini")

    for mod in modules:
        cmd.append(f"--hidden-import={mod}")

    cmd.append("punctaj_standalone_no_cloud.py")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)

    if result.returncode != 0:
        print("\n[ERROR] PyInstaller failed:")
        print(result.stderr[-1200:])
        return False

    exe_path = "dist_no_cloud/Punctaj_NoCloud/Punctaj_NoCloud.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n[OK] EXE built: {size_mb:.2f} MB")
        return True

    print("[ERROR] EXE not found after build")
    return False


def verify_distribution():
    """Verify expected files in no-cloud distribution"""
    print("\n[*] Verifying no-cloud distribution...")

    dist_dir = "dist_no_cloud/Punctaj_NoCloud"
    required_files = {
        "Punctaj_NoCloud.exe": "Main executable",
        "_internal": "Python runtime libraries",
    }

    if os.path.exists("discord_config.ini"):
        dst = os.path.join(dist_dir, "discord_config.ini")
        if not os.path.exists(dst):
            shutil.copy2("discord_config.ini", dst)
            print("  Copied: discord_config.ini to distribution")

    all_ok = True
    for filename, desc in required_files.items():
        path = os.path.join(dist_dir, filename)
        if os.path.exists(path):
            print(f"  [OK] {desc}: {filename}")
        else:
            print(f"  [ERROR] {desc}: {filename} - NOT FOUND")
            all_ok = False

    return all_ok


def create_zip():
    """Create zip package for no-cloud distribution"""
    print("\n[*] Creating no-cloud distribution package...")

    zip_name = "Punctaj_NoCloud_Distribution.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        dist_dir = "dist_no_cloud/Punctaj_NoCloud"
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                fpath = os.path.join(root, f)
                arcname = os.path.relpath(fpath, "dist_no_cloud")
                zf.write(fpath, arcname)

    size = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"[OK] Package created: {zip_name} ({size:.2f} MB)")
    return zip_name


def main():
    print("=" * 70)
    print("BUILDING STANDALONE PUNCTAJ (NO CLOUD DB)")
    print("=" * 70)

    try:
        cleanup()

        if not build_app():
            return False

        if not verify_distribution():
            print("\n[WARNING] Some files may be missing")

        zip_file = create_zip()

        print("\n" + "=" * 70)
        print("[SUCCESS] STANDALONE NO-CLOUD APPLICATION READY!")
        print("=" * 70)
        print("\nDistribution folder: dist_no_cloud/Punctaj_NoCloud/")
        print(f"Package file: {zip_file}")
        print("\nTo run the application:")
        print("  1. Extract the ZIP file")
        print("  2. Run: .\\Punctaj_NoCloud.exe")
        print("\nCloud DB (Supabase) is disabled in this build.")
        print("All authenticated users are forced to SUPERUSER permissions.")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
