#!/usr/bin/env python3
"""
Punctaj Application Installer
Creates an installable executable package
This script bundles the application and creates a self-extracting installer
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path

def create_installer():
    """Create installer executable using PyInstaller"""
    
    print("=" * 70)
    print("PUNCTAJ APPLICATION INSTALLER BUILDER")
    print("=" * 70)
    
    # Paths
    project_root = Path(__file__).parent
    app_folder = project_root / "installer_outputs" / "Punctaj"
    installer_script = project_root / "installer_main.py"
    
    # Check if app folder exists
    if not app_folder.exists():
        print(f"ERROR: Application folder not found: {app_folder}")
        return False
    
    print(f"\n✓ Application folder found: {app_folder}")
    print(f"  Files: {len(list(app_folder.glob('**/*')))}")
    
    # Create installer main script
    print("\n[1/3] Creating installer main script...")
    installer_code = '''#!/usr/bin/env python3
"""
Punctaj Application Installer - Main Entry Point
Installs Punctaj application and creates shortcuts
"""

import os
import sys
import shutil
import json
from pathlib import Path
from tkinter import Tk, messagebox, Label, Button, Frame, StringVar, OptionMenu, filedialog
import threading

class PunctajInstaller:
    def __init__(self):
        self.root = Tk()
        self.root.title("Punctaj Application Installer")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        self.install_path = StringVar(value=os.path.expanduser("~\\AppData\\Local\\Punctaj"))
        self.create_ui()
        
    def create_ui(self):
        """Create installer UI"""
        
        # Header
        header = Label(self.root, text="Punctaj Application Installer v1.0", 
                      font=("Arial", 14, "bold"), bg="#007bff", fg="white", pady=15)
        header.pack(fill="x")
        
        # Info
        info = Label(self.root, text="This installer will set up Punctaj on your computer.",
                    font=("Arial", 10), bg="#f0f0f0", wraplength=500, justify="left")
        info.pack(pady=10, padx=20)
        
        # Installation path
        frame = Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=15, padx=20, fill="x")
        
        Label(frame, text="Installation Folder:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w")
        
        path_frame = Frame(frame, bg="#f0f0f0")
        path_frame.pack(fill="x", pady=5)
        
        Label(path_frame, textvariable=self.install_path, font=("Arial", 9), 
              bg="white", relief="sunken", padx=10, pady=8).pack(side="left", fill="x", expand=True)
        Button(path_frame, text="Browse...", command=self.browse_folder, width=12).pack(side="right", padx=5)
        
        # Features
        features = Label(self.root, text=
            "✓ Standalone executable (no Python required)\\n" +
            "✓ Cloud synchronization with Supabase\\n" +
            "✓ Employee punctaj management\\n" +
            "✓ Weekly reports and archives\\n" +
            "✓ Discord integration (optional)",
            font=("Arial", 9), bg="#f0f0f0", justify="left")
        features.pack(pady=10, padx=20, anchor="w")
        
        # Buttons
        button_frame = Frame(self.root, bg="#f0f0f0")
        button_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        Button(button_frame, text="Install", command=self.install, bg="#28a745", fg="white", 
               font=("Arial", 11, "bold"), height=2, width=15).pack(side="left", padx=5)
        Button(button_frame, text="Cancel", command=self.root.quit, bg="#dc3545", fg="white",
               font=("Arial", 11, "bold"), height=2, width=15).pack(side="right", padx=5)
    
    def browse_folder(self):
        """Browse for installation folder"""
        folder = filedialog.askdirectory(title="Select Installation Folder")
        if folder:
            self.install_path.set(folder)
    
    def install(self):
        """Perform installation"""
        install_dir = Path(self.install_path.get())
        
        try:
            self.root.withdraw()
            
            # Create installation directory
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy application files
            messagebox.showinfo("Installing", "Installing Punctaj Application...\\nThis may take a moment.")
            
            # Get bundled app directory (from PyInstaller temp folder)
            if getattr(sys, 'frozen', False):
                bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
                app_source = os.path.join(bundle_dir, "_punctaj_app")
                
                if os.path.exists(app_source):
                    # Copy application folder
                    for item in os.listdir(app_source):
                        src = os.path.join(app_source, item)
                        dst = os.path.join(install_dir, item)
                        
                        if os.path.isdir(src):
                            if os.path.exists(dst):
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst)
                        else:
                            shutil.copy2(src, dst)
            
            # Create data folders
            (install_dir / "data").mkdir(exist_ok=True)
            (install_dir / "arhiva").mkdir(exist_ok=True)
            (install_dir / "logs").mkdir(exist_ok=True)
            
            # Create desktop shortcut (Windows)
            if sys.platform == "win32":
                self.create_shortcut(install_dir)
            
            messagebox.showinfo("Success", 
                f"Punctaj has been installed successfully!\\n\\n" +
                f"Location: {install_dir}\\n\\n" +
                "You can now run Punctaj.exe from the installation folder.")
            
        except Exception as e:
            messagebox.showerror("Installation Error", f"Failed to install:\\n{str(e)}")
        
        finally:
            self.root.quit()
    
    def create_shortcut(self, install_dir):
        """Create desktop shortcut for Windows"""
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "Punctaj.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = str(install_dir / "Punctaj.exe")
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.IconLocation = str(install_dir / "Punctaj.exe")
            shortcut.save()
            
        except:
            pass  # Shortcut creation is optional

def main():
    """Main installer entry point"""
    installer = PunctajInstaller()
    installer.root.mainloop()

if __name__ == "__main__":
    main()
'''
    
    with open(installer_script, 'w', encoding='utf-8') as f:
        f.write(installer_code)
    print("✓ Installer script created")
    
    print("\n[2/3] Creating installer spec file...")
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import os
import shutil

a = Analysis(
    ['installer_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('installer_outputs/Punctaj', '_punctaj_app'),
    ],
    hiddenimports=['tkinter', 'win32com'],
    hookspath=[],
    hooksconfig={},
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
    name='Punctaj_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    spec_path = project_root / "installer.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    print("✓ Installer spec file created")
    
    print("\n[3/3] Building installer executable...")
    print("This may take 1-2 minutes...")
    
    os.chdir(project_root)
    result = os.system(f'{sys.executable} -m PyInstaller installer.spec --distpath dist --workpath build -y --onefile')
    
    if result == 0:
        installer_exe = project_root / "dist" / "Punctaj_Installer.exe"
        output_exe = project_root / "installer_outputs" / "Punctaj_Installer.exe"
        
        if installer_exe.exists():
            shutil.copy2(installer_exe, output_exe)
            print(f"\n✓ Installer created successfully!")
            print(f"  Location: {output_exe}")
            print(f"  Size: {output_exe.stat().st_size / 1024 / 1024:.1f} MB")
            return True
    
    print("ERROR: Failed to create installer")
    return False

if __name__ == "__main__":
    success = create_installer()
    sys.exit(0 if success else 1)
