#!/usr/bin/env python3
"""
Build script pentru Git Clone Downloader
Generează executabile în directorul dist/
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def check_pyinstaller():
    """Verifică dacă PyInstaller este instalat"""
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_pyinstaller():
    """Instalează PyInstaller"""
    print("Instalez PyInstaller...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                      check=True)
        print("✅ PyInstaller instalat cu succes!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Eroare la instalarea PyInstaller: {e}")
        return False

def build_executable():
    """Construiește executabilul folosind PyInstaller"""
    
    # Verifică dacă scriptul existe
    source_script = Path("git_clone_downloader.py")
    if not source_script.exists():
        print(f"❌ Scriptul {source_script} nu a fost găsit!")
        return False
    
    # Creează directorul dist dacă nu există
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    print("🔧 Construiesc executabilul...")
    
    # Comandă PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                           # Un singur fișier executabil
        '--windowed',                          # Fără consolă (GUI only)
        '--name', 'PunctajDownloader',         # Numele executabilului
        '--distpath', str(dist_dir),          # Directorul de destinație
        '--workpath', 'build_temp',           # Directorul temporar
        '--specpath', 'build_temp',           # Unde să pună fișierul .spec
        '--clean',                            # Curăță cache-ul anterior
        '--noconfirm',                        # Nu cere confirmare pentru suprascrierea
        str(source_script)
    ]
    
    try:
        # Rulează PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            executable_path = dist_dir / "PunctajDownloader.exe"
            if executable_path.exists():
                print(f"✅ Executabil creat cu succes: {executable_path}")
                print(f"📁 Mărime fișier: {executable_path.stat().st_size / (1024*1024):.1f} MB")
                
                # Curăță fișierele temporare
                cleanup_temp_files()
                
                return True
            else:
                print("❌ Executabilul nu a fost găsit după construire!")
                return False
        else:
            print("❌ Eroare la construirea executabilului:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Eroare neașteptată: {e}")
        return False

def cleanup_temp_files():
    """Curăță fișierele temporare"""
    temp_dirs = ['build_temp', 'build', '__pycache__']
    
    for temp_dir in temp_dirs:
        temp_path = Path(temp_dir)
        if temp_path.exists():
            try:
                shutil.rmtree(temp_path)
                print(f"🗑️ Șters directorul temporar: {temp_dir}")
            except Exception as e:
                print(f"⚠️ Nu am putut șterge {temp_dir}: {e}")

def create_readme():
    """Creează un fișier README pentru utilizarea executabilului"""
    readme_content = """# Punctaj Project Downloader

## Descriere
Acest executabil permite descărcarea proiectului Punctaj de pe GitHub într-o locație selectată de utilizator.

## Utilizare
1. Rulează `PunctajDownloader.exe`
2. Selectează un folder unde vrei să descarci proiectul
3. Apasă butonul "Descarcă Proiect"
4. Așteaptă ca descărcarea să se termine

## Cerințe
- Windows 10/11
- Conexiune la internet
- Git instalat pe sistem (https://git-scm.com/download/win)

## Caracteristici
- Interfață grafică intuitivă
- Verificare automată pentru Git
- Progres în timp real
- Gestionare erori
- Deschidere automată folder după descărcare

## Repository
Proiectul se descarcă de la: https://github.com/parjanul123/punctaj.git

## Suport
Pentru probleme sau întrebări, contactează dezvoltatorul.
"""
    
    readme_path = Path("dist") / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📄 Creat fișier README: {readme_path}")

def main():
    """Funcția principală de build"""
    print("🚀 Punctaj Project - Build Git Clone Downloader")
    print("=" * 50)
    
    # Verifică și instalează PyInstaller dacă este nevoie
    if not check_pyinstaller():
        print("PyInstaller nu este instalat.")
        if not install_pyinstaller():
            print("❌ Nu am putut instala PyInstaller. Ieșire...")
            sys.exit(1)
    else:
        print("✅ PyInstaller este disponibil")
    
    # Construiește executabilul
    if build_executable():
        create_readme()
        print("\n✅ Build complet!")
        print(f"📁 Executabilul se află în: {Path('dist').absolute()}")
        print("\n📋 Instrucțiuni:")
        print("1. Navighează la folderul 'dist'")
        print("2. Rulează 'PunctajDownloader.exe'")
        print("3. Urmează instrucțiunile din aplicație")
    else:
        print("\n❌ Build eșuat!")
        sys.exit(1)

if __name__ == "__main__":
    main()