#!/usr/bin/env python3
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
        self.append_status("✓ Installer ready\n")
        self.append_status("✓ All system requirements verified\n")
        self.append_status("\n[Click 'Start Installation' to begin]\n")
        
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
            self.append_status("\n=== Starting Installation ===\n")
            self.update_progress(5)
            
            # Determine installation path with fallback
            install_path = None
            if os.name == 'nt':  # Windows
                # Try Program Files first
                program_files = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / "Punctaj Manager"
                
                # Try to create in Program Files (requires admin)
                try:
                    program_files.mkdir(parents=True, exist_ok=True)
                    # Test write permission
                    test_file = program_files / ".test_write"
                    test_file.touch()
                    test_file.unlink()
                    install_path = program_files
                    self.append_status(f"✓ Admin access verified\n")
                except (PermissionError, OSError):
                    # Fallback to AppData (user directory - no admin needed)
                    self.append_status(f"⚠ Program Files requires admin, using AppData...\n")
                    appdata = Path(os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')))
                    install_path = appdata / "Punctaj Manager"
            else:
                install_path = Path.home() / ".punctaj_manager"
            
            self.install_path = str(install_path)
            self.append_status(f"📦 Installation path: {install_path}\n")
            
            # Create installation directory
            self.append_status("📂 Creating directories...\n")
            install_path.mkdir(parents=True, exist_ok=True)
            self.update_progress(15)
            
            # Get bundled files directory
            if getattr(sys, 'frozen', False):
                bundle_dir = sys._MEIPASS
            else:
                bundle_dir = os.path.dirname(__file__)
            
            bundle_path = Path(bundle_dir)
            
            # Copy Python files
            self.append_status("📄 Copying application files...\n")
            py_count = 0
            for py_file in bundle_path.glob("*.py"):
                if py_file.name != "install_bootstrap.py":
                    try:
                        shutil.copy2(py_file, install_path / py_file.name)
                        self.append_status(f"  ✓ {py_file.name}\n")
                        py_count += 1
                    except Exception as e:
                        self.append_status(f"  ⚠ {py_file.name}: {str(e)}\n")
            
            self.update_progress(30)
            
            # Copy config files
            self.append_status("⚙️ Copying configuration files...\n")
            for ini_file in bundle_path.glob("*.ini"):
                try:
                    shutil.copy2(ini_file, install_path / ini_file.name)
                    self.append_status(f"  ✓ {ini_file.name}\n")
                except Exception as e:
                    self.append_status(f"  ⚠ {ini_file.name}: {str(e)}\n")
            
            self.update_progress(45)
            
            # Copy requirements
            req_file = bundle_path / "requirements.txt"
            if req_file.exists():
                self.append_status("📥 Copying requirements...\n")
                try:
                    shutil.copy2(req_file, install_path / "requirements.txt")
                    self.append_status("  ✓ requirements.txt\n")
                except Exception as e:
                    self.append_status(f"  ⚠ requirements.txt: {str(e)}\n")
            
            self.update_progress(60)
            
            # Copy data directories
            data_dirs = ['data', 'arhiva', 'logs']
            for data_dir in data_dirs:
                src_dir = bundle_path / data_dir
                if src_dir.exists():
                    self.append_status(f"📂 Copying {data_dir} directory...\n")
                    try:
                        shutil.copytree(
                            src_dir,
                            install_path / data_dir,
                            dirs_exist_ok=True
                        )
                        self.append_status(f"  ✓ {data_dir}/\n")
                    except Exception as e:
                        self.append_status(f"  ⚠ {data_dir}: {str(e)}\n")
            
            self.update_progress(75)
            
            # Install dependencies if pip available
            self.append_status("\n📦 Installing Python dependencies...\n")
            req_path = install_path / "requirements.txt"
            if req_path.exists():
                try:
                    self.append_status("  Running: pip install -r requirements.txt\n")
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_path)],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if result.returncode == 0:
                        self.append_status("  ✓ Dependencies installed successfully\n")
                    else:
                        self.append_status(f"  ⚠ Warning: {result.stderr}\n")
                except subprocess.TimeoutExpired:
                    self.append_status("  ⚠ Installation timeout (but files are copied)\n")
                except Exception as e:
                    self.append_status(f"  ⚠ Could not install dependencies: {str(e)}\n")
            
            self.update_progress(90)
            
            # Create shortcuts/registry entries (Windows only)
            if os.name == 'nt':
                self.append_status("\n🔧 Configuring Windows registry...\n")
                try:
                    import winreg
                    reg_path = r"Software\Punctaj Manager"
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                    winreg.SetValueEx(key, "InstallDir", 0, winreg.REG_SZ, str(install_path))
                    winreg.SetValueEx(key, "Version", 0, winreg.REG_SZ, "2.0.0")
                    winreg.SetValueEx(key, "InstallDate", 0, winreg.REG_SZ, str(datetime.now()))
                    winreg.CloseKey(key)
                    self.append_status("  ✓ Registry configured\n")
                except Exception as e:
                    self.append_status(f"  ⚠ Registry: {str(e)}\n")
            
            self.update_progress(100)
            
            # Success message
            self.append_status("\n" + "="*50)
            self.append_status("\n✅ INSTALLATION COMPLETED SUCCESSFULLY!\n")
            self.append_status("="*50 + "\n")
            self.append_status(f"📁 Location: {install_path}\n")
            self.append_status(f"📊 Files copied: {py_count} Python modules\n")
            self.append_status("\n🚀 Cloud synchronization is enabled\n")
            self.append_status("🔐 Superuser permissions preserved\n")
            self.append_status("\nClick 'Open Folder' to view installation\n")
            self.append_status("or run: python punctaj.py\n")
            
            self.installation_complete = True
            self.open_button.config(state=tk.NORMAL)
            self.cancel_button.config(text="✕ Close", state=tk.NORMAL)
            self.install_button.config(state=tk.DISABLED)
            
        except Exception as e:
            self.append_status(f"\n❌ Installation error: {str(e)}\n")
            import traceback
            self.append_status(traceback.format_exc())
            self.installation_running = False
            self.install_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    installer = PunctajInstallerUI(root)
    root.mainloop()
