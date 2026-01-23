"""
Setup pentru PyInstaller - Convertește aplicația Python în EXE
"""
import sys
import os
import PyInstaller.__main__

def build_exe():
    """Build-ează aplicația ca single EXE file"""
    
    print("=" * 60)
    print("🔨 Construiesc Punctaj Manager EXE...")
    print("=" * 60)
    
    # Parametri PyInstaller
    args = [
        'punctaj.py',
        '--name=PunctajManager',
        '--onefile',  # Single EXE file
        '--windowed',  # Fără console window
        '--icon=icon.ico' if os.path.exists('icon.ico') else '',  # Icon (opțional)
        '--add-data=data:data',  # Include data folder
        '--add-data=arhiva:arhiva',  # Include archive folder
        '--distpath=dist',
        '--workpath=build',  # Schimbat din --buildpath
        '--specpath=.',
        '--python-option=u',
    ]
    
    # Elimină string-uri goale
    args = [arg for arg in args if arg]
    
    print(f"\n📦 PyInstaller options: {' '.join(args)}\n")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        print("\n📁 Executable locație: dist/PunctajManager.exe")
        print("🚀 Poți rula aplicația direct din dist folder!\n")
    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}\n")
        return False
    
    return True


if __name__ == "__main__":
    build_exe()
