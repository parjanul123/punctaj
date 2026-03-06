# -*- coding: utf-8 -*-
"""
🔨 Build Punctaj Update Executable
Construiește aplicația Punctaj Update ca exe standalone
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configurare
SCRIPT_NAME = "punctaj_update.py"
EXE_NAME = "Punctaj_Update"
OUTPUT_DIR = "dist"  # Folosește directorul dist standard

def clean_previous_builds():
    """Șterge build-urile anterioare"""
    print("🧹 Curățând build-urile anterioare...")
    
    dirs_to_clean = ["build_punctaj", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"   ✓ Șters: {dir_name}/")
            except Exception as e:
                print(f"   ⚠️ Nu pot șterge {dir_name}: {e}")
    
    # Șterge doar exe-ul vechi din dist, nu tot directorul
    old_exe = os.path.join(OUTPUT_DIR, f"{EXE_NAME}.exe")
    if os.path.exists(old_exe):
        try:
            os.remove(old_exe)
            print(f"   ✓ Șters exe vechi: {EXE_NAME}.exe")
        except Exception as e:
            print(f"   ⚠️ Nu pot șterge exe-ul vechi: {e}")

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
    
    # Verifică dacă icon.ico există
    icon_data = ""
    icon_param = ""
    if os.path.exists("icon.ico"):
        icon_data = "('icon.ico', '.'),"
        icon_param = "icon='icon.ico',"
        print("   ✓ Icon găsit - va fi inclus")
    else:
        print("   ℹ️ Icon nu găsit - continuă fără icon")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{SCRIPT_NAME}'],
    pathex=[],
    binaries=[],
    datas=[
        {icon_data}
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk', 
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'subprocess',
        'threading',
        'json',
        'configparser',
        'requests',
        'pathlib'
    ],
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
    {icon_param}
    version_info=None,
    onefile=True,    # Creează un singur exe
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
        "--workpath", "build_punctaj", 
        "--clean",
        "--noconfirm",
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
    print("📁 Verificând dependențele...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"   ✓ Creat directorul: {OUTPUT_DIR}")
    
    # Verifică că exe-ul există
    exe_path = os.path.join(OUTPUT_DIR, f"{EXE_NAME}.exe")
    if os.path.exists(exe_path):
        print(f"   ✓ Exe găsit: {EXE_NAME}.exe")
    else:
        print(f"   ⚠️ Exe nu găsit: {EXE_NAME}.exe")

def create_readme():
    """Creează README pentru punctaj_update în directorul dist"""
    readme_content = """# 🛡️ Punctaj Update

Aplicație specializată pentru actualizarea sistemului de management polițist Punctaj.

## 🚀 Funcții Principale

### 🔍 Verifică Actualizări
- Conectează la repository git
- Verifică commit-uri noi disponibile
- Afișează lista modificărilor

### ⬇️ Actualizează Punctaj  
- Backup automat configurații
- Git stash pentru modificări locale
- Git pull cu ultimele modificări
- Re-aplică modificări locale
- Verifică integritatea după update

### 💾 Backup Config
- Salvează fișiere importante: supabase_config.ini, users_permissions.json, discord_config.json
- Timestamp pentru organizare
- Locație: backup_configs/

### 🔄 Restart Punctaj
- Detectează automat aplicația principală  
- Pornește Punctaj.exe sau punctaj.py
- Închide updater-ul după restart

## 📊 Interfață

- **Design specializat** cu tema roșu-polițească
- **Status în timp real** pentru git, aplicație și config
- **Progres vizual** cu bara de progres  
- **Jurnal detaliat** cu color-coding pentru nivele
- **Butoane intuitive** cu icons și colors

## 🛡️ Siguranță

- Backup automat înainte de actualizare
- Git stash pentru modificări necommit-ate  
- Verificări de integritate
- Confirmări utilizator pentru operații critice
- Timeout pentru comenzi git (2 minute)

## ⚙️ Utilizare

1. **Dublu-click** pe Punctaj_Update.exe
2. **Verifică** statusul sistemului
3. **Apasă** "Verifică Actualizări" pentru a vedea ce e nou
4. **Apasă** "Actualizează Punctaj" pentru update complet
5. **Restart** aplicația după actualizare

## 🔧 Integrare

- Lansare din aplicația principală cu butonul "🛡️ Punctaj Update"
- Exe standalone în folderul dist/
- Compatibil cu toate versiunile Punctaj

---

**Versiune:** 2.0.0  
**Aplicație pentru:** Sistem Punctaj - Management Polițist  
**Build cu:** PyInstaller + Python 3.x
"""
    
    readme_path = os.path.join(OUTPUT_DIR, "Punctaj_Update_README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✓ Creat Punctaj_Update_README.md în dist/")

def create_batch_launcher():
    """Creează un batch file pentru lansare rapidă"""
    batch_content = f'''@echo off
echo ==========================================
echo    🛡️ PUNCTAJ UPDATE LAUNCHER
echo ==========================================
echo.
echo 🔄 Lansând Punctaj Update...
cd /d "%~dp0"
"{EXE_NAME}.exe"
echo.
echo 📝 Punctaj Update s-a închis.
pause
'''
    
    batch_path = os.path.join(OUTPUT_DIR, "Launch_Punctaj_Update.bat")
    with open(batch_path, "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("✓ Creat Launch_Punctaj_Update.bat în dist/")

def main():
    """Main function"""
    print("=" * 60)
    print(f"🛡️ BUILD PUNCTAJ UPDATE EXE")
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
    
    # Creează documentația
    create_readme()
    
    # Creează batch launcher
    create_batch_launcher()
    
    # Finalizare
    exe_path = os.path.join(OUTPUT_DIR, f"{EXE_NAME}.exe") 
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n✅ BUILD COMPLETAT CU SUCCES!")
        print(f"📄 Exe: {exe_path}")
        print(f"📦 Mărime: {file_size:.1f} MB")
        print(f"📁 Output: {OUTPUT_DIR}/")
        print(f"🚀 Lansare: dist/Launch_Punctaj_Update.bat")
        print(f"📋 Docs: dist/Punctaj_Update_README.md")
        
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
        print("🎉 Punctaj Update gata pentru distribuire!")
        print(f"▶️  Rulează: dist/{EXE_NAME}.exe")
        print(f"🚀 SAU: dist/Launch_Punctaj_Update.bat")
        print(f"📋 Documentație: dist/Punctaj_Update_README.md")
    else:
        print("💥 Build eșuat - verifică erorile de mai sus")
    print("=" * 60)
    
    input("\nApasă ENTER pentru ieșire...")