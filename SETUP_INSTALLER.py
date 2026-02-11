#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROFESSIONAL SETUP INSTALLER
Instalează Punctaj Manager cu sincronizare în timp real
Configurează accesul la Supabase și permisiuni automate
"""

import os
import shutil
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class PunctajInstaller:
    """Instalează Punctaj Manager pe calculator"""
    
    def __init__(self):
        self.install_dir = os.path.expandvars(r"%APPDATA%\PunctajManager")
        self.data_dir = os.path.join(self.install_dir, "data")
        self.config_dir = os.path.join(self.install_dir, "config")
        self.logs_dir = os.path.join(self.install_dir, "logs")
        self.archive_dir = os.path.join(self.install_dir, "arhiva")
        self.shortcut_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
        
    def print_header(self):
        """Afisează header-ul"""
        print("=" * 80)
        print("🚀 PUNCTAJ MANAGER - PROFESSIONAL SETUP INSTALLER")
        print("=" * 80)
        print()
        print(f"📦 Installation directory: {self.install_dir}")
        print(f"💾 Data directory: {self.data_dir}")
        print(f"⚙️  Config directory: {self.config_dir}")
        print(f"📋 Logs directory: {self.logs_dir}")
        print()
        
    def check_prerequisites(self):
        """Verifică dacă sunt îndeplinite cerințele"""
        print("1️⃣ Checking prerequisites...")
        print()
        
        # Check Python
        print("   ✓ Python: OK (you're running this script)")
        
        # Check required modules
        required_modules = {
            'tkinter': 'GUI',
            'requests': 'API calls',
            'cryptography': 'Encryption',
        }
        
        all_ok = True
        for module, purpose in required_modules.items():
            try:
                __import__(module)
                print(f"   ✓ {module}: OK ({purpose})")
            except ImportError:
                print(f"   ❌ {module}: MISSING ({purpose})")
                print(f"      Install with: pip install {module}")
                all_ok = False
        
        print()
        
        if not all_ok:
            print("⚠️  Some required modules are missing!")
            print("Install them with: pip install tkinter requests cryptography")
            response = input("Continue anyway? (y/n): ").lower()
            if response != 'y':
                sys.exit(1)
        
        return True
    
    def create_directories(self):
        """Creează directoarele necesare"""
        print("2️⃣ Creating directories...")
        print()
        
        for dir_path in [self.install_dir, self.data_dir, self.config_dir, self.logs_dir, self.archive_dir]:
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✓ Created: {dir_path}")
        
        print()
    
    def copy_application_files(self):
        """Copiază fișierele aplicației"""
        print("3️⃣ Copying application files...")
        print()
        
        # Get the location of installer_source (same as where this script is)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        installer_source = os.path.join(script_dir, 'installer_source')
        
        # Check if installer_source exists
        if not os.path.exists(installer_source):
            print(f"❌ installer_source not found at: {installer_source}")
            print("   Please ensure installer_source folder exists in the same directory as this script")
            return False
        
        # Files to copy from installer_source
        files_to_copy = [
            'punctaj.py',
            'discord_auth.py',
            'supabase_sync.py',
            'permission_sync_fix.py',
            'realtime_sync.py',
            'admin_panel.py',
            'admin_permissions.py',
            'admin_ui.py',
            'action_logger.py',
            'config_resolver.py',
            'json_logger.py',
            'organization_view.py',
        ]
        
        for file in files_to_copy:
            src = os.path.join(installer_source, file)
            if os.path.exists(src):
                dst = os.path.join(self.install_dir, file)
                shutil.copy2(src, dst)
                print(f"   ✓ Copied: {file}")
            else:
                print(f"   ⚠️  Skipped: {file} (not found)")
        
        # Copy config files if they exist
        if os.path.exists(os.path.join(installer_source, 'discord_config.ini')):
            shutil.copy2(
                os.path.join(installer_source, 'discord_config.ini'),
                os.path.join(self.config_dir, 'discord_config.ini')
            )
            print(f"   ✓ Copied: discord_config.ini")
        
        if os.path.exists(os.path.join(installer_source, 'supabase_config.ini')):
            shutil.copy2(
                os.path.join(installer_source, 'supabase_config.ini'),
                os.path.join(self.config_dir, 'supabase_config.ini')
            )
            print(f"   ✓ Copied: supabase_config.ini")
        
        print()
        return True
    
    def create_config_files(self):
        """Creează fișierele de configurare dacă nu există"""
        print("4️⃣ Setting up configuration files...")
        print()
        
        # Check if Supabase config exists
        supabase_config_path = os.path.join(self.config_dir, 'supabase_config.ini')
        if not os.path.exists(supabase_config_path):
            print("   ⚠️  supabase_config.ini not found!")
            print("      You need to manually add this file with your Supabase credentials")
            print()
            print("      Content should be:")
            print("""
[supabase]
url = https://your-project.supabase.co
key = your_api_key
table_sync = police_data
table_logs = audit_logs
table_users = discord_users

[sync]
enabled = true
auto_sync = true
sync_interval = 30
            """)
        else:
            print(f"   ✓ Supabase config found: {supabase_config_path}")
        
        # Check if Discord config exists
        discord_config_path = os.path.join(self.config_dir, 'discord_config.ini')
        if not os.path.exists(discord_config_path):
            print("   ⚠️  discord_config.ini not found!")
            print("      You need to manually add this file with your Discord OAuth credentials")
        else:
            print(f"   ✓ Discord config found: {discord_config_path}")
        
        print()
    
    def create_batch_launcher(self):
        """Creează fișier batch pentru lansarea aplicației"""
        print("5️⃣ Creating launcher scripts...")
        print()
        
        # Create .bat launcher
        bat_content = f"""@echo off
REM Punctaj Manager Launcher
title Punctaj Manager
cd /d "{self.install_dir}"
python punctaj.py
pause
"""
        bat_path = os.path.join(self.install_dir, 'launch_punctaj.bat')
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print(f"   ✓ Created: launch_punctaj.bat")
        
        # Create Python launcher
        py_content = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess

os.chdir(r"{self.install_dir}")
sys.path.insert(0, r"{self.install_dir}")

# Import and run the main app
from punctaj import *

if __name__ == "__main__":
    print("🚀 Starting Punctaj Manager...")
    print(f"📁 Working directory: {{os.getcwd()}}")
    print(f"🔌 Data directory: {self.data_dir}")
    
    try:
        root = tk.Tk()
        root.geometry("1024x768")
        root.title("Punctaj Manager")
        
        # Initialize application
        show_login_window(root)
        
        root.mainloop()
    except Exception as e:
        print(f"❌ Error: {{e}}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
"""
        py_path = os.path.join(self.install_dir, 'launch_punctaj.py')
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(py_content)
        print(f"   ✓ Created: launch_punctaj.py")
        
        # Create shortcut in Start Menu
        try:
            shortcut_path = os.path.join(self.shortcut_dir, 'Punctaj Manager.bat')
            shutil.copy2(bat_path, shortcut_path)
            print(f"   ✓ Created Start Menu shortcut")
        except Exception as e:
            print(f"   ⚠️  Could not create Start Menu shortcut: {e}")
        
        print()
    
    def create_installation_log(self):
        """Creează log-ul de instalare"""
        print("6️⃣ Creating installation log...")
        print()
        
        log_content = f"""
PUNCTAJ MANAGER - INSTALLATION LOG
=====================================

Installation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Installation Directory: {self.install_dir}
Data Directory: {self.data_dir}
Config Directory: {self.config_dir}
Logs Directory: {self.logs_dir}
Archive Directory: {self.archive_dir}

INSTALLED MODULES:
- Permission Sync Manager: Real-time permission synchronization
- Real-Time Cloud Sync: Automatic data sync from Supabase every 30 seconds
- Discord Authentication: OAuth2 login with auto-registration
- Action Logger: Automatic logging of all user actions
- Admin Panel: Granular permission management

FIRST TIME SETUP REQUIRED:
1. Add configuration files to: {self.config_dir}
   - discord_config.ini (Discord OAuth credentials)
   - supabase_config.ini (Supabase API credentials)

2. Run launch_punctaj.bat or launch_punctaj.py

3. Login with Discord (auto-creates user in Supabase)

4. Ask admin to assign permissions

FEATURES:
✅ Permission Sync: Permissions updated every 5 seconds
✅ Auto-Registration: New Discord users auto-created in Supabase
✅ Real-Time Sync: Database synced every 30 seconds (no restart needed!)
✅ Admin Panel: Granular permission control
✅ Action Logging: All changes logged to Supabase

TROUBLESHOOTING:
- If permissions don't sync: Check supabase_config.ini
- If Discord login fails: Check discord_config.ini
- If data doesn't update: Check real-time sync logs

For support, check the README.md files in the installation directory.
"""
        
        log_path = os.path.join(self.install_dir, 'INSTALLATION_LOG.txt')
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        print(f"   ✓ Created: INSTALLATION_LOG.txt")
        print()
    
    def create_readme(self):
        """Creează README cu instrucțiuni de utilizare"""
        print("7️⃣ Creating README files...")
        print()
        
        readme_content = """# 🎯 PUNCTAJ MANAGER - USER GUIDE

## ✅ Installation Complete!

Your Punctaj Manager has been installed in:
```
%APPDATA%\\PunctajManager
```

## 🚀 Getting Started

### Step 1: Configure Credentials
1. Navigate to: `%APPDATA%\\PunctajManager\\config\\`
2. Edit `discord_config.ini` with your Discord OAuth settings
3. Edit `supabase_config.ini` with your Supabase API credentials

### Step 2: Launch the Application
**Option A - Batch File (Recommended)**
```bash
launch_punctaj.bat
```

**Option B - Python**
```bash
python launch_punctaj.py
```

**Option C - From Start Menu**
Click `Punctaj Manager` in Windows Start Menu

### Step 3: Login with Discord
1. Click "Login cu Discord"
2. Approve the permissions
3. You'll be automatically registered in the system

## 🔄 Real-Time Features

### ⚡ Automatic Permission Sync
- Permissions sync EVERY 5 SECONDS
- No need to restart to see permission changes
- Admin changes appear instantly in your app

### 🌐 Cloud Data Sync
- Data syncs EVERY 30 SECONDS from Supabase
- Changes from other users appear automatically
- Local files kept in: `%APPDATA%\\PunctajManager\\data\\`

### 🔐 Auto-Registration
- First Discord login auto-creates your account
- You'll have VIEWER role (limited access)
- Ask your admin to assign permissions

## 👤 User Roles

- **VIEWER** 👁️ - Read-only access (default for new users)
- **EDITOR** ✏️ - Can edit institution data
- **ADMIN** 👑 - Can manage users and permissions
- **SUPERUSER** 🔐 - Full system access

## 📊 Admin Features

### Assigning Permissions (Admin Only)
1. Go to Admin Panel
2. Select user from list
3. Check permissions needed
4. Click "Save"
5. Changes sync in < 5 seconds

### Granular Permissions
- `can_view` - View data
- `can_edit` - Modify data
- `can_delete` - Delete data
- `can_manage_users` - User management
- `can_manage_institutions` - Institution management

## 🔧 Configuration Files

### discord_config.ini
```ini
[discord]
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
redirect_uri = http://localhost:8000/callback
```

### supabase_config.ini
```ini
[supabase]
url = https://your-project.supabase.co
key = your_api_key
table_sync = police_data
table_logs = audit_logs
table_users = discord_users

[sync]
enabled = true
auto_sync = true
sync_interval = 30
```

## 📂 Directory Structure

```
%APPDATA%\\PunctajManager\\
├── punctaj.py                    ← Main application
├── launch_punctaj.bat            ← Launcher script
├── config/
│   ├── discord_config.ini        ← Discord settings
│   └── supabase_config.ini       ← Supabase settings
├── data/                         ← Local data files
├── arhiva/                       ← Archived data
└── logs/                         ← Application logs
```

## 🆘 Troubleshooting

### "Discord login failed"
- Check your internet connection
- Verify `discord_config.ini` is correct
- Check Discord OAuth settings

### "Cannot sync with Supabase"
- Verify `supabase_config.ini` is correct
- Check your Supabase project settings
- Ensure the API key is valid

### "Permissions not updating"
- Permission sync happens every 5 seconds
- Check if you have VIEWER role (need admin to assign permissions)
- Restart app if permissions still don't appear

### "Data not syncing from cloud"
- Real-time sync happens every 30 seconds
- Check your internet connection
- Wait up to 30 seconds for changes to appear

## 💡 Tips & Tricks

- **Keyboard Shortcut**: Press `Ctrl+R` to force immediate sync
- **Backup Data**: Data is automatically synced to Supabase
- **Check Logs**: Application logs are saved in `logs/` folder
- **Admin View**: Click "Admin Panel" to manage permissions

## 📞 Support

For issues or questions:
1. Check the logs in `%APPDATA%\\PunctajManager\\logs\\`
2. Review the INSTALLATION_LOG.txt
3. Contact your system administrator

---

**Punctaj Manager v2.5 with Real-Time Sync**
Last Updated: 2026-02-03
"""
        
        readme_path = os.path.join(self.install_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"   ✓ Created: README.md")
        print()
    
    def run_installation(self):
        """Execută instalarea"""
        self.print_header()
        
        try:
            self.check_prerequisites()
            self.create_directories()
            if not self.copy_application_files():
                return False
            self.create_config_files()
            self.create_batch_launcher()
            self.create_installation_log()
            self.create_readme()
            
            # Success message
            print("=" * 80)
            print("✅ INSTALLATION COMPLETE!")
            print("=" * 80)
            print()
            print("📍 Next Steps:")
            print(f"1. Edit config files in: {self.config_dir}")
            print(f"   - discord_config.ini")
            print(f"   - supabase_config.ini")
            print()
            print("2. Launch the application:")
            print(f"   {os.path.join(self.install_dir, 'launch_punctaj.bat')}")
            print()
            print("3. Login with Discord (auto-creates your account)")
            print()
            print("4. Ask admin to assign your permissions")
            print()
            print("✨ You're all set!")
            print()
            
            # Offer to open the installation folder
            try:
                import webbrowser
                response = input("Open installation folder? (y/n): ").lower()
                if response == 'y':
                    os.startfile(self.install_dir)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    installer = PunctajInstaller()
    success = installer.run_installation()
    
    if not success:
        sys.exit(1)
