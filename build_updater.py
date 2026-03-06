# -*- coding: utf-8 -*-
"""
🔨 Build Git Updater Executable
Construiește aplicația Git Updater ca exe standalone
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configurare
SCRIPT_NAME = "git_updater.py"
EXE_NAME = "Git_Updater"
OUTPUT_DIR = "dist_updater"

def clean_previous_builds():
    """Șterge build-urile anterioare"""
    print("🧹 Curățând build-urile anterioare...")
    
    dirs_to_clean = ["build", OUTPUT_DIR, "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"   ✓ Șters: {dir_name}/")
            except Exception as e:
                print(f"   ⚠️ Nu pot șterge {dir_name}: {e}")

def check_pyinstaller():
    """Verifică dacă PyInstaller este instalat"""
    try:
        result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ PyInstaller găsit: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ PyInstaller nu este instalat")
    print("💡 Instalează cu: pip install pyinstaller")
    return False

def create_spec_file():
    """Creează fișierul spec pentru PyInstaller"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{SCRIPT_NAME}'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),  # Include icon dacă există
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{EXE_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Icon pentru exe
)
'''
    
    spec_file = f"{EXE_NAME}.spec"
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print(f"✓ Creat {spec_file}")
    return spec_file

def build_exe():
    """Construiește exe-ul cu PyInstaller"""
    print(f"🔨 Construind {EXE_NAME}.exe...")
    
    # Creează spec file
    spec_file = create_spec_file()
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--distpath", OUTPUT_DIR,
        "--workpath", "build_updater", 
        "--clean",
        spec_file
    ]
    
    print(f"🚀 Rulând: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completat cu succes!")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Eroare la build:")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def copy_dependencies():
    """Copiază fișierele necesare în directorul de output"""
    print("📁 Copiez dependențele...")
    
    exe_dir = Path(OUTPUT_DIR) / EXE_NAME
    if not exe_dir.exists():
        print(f"❌ Directorul exe nu există: {exe_dir}")
        return
    
    # Fișiere de copiat
    files_to_copy = [
        "icon.ico",
        "README.md"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            try:
                shutil.copy2(file_name, exe_dir)
                print(f"   ✓ Copiat: {file_name}")
            except Exception as e:
                print(f"   ⚠️ Eroare la copierea {file_name}: {e}")

def create_readme():
    """Creează README pentru updater"""
    readme_content = """# 🔄 Git Updater

Aplicație pentru actualizarea automată a proiectului din git.

## 🚀 Utilizare

1. **Verifică Modificări**: Verifică dacă sunt actualizări disponibile
2. **Actualizează**: Descarcă ultimele modificări cu git pull  
3. **Restart**: Restartează aplicația principală după actualizare

## ⌨️ Funcții

- ✅ Verificare status git
- ✅ Backup automat config files
- ✅ Git stash pentru modificări locale
- ✅ Progress în timp real
- ✅ Log detaliat
- ✅ Restart aplicație principală

## 📋 Cerințe

- Git instalat și configurat
- Repository git valid
- Conexiune la internet

## 🛠️ Tehnologii

- Python 3.x
- Tkinter (GUI)
- Git (version control)
- PyInstaller (exe build)

---
Generat automat cu build_updater.py
"""
    
    readme_path = Path(OUTPUT_DIR) / EXE_NAME / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✓ Creat README.md")

def main():
    """Main function"""
    print("=" * 60)
    print(f"🔨 BUILD GIT UPDATER EXE")
    print("=" * 60)
    
    # Verifică dacă scriptul există
    if not os.path.exists(SCRIPT_NAME):
        print(f"❌ Script nu găsit: {SCRIPT_NAME}")
        return False
    
    # Verifică PyInstaller
    if not check_pyinstaller():
        return False
    
    # Curăță build-urile anterioare
    clean_previous_builds()
    
    # Build exe
    if not build_exe():
        return False
    
    # Copiază dependențele
    copy_dependencies()
    
    # Creează README
    create_readme()
    
    # Finalizare
    exe_path = Path(OUTPUT_DIR) / EXE_NAME / f"{EXE_NAME}.exe"
    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ BUILD COMPLETAT CU SUCCES!")
        print(f"📄 Exe: {exe_path}")
        print(f"📦 Mărime: {file_size:.1f} MB")
        print(f"📁 Output: {OUTPUT_DIR}/{EXE_NAME}/")
        
        # Cleanup spec file
        spec_file = f"{EXE_NAME}.spec"
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"🧹 Șters {spec_file}")
        
        return True
    else:
        print("❌ Exe-ul nu a fost generat corect")
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Git Updater gata pentru distribuire!")
        print(f"▶️  Rulează: {OUTPUT_DIR}/{EXE_NAME}/{EXE_NAME}.exe")
    else:
        print("💥 Build eșuat - verifică erorile de mai sus")
    print("=" * 60)
    
    input("\nApasă ENTER pentru ieșire...")