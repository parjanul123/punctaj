#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punctaj Manager v2.0.0 Professional Installer
GUI Installer - No console, just graphical interface with auto-configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import shutil
import subprocess
from pathlib import Path

class PunctajInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Punctaj Manager v2.0.0 Setup")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # Get bundle directory if running as EXE
        if getattr(sys, 'frozen', False):
            self.bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.install_path = Path(os.path.expandvars(r"%ProgramFiles%\Punctaj"))
        self.appdata_path = Path(os.path.expandvars(r"%APPDATA%\Punctaj"))
        self.progress_value = 0
        
        self.setup_ui()
        self.center_window()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Create installer UI"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#0066cc", height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(header_frame, text="Punctaj Manager v2.0.0",
                              font=("Arial", 20, "bold"), bg="#0066cc", fg="white")
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Professional Employee Attendance & Tracking System",
                                 font=("Arial", 10), bg="#0066cc", fg="white")
        subtitle_label.pack(pady=5)
        
        # Main content
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Installation info
        info_label = tk.Label(content_frame, text="Installation Information",
                             font=("Arial", 11, "bold"))
        info_label.pack(anchor=tk.W, pady=(10, 5))
        
        install_info = tk.Frame(content_frame, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
        install_info.pack(fill=tk.X, pady=5)
        
        tk.Label(install_info, text=f"📁 Install: {self.install_path}",
                font=("Arial", 9), bg="#f0f0f0", justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(install_info, text=f"📊 Data: {self.appdata_path}",
                font=("Arial", 9), bg="#f0f0f0", justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)
        
        # Features
        features_label = tk.Label(content_frame, text="Included Features",
                                 font=("Arial", 11, "bold"))
        features_label.pack(anchor=tk.W, pady=(15, 5))
        
        features_frame = tk.Frame(content_frame, bg="#f9f9f9", relief=tk.SUNKEN, bd=1)
        features_frame.pack(fill=tk.X, pady=5)
        
        features = [
            "✓ Discord OAuth2 Authentication (pre-configured)",
            "✓ Cloud Sync with Supabase (pre-configured)",
            "✓ AES-256 Data Encryption",
            "✓ Automatic Backups & Archives",
            "✓ Action Audit Trail & Logging"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=feature, font=("Arial", 9),
                    bg="#f9f9f9", justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=3)
        
        # Progress bar
        self.progress = ttk.Progressbar(content_frame, mode='determinate',
                                       length=400, maximum=100)
        self.progress.pack(pady=15)
        
        # Status text
        self.status_var = tk.StringVar(value="Click 'Install' to begin")
        status_label = tk.Label(content_frame, textvariable=self.status_var,
                               font=("Arial", 9), fg="#666")
        status_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.install_btn = tk.Button(button_frame, text="Install",
                                    command=self.start_installation,
                                    font=("Arial", 13, "bold"),
                                    bg="#28a745", fg="white",
                                    padx=50, pady=15, cursor="hand2")
        self.install_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.BOTH)
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                              command=self.root.quit,
                              font=("Arial", 13),
                              bg="#6c757d", fg="white",
                              padx=50, pady=15, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.BOTH)
        
        # Check admin
        if not self.is_admin():
            messagebox.showerror("Administrator Required",
                               "This installer requires Administrator privileges.\n\n"
                               "Please right-click the installer and select:\n"
                               "'Run as Administrator'")
            self.install_btn.config(state=tk.DISABLED)
    
    def is_admin(self):
        """Check if running as administrator"""
        try:
            import ctypes
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False
    
    def update_progress(self, value, message):
        """Update progress bar"""
        self.progress_value = value
        self.progress['value'] = value
        self.status_var.set(message)
        self.root.update()
    
    def start_installation(self):
        """Start installation process"""
        self.install_btn.config(state=tk.DISABLED)
        
        try:
            # Step 1: Create directories
            self.update_progress(10, "Creating directories...")
            self.create_directories()
            
            # Step 2: Copy executable
            self.update_progress(25, "Installing application...")
            self.copy_executable()
            
            # Step 3: Configure Discord
            self.update_progress(40, "Configuring Discord authentication...")
            self.configure_discord()
            
            # Step 4: Configure Supabase
            self.update_progress(55, "Configuring cloud database...")
            self.configure_supabase()
            
            # Step 5: Copy encryption module
            self.update_progress(70, "Installing security modules...")
            self.copy_encryption_module()
            
            # Step 6: Create shortcuts
            self.update_progress(85, "Creating shortcuts...")
            self.create_shortcuts()
            
            # Step 7: Register
            self.update_progress(95, "Registering application...")
            self.register_windows()
            
            # Complete
            self.update_progress(100, "Installation complete!")
            
            messagebox.showinfo("Installation Successful",
                              "✅ Punctaj Manager has been installed successfully!\n\n"
                              "A shortcut has been created on your desktop.\n\n"
                              "Double-click 'Punctaj Manager' to launch the application.\n\n"
                              "First launch: Discord authentication will appear.")
            
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Installation Error",
                               f"❌ Installation failed:\n\n{str(e)}")
            self.install_btn.config(state=tk.NORMAL)
    
    def create_directories(self):
        """Create installation directories"""
        self.install_path.mkdir(parents=True, exist_ok=True)
        (self.install_path / "data").mkdir(exist_ok=True)
        (self.install_path / "logs").mkdir(exist_ok=True)
        (self.install_path / "arhiva").mkdir(exist_ok=True)
        self.appdata_path.mkdir(parents=True, exist_ok=True)
        
        # Create initial JSON structure for Supabase sync
        self.create_initial_json_files()
    
    def copy_executable(self):
        """Copy main executable"""
        # Try multiple possible names
        possible_names = ["punctaj.exe", "Punctaj_Manager.exe", "Punctaj.exe"]
        source = None
        
        # First try in bundle directory (when running from PyInstaller bundle)
        for name in possible_names:
            path = Path(self.bundle_dir) / name
            if path.exists():
                source = path
                break
        
        # If not found in bundle dir, try current directory
        if not source:
            for name in possible_names:
                path = Path.cwd() / name
                if path.exists():
                    source = path
                    break
        
        if not source:
            raise FileNotFoundError(f"Application executable not found. Expected: {possible_names}")
        
        dest = self.install_path / "Punctaj_Manager.exe"
        shutil.copy2(source, dest)
    
    def configure_discord(self):
        """Configure Discord settings"""
        config_content = """[discord]
CLIENT_ID = 1465698276375527622
CLIENT_SECRET = aM0uvwRSZSIEkzxHG7k01rs_xlF3SW5Q
REDIRECT_URI = http://localhost:8888/callback
WEBHOOK_URL =
"""
        
        config_file = self.install_path / "discord_config.ini"
        config_file.write_text(config_content, encoding='utf-8')
        
        appdata_config = self.appdata_path / "discord_config.ini"
        appdata_config.write_text(config_content, encoding='utf-8')
    
    def configure_supabase(self):
        """Configure Supabase settings"""
        config_content = """[supabase]
url = https://yzlkgifumrwqlfgimcai.supabase.co
key = sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM
table_sync = police_data
table_logs = audit_logs
table_users = users

[sync]
enabled = true
auto_sync = true
sync_interval = 30
conflict_resolution = latest_timestamp
sync_on_startup = true

[permissions]
default_role = superuser
admin_role = superuser
superuser_enabled = true
enforce_hierarchy = true
institution_level = system
"""
        
        config_file = self.install_path / "supabase_config.ini"
        config_file.write_text(config_content, encoding='utf-8')
        
        appdata_config = self.appdata_path / "supabase_config.ini"
        appdata_config.write_text(config_content, encoding='utf-8')
    
    def copy_encryption_module(self):
        """Copy JSON encryptor module"""
        source = Path(self.bundle_dir) / "json_encryptor.py"
        if source.exists():
            dest = self.install_path / "json_encryptor.py"
            shutil.copy2(source, dest)
    
    def create_initial_json_files(self):
        """Create initial JSON structure for Supabase data sync"""
        import json
        
        # Sample cities and institutions
        cities = {
            "Saint_Denis": ["Politie", "Pompieri", "Spital", "Primarie"],
            "BlackWater": ["Politie", "Pompieri", "Gendarmi"],
            "Davis": ["Politie", "Hospital"]
        }
        
        # Create data/{city}/{institution}.json for each city/institution
        data_dir = self.install_path / "data"
        for city, institutions in cities.items():
            city_dir = data_dir / city
            city_dir.mkdir(parents=True, exist_ok=True)
            
            for institution in institutions:
                json_file = city_dir / f"{institution}.json"
                
                # Initial structure matching Supabase schema
                initial_data = {
                    "city": city,
                    "institution": institution,
                    "employees": [],
                    "records": [],
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "updated_by": "system",
                    "version": "2.0.0"
                }
                
                try:
                    json_file.write_text(json.dumps(initial_data, indent=2, ensure_ascii=False), 
                                       encoding='utf-8')
                except:
                    pass
        
        # Create logs/{city}/{institution}.json structure
        logs_dir = self.install_path / "logs"
        for city, institutions in cities.items():
            city_dir = logs_dir / city
            city_dir.mkdir(parents=True, exist_ok=True)
            
            for institution in institutions:
                json_file = city_dir / f"{institution}.json"
                
                initial_logs = {
                    "city": city,
                    "institution": institution,
                    "actions": [],
                    "created_at": "2024-01-01T00:00:00",
                    "version": "2.0.0"
                }
                
                try:
                    json_file.write_text(json.dumps(initial_logs, indent=2, ensure_ascii=False),
                                       encoding='utf-8')
                except:
                    pass
        
        # Create global summary file
        summary_file = logs_dir / "SUMMARY_global.json"
        global_summary = {
            "total_actions": 0,
            "actions_by_type": {},
            "last_updated": "2024-01-01T00:00:00",
            "version": "2.0.0"
        }
        
        try:
            summary_file.write_text(json.dumps(global_summary, indent=2, ensure_ascii=False),
                                  encoding='utf-8')
        except:
            pass
    
    def create_shortcuts(self):
        """Create desktop and Start Menu shortcuts"""
        try:
            ps_cmd = f"""
$WshShell = New-Object -ComObject WScript.Shell

# Desktop shortcut
$DesktopPath = [Environment]::GetFolderPath('Desktop')
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\\Punctaj Manager.lnk")
$Shortcut.TargetPath = '{self.install_path}\\Punctaj_Manager.exe'
$Shortcut.Description = 'Punctaj Manager - Employee Attendance System'
$Shortcut.IconLocation = '{self.install_path}\\Punctaj_Manager.exe,0'
$Shortcut.Save()

# Start Menu shortcut
$StartMenuPath = [Environment]::GetFolderPath('Programs')
$Shortcut = $WshShell.CreateShortcut("$StartMenuPath\\Punctaj Manager.lnk")
$Shortcut.TargetPath = '{self.install_path}\\Punctaj_Manager.exe'
$Shortcut.Description = 'Punctaj Manager - Employee Attendance System'
$Shortcut.IconLocation = '{self.install_path}\\Punctaj_Manager.exe,0'
$Shortcut.Save()
"""
            subprocess.run(['powershell', '-NoProfile', '-Command', ps_cmd],
                         capture_output=True, check=False)
        except Exception as e:
            print(f"Warning: Could not create shortcuts: {e}")
    
    def register_windows(self):
        """Register application in Windows"""
        try:
            import winreg
            
            # Create registry key
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Punctaj")
            winreg.SetValueEx(key, "Install_Dir", 0, winreg.REG_SZ, str(self.install_path))
            winreg.SetValueEx(key, "Version", 0, winreg.REG_SZ, "2.0.0")
            winreg.CloseKey(key)
            
            # Add to Add/Remove Programs
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                                  r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj")
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Punctaj Manager 2.0.0")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "2.0.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Punctaj Team")
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Warning: Registry registration failed: {e}")


def main():
    root = tk.Tk()
    app = PunctajInstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Create installer UI"""
        
        # Header frame
        header_frame = tk.Frame(self.root, bg="#007bff", height=80)
        header_frame.pack(fill=tk.X)
        
        title = tk.Label(header_frame, text="Punctaj Application", 
                        font=("Arial", 18, "bold"), bg="#007bff", fg="white")
        title.pack(pady=10)
        
        subtitle = tk.Label(header_frame, text="Professional Employee Punctaj Management System",
                           font=("Arial", 10), bg="#007bff", fg="white")
        subtitle.pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg="#f8f9fa")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Installation path section
        path_label = tk.Label(content_frame, text="Installation Folder:", 
                             font=("Arial", 11, "bold"), bg="#f8f9fa")
        path_label.pack(anchor=tk.W, pady=(10, 5))
        
        path_frame = tk.Frame(content_frame, bg="#f8f9fa")
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.path_entry = tk.Entry(path_frame, textvariable=self.install_path, 
                                   font=("Arial", 10), width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(path_frame, text="Browse...", command=self.browse_folder,
                              font=("Arial", 9), width=12, bg="#6c757d", fg="white",
                              activebackground="#5a6268")
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Features frame
        features_label = tk.Label(content_frame, text="Features:", 
                                 font=("Arial", 11, "bold"), bg="#f8f9fa")
        features_label.pack(anchor=tk.W, pady=(15, 10))
        
        features_text = (
            "✓ Standalone executable (no Python required)\n"
            "✓ Cloud synchronization with Supabase\n"
            "✓ Employee punctaj management\n"
            "✓ Weekly reports and archives\n"
            "✓ Discord integration (optional)\n"
            "✓ Automatic backup system"
        )
        
        features = tk.Label(content_frame, text=features_text,
                           font=("Arial", 10), bg="#f8f9fa", justify=tk.LEFT)
        features.pack(anchor=tk.W)
        
        # System requirements frame
        req_label = tk.Label(content_frame, text="System Requirements:",
                            font=("Arial", 11, "bold"), bg="#f8f9fa")
        req_label.pack(anchor=tk.W, pady=(15, 10))
        
        req_text = "• Windows 7 or later  • 100 MB free space  • Internet connection (for cloud sync)"
        
        requirements = tk.Label(content_frame, text=req_text,
                               font=("Arial", 9), bg="#f8f9fa", justify=tk.LEFT)
        requirements.pack(anchor=tk.W)
        
        # Progress bar (hidden initially)
        self.progress = ttk.Progressbar(content_frame, mode='indeterminate', length=400)
        self.progress.pack(fill=tk.X, pady=(15, 0))
        
        self.progress_label = tk.Label(content_frame, text="", font=("Arial", 9), bg="#f8f9fa")
        self.progress_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="white", height=70)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        install_btn = tk.Button(button_frame, text="Install", command=self.install,
                               font=("Arial", 12, "bold"), bg="#28a745", fg="white",
                               width=15, height=2, activebackground="#218838")
        install_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.root.quit,
                              font=("Arial", 12, "bold"), bg="#dc3545", fg="white",
                              width=15, height=2, activebackground="#c82333")
        cancel_btn.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def browse_folder(self):
        """Browse for installation folder"""
        folder = filedialog.askdirectory(
            title="Select Installation Folder",
            initialdir=self.default_install_path
        )
        if folder:
            self.install_path.set(folder)
    
    def install(self):
        """Perform installation in separate thread"""
        thread = threading.Thread(target=self._install_thread)
        thread.daemon = True
        thread.start()
    
    def _install_thread(self):
        """Installation process (runs in background thread)"""
        try:
            install_dir = Path(self.install_path.get())
            
            if not install_dir.as_posix().startswith(('C:', 'D:', 'E:')):
                messagebox.showerror("Invalid Path", "Please select a valid installation path")
                return
            
            self.root.after(0, self._update_progress, True, "Creating installation directory...")
            
            # Create installation directory
            install_dir.mkdir(parents=True, exist_ok=True)
            
            self.root.after(0, self._update_progress, True, "Creating application folders...")
            
            # Create required folders
            (install_dir / "data").mkdir(exist_ok=True)
            (install_dir / "arhiva").mkdir(exist_ok=True)
            (install_dir / "logs").mkdir(exist_ok=True)
            
            self.root.after(0, self._update_progress, True, "Copying application files...")
            
            # Copy application folder from bundle
            if getattr(sys, 'frozen', False):
                # Running as EXE - copy from bundle
                bundle_app_path = os.path.join(self.bundle_dir, "_punctaj_app")
                
                if os.path.exists(bundle_app_path):
                    for item in os.listdir(bundle_app_path):
                        src = os.path.join(bundle_app_path, item)
                        dst = os.path.join(install_dir, item)
                        
                        if os.path.isdir(src):
                            if os.path.exists(dst):
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst)
                        else:
                            shutil.copy2(src, dst)
            else:
                # Running as script - try to find application
                app_source = Path(__file__).parent / "installer_outputs" / "Punctaj"
                if app_source.exists():
                    for item in app_source.iterdir():
                        if item.name not in ["data", "arhiva", "logs"]:
                            dst = install_dir / item.name
                            if item.is_dir():
                                if dst.exists():
                                    shutil.rmtree(dst)
                                shutil.copytree(item, dst)
                            else:
                                shutil.copy2(item, dst)
            
            self.root.after(0, self._update_progress, True, "Creating desktop shortcut...")
            
            # Create desktop shortcut (Windows)
            if sys.platform == "win32":
                self._create_shortcut(install_dir)
            
            self.root.after(0, self._update_progress, False, "")
            
            # Show success message
            self.root.after(0, self._show_success, str(install_dir))
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _update_progress(self, show, text):
        """Update progress bar"""
        if show:
            self.progress.start()
            self.progress_label.config(text=text)
        else:
            self.progress.stop()
            self.progress_label.config(text="")
    
    def _create_shortcut(self, install_dir):
        """Create desktop shortcut for Windows"""
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "Punctaj.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = str(install_dir / "Punctaj.exe")
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.Description = "Punctaj Application - Employee Management"
            shortcut.IconLocation = str(install_dir / "Punctaj.exe")
            shortcut.save()
            
        except Exception:
            pass  # Shortcut creation is optional
    
    def _show_success(self, install_path):
        """Show success message"""
        result = messagebox.showinfo(
            "Installation Complete",
            f"Punctaj has been successfully installed!\n\n"
            f"Installation folder: {install_path}\n\n"
            f"A shortcut has been created on your desktop.\n\n"
            f"Before running:\n"
            f"1. Edit supabase_config.ini with your database credentials\n"
            f"2. (Optional) Edit discord_config.ini for Discord OAuth\n\n"
            f"Click OK to open the setup wizard."
        )
        
        # Incearca sa ruleaza setup wizard daca exista
        setup_wizard_path = os.path.join(install_path, "SETUP_SUPABASE_WIZARD.py")
        if os.path.exists(setup_wizard_path):
            try:
                import subprocess
                subprocess.Popen([sys.executable, setup_wizard_path])
            except:
                pass
        
        self.root.quit()
    
    def _show_error(self, error):
        """Show error message"""
        messagebox.showerror(
            "Installation Error",
            f"Failed to install Punctaj:\n\n{error}\n\n"
            f"Please ensure you have administrator privileges and\n"
            f"sufficient disk space for installation."
        )

def main():
    """Main installer entry point"""
    root = tk.Tk()
    
    # Set window icon if available
    try:
        root.iconbitmap(default='')
    except:
        pass
    
    app = PunctajInstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
