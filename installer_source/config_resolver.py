#!/usr/bin/env python3
"""
Configuration Path Resolver
Ajuta aplicatia sa gaseasca fisierele de configurare pe diferite dispozitive
"""

import os
import sys
from pathlib import Path

class ConfigResolver:
    """Rezolva caile pentru fisierele de configurare"""
    
    @staticmethod
    def get_app_root():
        """Gaseste folderul root al aplicatiei"""
        # Priority 1: Running as frozen executable
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            if os.path.exists(os.path.join(exe_dir, 'supabase_config.ini')):
                return exe_dir
        
        # Priority 2: Script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(script_dir, 'supabase_config.ini')):
            return script_dir
        
        # Priority 3: Current working directory
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, 'supabase_config.ini')):
            return cwd
        
        # Priority 4: Program Files
        program_files = os.path.expandvars(r"%ProgramFiles%\Punctaj")
        if os.path.exists(program_files):
            return program_files
        
        # Default: Return script directory
        return script_dir
    
    @staticmethod
    def get_config_paths():
        """Returneaza lista de locatii unde sa caute fisierele de configurare"""
        paths = []
        
        # 1. Executable directory (if running as EXE)
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            paths.append(exe_dir)
        
        # 2. Script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        paths.append(script_dir)
        
        # 3. Current working directory
        paths.append(os.getcwd())
        
        # 4. Standard Windows installation paths
        paths.append(os.path.expandvars(r"%ProgramFiles%\Punctaj"))
        paths.append(os.path.expandvars(r"%ProgramFiles(x86)%\Punctaj"))
        
        # 5. User paths
        paths.append(os.path.expandvars(r"%APPDATA%\Punctaj"))
        paths.append(os.path.expandvars(r"%LOCALAPPDATA%\Punctaj"))
        paths.append(os.path.expanduser("~/Punctaj"))
        
        # 6. Common locations
        paths.extend([
            r"C:\Punctaj",
            r"D:\Punctaj",
            r"C:\Users\Public\Punctaj"
        ])
        
        # Elimina duplicatele si verifica care exista
        unique_paths = []
        for path in paths:
            if path not in unique_paths and os.path.exists(path):
                unique_paths.append(path)
        
        return unique_paths if unique_paths else paths
    
    @staticmethod
    def find_config_file(filename='supabase_config.ini'):
        """Gaseste un fisier de configurare"""
        paths = ConfigResolver.get_config_paths()
        
        for path in paths:
            config_path = os.path.join(path, filename)
            if os.path.exists(config_path):
                return config_path
        
        # Daca nu gaseste nimic, returneaza calea preferata
        return os.path.join(ConfigResolver.get_app_root(), filename)
    
    @staticmethod
    def ensure_config_exists(filename='supabase_config.ini', template=None):
        """Asigura ca fisierul de configurare exista"""
        config_path = ConfigResolver.find_config_file(filename)
        
        if not os.path.exists(config_path):
            app_root = ConfigResolver.get_app_root()
            config_path = os.path.join(app_root, filename)
            
            # Creeaza configurare implicita daca template e furnizat
            if template and not os.path.exists(config_path):
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                try:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(template)
                except:
                    pass
        
        return config_path

# Supabase config template
SUPABASE_CONFIG_TEMPLATE = """[supabase]
# Gaseste aceste valori in Supabase project settings
url = https://your-project.supabase.co
key = your-api-key-here
table_sync = police_data
table_logs = audit_logs
table_users = users

[sync]
enabled = true
auto_sync = true
sync_interval = 30
conflict_resolution = latest_timestamp
sync_on_startup = true
"""

# Discord config template
DISCORD_CONFIG_TEMPLATE = """[discord]
# Discord OAuth2 Configuration
# Obtine aceste valori din Discord Developer Portal: https://discord.com/developers/applications
CLIENT_ID = your-client-id-here
CLIENT_SECRET = your-client-secret-here
REDIRECT_URI = http://localhost:8888/callback
WEBHOOK_URL = https://discordapp.com/api/webhooks/your-webhook-url
"""

def setup_config_files():
    """Configureaza fisierele de configurare pe prima rulare"""
    
    app_root = ConfigResolver.get_app_root()
    
    # Supabase config
    supabase_path = ConfigResolver.ensure_config_exists(
        'supabase_config.ini',
        SUPABASE_CONFIG_TEMPLATE
    )
    
    # Discord config
    discord_path = os.path.join(app_root, 'discord_config.ini')
    if not os.path.exists(discord_path):
        try:
            with open(discord_path, 'w', encoding='utf-8') as f:
                f.write(DISCORD_CONFIG_TEMPLATE)
        except:
            pass
    
    return supabase_path, discord_path

if __name__ == "__main__":
    # Test resolver
    print("Configuration Path Resolver Test")
    print("=" * 50)
    print(f"\nApp Root: {ConfigResolver.get_app_root()}")
    print(f"\nSearching for config files in:")
    for path in ConfigResolver.get_config_paths():
        print(f"  - {path}")
    
    config_file = ConfigResolver.find_config_file()
    print(f"\nFound config: {config_file}")
    print(f"Exists: {os.path.exists(config_file)}")
