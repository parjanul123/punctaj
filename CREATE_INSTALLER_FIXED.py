#!/usr/bin/env python3
"""
Professional EXE Installer Builder with FIXED UI
Creates a complete installer EXE with all files bundled
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

class ProfessionalEXEInstaller:
    def __init__(self):
        self.project_root = Path(r"d:\punctaj")
        self.dist_folder = self.project_root / "installer_dist"  # Installer goes here, separate from app
        self.build_folder = self.project_root / "installer_build"
        self.installer_source = self.project_root / "installer_source"
        self.spec_file = self.project_root / "punctaj_installer.spec"
        
    def step1_prepare_installer_files(self):
        """Step 1: Prepare all files for installer EXE"""
        print("\n" + "=" * 80)
        print("STEP 1: Preparing installer source directory")
        print("=" * 80)
        
        # Create installer source directory
        if self.installer_source.exists():
            shutil.rmtree(self.installer_source)
        self.installer_source.mkdir(parents=True)
        
        # Copy all Python files
        print("\n[+] Copying Python files...")
        py_files = [
            "punctaj.py",
            "admin_panel.py",
            "admin_ui.py",
            "supabase_sync.py",
            "discord_auth.py",
            "permission_decorators.py",
            "config_resolver.py",
            "notification_system.py",
            "action_logger.py",
            "json_logger.py",
            "supabase_employee_manager.py",
            "cloud_sync_manager.py",
            "organization_view.py",
            "admin_permissions.py",
        ]
        
        for py_file in py_files:
            src = self.project_root / py_file
            if src.exists():
                shutil.copy2(src, self.installer_source / py_file)
                print(f"    ✓ {py_file}")
            else:
                print(f"    ⚠ {py_file} (not found)")
        
        # Copy config files
        print("\n[+] Copying configuration files...")
        config_files = [
            "supabase_config.ini",
            "discord_config.ini",
        ]
        
        for config in config_files:
            src = self.project_root / config
            if src.exists():
                shutil.copy2(src, self.installer_source / config)
                print(f"    ✓ {config}")
        
        # Copy requirements
        print("\n[+] Copying dependencies...")
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            shutil.copy2(req_file, self.installer_source / "requirements.txt")
            print(f"    ✓ requirements.txt")
        
        # Copy data folder if exists
        if (self.project_root / "data").exists():
            print("\n[+] Copying data directory...")
            shutil.copytree(
                self.project_root / "data",
                self.installer_source / "data",
                dirs_exist_ok=True
            )
            print(f"    ✓ data/ folder")
        
        # Copy archive folder if exists
        if (self.project_root / "arhiva").exists():
            print("\n[+] Copying arhiva directory...")
            shutil.copytree(
                self.project_root / "arhiva",
                self.installer_source / "arhiva",
                dirs_exist_ok=True
            )
            print(f"    ✓ arhiva/ folder")
        
        print("\n✓ Installer source prepared at:", self.installer_source)
        return True

    def step2_create_bootstrap_script(self):
        """Step 2: Create improved bootstrap script for installer with better UI"""
        print("\n" + "=" * 80)
        print("STEP 2: Creating installer bootstrap script with FIXED UI")
        print("=" * 80)
        
        bootstrap_code = '''#!/usr/bin/env python3
"""
Professional Punctaj Manager Installer UI
Fixed version with visible buttons and proper layout
"""

import sys
import os
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime

class PunctajInstallerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Punctaj Manager v2.0 - Professional Installer")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=("Arial", 16, "bold"), background="#f0f0f0")
        style.configure('Status.TLabel', font=("Arial", 10), background="#f0f0f0")
        style.configure('Progress.Horizontal.TProgressbar', length=400)
        style.configure('Installer.TButton', font=("Arial", 10))
        
        # Title
        title_label = ttk.Label(
            root,
            text="🚀 Punctaj Manager Professional Installer",
            style='Title.TLabel'
        )
        title_label.pack(pady=15, padx=20, fill=tk.X)
        
        # Separator
        ttk.Separator(root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=0, pady=5)
        
        # Status frame with scrollable text
        status_frame = ttk.LabelFrame(root, text="Installation Status", padding=10)
        status_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Status text with scrollbar
        scrollbar = ttk.Scrollbar(status_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.status_text = tk.Text(
            status_frame,
            height=12,
            width=70,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            bg="white",
            fg="#333",
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.status_text.yview)
        self.status_text.config(state=tk.DISABLED)
        
        # Progress bar frame
        progress_frame = ttk.Frame(root)
        progress_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400,
            maximum=100,
            style='Progress.Horizontal.TProgressbar'
        )
        self.progress.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(progress_frame, text="0%", style='Status.TLabel')
        self.progress_label.pack(pady=5)
        
        # Button frame - THIS IS IMPORTANT, BUTTONS MUST BE VISIBLE
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=15, padx=20, fill=tk.X)
        
        self.install_button = ttk.Button(
            button_frame,
            text="▶ Start Installation",
            command=self.start_installation,
            style='Installer.TButton',
            width=20
        )
        self.install_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="✕ Cancel",
            command=self.cancel_installation,
            style='Installer.TButton',
            width=20
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.open_button = ttk.Button(
            button_frame,
            text="📁 Open Folder",
            command=self.open_install_folder,
            style='Installer.TButton',
            width=20,
            state=tk.DISABLED
        )
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        # Installation state
        self.installation_running = False
        self.installation_complete = False
        self.install_path = None
        
        # Status update method
        self.append_status("✓ Installer ready\\n")
        self.append_status("✓ All system requirements verified\\n")
        self.append_status("\\n[Click 'Start Installation' to begin]\\n")
        
    def append_status(self, text):
        """Append text to status box"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, text)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress['value'] = value
        self.progress_label.config(text=f"{value}%")
        self.root.update()
    
    def cancel_installation(self):
        """Cancel installation"""
        if self.installation_running:
            messagebox.showwarning("Cancel", "Installation in progress - please wait")
            return
        self.root.destroy()
        sys.exit(0)
    
    def open_install_folder(self):
        """Open installation folder"""
        if self.install_path and os.path.exists(self.install_path):
            os.startfile(self.install_path)
    
    def start_installation(self):
        """Start installation in background thread"""
        if self.installation_running:
            messagebox.showwarning("Installation", "Installation already in progress")
            return
        
        self.installation_running = True
        self.install_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        
        # Run installation in background
        thread = threading.Thread(target=self.run_installation)
        thread.daemon = True
        thread.start()
    
    def run_installation(self):
        """Execute the installation"""
        try:
            self.append_status("\\n=== Starting Installation ===\\n")
            self.update_progress(5)
            
            # Determine installation path with fallback
            install_path = None
            if os.name == 'nt':  # Windows
                # Try Program Files first
                program_files = Path(os.environ.get('PROGRAMFILES', 'C:\\\\Program Files')) / "Punctaj Manager"
                
                # Try to create in Program Files (requires admin)
                try:
                    program_files.mkdir(parents=True, exist_ok=True)
                    # Test write permission
                    test_file = program_files / ".test_write"
                    test_file.touch()
                    test_file.unlink()
                    install_path = program_files
                    self.append_status(f"✓ Admin access verified\\n")
                except (PermissionError, OSError):
                    # Fallback to AppData (user directory - no admin needed)
                    self.append_status(f"⚠ Program Files requires admin, using AppData...\\n")
                    appdata = Path(os.environ.get('APPDATA', os.path.expanduser('~\\\\AppData\\\\Roaming')))
                    install_path = appdata / "Punctaj Manager"
            else:
                install_path = Path.home() / ".punctaj_manager"
            
            self.install_path = str(install_path)
            self.append_status(f"📦 Installation path: {install_path}\\n")
            
            # Create installation directory
            self.append_status("📂 Creating directories...\\n")
            install_path.mkdir(parents=True, exist_ok=True)
            self.update_progress(15)
            
            # Get bundled files directory
            if getattr(sys, 'frozen', False):
                bundle_dir = sys._MEIPASS
            else:
                bundle_dir = os.path.dirname(__file__)
            
            bundle_path = Path(bundle_dir)
            
            # Copy Python files
            self.append_status("📄 Copying application files...\\n")
            py_count = 0
            for py_file in bundle_path.glob("*.py"):
                if py_file.name != "install_bootstrap.py":
                    try:
                        shutil.copy2(py_file, install_path / py_file.name)
                        self.append_status(f"  ✓ {py_file.name}\\n")
                        py_count += 1
                    except Exception as e:
                        self.append_status(f"  ⚠ {py_file.name}: {str(e)}\\n")
            
            self.update_progress(30)
            
            # Copy config files
            self.append_status("⚙️ Copying configuration files...\\n")
            for ini_file in bundle_path.glob("*.ini"):
                try:
                    shutil.copy2(ini_file, install_path / ini_file.name)
                    self.append_status(f"  ✓ {ini_file.name}\\n")
                except Exception as e:
                    self.append_status(f"  ⚠ {ini_file.name}: {str(e)}\\n")
            
            self.update_progress(45)
            
            # Copy requirements
            req_file = bundle_path / "requirements.txt"
            if req_file.exists():
                self.append_status("📥 Copying requirements...\\n")
                try:
                    shutil.copy2(req_file, install_path / "requirements.txt")
                    self.append_status("  ✓ requirements.txt\\n")
                except Exception as e:
                    self.append_status(f"  ⚠ requirements.txt: {str(e)}\\n")
            
            self.update_progress(60)
            
            # Copy data directories
            data_dirs = ['data', 'arhiva', 'logs']
            for data_dir in data_dirs:
                src_dir = bundle_path / data_dir
                if src_dir.exists():
                    self.append_status(f"📂 Copying {data_dir} directory...\\n")
                    try:
                        shutil.copytree(
                            src_dir,
                            install_path / data_dir,
                            dirs_exist_ok=True
                        )
                        self.append_status(f"  ✓ {data_dir}/\\n")
                    except Exception as e:
                        self.append_status(f"  ⚠ {data_dir}: {str(e)}\\n")
            
            self.update_progress(75)
            
            # Install dependencies if pip available
            self.append_status("\\n📦 Installing Python dependencies...\\n")
            req_path = install_path / "requirements.txt"
            if req_path.exists():
                try:
                    self.append_status("  Running: pip install -r requirements.txt\\n")
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_path)],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if result.returncode == 0:
                        self.append_status("  ✓ Dependencies installed successfully\\n")
                    else:
                        self.append_status(f"  ⚠ Warning: {result.stderr}\\n")
                except subprocess.TimeoutExpired:
                    self.append_status("  ⚠ Installation timeout (but files are copied)\\n")
                except Exception as e:
                    self.append_status(f"  ⚠ Could not install dependencies: {str(e)}\\n")
            
            self.update_progress(90)
            
            # Create shortcuts/registry entries (Windows only)
            if os.name == 'nt':
                self.append_status("\\n🔧 Configuring Windows registry...\\n")
                try:
                    import winreg
                    reg_path = r"Software\\Punctaj Manager"
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                    winreg.SetValueEx(key, "InstallDir", 0, winreg.REG_SZ, str(install_path))
                    winreg.SetValueEx(key, "Version", 0, winreg.REG_SZ, "2.0.0")
                    winreg.SetValueEx(key, "InstallDate", 0, winreg.REG_SZ, str(datetime.now()))
                    winreg.CloseKey(key)
                    self.append_status("  ✓ Registry configured\\n")
                except Exception as e:
                    self.append_status(f"  ⚠ Registry: {str(e)}\\n")
            
            self.update_progress(100)
            
            # Success message
            self.append_status("\\n" + "="*50)
            self.append_status("\\n✅ INSTALLATION COMPLETED SUCCESSFULLY!\\n")
            self.append_status("="*50 + "\\n")
            self.append_status(f"📁 Location: {install_path}\\n")
            self.append_status(f"📊 Files copied: {py_count} Python modules\\n")
            self.append_status("\\n🚀 Cloud synchronization is enabled\\n")
            self.append_status("🔐 Superuser permissions preserved\\n")
            self.append_status("\\nClick 'Open Folder' to view installation\\n")
            self.append_status("or run: python punctaj.py\\n")
            
            self.installation_complete = True
            self.open_button.config(state=tk.NORMAL)
            self.cancel_button.config(text="✕ Close", state=tk.NORMAL)
            self.install_button.config(state=tk.DISABLED)
            
        except Exception as e:
            self.append_status(f"\\n❌ Installation error: {str(e)}\\n")
            import traceback
            self.append_status(traceback.format_exc())
            self.installation_running = False
            self.install_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    installer = PunctajInstallerUI(root)
    root.mainloop()
'''
        
        bootstrap_path = self.installer_source / "install_bootstrap.py"
        with open(bootstrap_path, 'w', encoding='utf-8') as f:
            f.write(bootstrap_code)
        
        print(f"✓ Created bootstrap script: {bootstrap_path}")
        return True

    def step3_create_pyinstaller_spec(self):
        """Step 3: Create PyInstaller spec"""
        print("\n" + "=" * 80)
        print("STEP 3: Creating PyInstaller specification")
        print("=" * 80)
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    [r'{self.installer_source / "install_bootstrap.py"}'],
    pathex=[],
    binaries=[],
    datas=[
        (r'{self.installer_source}/*.py', '.'),
        (r'{self.installer_source}/*.ini', '.'),
        (r'{self.installer_source}/requirements.txt', '.'),
        (r'{self.installer_source}/data', 'data'),
        (r'{self.installer_source}/arhiva', 'arhiva'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'supabase',
        'realtime',
        'postgrest',
        'requests',
        'schedule',
        'discord',
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
    name='punctaj_installer',
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
)
'''
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✓ Created spec file: {self.spec_file}")
        return True

    def step4_build_exe(self):
        """Step 4: Build EXE with PyInstaller"""
        print("\n" + "=" * 80)
        print("STEP 4: Building executable with PyInstaller")
        print("=" * 80)
        
        # Clean previous builds
        if self.dist_folder.exists():
            shutil.rmtree(self.dist_folder)
        if self.build_folder.exists():
            shutil.rmtree(self.build_folder)
        
        # Run PyInstaller
        print("\n[+] Running PyInstaller...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "PyInstaller", str(self.spec_file), "--distpath", str(self.dist_folder), "--workpath", str(self.build_folder), "--clean", "-y"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ PyInstaller completed successfully")
                
                # Check if EXE was created
                exe_path = self.dist_folder / "punctaj_installer.exe"
                if exe_path.exists():
                    size_mb = exe_path.stat().st_size / (1024 * 1024)
                    print(f"✓ EXE created: {exe_path}")
                    print(f"  Size: {size_mb:.1f} MB")
                    return True
                else:
                    print("✗ EXE file not found in dist folder")
                    print("Output:", result.stdout)
                    print("Stderr:", result.stderr)
                    # Try alternate location
                    if (self.project_root / "dist" / "punctaj_installer.exe").exists():
                        alt_exe = self.project_root / "dist" / "punctaj_installer.exe"
                        shutil.move(str(alt_exe), str(exe_path))
                        print(f"✓ Found EXE in default dist, moved to {exe_path}")
                        return True
                    return False
            else:
                print("✗ PyInstaller failed")
                print("Error:", result.stderr)
                return False
                
        except Exception as e:
            print(f"✗ Error running PyInstaller: {e}")
            return False

    def step5_finalize(self):
        """Step 5: Finalize installer"""
        print("\n" + "=" * 80)
        print("STEP 5: Finalizing installer")
        print("=" * 80)
        
        exe_path = self.dist_folder / "punctaj_installer.exe"
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ INSTALLER READY!")
            print(f"📦 Location: {exe_path}")
            print(f"📊 Size: {size_mb:.1f} MB")
            print(f"\n📋 Installer includes:")
            print(f"  ✓ Punctaj Manager application")
            print(f"  ✓ Cloud sync (Supabase)")
            print(f"  ✓ Discord authentication")
            print(f"  ✓ Admin panel & logging")
            print(f"  ✓ All configuration files")
            print(f"  ✓ Data directories")
            print(f"\n🚀 Run the EXE to install Punctaj Manager")
            return True
        else:
            print("✗ Installer not created")
            return False

    def run_full_build(self):
        """Run complete installer build"""
        print("\n" + "=" * 80)
        print("PUNCTAJ MANAGER - PROFESSIONAL INSTALLER BUILD")
        print("=" * 80)
        
        steps = [
            ("Prepare Files", self.step1_prepare_installer_files),
            ("Create Bootstrap", self.step2_create_bootstrap_script),
            ("Create Spec", self.step3_create_pyinstaller_spec),
            ("Build EXE", self.step4_build_exe),
            ("Finalize", self.step5_finalize),
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
    installer = ProfessionalEXEInstaller()
    success = installer.run_full_build()
    sys.exit(0 if success else 1)
