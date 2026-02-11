#!/usr/bin/env python3
"""
Build Punctaj.py as a standalone EXE application
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

class ApplicationBuilder:
    def __init__(self):
        self.project_root = Path(r"d:\punctaj")
        self.dist_folder = self.project_root / "dist"
        self.build_folder = self.project_root / "app_build"
        self.spec_file = self.project_root / "punctaj_app.spec"
        
    def step1_create_spec(self):
        """Create PyInstaller spec for the main application"""
        print("\n" + "=" * 80)
        print("STEP 1: Creating PyInstaller spec for Punctaj Manager Application")
        print("=" * 80)
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    [r'{self.project_root / "punctaj.py"}'],
    pathex=[],
    binaries=[],
    datas=[
        (r'{self.project_root / "data"}', 'data'),
        (r'{self.project_root / "arhiva"}', 'arhiva'),
        (r'{self.project_root / "logs"}', 'logs'),
        (r'{self.project_root / "supabase_config.ini"}', '.'),
        (r'{self.project_root / "discord_config.ini"}', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
        'supabase',
        'supabase.lib.query_options',
        'realtime',
        'postgrest',
        'requests',
        'schedule',
        'discord',
        'json',
        'csv',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='punctaj',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='punctaj'
)
'''
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✓ Created spec file: {self.spec_file}")
        return True

    def step2_build_exe(self):
        """Build EXE with PyInstaller"""
        print("\n" + "=" * 80)
        print("STEP 2: Building Punctaj Manager Application EXE")
        print("=" * 80)
        
        # Clean previous builds
        if self.build_folder.exists():
            shutil.rmtree(self.build_folder)
        
        # Run PyInstaller
        print("\n[+] Running PyInstaller...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "PyInstaller", str(self.spec_file), 
                 "--distpath", str(self.dist_folder), 
                 "--workpath", str(self.build_folder), 
                 "--clean", "-y"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ PyInstaller completed successfully")
                
                # Check if EXE was created
                exe_path = self.dist_folder / "punctaj" / "punctaj.exe"
                if exe_path.exists():
                    size_mb = exe_path.stat().st_size / (1024 * 1024)
                    print(f"✓ EXE created: {exe_path}")
                    print(f"  Size: {size_mb:.1f} MB")
                    return True
                else:
                    print("Checking alternate location...")
                    exe_path = self.dist_folder / "punctaj.exe"
                    if exe_path.exists():
                        size_mb = exe_path.stat().st_size / (1024 * 1024)
                        print(f"✓ EXE created: {exe_path}")
                        print(f"  Size: {size_mb:.1f} MB")
                        return True
                    
                    print("✗ EXE file not found in dist folder")
                    print("Output:", result.stdout[-500:] if result.stdout else "No output")
                    return False
            else:
                print("✗ PyInstaller failed")
                print("Error:", result.stderr[-1000:] if result.stderr else "No error")
                return False
                
        except Exception as e:
            print(f"✗ Error running PyInstaller: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step3_finalize(self):
        """Finalize application"""
        print("\n" + "=" * 80)
        print("STEP 3: Finalizing Application")
        print("=" * 80)
        
        exe_candidates = [
            self.dist_folder / "punctaj" / "punctaj.exe",
            self.dist_folder / "punctaj.exe",
        ]
        
        exe_path = None
        for candidate in exe_candidates:
            if candidate.exists():
                exe_path = candidate
                break
        
        if exe_path and exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ APPLICATION EXE READY!")
            print(f"📦 Location: {exe_path}")
            print(f"📊 Size: {size_mb:.1f} MB")
            print(f"\n📋 Application includes:")
            print(f"  ✓ Punctaj Manager main application")
            print(f"  ✓ Cloud sync (Supabase)")
            print(f"  ✓ Discord authentication")
            print(f"  ✓ Admin panel & logging")
            print(f"  ✓ All configuration files")
            print(f"  ✓ Data directories")
            return True
        else:
            print("✗ Application EXE not found")
            return False

    def run_full_build(self):
        """Run complete build"""
        print("\n" + "=" * 80)
        print("PUNCTAJ MANAGER - BUILD STANDALONE APPLICATION EXE")
        print("=" * 80)
        
        steps = [
            ("Create Spec", self.step1_create_spec),
            ("Build EXE", self.step2_build_exe),
            ("Finalize", self.step3_finalize),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*80}")
            print(f"Running: {step_name}")
            print(f"{'='*80}")
            
            try:
                if not step_func():
                    print(f"\n❌ Failed at step: {step_name}")
                    return False
            except Exception as e:
                print(f"\n❌ Error in {step_name}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("\n" + "=" * 80)
        print("✅ BUILD COMPLETE!")
        print("=" * 80)
        return True


if __name__ == "__main__":
    builder = ApplicationBuilder()
    success = builder.run_full_build()
    sys.exit(0 if success else 1)
