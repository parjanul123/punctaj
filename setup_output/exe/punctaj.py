import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import shutil
import csv
from datetime import datetime
import schedule
import threading
import time
import sys
import requests

# Adaugă calea pentru PyInstaller bundle (sys._MEIPASS)
if getattr(sys, 'frozen', False):
    # Rulează ca executabil - adaugă calea către fișierele bundle-uite
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
    print(f"📦 Executabil mode - bundle dir: {bundle_dir}")

# ================== CONFIG / PATHS (EARLY DEFINITION) ==================
# Define BASE_DIR early so it can be used by other modules
# BASE_DIR TREBUIE SA FIE d:\punctaj pentru AMBELE (EXE și Python script)

def get_base_directory():
    """
    Determină folderul de bază pentru aplicație.
    ATÂT EXE cât și Python script-ul vor folosi ACELAȘI folder,
    indiferent de dispozitiv (Device 1, Device 2, Device 3, etc.)
    """
    if getattr(sys, 'frozen', False):
        # Rulează ca EXE
        print(f"📦 Running as EXE")
        exe_dir = os.path.dirname(sys.executable)
        
        # Verifică dacă EXE e în dist/ subfolder
        # Dacă da, mergi la folderul PARENTAL (rădăcina aplicației)
        if exe_dir.endswith("\\dist") or exe_dir.endswith("/dist"):
            parent_dir = os.path.dirname(exe_dir)
            print(f"🔧 EXE in dist/ subfolder, using parent: {parent_dir}")
            return parent_dir
        
        # EXE e în folderul rădăcina - folosește-l direct
        print(f"🔧 Using EXE directory as BASE_DIR: {exe_dir}")
        return exe_dir
    
    # Python script - foloseşte folderul scriptului
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"🔧 Using script directory as BASE_DIR: {script_dir}")
    return script_dir

BASE_DIR = get_base_directory()
print(f"📁 BASE_DIR set to: {BASE_DIR}")

# Import config resolver pentru caile de configurare
try:
    from config_resolver import ConfigResolver
    CONFIG_RESOLVER = ConfigResolver()
    print("✓ Config resolver loaded")
except ImportError:
    print("⚠️ Config resolver not available")
    CONFIG_RESOLVER = None

# Discord Authentication (OBLIGATORIU)
DISCORD_AUTH_ENABLED = True  # ✅ ACTIVAT - Discord login is required
DISCORD_AUTH = None
DISCORD_CONFIG = {}
DiscordAuth = None  # Fallback - será setat de import

try:
    from discord_auth import DiscordAuth, DiscordWebhook
    DISCORD_AUTH_ENABLED = True
    print("[OK] Discord auth module loaded")
except ImportError as e:
    print(f"[ERROR] Discord authentication module import failed: {e}")
    print("[WARNING] Verifica daca discord_auth.py este in bundle")
    DISCORD_AUTH_ENABLED = False
    # Create stub class so code doesn't crash
    class DiscordAuth:
        def __init__(self, *args, **kwargs):
            raise Exception("DiscordAuth not available - import failed")

# Load Discord config
try:
    import configparser
    config = configparser.ConfigParser()
    
    # Build all possible paths
    meipass = getattr(sys, '_MEIPASS', None)
    exe_dir = os.path.dirname(sys.executable) if hasattr(sys, 'executable') else None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    config_paths = [
        os.path.join(meipass, "discord_config.ini") if meipass else None,
        os.path.join(exe_dir, "discord_config.ini") if exe_dir else None,
        os.path.join(script_dir, "discord_config.ini"),
        os.path.join(BASE_DIR, "discord_config.ini"),
        "discord_config.ini"
    ]
    
    # Remove None entries
    config_paths = [p for p in config_paths if p is not None]
    
    print(f"[DEBUG] Looking for discord_config.ini in:")
    print(f"  _MEIPASS: {meipass}")
    print(f"  exe_dir: {exe_dir}")
    print(f"  script_dir: {script_dir}")
    print(f"  BASE_DIR: {BASE_DIR}")
    
    for config_path in config_paths:
        print(f"  Checking: {config_path}")
        if os.path.exists(config_path):
            print(f"    ✓ FOUND!")
            config.read(config_path)
            if 'discord' in config:
                DISCORD_CONFIG = {
                    'CLIENT_ID': config.get('discord', 'CLIENT_ID', fallback=None),
                    'CLIENT_SECRET': config.get('discord', 'CLIENT_SECRET', fallback=None),
                    'REDIRECT_URI': config.get('discord', 'REDIRECT_URI', fallback='http://localhost:8888/callback'),
                    'WEBHOOK_URL': config.get('discord', 'WEBHOOK_URL', fallback=None),
                }
                print(f"✓ Discord config loaded from {config_path}")
                print(f"  CLIENT_ID: {DISCORD_CONFIG.get('CLIENT_ID', 'NOT SET')}")
                print(f"  REDIRECT_URI: {DISCORD_CONFIG.get('REDIRECT_URI')}")
                break
        else:
            print(f"    ✗ not found")
    
    # FALLBACK: Use hardcoded values if config not found
    if not DISCORD_CONFIG.get('CLIENT_ID'):
        print("[FALLBACK] Config file not found, using hardcoded Discord credentials")
        DISCORD_CONFIG = {
            'CLIENT_ID': '1465698276375527622',
            'CLIENT_SECRET': '6NyZKnBlaZWrHA0s72Lyxyr1FI2cqqfY',
            'REDIRECT_URI': 'http://localhost:8888/callback',
            'WEBHOOK_URL': None,
        }
        print(f"[FALLBACK] CLIENT_ID: {DISCORD_CONFIG['CLIENT_ID']}")
    
    print(f"\n✅ DISCORD_CONFIG READY:")
    print(f"   CLIENT_ID: {DISCORD_CONFIG.get('CLIENT_ID')}")
    print(f"   CLIENT_SECRET: {DISCORD_CONFIG.get('CLIENT_SECRET', 'NOT SET')}")
    print(f"   REDIRECT_URI: {DISCORD_CONFIG.get('REDIRECT_URI')}")
    print()
    
    if not DISCORD_CONFIG.get('CLIENT_ID'):
        print("⚠️ Discord CLIENT_ID not configured - configure discord_config.ini")
        
except Exception as e:
    print(f"⚠️ Error loading Discord config: {e}")

# Supabase sync module
try:
    from supabase_sync import SupabaseSync
    SUPABASE_MODULE_AVAILABLE = True
    print("✓ Supabase sync module loaded")
except ImportError as e:
    SUPABASE_MODULE_AVAILABLE = False
    print(f"⚠️ Supabase sync module lipsește: {e}")

# Robust Config Loader for Supabase - ensures config is found on ANY device
try:
    from config_loader_robust import RobustConfigLoader
    CONFIG_LOADER = RobustConfigLoader(debug=False)  # Set to True for debugging
    if CONFIG_LOADER.is_valid():
        print(f"✅ SUPABASE CONFIG LOADED from: {CONFIG_LOADER.get_config_path()}")
    else:
        print(f"⚠️  WARNING: Supabase config may not be valid")
except ImportError as e:
    print(f"⚠️ Robust config loader error: {e}")
    CONFIG_LOADER = None

# Supabase Employee Manager (for cities/institutions/employees sync)
try:
    from supabase_employee_manager import SupabaseEmployeeManager
    SUPABASE_EMPLOYEE_MANAGER = SupabaseEmployeeManager()
    SUPABASE_EMPLOYEE_MANAGER_AVAILABLE = True
    print("✓ Supabase Employee Manager loaded")
except Exception as e:
    SUPABASE_EMPLOYEE_MANAGER_AVAILABLE = False
    SUPABASE_EMPLOYEE_MANAGER = None
    print(f"⚠️ Supabase Employee Manager error: {e}")

# Cloud Sync Manager - sincronizare forțată cu cloud
try:
    from cloud_sync_manager import CloudSyncManager
    CLOUD_SYNC_AVAILABLE = True
    print("✓ Cloud sync manager module loaded")
except ImportError as e:
    CLOUD_SYNC_AVAILABLE = False
    CloudSyncManager = None
    print(f"⚠️ Cloud sync manager module lipsește: {e}")

# Backup Manager - periodic backup of local data
try:
    from backup_manager import BackupManager, create_backup_ui
    BACKUP_MANAGER_AVAILABLE = True
    print("✓ Backup manager module loaded")
except ImportError as e:
    BACKUP_MANAGER_AVAILABLE = False
    BackupManager = None
    create_backup_ui = None
    print(f"⚠️ Backup manager module lipsește: {e}")

# Admin Panel & Action Logger
try:
    from admin_panel import ActionLogger, AdminPanel
    from admin_ui import open_admin_panel
    from admin_permissions import open_granular_permissions_panel, InstitutionPermissionManager
    from action_logger import ActionLogger as ActionLoggerNew
    from permission_check_helpers import (
        check_can_add_city,
        check_can_edit_city,
        check_can_delete_city
    )
    ADMIN_PANEL_AVAILABLE = True
    print("✓ Admin panel and logging module loaded")
except Exception as e:
    ADMIN_PANEL_AVAILABLE = False
    open_admin_panel = None
    open_granular_permissions_panel = None
    ActionLoggerNew = None
    print(f"⚠️ Admin panel module error: {e}")
    import traceback
    traceback.print_exc()

# Permission Sync Manager - for keeping permissions in sync with Supabase
try:
    from permission_sync_fix import PermissionSyncManager
    PERMISSION_SYNC_AVAILABLE = True
    print("✓ Permission sync manager loaded")
except Exception as e:
    PERMISSION_SYNC_AVAILABLE = False
    PermissionSyncManager = None
    print(f"⚠️ Permission sync manager error: {e}")

# Real-Time Cloud Sync Manager - for syncing institution data in real-time
try:
    from realtime_sync import RealTimeSyncManager
    REALTIME_SYNC_AVAILABLE = True
    print("✓ Real-time cloud sync manager loaded")
except Exception as e:
    REALTIME_SYNC_AVAILABLE = False
    RealTimeSyncManager = None
    print(f"⚠️ Real-time sync manager error: {e}")

# Organization View (hierarchical display)
try:
    from organization_view import create_city_institution_view
    ORGANIZATION_VIEW_AVAILABLE = True
    print("✓ Organization view module loaded")
except Exception as e:
    ORGANIZATION_VIEW_AVAILABLE = False
    create_city_institution_view = None
    print(f"⚠️ Organization view error: {e}")
    InstitutionPermissionManager = None
    print(f"⚠️ Admin panel module lipsește: {e}")
    import traceback
    traceback.print_exc()

# JSON Action Logger - înregistrează orice modificare pe JSON-uri
try:
    from json_logger import JSONActionLogger, LOGGER
    LOGGER_AVAILABLE = True
    print("✓ JSON logger module loaded")
except ImportError as e:
    LOGGER_AVAILABLE = False
    LOGGER = None
    print(f"⚠️ JSON logger module lipsește: {e}")

# Git support - complet opțional (DEPRECATED - folosește Supabase)
try:
    from git import Repo
    from git.exc import InvalidGitRepositoryError
    GIT_AVAILABLE = True
except ImportError:
    # Git nu e instalat sau GitPython lipsește - aplicația va funcționa fără Git
    GIT_AVAILABLE = False
    print("⚠️ Git nu este disponibil - funcționalitatea Git este dezactivată")

# ================== GLOBAL OBJECTS INITIALIZATION ==================
# Permission Sync Manager instance
PERMISSION_SYNC_MANAGER = None

# Real-Time Sync Manager instance
REALTIME_SYNC_MANAGER = None

# Backup Manager instance
BACKUP_MANAGER = None

# ================== DATA DIRECTORIES CONFIGURATION ==================
# STANDARDIZED across ALL devices
# Data is ALWAYS in BASE_DIR\data and BASE_DIR\arhiva
# Works the same on Device 1, Device 2, Device 3, etc.

# Use data directory manager for multi-device compatibility
try:
    from data_directory_manager import DataDirectoryManager
    DATA_MANAGER = DataDirectoryManager(base_path=BASE_DIR)
    DATA_DIR = str(DATA_MANAGER.get_data_dir())
    ARCHIVE_DIR = str(DATA_MANAGER.get_archive_dir())
    LOGS_DIR = str(DATA_MANAGER.get_logs_dir())
    print(f"✅ Data manager initialized")
except Exception as e:
    print(f"⚠️  Data manager error: {e}")
    # Fallback to simple directory setup
    DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data"))
    ARCHIVE_DIR = os.path.abspath(os.path.join(BASE_DIR, "arhiva"))
    LOGS_DIR = os.path.abspath(os.path.join(BASE_DIR, "logs"))

# Creează folderele dacă nu există
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Log locația pentru debugging
print(f"📁 Data directory: {DATA_DIR}")
print(f"📂 Archive directory: {ARCHIVE_DIR}")
print(f"📋 Logs directory: {LOGS_DIR}")
print(f"✓ Both EXE and Python script use the SAME data directories")

# ================== BACKUP MANAGER INITIALIZATION ==================
# Auto-backup periodic al datelor locale
if BACKUP_MANAGER_AVAILABLE and BackupManager:
    try:
        BACKUP_MANAGER = BackupManager(
            data_dir=DATA_DIR,
            archive_dir=ARCHIVE_DIR,
            backup_interval=300  # Backup every 5 minutes
        )
        BACKUP_MANAGER.start()
        print("✅ Backup Manager initialized and started (every 5 minutes)")
    except Exception as e:
        print(f"⚠️ Error initializing Backup Manager: {e}")
        BACKUP_MANAGER = None
else:
    print("⚠️ Backup Manager not available")

# ================== SUPABASE SYNC CONFIGURATION ==================
# Sincronizare cloud cu Supabase PostgreSQL
SUPABASE_SYNC = None
if SUPABASE_MODULE_AVAILABLE:
    # Caută config în folderul aplicației sau în BASE_DIR
    config_paths = [
        os.path.join(os.path.dirname(__file__), "supabase_config.ini"),
        os.path.join(BASE_DIR, "supabase_config.ini"),
        "supabase_config.ini"
    ]
    
    config_found = None
    for config_path in config_paths:
        if os.path.exists(config_path):
            config_found = config_path
            break
    
    if config_found:
        SUPABASE_SYNC = SupabaseSync(config_found)
        print(f"📡 Supabase config: {config_found}")
    else:
        print("⚠️ supabase_config.ini nu găsit")
else:
    print("ℹ️ Aplicația rulează fără sincronizare cloud")

# ================== ACTION LOGGER INITIALIZATION ==================
# Inițializează action logger pentru logging automat pe Supabase
ACTION_LOGGER = None
if ActionLoggerNew and SUPABASE_SYNC and SUPABASE_SYNC.enabled:
    try:
        ACTION_LOGGER = ActionLoggerNew(SUPABASE_SYNC)
        print("✓ Action logger initialized for automatic logging")
        print(f"  📊 Logs table: {SUPABASE_SYNC.table_logs}")
        print(f"  🔗 Supabase: {SUPABASE_SYNC.url[:50]}...")
    except Exception as e:
        print(f"⚠️ Error initializing action logger: {e}")
        ACTION_LOGGER = None
else:
    reasons = []
    if not ActionLoggerNew:
        reasons.append("ActionLoggerNew module not loaded")
    if not SUPABASE_SYNC:
        reasons.append("SUPABASE_SYNC not configured")
    elif not SUPABASE_SYNC.enabled:
        reasons.append("SUPABASE_SYNC.enabled = False")
    print(f"⚠️ Action logger NOT initialized: {', '.join(reasons)}")

# ================== INSTITUTION PERMISSION MANAGER INITIALIZATION ==================
# Inițializează manager-ul de permisiuni per-instituție
INSTITUTION_PERM_MANAGER = None
if InstitutionPermissionManager and SUPABASE_SYNC and SUPABASE_SYNC.enabled:
    try:
        INSTITUTION_PERM_MANAGER = InstitutionPermissionManager(SUPABASE_SYNC, DATA_DIR)
        print("✓ Institution permission manager initialized")
    except Exception as e:
        print(f"⚠️ Error initializing institution permission manager: {e}")
        INSTITUTION_PERM_MANAGER = None

# ================== USERS & PERMISSIONS JSON MANAGER ==================
# Manages users and granular permissions in JSON format
# Syncs bidirectionally with Supabase discord_users table
USERS_PERMS_JSON_MANAGER = None
try:
    from users_permissions_json_manager import UsersPermissionsJsonManager
    if SUPABASE_SYNC and SUPABASE_SYNC.enabled:
        USERS_PERMS_JSON_MANAGER = UsersPermissionsJsonManager(
            supabase_url=SUPABASE_SYNC.url,
            supabase_key=SUPABASE_SYNC.key,
            data_dir=DATA_DIR
        )
        USERS_PERMS_JSON_MANAGER.ensure_json_exists()
        print("✓ Users permissions JSON manager initialized")
        print(f"  📋 JSON file: {DATA_DIR}/users_permissions.json")
    else:
        print("⚠️ Users permissions JSON manager skipped (Supabase not configured)")
except Exception as e:
    print(f"⚠️ Error initializing users permissions JSON manager: {e}")
    USERS_PERMS_JSON_MANAGER = None

# Git configuration - DEPRECATED (păstrat pentru compatibilitate)
# Folosește Supabase pentru sincronizare!
GIT_ENABLED = False
GIT_REPO = None
GIT_AUTHOR = "PunctajApp"
GIT_EMAIL = "app@punctaj.local"

# Inițializează Git repo în folderul datelor (Documents\PunctajManager)
if GIT_AVAILABLE:
    try:
        GIT_REPO = Repo(BASE_DIR)
        GIT_ENABLED = True
        print("✓ Git repo activ în Documents (DEPRECATED - folosește Supabase)")
    except (InvalidGitRepositoryError, NameError):
        try:
            print("Inițializez Git repository în Documents...")
            GIT_REPO = Repo.init(BASE_DIR)
            
            # Configurează remote la repo-ul GitHub
            try:
                origin = GIT_REPO.create_remote('origin', 'https://github.com/parjanul123/punctaj.git')
                print("✓ Git remote configurat")
            except:
                # Remote deja există
                pass
            
            GIT_ENABLED = True
        except Exception as e:
            print(f"Nu pot inițializa Git: {e}")
            GIT_ENABLED = False
else:
    print("ℹ️ Aplicația rulează fără suport Git")


# Ora = tabel principal, institutia = sub-tabel, angajat = rand
def city_dir(city):
    return os.path.join(DATA_DIR, city)


def institution_path(city, institution):
    return os.path.join(city_dir(city), f"{institution}.json")


def ensure_city(city):
    os.makedirs(city_dir(city), exist_ok=True)


def deduplicate_rows(rows):
    """
    Remove duplicate employees by DISCORD ID
    Keeps the first occurrence, removes subsequent duplicates
    Returns: deduplicated rows list
    """
    if not rows:
        return rows
    
    seen_discord = set()
    deduplicated = []
    duplicates_count = 0
    
    for row in rows:
        discord_id = row.get("DISCORD", "")
        
        if discord_id and discord_id in seen_discord:
            # This is a duplicate - skip it
            duplicates_count += 1
            emp_name = row.get("NUME IC", "Unknown")
            # Optionally log duplicates found
            # print(f"   ⚠️ Skipped duplicate: {emp_name} (Discord: {discord_id})")
        else:
            # First time seeing this ID - add it
            deduplicated.append(row)
            if discord_id:
                seen_discord.add(discord_id)
    
    if duplicates_count > 0:
        print(f"   🧹 Removed {duplicates_count} duplicate rows (by Discord ID)")
    
    return deduplicated


# ================== SUPABASE SYNC FUNCTIONS ==================
def supabase_upload(city, institution, json_data, file_path=None):
    """
    Upload date pe Supabase după salvare
    Sincronizează angajații cu Supabase din JSON local
    Include și logurile din folderul logs/
    """
    if not SUPABASE_EMPLOYEE_MANAGER_AVAILABLE:
        return {"status": "disabled"}

    try:
        # Extrage angajații din JSON și sincronizează cu Supabase
        rows = json_data.get("rows", [])
        city_id = json_data.get("city_id")
        institution_id = json_data.get("institution_id")
        
        if not city_id or not institution_id:
            # Dacă nu avem IDs, încearcă să le găsim
            try:
                city_obj = SUPABASE_EMPLOYEE_MANAGER.get_city_by_name(city)
                if city_obj:
                    inst_obj = SUPABASE_EMPLOYEE_MANAGER.get_institution_by_name(city_obj['id'], institution)
                    if inst_obj:
                        city_id = city_obj['id']
                        institution_id = inst_obj['id']
            except:
                pass
        
        if not city_id or not institution_id:
            print(f"⚠️ Eroare: Nu pot găsi city_id/institution_id pentru {city}/{institution}")
            return {"status": "error", "message": "Missing city/institution IDs"}
        
        # Sincronizează fiecare angajat
        synced = 0
        for row in rows:
            try:
                emp_data = SUPABASE_EMPLOYEE_MANAGER.format_employee_for_supabase(row)
                # Caută dacă angajatul deja există
                existing = SUPABASE_EMPLOYEE_MANAGER.get_employee_by_name(institution_id, row.get("NUME IC", ""))
                if existing:
                    # Update
                    SUPABASE_EMPLOYEE_MANAGER.update_employee(existing['id'], emp_data)
                else:
                    # Adaugă nou
                    SUPABASE_EMPLOYEE_MANAGER.add_employee(institution_id, emp_data)
                synced += 1
            except Exception as e:
                print(f"⚠️ Eroare sync angajat {row.get('NUME IC', 'Unknown')}: {e}")
        
        print(f"✓ Sincronizat {synced}/{len(rows)} angajați")
        
        # Upload logurile din folderul logs/ (organized by city/institution)
        try:
            import glob
            logs_uploaded = 0
            logs_dir = "logs"
            if os.path.exists(logs_dir):
                # Find all institution log files (logs/{city}/{institution}.json)
                institution_log_files = glob.glob(os.path.join(logs_dir, "*/*.json"))
                
                for log_file in institution_log_files:
                    # Skip global summary file
                    if "SUMMARY" in log_file:
                        continue
                    
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            logs_array = json.load(f)
                        
                        # logs_array should be a list of log entries
                        if not isinstance(logs_array, list):
                            logs_array = [logs_array]
                        
                        # Upload each log entry
                        for log_data in logs_array:
                            url = f"{SUPABASE_SYNC.url}/rest/v1/{SUPABASE_SYNC.table_logs}"
                            headers = {
                                'apikey': SUPABASE_SYNC.key,
                                'Authorization': f'Bearer {SUPABASE_SYNC.key}',
                                'Content-Type': 'application/json'
                            }
                            response = requests.post(url, json=log_data, headers=headers, timeout=5)
                            
                            if response.status_code in [200, 201]:
                                logs_uploaded += 1
                            else:
                                print(f"⚠️ Failed to upload log from {os.path.basename(log_file)}: HTTP {response.status_code}")
                        
                        # Delete file after successful upload of all logs
                        os.remove(log_file)
                        print(f"✓ All logs uploaded from: {log_file}")
                    except Exception as e:
                        print(f"⚠️ Eroare la upload logs din {log_file}: {e}")
                
                # Upload global summary
                summary_file = os.path.join(logs_dir, "SUMMARY_global.json")
                if os.path.exists(summary_file):
                    try:
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            summary_data = json.load(f)
                        
                        # Save summary as metadata or in a separate way
                        # For now, just mark it as uploaded
                        print(f"✓ Global summary marked for sync")
                    except Exception as e:
                        print(f"⚠️ Eroare la read summary: {e}")
                
                if logs_uploaded > 0:
                    print(f"✓ Uploadate {logs_uploaded} loguri total")
        except Exception as e:
            print(f"⚠️ Eroare uploadare loguri: {e}")
        
        # ===== SYNC INSTITUTION DATA TO SUPABASE DATA TABLE =====
        # This synchronizes the complete institution JSON to the "data" table
        if SUPABASE_SYNC:
            try:
                result = SUPABASE_SYNC.sync_data(city, institution, json_data)
                if result:
                    print(f"✅ Institution data synced to Supabase data table: {city}/{institution}")
                else:
                    print(f"⚠️ Failed to sync institution data to Supabase data table: {city}/{institution}")
            except Exception as e:
                print(f"⚠️ Error syncing institution data to Supabase: {e}")
        
        return {"status": "success" if synced > 0 else "no_data"}
    except Exception as e:
        print(f"❌ Eroare sincronizare Supabase: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# ================== PERMISSION CHECK FUNCTIONS ==================
def can_view_city(city_name):
    """Verifică dacă utilizatorul poate vedea orașul"""
    if not DISCORD_AUTH:
        return True  # Fără auth = acces complet
    
    return DISCORD_AUTH.can_view_city(city_name)


def can_edit_city(city_name):
    """Verifică dacă utilizatorul poate edita orașul"""
    if not DISCORD_AUTH:
        return True  # Fără auth = acces complet
    
    # Superuser și admin au acces complet
    if DISCORD_AUTH.is_admin() or DISCORD_AUTH.get_role() == "superuser":
        return True
    
    return DISCORD_AUTH.can_edit_city_granular(city_name)


def can_perform_action(action_id, city_name=None):
    """
    Verifică dacă utilizatorul poate efectua o acțiune specifică
    
    Args:
        action_id: ID-ul acțiunii (ex: "add_city", "edit_institution", etc.)
        city_name: Opțional - orașul pentru care se verifică permisiunea
    
    Returns:
        bool: True dacă utilizatorul poate efectua acțiunea
    """
    if not DISCORD_AUTH:
        return True  # Fără auth = acces complet
    
    return DISCORD_AUTH.can_perform_action(action_id, city_name)


def is_read_only_user():
    """Verifică dacă utilizatorul e read-only (viewer role)"""
    if not DISCORD_AUTH:
        return False
    

def check_institution_permission(city, institution, permission_type):
    """
    Verifică dacă utilizatorul curent are permisiune pentru o acțiune specifică pe o instituție
    
    Args:
        city: Orașul
        institution: Instituția
        permission_type: Tipul de permisiune ('can_view', 'can_edit', 'can_delete')
    
    Returns:
        bool: True dacă utilizatorul are permisiunea, False altfel
    """
    # Superuserii au acces la toate
    if DISCORD_AUTH and DISCORD_AUTH.is_superuser():
        return True
    
    # Verifică permisiunile granulare
    if INSTITUTION_PERM_MANAGER and DISCORD_AUTH:
        discord_id = DISCORD_AUTH.get_discord_id()
        if discord_id:
            return INSTITUTION_PERM_MANAGER.check_user_institution_permission(
                discord_id,
                city,
                institution,
                permission_type
            )
    
    # Default: acces dacă nu e configurat sistemul de permisiuni
    return True
    return DISCORD_AUTH.get_user_role() == 'viewer'


def get_accessible_cities():
    """
    Returnează lista orașelor la care utilizatorul are acces
    None = toate orașele
    """
    if not DISCORD_AUTH:
        return None  # Fără auth = toate orașele
    
    return DISCORD_AUTH.get_accessible_cities()


# Alias pentru compatibilitate
def can_use_button(action_id, city_name=None):
    """
    Alias pentru can_perform_action() pentru compatibilitate cu cod vechi
    """
    return can_perform_action(action_id, city_name)


def supabase_sync_all():
    """
    Sincronizează toate datele din cloud la pornire
    """
    if not SUPABASE_SYNC or not SUPABASE_SYNC.enabled:
        return {"status": "disabled"}
    
    if not SUPABASE_SYNC.sync_on_startup:
        return {"status": "sync_disabled"}
    
    try:
        result = SUPABASE_SYNC.sync_all_from_cloud(DATA_DIR)
        return result
    except Exception as e:
        print(f"❌ Eroare sincronizare din cloud: {e}")
        return {"status": "error", "message": str(e)}


# ================== GIT SYNC FUNCTIONS (DEPRECATED) ==================
def git_commit_and_push(file_path, message):
    """
    DEPRECATED: Folosește supabase_upload() în loc de Git
    Păstrat pentru compatibilitate backwards
    """
    if not GIT_ENABLED or not GIT_REPO:
        return
    
    try:
        # Convertește path-ul la relativ față de BASE_DIR pentru Git
        rel_path = os.path.relpath(file_path, BASE_DIR)
        
        # Adaugă fișierul la staging
        GIT_REPO.index.add([rel_path])
        
        # Face commit
        GIT_REPO.index.commit(message, author=None)
        
        # Push la remote (dacă există)
        try:
            origin = GIT_REPO.remote('origin')
            origin.push()
            print(f"✓ Git push: {rel_path}")
        except:
            # Dacă nu e setup remote, doar commit local
            print(f"✓ Git commit (local): {rel_path}")
    
    except Exception as e:
        print(f"✗ Git error: {str(e)}")


def git_pull_and_sync():
    """Face pull de pe Git și sincronizează datele locale"""
    if not GIT_ENABLED or not GIT_REPO:
        return
    
    try:
        # Încearcă să facă pull
        try:
            origin = GIT_REPO.remote('origin')
            origin.pull()
            print("✓ Git pull: Sincronizare cu serverul")
            return True
        except:
            # Dacă nu e setup remote, skip
            return False
    
    except Exception as e:
        print(f"✗ Git pull error: {str(e)}")
        return False


def ensure_institution(city, institution):
    ensure_city(city)
    path = institution_path(city, institution)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)


def load_institution(city, institution):
    """
    Load institution data - PRIORITIZE LOCAL FILE FIRST
    Falls back to Supabase if local file doesn't exist
    """
    
    # PRIORITIZE LOCAL JSON FIRST
    local_path = institution_path(city, institution)
    if os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Asigură că avem structura corectă
            if isinstance(data, list):
                rows = deduplicate_rows(data)
                return {
                    "columns": ["DISCORD", "RANK", "PUNCTAJ"],
                    "ranks": {},
                    "rows": rows,
                    "version": 1,
                    "source": "local"
                }
            
            # Asigură rankuri și rânduri
            if "ranks" not in data:
                data["ranks"] = {}
            if "rows" not in data:
                data["rows"] = []
            if "version" not in data:
                data["version"] = 1
            
            # Deduplicate rows
            if data["rows"]:
                data["rows"] = deduplicate_rows(data["rows"])
            
            data["source"] = "local"
            return data
        except Exception as e:
            print(f"⚠️ Error loading local JSON {city}/{institution}: {e}")
            # Fall through to Supabase
    
    # FALLBACK: Try Supabase if local doesn't exist
    if SUPABASE_EMPLOYEE_MANAGER_AVAILABLE:
        try:
            city_obj = SUPABASE_EMPLOYEE_MANAGER.get_city_by_name(city)
            if city_obj:
                institution_obj = SUPABASE_EMPLOYEE_MANAGER.get_institution_by_name(city_obj['id'], institution)
                if institution_obj:
                    employees = SUPABASE_EMPLOYEE_MANAGER.get_employees_by_institution(institution_obj['id'])
                    
                    rows = []
                    seen_discord = set()
                    for emp in employees:
                        formatted = SUPABASE_EMPLOYEE_MANAGER.format_employee_for_app(emp)
                        discord_id = formatted.get("DISCORD", "")
                        if discord_id and discord_id not in seen_discord:
                            rows.append(formatted)
                            seen_discord.add(discord_id)
                        elif not discord_id:
                            rows.append(formatted)
                    
                    rows = deduplicate_rows(rows)
                    
                    result = {
                        "columns": ["DISCORD", "NUME IC", "SERIE DE BULETIN", "RANK", "ROLE", "PUNCTAJ", "ULTIMA_MOD"],
                        "ranks": {
                            "1": "Offiter",
                            "2": "Caporal",
                            "3": "Sergent",
                            "4": "Plutonier",
                            "5": "Locotenent Instructor",
                            "6": "Sherif Adjunct",
                            "7": "Sherif"
                        },
                        "rows": rows,
                        "version": 2,
                        "source": "supabase",
                        "city_id": city_obj['id'],
                        "institution_id": institution_obj['id']
                    }
                    
                    # Save to local for future use
                    try:
                        path = institution_path(city, institution)
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(result, f, indent=2, ensure_ascii=False)
                    except:
                        pass
                    
                    return result
        except Exception as e:
            print(f"⚠️ Error loading from Supabase: {e}")
    
    # DEFAULT: Return empty structure
    return {
        "columns": ["DISCORD", "NUME IC", "SERIE DE BULETIN", "RANK", "ROLE", "PUNCTAJ", "ULTIMA_MOD"],
        "ranks": {
            "1": "Offiter",
            "2": "Caporal",
            "3": "Sergent",
            "4": "Plutonier",
            "5": "Locotenent Instructor",
            "6": "Sherif Adjunct",
            "7": "Sherif"
        },
        "rows": [],
        "version": 2,
        "source": "none"
    }


# ================== CLOUD-FIRST SYNC FUNCTIONS ==================

def sync_cloud_first_delete(city, institution, deleted_names, parent_window=None):
    """
    CLOUD-FIRST SYNC: Sincronizează ștergerea imediat în cloud
    - Delete local → Salvează → Sincronizează cloud
    - Feedback imediat și retry logic dacă eșuează
    """
    if not SUPABASE_SYNC or not SUPABASE_SYNC.enabled:
        # Cloud disabled - doar local
        messagebox.showinfo(
            "Ștergere Locală",
            f"✅ Angajați șterși local (cloud sync dezactivat):\n"
            f"{', '.join(deleted_names[:3])}" + 
            ("..." if len(deleted_names) > 3 else "")
        )
        return
    
    # Crează progress dialog
    sync_dialog = tk.Toplevel(parent_window if parent_window else root)
    sync_dialog.title("Sincronizare Cloud")
    sync_dialog.geometry("400x200")
    sync_dialog.grab_set()
    sync_dialog.transient(parent_window if parent_window else root)
    
    # Centrare
    sync_dialog.update_idletasks()
    x = (sync_dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (sync_dialog.winfo_screenheight() // 2) - (200 // 2)
    sync_dialog.geometry(f"+{x}+{y}")
    
    # Status label
    status_label = tk.Label(
        sync_dialog,
        text="🔄 Sincronizare în curs...",
        font=("Segoe UI", 11, "bold"),
        fg="#2196F3"
    )
    status_label.pack(pady=20)
    
    # Progress bar
    progress = ttk.Progressbar(sync_dialog, mode="indeterminate", length=300)
    progress.pack(pady=10)
    progress.start()
    
    # Info label
    info_label = tk.Label(
        sync_dialog,
        text=f"Ștergere: {', '.join(deleted_names[:3])}" +  
             ("..." if len(deleted_names) > 3 else ""),
        font=("Segoe UI", 9),
        fg="#666"
    )
    info_label.pack(pady=10)
    
    sync_dialog.update()
    
    try:
        # Încarcă datele curente
        inst_data = load_institution(city, institution)
        file_path = institution_path(city, institution)
        
        # Incrementează versione pentru cloud-first tracking
        inst_data["version"] = inst_data.get("version", 1) + 1
        inst_data["last_synced"] = datetime.now().isoformat()
        inst_data["pending_sync"] = False
        
        # Sincronizează în cloud
        result = supabase_upload(city, institution, inst_data, file_path)
        
        sync_dialog.destroy()
        
        if result.get("status") == "success":
            messagebox.showinfo(
                "✅ Sincronizare Completă",
                f"Angajații au fost șterși și sincronizați în cloud:\n\n" +
                f"{', '.join(deleted_names[:3])}" + 
                ("..." if len(deleted_names) > 3 else "") +
                f"\n\nVersiune: v{inst_data['version']}\n"
                f"Status: SINCRONIZAT"
            )
        else:
            # Ștergerea a eșuat pe cloud - marcheaza pendin g_sync
            inst_data["pending_sync"] = True
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(inst_data, f, indent=4, ensure_ascii=False)
            
            messagebox.showwarning(
                "⚠️ Sincronizare Eșuată",
                f"Angajații au fost șterși local, dar sincronizarea în cloud a EȘUAT:\n\n" +
                f"{', '.join(deleted_names[:3])}" +
                ("..." if len(deleted_names) > 3 else "") +
                f"\n\n🔧 Acțiune necesară:\n" +
                f"1. Verifică conexiunea internet\n" +
                f"2. Apasă ☁️ Sincronizare Cloud din meniu\n" +
                f"3. Alege 📤 UPLOAD pentru a retenta"
            )
    except Exception as e:
        sync_dialog.destroy()
        
        print(f"❌ Eroare sync cloud-first: {e}")
        messagebox.showerror(
            "❌ Eroare Sincronizare",
            f"Ștergerea locală: ✅ Reușit\n"
            f"Sincronizare cloud: ❌ Eșuat\n\n"
            f"Eroare: {str(e)[:100]}\n\n"
            f"Apasă ☁️ Sincronizare Cloud din meniu"
        )


def save_institution(city, institution, tree, update_timestamp=False, updated_items=None, skip_logging=False):
    # Verifică permisiuni Discord
    if is_read_only_user():
        messagebox.showerror(
            "Acces Interzis",
            "Contul tău este read-only.\n\n"
            "Nu poți salva modificări."
        )
        return
    
    if not can_edit_city(city):
        messagebox.showerror(
            "Acces Interzis",
            f"Nu ai permisiunea să editezi orașul: {city}\n\n"
            f"Contactează un administrator pentru acces."
        )
        return
    
    # Încarcă datele existente pentru a păstra rankurile și timestamp-ul
    existing_data = load_institution(city, institution)
    ranks_map = existing_data.get("ranks", {})
    ranks_desc = existing_data.get("rankuri_desc", "")
    last_update = existing_data.get("last_punctaj_update", "")
    existing_rows = {str(row.get("DISCORD", "")): row for row in existing_data.get("rows", [])}
    
    # CLOUD-FIRST SYNC: Păstrează versioning și sync metadata
    current_version = existing_data.get("version", 1)
    last_synced = existing_data.get("last_synced")
    pending_sync = existing_data.get("pending_sync", False)
    
    # Dacă e o modificare de punctaj, actualizează timestamp-ul global
    if update_timestamp:
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Asigură că ULTIMA_MOD este în coloane
    columns = list(tree.columns)
    if "ULTIMA_MOD" not in columns:
        columns.append("ULTIMA_MOD")
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {
        "columns": columns,
        "ranks": ranks_map,
        "rankuri_desc": ranks_desc,
        "last_punctaj_update": last_update,
        # CLOUD-FIRST SYNC: Versioning info
        "version": current_version,
        "last_synced": last_synced,
        "pending_sync": pending_sync,
        "rows": []
    }
    
    for item in tree.get_children():
        values = list(tree.item(item, "values"))
        row_dict = dict(zip(tree.columns, values))
        
        # Dacă rândul este în updated_items, actualizează ULTIMA_MOD
        if updated_items and item in updated_items:
            row_dict["ULTIMA_MOD"] = current_timestamp
        else:
            # Păstrează ULTIMA_MOD vechia dacă nu e actualizat
            discord_val = row_dict.get("DISCORD", "")
            if discord_val in existing_rows:
                row_dict["ULTIMA_MOD"] = existing_rows[discord_val].get("ULTIMA_MOD", "")
        
        data["rows"].append(row_dict)
    
    file_path = institution_path(city, institution)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # LOG: Salvare date
    log_json_action(file_path, "edit", {
        "rows_count": len(data.get("rows", [])),
        "updated_items": len(updated_items) if updated_items else 0,
        "version": data.get("version")
    })
    
    # ACTION LOGGER: Log institution data save - ONLY if there are actual updates
    # Skip if skip_logging=True (already logged by calling function like log_edit_points)
    if ACTION_LOGGER and updated_items and not skip_logging:
        try:
            discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else "unknown"
            discord_username = DISCORD_AUTH.user_info.get('username', discord_id) if DISCORD_AUTH and DISCORD_AUTH.user_info else discord_id
            
            print(f"🔍 Logging from save_institution: discord_id={discord_id}, discord_username={discord_username}")
            
            # For each updated item, detect what field changed
            for item in updated_items:
                values = list(tree.item(item, "values"))
                new_row = dict(zip(tree.columns, values))
                entity_name = new_row.get("NUME IC", new_row.get("DISCORD", "Unknown"))
                entity_id = new_row.get("DISCORD", "")
                
                # Find the old values from existing_rows
                discord_val = new_row.get("DISCORD", "")
                if discord_val in existing_rows:
                    old_row = existing_rows[discord_val]
                    
                    # Check which fields changed and log each one
                    # Only check fields that actually exist in the data
                    fields_to_check = ["RANK", "ROLE", "PUNCTAJ", "NUME IC", "DISCORD", "SERIE DE BULETIN"]
                    changes_found = []
                    
                    for field in fields_to_check:
                        old_val = str(old_row.get(field, ""))
                        new_val = str(new_row.get(field, ""))
                        
                        if old_val != new_val:
                            changes_found.append({
                                "field": field,
                                "old": old_val,
                                "new": new_val
                            })
                    
                    # Log each field change separately for detailed audit trail
                    if changes_found:
                        for change in changes_found:
                            ACTION_LOGGER.log_institution_field_edit(
                                discord_id=discord_id,
                                city=city,
                                institution_name=institution,
                                employee_name=entity_name,
                                field_name=change["field"],
                                old_value=change["old"],
                                new_value=change["new"],
                                discord_username=discord_username,
                                entity_id=entity_id
                            )
        except Exception as e:
            print(f"⚠️ Error logging institution save: {e}")
    
    # Sincronizare Supabase (înlocuiește Git)
    try:
        result = supabase_upload(city, institution, data, file_path)
        if result.get("status") == "success":
            print(f"✅ Auto-sync UPLOAD: {city}/{institution} → Supabase")
        else:
            print(f"⚠️  Auto-sync UPLOAD failed: {city}/{institution} (will retry later)")
    except Exception as e:
        print(f"❌ Auto-sync error: {e}")
    
    # Auto-commit și push la Git (DEPRECATED)
    git_commit_and_push(file_path, f"Update {city}/{institution}")


def delete_institution(city, institution):
    path = institution_path(city, institution)
    if os.path.exists(path):
        os.remove(path)
        # Commit delete-ul la Git
        if GIT_ENABLED and GIT_REPO:
            try:
                GIT_REPO.index.remove([path])
                GIT_REPO.index.commit(f"Delete {city}/{institution}")
                print(f"✓ Git: Ștergere {path}")
            except:
                pass


def delete_city(city):
    path = city_dir(city)
    if os.path.exists(path):
        shutil.rmtree(path)


# ================== LOGGING HELPER ==================
def log_json_action(file_path, action, details=None):
    """
    Logare acțiune pe JSON - ce user a modificat ce și când
    
    Args:
        file_path (str): Path-ul JSON-ului
        action (str): Acțiunea (edit, delete, create, upload, download)
        details (dict): Detalii suplimentare
    """
    try:
        if not LOGGER_AVAILABLE or not LOGGER:
            return
        
        # Obține Discord ID și nume
        discord_id = "UNKNOWN"
        discord_name = "UNKNOWN"
        
        if DISCORD_AUTH and DISCORD_AUTH.user_info:
            discord_id = str(DISCORD_AUTH.user_info.get("id", "UNKNOWN"))
            discord_name = DISCORD_AUTH.user_info.get("username", "UNKNOWN")
            if DISCORD_AUTH.user_info.get("discriminator"):
                discord_name = f"{discord_name}#{DISCORD_AUTH.user_info.get('discriminator')}"
        
        # Path relativ
        rel_path = file_path
        if file_path.startswith(DATA_DIR):
            rel_path = os.path.relpath(file_path, DATA_DIR)
        
        LOGGER.log_action(rel_path, discord_id, discord_name, action, details)
    except Exception as e:
        print(f"⚠️ Logging error: {e}")


# ================== DISCORD AUTHENTICATION FUNCTIONS ==================
def discord_login():
    """Discord authentication at startup - MANDATORY"""
    global DISCORD_AUTH
    
    # Discord authentication is REQUIRED to use the application
    if not DISCORD_AUTH_ENABLED or not DISCORD_CONFIG.get('CLIENT_ID'):
        print("❌ ERROR: Discord authentication is REQUIRED but not configured")
        
        messagebox.showerror(
            "Discord Authentication Required",
            "❌ EROARE: Discord authentication este OBLIGATORIU!\n\n"
            "Aplicația necesită autentificare cu Discord pentru a accesa datele.\n\n"
            "SETUP OBLIGATORIU:\n"
            "1. Mergi la https://discord.com/developers/applications\n"
            "2. Creează o nouă aplicație Discord\n"
            "3. Copiază CLIENT_ID și CLIENT_SECRET\n"
            "4. Editează discord_config.ini cu credențialele tale\n"
            "5. Redeschide aplicația\n\n"
            "Fără Discord, nu poți folosi aplicația!"
        )
        
        # Open Discord Developer Portal
        import webbrowser
        webbrowser.open("https://discord.com/developers/applications")
        
        # Exit application - Discord is mandatory
        print("Aplicația se închide - Discord authentication este obligatoriu")
        sys.exit(1)
    
    try:
        # Create Discord auth instance
        DISCORD_AUTH = DiscordAuth(
            client_id=DISCORD_CONFIG['CLIENT_ID'],
            client_secret=DISCORD_CONFIG['CLIENT_SECRET'],
            redirect_uri=DISCORD_CONFIG['REDIRECT_URI']
        )
        
        # Check if user is already authenticated
        if DISCORD_AUTH.is_authenticated():
            username = DISCORD_AUTH.user_info.get('username', 'Unknown')
            user_id = DISCORD_AUTH.user_info.get('id', '')
            
            print(f"✅ Discord: Already authenticated as {username} (ID: {user_id})")
            # Proceed silently - no messagebox needed
            return True
        
        # Need to authenticate - start automatic login
        print("🔐 Starting MANDATORY Discord authentication...")
        
        # Show progress window
        login_window = tk.Toplevel(root)
        login_window.title("🔐 Discord Login - OBLIGATORIU")
        login_window.geometry("550x400")
        login_window.grab_set()
        login_window.transient(root)
        login_window.resizable(False, False)
        
        # Center window
        login_window.update_idletasks()
        x = (login_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (login_window.winfo_screenheight() // 2) - (400 // 2)
        login_window.geometry(f"+{x}+{y}")
        
        # Make main window closable during login (user can X to close app, even during auth)
        def close_app_cleanly():
            if messagebox.askyesno("Închide", "Sigur vrei să inchizi aplicația?"):
                # Stop backup manager if running
                global PERMISSION_SYNC_MANAGER, REALTIME_SYNC_MANAGER, BACKUP_MANAGER
                if BACKUP_MANAGER:
                    try:
                        BACKUP_MANAGER.stop()
                        print("✅ Backup manager stopped")
                    except Exception as e:
                        print(f"⚠️ Error stopping backup manager: {e}")
                
                # Stop permission sync if running
                if PERMISSION_SYNC_MANAGER:
                    try:
                        PERMISSION_SYNC_MANAGER.stop()
                        print("✅ Permission sync manager stopped")
                    except Exception as e:
                        print(f"⚠️ Error stopping permission sync: {e}")
                
                # Stop real-time sync if running
                if REALTIME_SYNC_MANAGER:
                    try:
                        REALTIME_SYNC_MANAGER.stop()
                        print("✅ Real-time sync manager stopped")
                    except Exception as e:
                        print(f"⚠️ Error stopping real-time sync: {e}")
                
                root.quit()
        
        root.protocol("WM_DELETE_WINDOW", close_app_cleanly)
        login_window.protocol("WM_DELETE_WINDOW", lambda: (
            messagebox.showinfo(
                "Inchide",
                "Aplicația se va inchide deoarece autentificarea cu Discord\n"
                "este în progress."
            ),
            login_window.destroy(),
            root.quit()
        ))
        
        # Header with Discord color
        header = tk.Frame(login_window, bg="#5865F2", height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔐 Autentificare Discord - OBLIGATORIE",
            font=("Segoe UI", 14, "bold"),
            bg="#5865F2",
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            header,
            text="Aplicația necesită login cu Discord pentru acces",
            font=("Segoe UI", 10),
            bg="#5865F2",
            fg="#e0e0e0"
        ).pack(pady=5)
        
        # Content frame
        content = tk.Frame(login_window, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            content,
            text="Se conectează la Discord...",
            font=("Segoe UI", 13, "bold"),
            bg="white"
        ).pack(pady=10)
        
        tk.Label(
            content,
            text="Se va deschide o fereastră de browser pentru autentificare.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#555",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Status label
        status_label = tk.Label(
            content,
            text="⏳ Se pregătește serverul de autentificare...",
            font=("Segoe UI", 10),
            bg="white",
            fg="#666"
        )
        status_label.pack(pady=10)
        
        # Progress bar
        progress = ttk.Progressbar(
            content,
            length=300,
            mode='indeterminate'
        )
        progress.pack(pady=10)
        progress.start()
        
        # Info frame
        info_frame = tk.Frame(content, bg="#f0f9ff", relief=tk.RIDGE, borderwidth=2)
        info_frame.pack(fill=tk.X, pady=15, padx=10)
        
        tk.Label(
            info_frame,
            text="🔒 SIGUR & SECURIZAT:",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f9ff",
            fg="#2196F3"
        ).pack(anchor="w", padx=10, pady=(10, 2))
        
        tk.Label(
            info_frame,
            text="• Datele tale nu sunt niciodată partajate\n"
                "• Citim DOAR username și Discord ID\n"
                "• Autentificare securizată prin Discord OAuth2",
            font=("Segoe UI", 8),
            bg="#f0f9ff",
            fg="#555",
            justify=tk.LEFT
        ).pack(anchor="w", padx=10, pady=(2, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(content, bg="white")
        buttons_frame.pack(pady=10)
        
        # Cancel button - BUT NOT REALLY (it must authenticate)
        cancel_login = [False]
        
        def cannot_cancel():
            # Discord authentication is MANDATORY
            result = messagebox.showwarning(
                "Discord Obligatoriu",
                "❌ Discord autentificarea este OBLIGATORIE!\n\n"
                "Nu poți folosi aplicația fără autentificare cu Discord.\n\n"
                "Deschide browserul și completează autentificarea,\n"
                "sau închide aplicația."
            )
        
        tk.Button(
            buttons_frame,
            text="❌ Anulează (se va închide)",
            bg="#f44336",
            fg="white",
            font=("Segoe UI", 9),
            command=cannot_cancel
        ).pack(side=tk.LEFT, padx=5)
        
        def do_login():
            try:
                if cancel_login[0]:
                    return False
                
                status_label.config(text="📱 Se deschide browserul de autentificare...")
                login_window.update()
                
                # Start OAuth2 server and open browser
                if DISCORD_AUTH.start_oauth_server():
                    progress.stop()
                    status_label.config(
                        text="✅ Autentificare reușită!",
                        fg="#4CAF50"
                    )
                    login_window.update()
                    
                    username = DISCORD_AUTH.user_info.get('username', 'User')
                    user_id = DISCORD_AUTH.user_info.get('id', '')
                    user_role = DISCORD_AUTH.get_user_role()
                    
                    print(f"✅ Discord authenticated as: {username} (ID: {user_id})")
                    print(f"   📊 Role: {user_role.upper()}")
                    print(f"   👑 Is Superuser: {DISCORD_AUTH._is_superuser}")
                    print(f"   🛡️  Is Admin: {DISCORD_AUTH._is_admin}")
                    
                    # Initialize permission sync manager
                    global PERMISSION_SYNC_MANAGER
                    if PERMISSION_SYNC_AVAILABLE and SUPABASE_SYNC:
                        try:
                            PERMISSION_SYNC_MANAGER = PermissionSyncManager(
                                supabase_sync=SUPABASE_SYNC,
                                discord_auth=DISCORD_AUTH,
                                users_perms_json_manager=USERS_PERMS_JSON_MANAGER,
                                sync_interval=5  # Sync every 5 seconds
                            )
                            DISCORD_AUTH.set_permission_sync_manager(PERMISSION_SYNC_MANAGER)
                            PERMISSION_SYNC_MANAGER.start()
                            print("✅ Permission sync manager initialized and started")
                            print("   📥 Auto-sync: Permisiunile se vor descarcar la fiecare 5 secunde")
                        except Exception as e:
                            print(f"⚠️ Failed to initialize permission sync: {e}")
                    
                    # Initialize real-time cloud sync manager
                    global REALTIME_SYNC_MANAGER
                    if REALTIME_SYNC_AVAILABLE and SUPABASE_SYNC:
                        try:
                            REALTIME_SYNC_MANAGER = RealTimeSyncManager(
                                supabase_sync=SUPABASE_SYNC,
                                data_dir=DATA_DIR,
                                sync_interval=30  # Sync every 30 seconds
                            )
                            REALTIME_SYNC_MANAGER.start()
                            print("✅ Real-time cloud sync manager initialized and started")
                        except Exception as e:
                            print(f"⚠️ Failed to initialize real-time sync: {e}")
                    
                    # 🌐 START WEBSOCKET REAL-TIME SYNC
                    if SUPABASE_SYNC and hasattr(SUPABASE_SYNC, 'start_realtime_sync'):
                        try:
                            SUPABASE_SYNC.start_realtime_sync()
                            print("🔌 WebSocket real-time sync activated")
                            print("   📱 Changes on other devices appear instantly!")
                        except Exception as e:
                            print(f"⚠️  WebSocket startup warning: {e}")
                    
                    # ⭐ AUTOCORRECT: Download user permissions from Supabase for client
                    print(f"\n📥 Descarcă permisiunile utilizatorului din cloud...")
                    if USERS_PERMS_JSON_MANAGER:
                        try:
                            success = USERS_PERMS_JSON_MANAGER.download_from_cloud()
                            if success:
                                status_label.config(text="✅ Permisiuni descărcate din cloud!", fg="#4CAF50")
                                print("✅ Permisiunile utilizatorului au fost descărcate din Supabase")
                                
                                # ⭐ IMPORTANT: Reload cache after download
                                if DISCORD_AUTH:
                                    DISCORD_AUTH.reload_granular_permissions_from_json()
                                    print("✅ Cache-ul de permisiuni a fost reîncărcat")
                            else:
                                print("⚠️ Nu am putut descărca permisiunile din Supabase")
                                status_label.config(text="⚠️ Permisiuni: parțial descărcate", fg="#FF9800")
                        except Exception as e:
                            print(f"⚠️ Eroare la descarcarea permisiunilor: {e}")
                            status_label.config(text="⚠️ Eroare permisiuni - va continua", fg="#FF9800")
                    else:
                        print("⚠️ Users Permissions Manager nu e disponibil")
                    
                    login_window.update()
                    
                    # CLOSE the login window after delay
                    root.after(1500, lambda: login_window.destroy())
                    
                    messagebox.showinfo(
                        "✅ Bun venit!",
                        f"🎉 Autentificare reușită!\n\n"
                        f"👤 Utilizator: {username}\n"
                        f"🔒 ID Discord: {user_id}\n"
                        f"📊 Rol: {user_role.upper()}\n\n"
                        f"Aplicația se va deschide acum."
                    )
                    
                    # Refresh UI to show permissions and role
                    root.after(500, refresh_discord_section)
                    root.after(600, refresh_admin_buttons)
                    
                    print(f"✅ Authenticated as {username} - Refreshing UI...")
                    return True
                else:
                    progress.stop()
                    status_label.config(
                        text="❌ Autentificare eșuată sau timeout",
                        fg="#F44336"
                    )
                    login_window.update()
                    
                    messagebox.showerror(
                        "❌ Autentificare Eșuată",
                        "Autentificarea Discord a EȘUAT.\n\n"
                        "Posibile cauze:\n"
                        "• Browser-ul s-a închis înainte de finalizare\n"
                        "• Conexiune internet întreruptă\n"
                        "• Timeout pe serverul de autentificare\n\n"
                        "Încearcă din nou sau contactează administatorul."
                    )
                    
                    # Retry option
                    if messagebox.askyesno(
                        "Reîncercă",
                        "Vrei să încerci din nou autentificarea?"
                    ):
                        status_label.config(
                            text="⏳ Se pregătește serverul de autentificare...",
                            fg="#666"
                        )
                        progress.start()
                        login_window.update()
                        root.after(500, do_login)
                    else:
                        # Close application - Discord is MANDATORY
                        login_window.destroy()
                        root.quit()
                        sys.exit(1)
                    
                    return False
                    
            except Exception as e:
                progress.stop()
                status_label.config(text=f"❌ Eroare: {str(e)}", fg="#F44336")
                login_window.update()
                print(f"❌ Login error: {e}")
                
                messagebox.showerror(
                    "❌ Eroare de Autentificare",
                    f"A apărut o eroare:\n\n{str(e)[:200]}\n\n"
                    "Discord autentificarea este OBLIGATORIE."
                )
                
                if messagebox.askyesno("Reîncercă", "Vrei să încerci din nou?"):
                    status_label.config(
                        text="⏳ Se pregătește serverul de autentificare...",
                        fg="#666"
                    )
                    progress.start()
                    login_window.update()
                    root.after(500, do_login)
                else:
                    login_window.destroy()
                    root.quit()
                    sys.exit(1)
                
                return False
        
        # Start automatic login immediately
        root.after(100, do_login)
        
        return True
        
    except Exception as e:
        print(f"❌ Discord auth error: {e}")
        import traceback
        traceback.print_exc()
        
        messagebox.showerror(
            "❌ EROARE CRITICĂ",
            f"Eroare inițializare Discord autentificare:\n\n{e}\n\n"
            "Verifică dacă discord_config.ini este configurat corect:\n"
            "1. CLIENT_ID\n"
            "2. CLIENT_SECRET\n"
            "3. REDIRECT_URI\n\n"
            "Discord autentificarea este OBLIGATORIE.\n"
            "Aplicația se va închide."
        )
        print("Closing application - Discord authentication is mandatory")
        root.quit()
        sys.exit(1)


def discord_logout():
    """Logout from Discord"""
    global DISCORD_AUTH
    
    if DISCORD_AUTH and DISCORD_AUTH.is_authenticated():
        DISCORD_AUTH.logout()
        refresh_discord_section()  # Refresh UI after logout
        messagebox.showinfo("Discord Logout", "You have been logged out from Discord")
        print("Discord logged out")
    else:
        messagebox.showinfo("Discord", "You are not logged in with Discord")


def show_discord_profile():
    """Show current Discord user profile"""
    if not DISCORD_AUTH or not DISCORD_AUTH.is_authenticated():
        messagebox.showinfo("Discord Profile", "Not authenticated with Discord")
        return
    
    user = DISCORD_AUTH.user_info
    username = user.get('username', 'Unknown')
    user_id = user.get('id', 'N/A')
    email = user.get('email', 'N/A')
    user_role = DISCORD_AUTH.get_user_role()
    
    # Permission descriptions
    permissions = {
        'admin': 'Full access - can manage users and all operations',
        'user': 'Can add, edit, and delete institutions and employees',
        'viewer': 'Read-only access - cannot make modifications'
    }
    
    role_permission = permissions.get(user_role.lower(), 'Unknown role')
    
    profile_text = f"""
Discord Profile

Username: {username}
User ID: {user_id}
Email: {email}
Role: {user_role.upper()}

Permissions: {role_permission}

Token Status: Valid
    """
    
    messagebox.showinfo("Discord Profile", profile_text)

# ================== UI ==================
root = tk.Tk()
root.title("Manager punctaj - orase / institutii / angajati")

# Responsive window sizing based on screen resolution
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()

# Calculate responsive size: 85% of screen but not less than min and not more than max
responsive_width = max(800, min(1400, int(screenwidth * 0.85)))
responsive_height = max(600, min(900, int(screenheight * 0.80)))

root.geometry(f"{responsive_width}x{responsive_height}")
root.minsize(800, 600)
root.resizable(True, True)

# Import admin panel
try:
    from admin_panel import AdminPanel
    ADMIN_PANEL_AVAILABLE = True
except Exception as e:
    ADMIN_PANEL_AVAILABLE = False
    print(f"⚠️ Admin panel nu este disponibil: {e}")

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", rowheight=28)
style.configure("Treeview.Heading", anchor="center")

# ================== LAYOUT ==================
main = tk.Frame(root)
main.pack(fill="both", expand=True)

# -------- SIDEBAR --------
sidebar = tk.Frame(main, width=200, bg="#f0f0f0")
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(sidebar, text="Orașe", font=("Segoe UI", 12, "bold"), bg="#f0f0f0").pack(pady=20)

btn_add_tab = tk.Button(sidebar, text="➕ Adaugă oraș", width=18)
btn_add_tab.pack(pady=8)
# Verificăm permisiunea pentru adăugare oraș - numai user și admin
if is_read_only_user():
    btn_add_tab.config(state='disabled')

btn_edit_tab = tk.Button(sidebar, text="✏️ Editează oraș", width=18)
btn_edit_tab.pack(pady=8)
# Verificăm permisiunea pentru editare oraș - numai user și admin
if is_read_only_user():
    btn_edit_tab.config(state='disabled')

btn_del_tab = tk.Button(sidebar, text="❌ Șterge oraș", width=18)
btn_del_tab.pack(pady=8)
# Verificăm permisiunea pentru ștergere oraș - numai user și admin
if is_read_only_user():
    btn_del_tab.config(state='disabled')

# Separator
tk.Frame(sidebar, height=2, bg="#cccccc").pack(fill=tk.X, pady=15, padx=10)

# Container pentru Discord user section (va fi populat după autentificare)
discord_section_container = tk.Frame(sidebar, bg="#f0f0f0")
discord_section_container.pack(fill=tk.X, padx=5, pady=10)

def open_backup_manager():
    """Open Backup Manager UI for manual backup/restore"""
    if not BACKUP_MANAGER:
        messagebox.showwarning(
            "⚠️ Backup Manager",
            "Backup Manager nu este disponibil.\n\n"
            "Backup-uri nu vor fi create."
        )
        return
    
    try:
        if create_backup_ui:
            create_backup_ui(root, BACKUP_MANAGER)
        else:
            messagebox.showerror("Error", "Backup UI not available")
    except Exception as e:
        messagebox.showerror("Error", f"Error opening backup manager:\n{str(e)}")
        print(f"Error opening backup manager: {e}")
        import traceback
        traceback.print_exc()

def refresh_discord_section():
    """Reîncarcă secțiunea Discord după autentificare"""
    global DISCORD_AUTH
    
    # Șterge secțiunea anterioară
    for widget in discord_section_container.winfo_children():
        widget.destroy()
    
    if not DISCORD_AUTH or not DISCORD_AUTH.is_authenticated():
        print("DEBUG: No Discord auth, section empty")
        return
    
    print("DEBUG: Rebuilding Discord section")
    
    username = DISCORD_AUTH.user_info.get('username', 'User')
    user_role = DISCORD_AUTH.get_user_role()
    user_id = DISCORD_AUTH.get_discord_id()
    print(f"DEBUG: user_role={user_role}, is_superuser={DISCORD_AUTH._is_superuser}, is_admin={DISCORD_AUTH._is_admin}")
    
    # Display username
    tk.Label(
        discord_section_container,
        text=f"👤 {username}",
        font=("Segoe UI", 9, "bold"),
        bg="#f0f0f0",
        fg="#5865F2"
    ).pack(pady=5)
    
    # Role badge with color coding + emoji
    role_colors = {
        'superuser': '#9b59b6',
        'admin': '#e74c3c',
        'user': '#3498db',
        'viewer': '#95a5a6'
    }
    role_emojis = {
        'superuser': '👑',
        'admin': '🛡️',
        'user': '👤',
        'viewer': '👁️'
    }
    role_color = role_colors.get(user_role.lower(), '#95a5a6')
    role_emoji = role_emojis.get(user_role.lower(), '❓')
    
    role_label = tk.Label(
        discord_section_container,
        text=f"{role_emoji} {user_role.upper()}",
        font=("Segoe UI", 9, "bold"),
        bg=role_color,
        fg="white",
        padx=10,
        pady=5
    )
    role_label.pack(pady=5, fill="x", padx=5)
    
    # Permisiuni detaliate - sub rolul principal
    perms_frame = tk.Frame(discord_section_container, bg="#f0f0f0")
    perms_frame.pack(fill="x", padx=5, pady=5)
    
    # Afișează permisiuni detaliate
    is_superuser = DISCORD_AUTH._is_superuser
    is_admin = DISCORD_AUTH._is_admin
    
    if is_superuser:
        perms_text = "✅ Full Access\n🔓 All Permissions"
        perms_color = "#2e7d32"
    elif is_admin:
        perms_text = "✅ Admin Access\n🔓 Most Permissions"
        perms_color = "#e74c3c"
    elif user_role == "user":
        perms_text = "✅ Can View\n✏️ Can Edit\n📝 Can Modify"
        perms_color = "#1976d2"
    else:  # viewer
        perms_text = "👁️ Read-Only\n❌ No Edit\n❌ No Delete"
        perms_color = "#9e9e9e"
    
    tk.Label(
        perms_frame,
        text=perms_text,
        font=("Segoe UI", 7),
        bg="#f0f0f0",
        fg=perms_color,
        justify="left"
    ).pack(anchor="w", padx=10, pady=3)
    
    # Afișează instituțiile accesibile
    if not is_superuser and not is_admin:
        print("DEBUG: Fetching accessible institutions...")
        institutions = DISCORD_AUTH.get_accessible_institutions()
        
        if institutions:
            # Group by city
            cities_dict = {}
            for inst in institutions:
                city = inst.get('city', 'Unknown')
                institution = inst.get('institution', 'Unknown')
                if city not in cities_dict:
                    cities_dict[city] = []
                cities_dict[city].append(institution)
            
            # Afișează instituțiile
            access_frame = tk.Frame(discord_section_container, bg="#e8f5e9", relief="solid", borderwidth=1)
            access_frame.pack(fill="x", padx=5, pady=5)
            
            tk.Label(
                access_frame,
                text="📋 Tabelele cu Acces:",
                font=("Segoe UI", 8, "bold"),
                bg="#e8f5e9",
                fg="#2e7d32"
            ).pack(anchor="w", padx=8, pady=(5, 2))
            
            for city in sorted(cities_dict.keys()):
                inst_list = cities_dict[city]
                city_text = f"  🏙️ {city}: {', '.join(inst_list)}"
                tk.Label(
                    access_frame,
                    text=city_text,
                    font=("Segoe UI", 7),
                    bg="#e8f5e9",
                    fg="#1b5e20",
                    justify="left",
                    wraplength=180
                ).pack(anchor="w", padx=10, pady=1)
            
            print(f"✅ Displayed {len(institutions)} accessible institutions")
        else:
            # No specific institutions - viewer role without granular access
            if user_role == "viewer":
                access_frame = tk.Frame(discord_section_container, bg="#ffebee", relief="solid", borderwidth=1)
                access_frame.pack(fill="x", padx=5, pady=5)
                
                tk.Label(
                    access_frame,
                    text="❌ Niciun acces",
                    font=("Segoe UI", 8, "bold"),
                    bg="#ffebee",
                    fg="#c62828"
                ).pack(anchor="w", padx=8, pady=5)
    else:
        # Superuser/Admin - full access message
        access_frame = tk.Frame(discord_section_container, bg="#e3f2fd", relief="solid", borderwidth=1)
        access_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(
            access_frame,
            text="✅ Acces la Toate Tabelele",
            font=("Segoe UI", 8, "bold"),
            bg="#e3f2fd",
            fg="#1565c0"
        ).pack(anchor="w", padx=8, pady=5)
    
    # Buton Admin - Pentru SUPERUSER sau utilizatori cu permisiunea 'can_see_admin_button'
    if open_granular_permissions_panel and DISCORD_AUTH:
        can_see_button = DISCORD_AUTH.is_superuser() or DISCORD_AUTH.has_granular_permission('can_see_admin_button')
        if can_see_button:
            print("DEBUG: Creating Admin permissions button")
            def open_admin_permissions():
                """Deschide panelul de gestiune permisiuni"""
                open_granular_permissions_panel(root, SUPABASE_SYNC, DISCORD_AUTH, DATA_DIR)
            
            btn_admin = tk.Button(
                discord_section_container,
                text="⚙️ Admin",
                width=18,
                font=("Segoe UI", 8),
                bg="#FF9800",
                fg="white",
                command=open_admin_permissions
            )
            btn_admin.pack(side=tk.LEFT, padx=2, pady=5, fill="x")

# Separator
tk.Frame(sidebar, height=2, bg="#cccccc").pack(fill=tk.X, pady=15, padx=10)

# Buton Sincronizare Cloud
if SUPABASE_SYNC and SUPABASE_SYNC.enabled:
    def manual_cloud_sync():
        """Sincronizare manuală cu cloud - Upload sau Download"""
        # Dialog pentru alegerea tipului de sincronizare
        sync_window = tk.Toplevel(root)
        sync_window.title("Sincronizare Cloud")
        sync_window.geometry("450x300")
        sync_window.grab_set()
        sync_window.transient(root)
        
        # Centrare fereastră
        sync_window.update_idletasks()
        x = (sync_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (sync_window.winfo_screenheight() // 2) - (300 // 2)
        sync_window.geometry(f"+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(sync_window, bg="#3498db", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="☁️ Sincronizare Cloud",
            font=("Segoe UI", 14, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=15)
        
        # Content
        content_frame = tk.Frame(sync_window, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            content_frame,
            text="Alege tipul de sincronizare:",
            font=("Segoe UI", 11, "bold"),
            bg="white"
        ).pack(pady=10)
        
        # Buton Upload (Trimite în cloud)
        upload_frame = tk.Frame(content_frame, bg="#e8f5e9", relief=tk.RAISED, borderwidth=2)
        upload_frame.pack(fill=tk.X, pady=5)
        
        def upload_to_cloud():
            sync_window.destroy()
            
            # Cloud upload este liber pentru toți
            if not messagebox.askyesno(
                "Upload în Cloud",
                "Trimiți toate datele locale în cloud?\n\n"
                "✅ Vor fi actualizate toate fișierele din Supabase\n"
                "⚠️ Datele din cloud vor fi suprascrise\n\n"
                "Continuă?"
            ):
                return
            
            # Upload toate fișierele locale
            uploaded = 0
            errors = 0
            cities_uploaded = []
            
            for city in os.listdir(DATA_DIR):
                city_path = os.path.join(DATA_DIR, city)
                if not os.path.isdir(city_path):
                    continue
                
                for file_name in os.listdir(city_path):
                    if not file_name.endswith('.json'):
                        continue
                    
                    institution = file_name[:-5]
                    file_path = os.path.join(city_path, file_name)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                        
                        result = supabase_upload(city, institution, json_data, file_path)
                        
                        if result.get("status") == "success":
                            uploaded += 1
                            if city not in cities_uploaded:
                                cities_uploaded.append(city)
                        else:
                            errors += 1
                    except Exception as e:
                        print(f"❌ Eroare upload {city}/{institution}: {e}")
                        errors += 1
            
            if uploaded > 0:
                messagebox.showinfo(
                    "Upload Complet",
                    f"✅ Upload reușit!\n\n"
                    f"Trimise în cloud: {uploaded} fișiere\n"
                    f"Orașe: {', '.join(cities_uploaded)}\n"
                    f"Erori: {errors}"
                )
            else:
                messagebox.showwarning(
                    "Upload",
                    f"⚠️ Nu s-au putut trimite fișiere\n\nErori: {errors}"
                )
        
        tk.Button(
            upload_frame,
            text="📤 UPLOAD - Trimite în Cloud",
            font=("Segoe UI", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            command=upload_to_cloud,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            upload_frame,
            text="Trimite datele locale în Supabase (ID: 17485)",
            font=("Segoe UI", 8),
            bg="#e8f5e9",
            fg="#555"
        ).pack(pady=5)
        
        # Buton Download (Descarcă din cloud)
        download_frame = tk.Frame(content_frame, bg="#e3f2fd", relief=tk.RAISED, borderwidth=2)
        download_frame.pack(fill=tk.X, pady=5)
        
        def download_from_cloud():
            sync_window.destroy()
            
            if not messagebox.askyesno(
                "Download din Cloud",
                "Descarci datele din cloud?\n\n"
                "⚠️ Doar fișierele mai noi decât cele locale vor fi descărcate\n"
                "💾 Datele locale vor fi salvate în backup automat\n\n"
                "Continuă?"
            ):
                return
            
            result = supabase_sync_all()
            
            if result.get("status") == "success":
                downloaded = result.get("downloaded", 0)
                skipped = result.get("skipped", 0)
                backup_info = result.get("backup", {})
                backup_path = backup_info.get("backup_path")
                backup_timestamp = backup_info.get("backup_timestamp")
                
                if downloaded > 0:
                    msg = (
                        f"✅ Sincronizare completă!\n\n"
                        f"Descărcate: {downloaded} fișiere\n"
                        f"Sărite (locale mai noi): {skipped}\n"
                        f"Orașe: {', '.join(result.get('cities', []))}\n\n"
                    )
                    
                    if backup_path:
                        msg += (
                            f"💾 BACKUP SALVAT:\n"
                            f"📁 {backup_timestamp}\n\n"
                        )
                    
                    msg += "🔄 Reîncarcă automat tabele..."
                    
                    messagebox.showinfo(
                        "Download Complet",
                        msg
                    )
                    
                    # AUTO-REFRESH: Reîncarcă toate tabelele AUTOMAT
                    print("🔄 Auto-refreshing all tables after cloud sync...")
                    root.after(500, load_existing_tables)
                    
                    # Refresh Discord section și admin buttons
                    root.after(1000, refresh_discord_section)
                    root.after(1500, refresh_admin_buttons)
                    
                    print("✅ Auto-refresh completed!")
                else:
                    msg = f"ℹ️ Fișierele locale sunt la zi!\n\nSărite: {skipped} fișiere"
                    
                    if backup_path:
                        msg += f"\n\n💾 BACKUP SALVAT:\n📁 {backup_timestamp}"
                    
                    messagebox.showinfo(
                        "Download",
                        msg
                    )
            else:
                messagebox.showerror(
                    "Download",
                    f"❌ Eroare:\n\n{result.get('message', 'Unknown')}"
                )
        
        tk.Button(
            download_frame,
            text="📥 DOWNLOAD - Descarcă din Cloud",
            font=("Segoe UI", 10, "bold"),
            bg="#2196F3",
            fg="white",
            command=download_from_cloud,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            download_frame,
            text="Descarcă datele din Supabase în local",
            font=("Segoe UI", 8),
            bg="#e3f2fd",
            fg="#555"
        ).pack(pady=5)
        
        # Buton Sincronizare Forțată Cloud
        force_sync_frame = tk.Frame(content_frame, bg="#fff3e0", relief=tk.RAISED, borderwidth=2)
        force_sync_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            force_sync_frame,
            text="⚡ FORȚEAZĂ SINCRONIZARE CLOUD",
            font=("Segoe UI", 10, "bold"),
            bg="#ff6f00",
            fg="white",
            command=force_cloud_sync_button,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            force_sync_frame,
            text="Notifică toți utilizatorii și forțează descărcare din cloud",
            font=("Segoe UI", 8),
            bg="#fff3e0",
            fg="#555"
        ).pack(pady=5)
        
        # ⭐ Buton Backup & Restore
        backup_frame = tk.Frame(content_frame, bg="#f3e5f5", relief=tk.RAISED, borderwidth=2)
        backup_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            backup_frame,
            text="💾 BACKUP & RESTORE",
            font=("Segoe UI", 10, "bold"),
            bg="#9c27b0",
            fg="white",
            command=open_backup_manager,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            backup_frame,
            text="Creează manual backup sau restaurează din backup anterior",
            font=("Segoe UI", 8),
            bg="#f3e5f5",
            fg="#555"
        ).pack(pady=5)
        
        # Buton Anulare
        tk.Button(
            content_frame,
            text="✗ Anulează",
            command=sync_window.destroy,
            bg="#e0e0e0",
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(pady=15)
    
    # ✅ AUTO-SYNC ENABLED - No manual button needed
    # Cloud sync happens automatically:
    # - UPLOAD: Each time you save modifications
    # - DOWNLOAD: Every 5 seconds via PermissionSyncManager
    
    # Status indicator (hidden, just for debugging)
    if os.getenv("SHOW_SYNC_DEBUG"):
        sync_status_frame = tk.Frame(sidebar, bg="#e8f5e9", height=40)
        sync_status_frame.pack(fill=tk.X, padx=10, pady=5)
        sync_status_frame.pack_propagate(False)
        
        tk.Label(
            sync_status_frame,
            text="⚡ AUTO-SYNC ACTIVE",
            font=("Segoe UI", 8, "bold"),
            bg="#e8f5e9",
            fg="#27ae60"
        ).pack(pady=5)
        
        tk.Label(
            sync_status_frame,
            text="↑ Upload on save | ↓ Download every 5s",
            font=("Segoe UI", 7),
            bg="#e8f5e9",
            fg="#555"
        ).pack(pady=2)

# Container pentru butoane admin (va fi populat după autentificare)
admin_buttons_container = tk.Frame(sidebar, bg="#f0f0f0")
admin_buttons_container.pack(fill=tk.X)

def refresh_admin_buttons():
    """Reîncarcă butoanele admin după autentificare"""
    global DISCORD_AUTH
    
    # Șterge butoanele anterioare
    for widget in admin_buttons_container.winfo_children():
        widget.destroy()
    
    if DISCORD_AUTH:
        role = DISCORD_AUTH.get_user_role()
        print(f"DEBUG: Refresh admin buttons - User={DISCORD_AUTH.get_username()}, Role={role}, is_admin={DISCORD_AUTH.is_admin()}")
    else:
        print(f"DEBUG: Refresh admin buttons - DISCORD_AUTH is None")
    
    # Butoane admin - Pentru SUPERUSER sau utilizatori cu permisiuni specifice
    if DISCORD_AUTH and open_granular_permissions_panel:
        can_see_permissions = DISCORD_AUTH.is_superuser() or DISCORD_AUTH.has_granular_permission('can_see_user_permissions_button')
        if can_see_permissions:
            print("✓ Creez buton Permisiuni Utilizatori")
            def open_permissions_panel():
                """Deschide panelul de permisiuni granulare"""
                open_granular_permissions_panel(root, SUPABASE_SYNC, DISCORD_AUTH, DATA_DIR)
            
            btn_permissions = tk.Button(
                admin_buttons_container,
                text="🔐 Permisiuni Utilizatori",
                width=18,
                bg="#e74c3c",
                fg="white",
                font=("Segoe UI", 9, "bold"),
                command=open_permissions_panel
            )
            btn_permissions.pack(pady=8)
    
    if DISCORD_AUTH and ADMIN_PANEL_AVAILABLE and open_admin_panel:
        can_see_panel = DISCORD_AUTH.is_superuser() or DISCORD_AUTH.has_granular_permission('can_see_admin_panel')
        if can_see_panel:
            print("✓ Creez buton Admin Panel")
            btn_admin = tk.Button(
                admin_buttons_container,
                text="🛡️ Admin Panel",
                width=18,
                bg="#e74c3c",
                fg="white",
                font=("Segoe UI", 9, "bold"),
                command=lambda: open_admin_panel(root, SUPABASE_SYNC, DISCORD_AUTH, DATA_DIR, ACTION_LOGGER)
            )
            btn_admin.pack(pady=8)
    
    # Buton Raport Săptămânal din Arhiva
    ttk.Button(
        admin_buttons_container,
        text="📋 Raport Săptămâna Trecută",
        width=18,
        command=show_weekly_report
    ).pack(pady=8)
    
    # Buton Activity Logs
    def open_logs_viewer():
        """Deschide fereastra cu logurile activității per instituție"""
        logs_window = tk.Toplevel(root)
        logs_window.title("📋 Activity Logs - Modificări efectuate")
        logs_window.geometry("950x650")
        logs_window.grab_set()
        
        # Header
        header = tk.Label(logs_window, text="📋 Loguri Activitate - Pe instituție", font=("Segoe UI", 12, "bold"), bg="#1565c0", fg="white")
        header.pack(fill="x", padx=0, pady=0, ipady=10)
        
        # Filter frame
        filter_frame = tk.Frame(logs_window, bg="#f0f0f0")
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(filter_frame, text="Selectează instituția:", font=("Segoe UI", 10), bg="#f0f0f0").pack(side="left", padx=5)
        
        # Obține lista instituțiilor
        institutions_list = []
        try:
            for city in sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(city_dir(d))]):
                inst_dir = city_dir(city)
                if os.path.exists(inst_dir):
                    for json_file in sorted([f for f in os.listdir(inst_dir) if f.endswith('.json')]):
                        institution = json_file[:-5]
                        institutions_list.append(f"{city} / {institution}")
        except:
            pass
        
        selected_institution = tk.StringVar(value="Toate")
        combo = ttk.Combobox(filter_frame, textvariable=selected_institution, values=["Toate"] + institutions_list, state="readonly", width=40)
        combo.pack(side="left", padx=5)
        
        # Frame pentru scroll
        canvas_frame = tk.Frame(logs_window)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg="#f5f5f5")
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f5f5f5")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def load_logs():
            """Reîncarcă logurile pentru instituția selectată"""
            # Clear frame
            for child in scroll_frame.winfo_children():
                child.destroy()
            
            try:
                if not SUPABASE_SYNC:
                    tk.Label(scroll_frame, text="⚠️ Supabase nu e disponibil", font=("Segoe UI", 10)).pack(pady=20)
                    return
                
                selected = selected_institution.get()
                
                # Build query
                url = f"{SUPABASE_SYNC.url}/rest/v1/{SUPABASE_SYNC.table_logs}?order=timestamp.desc&limit=100"
                if selected != "Toate":
                    # Filter by institution
                    inst_parts = selected.split(" / ")
                    if len(inst_parts) == 2:
                        city, institution = inst_parts
                        url += f"&institution=eq.{institution}&city=eq.{city}"
                
                headers = {
                    "apikey": SUPABASE_SYNC.key,
                    "Authorization": f"Bearer {SUPABASE_SYNC.key}"
                }
                
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    logs = response.json()
                    
                    if not logs:
                        tk.Label(scroll_frame, text="📭 Nicio activitate înregistrată", font=("Segoe UI", 10, "italic"), fg="#999").pack(pady=20)
                    else:
                        for log in logs:
                            # Card pentru fiecare log
                            card = tk.Frame(scroll_frame, bg="white", relief="solid", borderwidth=1)
                            card.pack(fill="x", padx=5, pady=5)
                            
                            # Timestamp + action
                            header_text = f"🕐 {log.get('timestamp', 'N/A')[:19]} - {log.get('action_type', 'unknown').upper()}"
                            tk.Label(card, text=header_text, font=("Segoe UI", 9, "bold"), bg="white", fg="#1565c0", anchor="w").pack(fill="x", padx=10, pady=(8, 3))
                            
                            # Discord ID
                            discord_id = log.get('discord_id', 'Unknown')
                            tk.Label(card, text=f"👤 Discord ID: {discord_id}", font=("Segoe UI", 9), bg="white", fg="#666", anchor="w").pack(fill="x", padx=20, pady=1)
                            
                            # Discord Username
                            discord_username = log.get('discord_username', discord_id)
                            tk.Label(card, text=f"👤 Discord Username: {discord_username}", font=("Segoe UI", 9, "bold"), bg="white", fg="#2196F3", anchor="w").pack(fill="x", padx=20, pady=1)
                            
                            # Institution
                            institution = log.get('institution', 'N/A')
                            city = log.get('city', 'N/A')
                            tk.Label(card, text=f"🏢 {city} / {institution}", font=("Segoe UI", 9), bg="white", fg="#666", anchor="w").pack(fill="x", padx=20, pady=1)
                            
                            # Details
                            details = log.get('details', 'No details')
                            tk.Label(card, text=f"📝 {details}", font=("Segoe UI", 8), bg="white", fg="#333", anchor="w", wraplength=850, justify="left").pack(fill="x", padx=20, pady=(1, 8))
                else:
                    tk.Label(scroll_frame, text=f"❌ Eroare la citire: {response.status_code}", font=("Segoe UI", 10), fg="#e74c3c").pack(pady=20)
            except Exception as e:
                tk.Label(scroll_frame, text=f"❌ Eroare: {str(e)}", font=("Segoe UI", 10), fg="#e74c3c").pack(pady=20)
            
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Bind combo change
        combo.bind("<<ComboboxSelected>>", lambda e: load_logs())
        
        # Load initial logs
        load_logs()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    btn_logs = tk.Button(
        admin_buttons_container,
        text="📋 Activity Logs",
        width=18,
        bg="#3498db",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        command=open_logs_viewer
    )
    btn_logs.pack(pady=8)

# Separator
tk.Frame(sidebar, height=2, bg="#cccccc").pack(fill=tk.X, pady=15, padx=10)

# -------- CONTENT --------
content = tk.Frame(main)
content.pack(side="right", fill="both", expand=True)

city_notebook = ttk.Notebook(content)
city_notebook.pack(fill="both", expand=True)


# ================== GIT PERIODIC SYNC ==================
def git_periodic_sync():
    """Sincronizează datele locale cu Git la fiecare 5 minute"""
    def sync():
        try:
            # Încearcă pull pentru a lua modificările de pe Git
            if git_pull_and_sync():
                # Dacă pull-ul a reușit și sunt conflicte, reload-ează interfața
                print("[Git] Datele au fost sincronizate cu serverul")
                # Ar putea triggera reload de tab-uri dacă necesare
        except Exception as e:
            print(f"[Git] Eroare la sync: {str(e)}")
    
    # Rulează sync la fiecare 5 minute
    schedule.every(5).minutes.do(sync)


# Inițializează Git sync
git_periodic_sync()


# ================== AUTO-RESET SCHEDULER ==================
def auto_reset_all_institutions():
    """Face reset automat la toate instituțiile din toate orașele"""
    print(f"[{datetime.now()}] Inițiez reset automat pentru prima zi a lunii...")
    
    # Iterează prin toate orașele
    for city_dir_name in os.listdir(DATA_DIR):
        city_path = os.path.join(DATA_DIR, city_dir_name)
        if not os.path.isdir(city_path):
            continue
        
        # Iterează prin toate instituțiile din oraș
        for json_file in os.listdir(city_path):
            if not json_file.endswith('.json'):
                continue
            
            institution = json_file[:-5]
            
            try:
                inst_data = load_institution(city_dir_name, institution)
                columns = inst_data.get("columns", [])
                rows = inst_data.get("rows", [])
                
                if "PUNCTAJ" not in columns:
                    continue
                
                # Creează folder de arhivă și salvează raport
                archive_city_dir = os.path.join(ARCHIVE_DIR, city_dir_name)
                os.makedirs(archive_city_dir, exist_ok=True)
                
                csv_filename = f"{institution}.csv"
                csv_path = os.path.join(archive_city_dir, csv_filename)
                
                reset_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Verifică dacă CSV-ul există
                file_exists = os.path.exists(csv_path)
                
                # Salvează datele vechi în CSV
                with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    
                    if not file_exists:
                        header = ["RESET_DATA"] + columns
                        writer.writerow(header)
                    
                    for row in rows:
                        if isinstance(row, dict):
                            values = [row.get(col, "") for col in columns]
                        else:
                            values = list(row) if isinstance(row, (list, tuple)) else [row]
                        
                        writer.writerow([reset_timestamp] + values)
                    
                    writer.writerow([])
                
                # Resetează PUNCTAJ la 0
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for row in rows:
                    if isinstance(row, dict):
                        row["PUNCTAJ"] = 0
                        row["ULTIMA_MOD"] = current_timestamp
                    else:
                        row_dict = {}
                        for i, col in enumerate(columns):
                            row_dict[col] = row[i] if i < len(row) else ""
                        row_dict["PUNCTAJ"] = 0
                        row_dict["ULTIMA_MOD"] = current_timestamp
                        rows[rows.index(row)] = row_dict
                
                # Asigură ULTIMA_MOD în coloane
                if "ULTIMA_MOD" not in columns:
                    columns.append("ULTIMA_MOD")
                
                # Salvează în JSON
                inst_data["columns"] = columns
                inst_data["rows"] = rows
                inst_data["last_punctaj_update"] = reset_timestamp
                
                with open(institution_path(city_dir_name, institution), "w", encoding="utf-8") as f:
                    json.dump(inst_data, f, indent=4, ensure_ascii=False)
                
                print(f"  ✓ Reset: {city_dir_name}/{institution}")
            
            except Exception as e:
                print(f"  ✗ Eroare la reset {city_dir_name}/{institution}: {str(e)}")
    
    print(f"[{datetime.now()}] Reset automat finalizat!")


def schedule_daily_check():
    """Scheduler care verifica daca e prima zi a lunii la 00:00"""
    def check_and_reset():
        now = datetime.now()
        if now.day == 1 and now.hour == 0:
            auto_reset_all_institutions()
    
    schedule.every(1).minutes.do(check_and_reset)
    
    while True:
        schedule.run_pending()
        time.sleep(30)  # Verifica la fiecare 30 de secunde


# Lansează scheduler-ul în background thread
scheduler_thread = threading.Thread(target=schedule_daily_check, daemon=True)
scheduler_thread.start()
tabs = {}  # oras -> {"nb": notebook institutii, "trees": {institutie: tree}}

# ================== FUNCȚII ==================
def create_city_ui(city):
    """Creează UI pentru un oraș și încarcă instituțiile existente."""
    ensure_city(city)

    city_frame = tk.Frame(city_notebook)
    city_notebook.add(city_frame, text=city)

    # Frame cu scroll bar pentru controls
    controls_container = tk.Frame(city_frame)
    controls_container.pack(fill="x", pady=8)
    
    # Horizontal scroll bar la controls
    controls_canvas = tk.Canvas(controls_container, height=50, bg="white", highlightthickness=0)
    h_scrollbar = tk.Scrollbar(controls_container, orient="horizontal", command=controls_canvas.xview)
    controls = tk.Frame(controls_canvas)
    
    controls.bind(
        "<Configure>",
        lambda e: controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))
    )
    
    controls_canvas.create_window((0, 0), window=controls, anchor="nw")
    controls_canvas.configure(xscrollcommand=h_scrollbar.set)
    
    controls_canvas.pack(fill="x")
    h_scrollbar.pack(fill="x")

    # Buton Adaugă Instituție
    btn_add_inst = tk.Button(controls, text="➕ Adaugă instituție", width=18, command=lambda c=city: add_institution(c))
    btn_add_inst.pack(side="left", padx=5)
    if not check_institution_permission(city, "", 'can_edit'):
        btn_add_inst.config(state='disabled')
    
    # Buton Editează Instituție
    btn_edit_inst = tk.Button(controls, text="✏️ Editează instituție", width=18, command=lambda c=city: edit_institution(c))
    btn_edit_inst.pack(side="left", padx=5)
    if not check_institution_permission(city, "", 'can_edit'):
        btn_edit_inst.config(state='disabled')
    
    # Buton Șterge Instituții
    btn_del_inst = tk.Button(controls, text="❌ Șterge instituții", width=18, command=lambda c=city: delete_institution_ui(c))
    btn_del_inst.pack(side="left", padx=5)
    if not check_institution_permission(city, "", 'can_delete'):
        btn_del_inst.config(state='disabled')

    inst_nb = ttk.Notebook(city_frame)
    inst_nb.pack(fill="both", expand=True)

    tabs[city] = {"nb": inst_nb, "trees": {}, "info_frames": {}}

    # Încarcă instituțiile existente din folderul orașului
    for json_file in sorted([f for f in os.listdir(city_dir(city)) if f.endswith('.json')]):
        inst = json_file[:-5]
        create_institution_tab(city, inst)

    return city_frame


def add_tab():
    # Check permission to add city
    discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else None
    can_add, msg = check_can_add_city(discord_id, INSTITUTION_PERM_MANAGER, DISCORD_AUTH)
    if not can_add:
        messagebox.showerror("Permisiune refuzată", msg)
        return
    
    city = simpledialog.askstring("Nume oraș", "Introdu numele orașului:")
    if not city:
        return

    city = city.strip().replace(" ", "_")

    if city in tabs:
        messagebox.showerror("Eroare", "Există deja un oraș cu acest nume!")
        return

    # Creează directorul local pentru oraș
    os.makedirs(city_dir(city), exist_ok=True)
    
    # Sincronizează cu Supabase (creează orașele automat la primul upload de instituție)
    if SUPABASE_SYNC and SUPABASE_SYNC.enabled:
        try:
            print(f"✓ Oraș nou '{city}' creat - va fi sincronizat la prima instituție")
        except Exception as e:
            print(f"⚠️ Eroare pregătire sincronizare oraș: {e}")
    
    frame = create_city_ui(city)
    city_notebook.select(frame)

def edit_tab():
    # Check permission to edit city
    discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else None
    can_edit, msg = check_can_edit_city(discord_id, INSTITUTION_PERM_MANAGER, DISCORD_AUTH)
    if not can_edit:
        messagebox.showerror("Permisiune refuzată", msg)
        return
    
    current = city_notebook.select()
    if not current:
        messagebox.showinfo("Info", "Selectează un oraș mai întâi!")
        return

    old_city = city_notebook.tab(current, "text")
    new_city = simpledialog.askstring("Editează oraș", "Nume nou:", initialvalue=old_city)
    if not new_city:
        return
    new_city = new_city.strip().replace(" ", "_")

    if new_city == old_city:
        return
    if new_city in tabs:
        messagebox.showerror("Eroare", "Există deja un oraș cu acest nume!")
        return

    try:
        os.rename(city_dir(old_city), city_dir(new_city))
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu pot redenumi orașul: {e}")
        return

    # Elimină tab-ul vechi și reconstruiește orașul cu numele nou
    for tab_id in city_notebook.tabs():
        if city_notebook.tab(tab_id, "text") == old_city:
            city_notebook.forget(tab_id)
            break
    tabs.pop(old_city, None)

    frame = create_city_ui(new_city)
    city_notebook.select(frame)


def delete_tab():
    # Check permission to delete city
    discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else None
    can_delete, msg = check_can_delete_city(discord_id, INSTITUTION_PERM_MANAGER, DISCORD_AUTH)
    if not can_delete:
        messagebox.showerror("Permisiune refuzată", msg)
        return
    
    # Șterge orașe (tabele principale)
    if not tabs:
        messagebox.showinfo("Info", "Nu există orașe de șters!")
        return

    win = tk.Toplevel(root)
    win.title("Șterge orașe")
    win.geometry("400x450")
    win.grab_set()

    frame_top = tk.Frame(win, bg="#ffe8e8", pady=10)
    frame_top.pack(fill="x")

    tk.Label(
        frame_top,
        text="Selectează orașele pe care vrei să le ștergi",
        font=("Segoe UI", 10, "bold"),
        bg="#ffe8e8"
    ).pack(pady=5)

    tk.Label(
        frame_top,
        text="⚠️ Se vor șterge toate instituțiile și angajații din orașele selectate",
        font=("Segoe UI", 9),
        fg="#d32f2f",
        bg="#ffe8e8"
    ).pack(pady=2)

    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, pady=10)

    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_cities = []
    for city in sorted(tabs.keys()):
        var = tk.BooleanVar(value=False)
        inst_count = len(tabs[city]["trees"])
        chk = tk.Checkbutton(
            scroll_frame,
            text=f"🏙️ {city} ({inst_count} instituții)",
            variable=var,
            anchor="w",
            font=("Segoe UI", 10)
        )
        chk.pack(fill="x", padx=10, pady=3)
        vars_cities.append((city, var))

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    def select_all():
        for _, var in vars_cities:
            var.set(True)

    tk.Button(btn_frame, text="✓ Selectează toate", command=select_all, width=18).pack(side="left", padx=5)

    def deselect_all():
        for _, var in vars_cities:
            var.set(False)

    tk.Button(btn_frame, text="✗ Deselectează toate", command=deselect_all, width=18).pack(side="left", padx=5)

    def aplica():
        selectate = [city for city, var in vars_cities if var.get()]
        if not selectate:
            messagebox.showwarning("Nicio selecție", "Nu ai selectat niciun oraș!")
            return

        if not messagebox.askyesno(
            "Confirmare ștergere",
            f"Ștergi {len(selectate)} oraș(e) și toate datele aferente?"
        ):
            return

        for city in selectate:
            # șterge tab din notebook
            for tab_id in city_notebook.tabs():
                if city_notebook.tab(tab_id, "text") == city:
                    city_notebook.forget(tab_id)
                    break
            delete_city(city)
            tabs.pop(city, None)

        win.destroy()
        messagebox.showinfo("Succes", "Orașele selectate au fost șterse.")

    tk.Button(
        win,
        text="🗑️ ȘTERGE ORAȘE",
        bg="#F44336",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=25,
        height=2,
        command=aplica
    ).pack(pady=15)
 
# ================== INSTITUȚII ==================
def sort_tree_by_punctaj(tree):
    """Sortează treeview-ul descrescător după coloana PUNCTAJ"""
    columns = tree.columns
    if "PUNCTAJ" not in columns:
        return
    
    punctaj_idx = columns.index("PUNCTAJ")
    
    # Extrage toate rândurile cu valorile lor
    items = []
    for item in tree.get_children():
        values = tree.item(item, "values")
        try:
            punctaj = int(values[punctaj_idx]) if punctaj_idx < len(values) else 0
        except (ValueError, IndexError):
            punctaj = 0
        items.append((item, values, punctaj))
    
    # Sortează descrescător după punctaj
    items.sort(key=lambda x: x[2], reverse=True)
    
    # Rearanjează rândurile în treeview
    for index, (item, values, _) in enumerate(items):
        tree.move(item, "", index)


def sync_roles_with_ranks(tree, ranks_map):
    """Sincronizează rolurile din ROLE coloană cu definiția rankurilor curente"""
    columns = tree.columns
    if "RANK" not in columns or "ROLE" not in columns:
        return
    
    rank_idx = columns.index("RANK")
    role_idx = columns.index("ROLE")
    
    needs_save = False
    for item in tree.get_children():
        values = list(tree.item(item, "values"))
        rank = str(values[rank_idx]).strip()
        old_role = str(values[role_idx]).strip()
        
        # Dacă rankul are o definiție în ranks_map și rolul nu se potrivește, actualizează
        if rank in ranks_map:
            new_role = ranks_map[rank]
            if old_role != new_role:
                values[role_idx] = new_role
                tree.item(item, values=tuple(values))
                needs_save = True
    
    return needs_save


def reset_punctaj(tree, city, institution):
    """Resetează PUNCTAJ-ul la 0, arhivează datele vechi în JSON cu timestamp"""
    
    print(f"\n🔄 RESET PUNCTAJ STARTED for {city}/{institution}")
    
    if not messagebox.askyesno(
        "Confirmare resetare",
        f"Sigur vrei să resetezi punctajul pentru toți angajații?\n\nDatele vechi vor fi salvate în arhiva."
    ):
        print("❌ Reset cancelled by user")
        return
    
    # 🚫 IMPORTANT: Load from LOCAL file ONLY, don't sync with Supabase yet
    # This prevents pulling old data from cloud and overwriting the reset
    inst_path = institution_path(city, institution)
    if not os.path.exists(inst_path):
        messagebox.showerror("Eroare", f"Fișierul instituției nu există!")
        return
    
    with open(inst_path, 'r', encoding='utf-8') as f:
        inst_data = json.load(f)
    
    columns = inst_data.get("columns", [])
    rows = inst_data.get("rows", [])
    
    print(f"📋 Loaded data: {len(rows)} employees, columns: {columns}")
    
    if "PUNCTAJ" not in columns:
        messagebox.showwarning("Eroare", "Nu există coloana PUNCTAJ!")
        print("❌ PUNCTAJ column not found!")
        return
    
    # Creează folder de arhivă pentru oraș
    archive_city_dir = os.path.join(ARCHIVE_DIR, city)
    os.makedirs(archive_city_dir, exist_ok=True)
    print(f"✅ Archive dir created: {archive_city_dir}")
    
    # Timestamp pentru reset - format: YYYY-MM-DD_HH-MM-SS
    reset_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # JSON-ul va fi salvat cu timestamp
    json_filename = f"{institution}_{reset_timestamp}.json"
    json_path = os.path.join(archive_city_dir, json_filename)
    
    # Salvează datele vechi în JSON (cu metadata)
    reset_by_name = DISCORD_AUTH.user_info.get('username', 'Unknown') if DISCORD_AUTH and DISCORD_AUTH.user_info else "Unknown"
    reset_by_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else ""
    
    archive_data = {
        "archived_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "institution": institution,
        "city": city,
        "reset_by": reset_by_name,
        "discord_id": reset_by_id,
        "columns": columns,
        "rows": rows,
        "employee_count": len(rows)
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Archive saved: {json_path}")
    
    # Resetează PUNCTAJ-ul la 0 și adaug ULTIMA_MOD
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🔄 Resetting PUNCTAJ for {len(rows)} employees...")
    updated_count = 0
    
    for i, row in enumerate(rows):
        if isinstance(row, dict):
            print(f"   Row {i}: {row.get('DISCORD', 'Unknown')} - Old PUNCTAJ: {row.get('PUNCTAJ', 'N/A')} → New: 0")
            row["PUNCTAJ"] = 0
            row["ULTIMA_MOD"] = current_timestamp
            updated_count += 1
        else:
            print(f"   ⚠️ Row {i} is not dict: {type(row)}")
            # Convertește la dict dacă e list
            row_dict = {}
            for j, col in enumerate(columns):
                row_dict[col] = row[j] if j < len(row) else ""
            row_dict["PUNCTAJ"] = 0
            row_dict["ULTIMA_MOD"] = current_timestamp
            rows[i] = row_dict
            updated_count += 1
    
    print(f"✅ Updated {updated_count} rows with PUNCTAJ = 0")
    
    # Asigură că ULTIMA_MOD este în coloane
    if "ULTIMA_MOD" not in columns:
        columns.append("ULTIMA_MOD")
        print(f"✅ Added ULTIMA_MOD column")
    
    # 📦 SALVEAZĂ RAPORTUL DUPĂ RESET ÎN ARHIVĂ (cu PUNCTAJ = 0)
    reset_report_filename = f"{institution}_{reset_timestamp}_AFTER_RESET.json"
    reset_report_path = os.path.join(archive_city_dir, reset_report_filename)
    
    reset_report_data = {
        "archived_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "institution": institution,
        "city": city,
        "reset_by": reset_by_name,
        "discord_id": reset_by_id,
        "columns": columns,
        "rows": rows,
        "employee_count": len(rows),
        "status": "after_reset",
        "reset_timestamp": reset_timestamp
    }
    
    with open(reset_report_path, "w", encoding="utf-8") as f:
        json.dump(reset_report_data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Reset report saved: {reset_report_path}")
    
    # Salvează datele resetate în JSON cu timestamp
    inst_data["columns"] = columns
    inst_data["rows"] = rows
    inst_data["last_punctaj_update"] = current_timestamp
    
    inst_path = institution_path(city, institution)
    print(f"💾 Saving to {inst_path}...")
    with open(inst_path, "w", encoding="utf-8") as f:
        json.dump(inst_data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Updated institution data: {inst_path}")
    
    # VERIFY that data was saved correctly
    print(f"✓ Verifying saved data...")
    with open(inst_path, 'r', encoding='utf-8') as f:
        verify_data = json.load(f)
    
    verify_rows = verify_data.get("rows", [])
    for i, row in enumerate(verify_rows):
        discord = row.get('DISCORD', 'Unknown')
        punctaj = row.get('PUNCTAJ', 'N/A')
        print(f"   Verify Row {i}: {discord} - PUNCTAJ: {punctaj}")
    
    print(f"✅ Verification complete")
    
    # 🔴 LOG RESET ACTION - CINE A RESETAT SCORUL
    if ACTION_LOGGER:
        discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else "unknown"
        discord_username = DISCORD_AUTH.user_info.get('username', discord_id) if DISCORD_AUTH and DISCORD_AUTH.user_info else discord_id
        
        employee_count = len(rows)
        
        ACTION_LOGGER.log_custom_action(
            discord_id=discord_id,
            action_type="reset_punctaj_all",
            institution_name=institution,
            city=city,
            details=f"Reset punctaj pentru {employee_count} angajați. Archive: {json_path}",
            discord_username=discord_username
        )
        
        print(f"✅ Reset action logged: {discord_username} resetted {employee_count} employees in {institution}")
    else:
        print("⚠️ ACTION_LOGGER not available")
    
    # 📊 SAVE TO SUPABASE weekly_reports TABLE
    print(f"💾 Attempting to save to Supabase...")
    try:
        if SUPABASE_SYNC and SUPABASE_SYNC.enabled:
            import requests
            from datetime import datetime as dt
            
            print(f"✅ SUPABASE_SYNC is enabled")
            
            # Get the Monday of the current week
            today = dt.now()
            monday = today - __import__('datetime').timedelta(days=today.weekday())
            
            discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else ""
            discord_username = DISCORD_AUTH.user_info.get('username', 'Unknown') if DISCORD_AUTH and DISCORD_AUTH.user_info else "Unknown"
            
            # Get institution_id from inst_data if available
            institution_id = inst_data.get("institution_id", None)
            
            # Prepare data for weekly_reports
            report_json = {
                "week_start": monday.strftime('%Y-%m-%d'),
                "week_end": today.strftime('%Y-%m-%d'),
                "city": city,
                "institution": institution,
                "employee_count": len(rows),
                "reset_by": discord_username,
                "discord_id": discord_id,
                "report_data": {
                    "columns": columns,
                    "rows": rows,
                    "employee_count": len(rows),
                    "reset_at": current_timestamp,
                    "action": "reset_punctaj"
                },
                "archived_at": current_timestamp
            }
            
            # Use REST API to insert into weekly_reports
            headers = {
                "apikey": SUPABASE_SYNC.key,
                "Authorization": f"Bearer {SUPABASE_SYNC.key}",
                "Content-Type": "application/json"
            }
            
            url = f"{SUPABASE_SYNC.url}/rest/v1/weekly_reports"
            print(f"📡 Posting to: {url}")
            response = requests.post(url, json=report_json, headers=headers)
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 201:
                print(f"✅ Reset logged to Supabase weekly_reports: {city}/{institution}")
            else:
                print(f"⚠️ Failed to log reset to Supabase (Status {response.status_code})")
                print(f"   Response: {response.text}")
            
            # 📊 UPDATE EMPLOYEES TABLE IN SUPABASE - Set all PUNCTAJ to 0
            if institution_id:
                print(f"💾 Updating employees in Supabase to PUNCTAJ = 0...")
                try:
                    # Update all employees for this institution to PUNCTAJ = 0
                    update_url = f"{SUPABASE_SYNC.url}/rest/v1/employees?institution_id=eq.{institution_id}"
                    update_data = {"punctaj": 0, "updated_at": current_timestamp}
                    
                    update_response = requests.patch(update_url, json=update_data, headers=headers)
                    
                    if update_response.status_code == 200:
                        print(f"✅ Updated employees in Supabase: PUNCTAJ = 0")
                    else:
                        print(f"⚠️ Failed to update employees (Status {update_response.status_code})")
                except Exception as e:
                    print(f"⚠️ Could not update employees in Supabase: {e}")
            else:
                print(f"⚠️ Institution ID not found - skipping employees update")
        else:
            print(f"⚠️ SUPABASE_SYNC not enabled or not initialized")
    except Exception as e:
        print(f"⚠️ Could not save reset to Supabase: {e}")
        import traceback
        traceback.print_exc()
    
    # Reîncarcă treeview-ul cu noua coloană
    print(f"🔄 Refreshing tree view...")
    if "ULTIMA_MOD" not in tree.columns:
        tree.columns = list(tree.columns) + ["ULTIMA_MOD"]
        tree.heading("ULTIMA_MOD", text="ULTIMA_MOD", anchor="center")
        tree.column("ULTIMA_MOD", anchor="center", width=200)
    
    tree.delete(*tree.get_children())
    for row in rows:
        if isinstance(row, dict):
            values = tuple(row.get(col, "") for col in tree.columns)
        else:
            values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
        tree.insert("", tk.END, values=values)
    
    update_info_label(city, institution)
    sort_tree_by_punctaj(tree)
    
    print(f"✅ RESET PUNCTAJ COMPLETED for {city}/{institution}\n")
    messagebox.showinfo("Succes", f"✅ Punctaj resetat!\n\n📦 Datele vechi salvate în:\n{json_path}")


def show_weekly_report():
    """Afișează raportul din arhiva - toate JSON-urile salvate"""
    try:
        from datetime import timedelta
        
        # Colectează toate fișierele JSON din arhiva
        archive_files = []
        
        print(f"📂 Căutam în: {ARCHIVE_DIR}")
        
        try:
            for city_folder in os.listdir(ARCHIVE_DIR):
                city_path = os.path.join(ARCHIVE_DIR, city_folder)
                if not os.path.isdir(city_path):
                    continue
                
                print(f"   📂 Oraș: {city_folder}")
                
                for json_file in os.listdir(city_path):
                    if not json_file.endswith('.json'):
                        continue
                    
                    # 🚫 Skip AFTER_RESET files - only show original reports before reset
                    if '_AFTER_RESET' in json_file:
                        print(f"      ⏭️ Skipped (AFTER_RESET): {json_file}")
                        continue
                    
                    json_path = os.path.join(city_path, json_file)
                    
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # Extrage din filename: Institution_YYYY-MM-DD_HH-MM-SS.json
                            filename_without_ext = json_file.replace('.json', '')
                            parts = filename_without_ext.rsplit('_', 2)  # Split din dreapta
                            
                            if len(parts) >= 3:
                                institution = parts[0]
                                date_str = parts[1]  # YYYY-MM-DD
                                time_str = parts[2]  # HH-MM-SS
                                
                                archive_files.append({
                                    'city': city_folder,
                                    'institution': institution,
                                    'file': json_file,
                                    'path': json_path,
                                    'data': data,
                                    'date': date_str,
                                    'time': time_str,
                                    'archived_at': data.get('archived_at', 'N/A'),
                                    'employee_count': data.get('employee_count', 0)
                                })
                                
                                print(f"      ✅ {institution} ({date_str}) - {data.get('employee_count', 0)} employees")
                    except Exception as e:
                        print(f"      ⚠️ Eroare parsare {json_file}: {e}")
        except FileNotFoundError:
            messagebox.showwarning("Eroare", f"Folderul arhiva nu există: {ARCHIVE_DIR}")
            return
        
        if not archive_files:
            messagebox.showinfo("Info", f"Nu s-au găsit rapoarte în arhiva\n({ARCHIVE_DIR})")
            return
        
        print(f"\n✅ Găsite {len(archive_files)} rapoarte în arhiva")
        
        # Creează fereastră pentru afișare raport
        report_window = tk.Toplevel(root)
        report_window.title(f"📋 Rapoarte din Arhiva ({len(archive_files)} fișiere)")
        report_window.geometry("1000x650")
        
        # Header
        ttk.Label(
            report_window,
            text=f"📋 Rapoarte din Arhiva - {len(archive_files)} fișiere",
            font=("Segoe UI", 12, "bold")
        ).pack(padx=10, pady=10)
        
        # Treeview cu fișierele găsite
        columns = ("City", "Institution", "Date", "Time", "Employees", "ArchivedAt")
        tree = ttk.Treeview(report_window, columns=columns, height=15)
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("City", anchor=tk.W, width=120)
        tree.column("Institution", anchor=tk.W, width=150)
        tree.column("Date", anchor=tk.CENTER, width=120)
        tree.column("Time", anchor=tk.CENTER, width=110)
        tree.column("Employees", anchor=tk.CENTER, width=100)
        tree.column("ArchivedAt", anchor=tk.W, width=150)
        
        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("City", text="🏙️ Oraș", anchor=tk.W)
        tree.heading("Institution", text="🏢 Instituție", anchor=tk.W)
        tree.heading("Date", text="📅 Dată", anchor=tk.CENTER)
        tree.heading("Time", text="⏰ Ora", anchor=tk.CENTER)
        tree.heading("Employees", text="👥 Angajați", anchor=tk.CENTER)
        tree.heading("ArchivedAt", text="📦 Arhivat la", anchor=tk.W)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Populează treeview
        for item in sorted(archive_files, key=lambda x: (x['date'], x['time']), reverse=True):
            values = (
                item['city'],
                item['institution'],
                item['date'],
                item['time'],
                str(item['employee_count']),
                item['archived_at']
            )
            tree.insert("", tk.END, values=values)
        
        # Buttons frame
        btn_frame = ttk.Frame(report_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def show_employees_details():
            """Afișează detaliile angajaților cu punctajul lor din raport selectat"""
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Avertisment", "Te rog selectează o instituție!")
                return
            
            item_id = selected[0]
            values = tree.item(item_id, 'values')
            city = values[0]
            institution = values[1]
            date_str = values[2]
            
            # Găsește fișierul în archive_files
            report_data = None
            for archive in archive_files:
                if archive['city'] == city and archive['institution'] == institution and archive['date'] == date_str:
                    report_data = archive['data']
                    break
            
            if not report_data:
                messagebox.showerror("Eroare", "Nu s-au găsit datele raportului!")
                return
            
            # Creează fereastră detalii
            details_window = tk.Toplevel(report_window)
            details_window.title(f"👥 Angajații - {institution} ({date_str})")
            details_window.geometry("1200x600")
            
            # Header
            header_text = f"📋 {city} - {institution}\n📅 Data: {date_str} | 👥 Angajați: {report_data.get('employee_count', 0)}"
            ttk.Label(
                details_window,
                text=header_text,
                font=("Segoe UI", 11, "bold")
            ).pack(padx=10, pady=10)
            
            # Treeview cu detaliile angajaților
            columns = ("Discord", "Nume IC", "Rank", "Role", "Punctaj", "Serie Buletin", "Ultima Modificare")
            emp_tree = ttk.Treeview(details_window, columns=columns, height=20)
            emp_tree.column("#0", width=0, stretch=tk.NO)
            emp_tree.column("Discord", anchor=tk.W, width=100)
            emp_tree.column("Nume IC", anchor=tk.W, width=180)
            emp_tree.column("Rank", anchor=tk.CENTER, width=50)
            emp_tree.column("Role", anchor=tk.W, width=150)
            emp_tree.column("Punctaj", anchor=tk.CENTER, width=80)
            emp_tree.column("Serie Buletin", anchor=tk.W, width=120)
            emp_tree.column("Ultima Modificare", anchor=tk.W, width=150)
            
            emp_tree.heading("#0", text="", anchor=tk.W)
            emp_tree.heading("Discord", text="🎮 Discord", anchor=tk.W)
            emp_tree.heading("Nume IC", text="👤 Nume", anchor=tk.W)
            emp_tree.heading("Rank", text="⭐ Rank", anchor=tk.CENTER)
            emp_tree.heading("Role", text="💼 Rol", anchor=tk.W)
            emp_tree.heading("Punctaj", text="📊 Punctaj", anchor=tk.CENTER)
            emp_tree.heading("Serie Buletin", text="🆔 Serie Buletin", anchor=tk.W)
            emp_tree.heading("Ultima Modificare", text="🕐 Ultima Mod", anchor=tk.W)
            
            emp_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Populează cu angajații din raport
            rows = report_data.get('rows', [])
            for employee in rows:
                values = (
                    employee.get('DISCORD', ''),
                    employee.get('NUME IC', ''),
                    employee.get('RANK', ''),
                    employee.get('ROLE', ''),
                    str(employee.get('PUNCTAJ', 0)),
                    employee.get('SERIE DE BULETIN', ''),
                    str(employee.get('ULTIMA_MOD', ''))[:19]  # Doar data, fără microsecunde
                )
                emp_tree.insert("", tk.END, values=values)
            
            # Buttons
            btn_frame_details = ttk.Frame(details_window)
            btn_frame_details.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Button(
                btn_frame_details,
                text="❌ Închide",
                command=details_window.destroy
            ).pack(side=tk.RIGHT, padx=5)
        
        def load_to_supabase():
            """Încarcă datele din arhiva în Local - DOAR dacă instituția deja are fișier JSON"""
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Avertisment", "Te rog selectează cel puțin o instituție!")
                return
            
            try:
                loaded_count = 0
                skipped_count = 0
                skipped_list = []
                
                for item_id in selected:
                    values = tree.item(item_id, 'values')
                    city = values[0]
                    institution = values[1]
                    
                    # Verifică dacă fișierul JSON deja există
                    inst_path = institution_path(city, institution)
                    
                    if not os.path.exists(inst_path):
                        # Nu suprascrie dacă instituția nu are deja fișier
                        skipped_count += 1
                        skipped_list.append(f"{city}/{institution}")
                        print(f"⏭️ Skipped {city}/{institution} - no existing file")
                        continue
                    
                    # Găsește fișierul în archive_files
                    for archive in archive_files:
                        if archive['city'] == city and archive['institution'] == institution:
                            # Salvează datele locale (SUPRASCRIE FIȘIERUL EXISTENT)
                            inst_data = {
                                'columns': archive['data'].get('columns', []),
                                'rows': archive['data'].get('rows', [])
                            }
                            
                            with open(inst_path, 'w', encoding='utf-8') as f:
                                json.dump(inst_data, f, indent=4, ensure_ascii=False)
                            
                            loaded_count += 1
                            print(f"✅ Updated {city}/{institution} from archive")
                            break
                
                # Afișează mesaj cu rezultatul
                msg = f"✅ {loaded_count} instituții actualizate din arhiva!"
                if skipped_count > 0:
                    msg += f"\n\n⏭️ {skipped_count} instituții omise (nu au fișier existent):"
                    for skip in skipped_list:
                        msg += f"\n   • {skip}"
                
                messagebox.showinfo("Rezultat", msg)
                report_window.destroy()
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la încărcare: {e}")
        
        ttk.Button(
            btn_frame,
            text="👥 Vezi Angajații",
            command=show_employees_details
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📥 Încarcă în Local",
            command=load_to_supabase
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="❌ Închide",
            command=report_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
    except Exception as e:
        print(f"❌ Error showing archive report: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Eroare", f"Eroare: {e}")


def update_info_label(city, institution):
    """Actualizează label-ul cu timestamp-ul ultimei modificări - LOCAL ONLY"""
    if city not in tabs or institution not in tabs[city]["info_frames"]:
        return
    
    # Load from LOCAL file ONLY - don't sync with Supabase
    inst_path = institution_path(city, institution)
    if not os.path.exists(inst_path):
        return
    
    with open(inst_path, 'r', encoding='utf-8') as f:
        inst_data = json.load(f)
    
    last_update = inst_data.get("last_punctaj_update", "N/A")
    info_label = tabs[city]["info_frames"][institution]
    info_label.config(text=f"⏱️ Ultima modificare: {last_update}")


def apply_search_filter(tree, search_column, search_text, all_rows, columns):
    """Filtrează treeview-ul pe baza coloanei și textului de căutare"""
    tree.delete(*tree.get_children())
    
    if not search_column or not search_text:
        # Dacă nu e specificată căutare, arată toate rândurile
        for row in all_rows:
            if isinstance(row, dict):
                values = tuple(row.get(col, "") for col in columns)
            else:
                values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
            tree.insert("", tk.END, values=values)
    else:
        # Filtrează rândurile care conțin textul de căutare în coloana specificată
        col_index = columns.index(search_column) if search_column in columns else 0
        search_lower = search_text.lower()
        
        for row in all_rows:
            if isinstance(row, dict):
                values = tuple(row.get(col, "") for col in columns)
            else:
                values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
            
            # Compară valoarea din coloana specificată
            if col_index < len(values):
                cell_value = str(values[col_index]).lower()
                if search_lower in cell_value:
                    tree.insert("", tk.END, values=values)
    
    sort_tree_by_punctaj(tree)


def create_institution_tab(city, institution):
    ensure_institution(city, institution)

    inst_nb = tabs[city]["nb"]
    frame = tk.Frame(inst_nb)
    inst_nb.add(frame, text=institution)

    inst_data = load_institution(city, institution)
    columns = inst_data.get("columns", ["Discord", "Nume", "Punctaj"])
    rows = inst_data.get("rows", [])
    ranks_map = inst_data.get("ranks", {})

    # Frame pentru treeview cu scrollbars
    tree_frame = tk.Frame(frame)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Vertical scrollbar
    v_scrollbar = tk.Scrollbar(tree_frame, orient="vertical")
    v_scrollbar.pack(side="right", fill="y")
    
    # Horizontal scrollbar
    h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal")
    h_scrollbar.pack(side="bottom", fill="x")
    
    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        selectmode="extended",
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )
    tree.pack(fill="both", expand=True)
    
    # Connect scrollbars to treeview
    v_scrollbar.config(command=tree.yview)
    h_scrollbar.config(command=tree.xview)
    
    # Salvează coloanele pe tree pentru a le folosi în save_institution
    tree.columns = columns

    for col in columns:
        tree.heading(col, text=col.upper(), anchor="center")
        tree.column(col, anchor="center", width=200)

    # Încarcă rândurile din date - deduplicare
    seen_discord = set()
    unique_rows = []
    for row in rows:
        if isinstance(row, dict):
            discord_id = row.get("DISCORD", "")
            # Skip if already seen (deduplicate)
            if discord_id and discord_id in seen_discord:
                print(f"⚠️ Duplicate employee skipped: {row.get('NUME IC', discord_id)}")
                continue
            if discord_id:
                seen_discord.add(discord_id)
            unique_rows.append(row)
        else:
            unique_rows.append(row)
    
    for row in unique_rows:
        if isinstance(row, dict):
            values = tuple(row.get(col, "") for col in columns)
        else:
            values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
        tree.insert("", tk.END, values=values)
    
    # Sincronizează rolurile cu rankurile curente
    if sync_roles_with_ranks(tree, ranks_map):
        save_institution(city, institution, tree)
    
    # Sortează angajații descrescător după PUNCTAJ
    sort_tree_by_punctaj(tree)

    # ===== INFO FRAME CU TIMESTAMP ULTIMEI MODIFICARI =====
    last_update = inst_data.get("last_punctaj_update", "N/A")
    info_frame = tk.Frame(frame, bg="#e3f2fd", relief="solid", borderwidth=1)
    info_frame.pack(fill="x", padx=10, pady=5)
    
    info_label = tk.Label(
        info_frame, 
        text=f"⏱️ Ultima modificare: {last_update}", 
        font=("Segoe UI", 9), 
        bg="#e3f2fd",
        fg="#1565c0"
    )
    info_label.pack(side="left", padx=10, pady=5)
    
    # Salvează referința la info_label pentru actualizare dinamică
    tabs[city]["info_frames"][institution] = info_label

    # ===== SEARCH FRAME =====
    search_frame = tk.Frame(frame, bg="#f0f0f0", relief="solid", borderwidth=1)
    search_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(search_frame, text="🔍 Cauta:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(side="left", padx=10, pady=8)
    
    # Dropdown pentru selectarea coloanei (excluzând ROLE)
    searchable_columns = [col for col in columns if col != "ROLE"]
    cb_column = ttk.Combobox(search_frame, values=searchable_columns, state="readonly", width=15, font=("Segoe UI", 9))
    cb_column.pack(side="left", padx=5)
    if searchable_columns:
        cb_column.current(0)
    
    # Entry pentru textul de căutare
    search_entry = tk.Entry(search_frame, font=("Segoe UI", 9), width=20)
    search_entry.pack(side="left", padx=5)
    
    # Funcție de căutare
    def do_search():
        search_col = cb_column.get()
        search_txt = search_entry.get().strip()
        apply_search_filter(tree, search_col, search_txt, rows, columns)
    
    # Funcție de reset
    def reset_search():
        search_entry.delete(0, tk.END)
        cb_column.current(0)
        apply_search_filter(tree, "", "", rows, columns)
    
    tk.Button(search_frame, text="🔎 Cauta", command=do_search, font=("Segoe UI", 9), bg="#2196F3", fg="white").pack(side="left", padx=5)
    tk.Button(search_frame, text="✕ Reset", command=reset_search, font=("Segoe UI", 9), bg="#757575", fg="white").pack(side="left", padx=5)
    
    # Bind Enter pe search_entry pentru căutare rapidă
    search_entry.bind("<Return>", lambda e: do_search())

    btn_frame = tk.Frame(frame)
    btn_frame.pack(pady=10)

    # Buton Adaugă Angajat
    btn_add_emp = tk.Button(
        btn_frame, text="Adaugă angajat", width=18,
        command=lambda t=tree, c=city, inst=institution: add_member(t, c, inst)
    )
    btn_add_emp.grid(row=0, column=0, padx=8, pady=5)
    # Verifică permisiuni pe instituție (granulare)
    if not check_institution_permission(city, institution, 'can_add_employee'):
        btn_add_emp.config(state='disabled')

    # Buton Șterge Angajat
    btn_del_emp = tk.Button(
        btn_frame, text="Șterge angajat", width=18,
        command=lambda t=tree, c=city, inst=institution: delete_members(t, c, inst)
    )
    btn_del_emp.grid(row=0, column=1, padx=8, pady=5)
    # Verifică permisiuni pe instituție (granulare)
    if not check_institution_permission(city, institution, 'can_delete_employee'):
        btn_del_emp.config(state='disabled')

    # Buton Editează Angajat
    btn_edit_emp = tk.Button(
        btn_frame, text="✏️ Editează angajat", width=18,
        command=lambda t=tree, c=city, inst=institution: edit_member(t, c, inst)
    )
    btn_edit_emp.grid(row=0, column=2, padx=8, pady=5)
    # Verifică permisiuni pe instituție (granulare)
    if not check_institution_permission(city, institution, 'can_edit_employee'):
        btn_edit_emp.config(state='disabled')

    btn_add_points = tk.Button(
        btn_frame, text="➕ Adaugă punctaj", width=18,
        command=lambda t=tree, c=city, inst=institution: punctaj_cu_selectie(t, c, inst, "add")
    )
    btn_add_points.grid(row=1, column=0, padx=8, pady=5)
    # Verifică permisiuni pe instituție (granulare)
    if not check_institution_permission(city, institution, 'can_add_score'):
        btn_add_points.config(state='disabled')

    btn_remove_points = tk.Button(
        btn_frame, text="➖ Scade punctaj", width=18,
        command=lambda t=tree, c=city, inst=institution: punctaj_cu_selectie(t, c, inst, "remove")
    )
    btn_remove_points.grid(row=1, column=1, padx=8, pady=5)
    # Verifică permisiuni pe instituție (granulare)
    if not check_institution_permission(city, institution, 'can_add_score'):
        btn_remove_points.config(state='disabled')

    btn_reset_points = tk.Button(
        btn_frame, text="🔄 Reset punctaj", width=18, bg="#FF9800", fg="white",
        command=lambda t=tree, c=city, inst=institution: reset_punctaj(t, c, inst)
    )
    btn_reset_points.grid(row=1, column=2, padx=8, pady=5)
    # Verifică permisiuni pe instituție (granulare)
    if not check_institution_permission(city, institution, 'can_add_score'):
        btn_reset_points.config(state='disabled')

    tabs[city]["trees"][institution] = tree
    inst_nb.select(frame)




def add_institution(city):
    name = simpledialog.askstring("Instituție", f"Instituție nouă în {city}:")
    if not name:
        return
    name = name.strip().replace(" ", "_")
    if name in tabs[city]["trees"]:
        messagebox.showerror("Eroare", "Există deja o instituție cu acest nume în oraș!")
        return
    
    # Fereastră pentru definire variabile suplimentare
    win = tk.Toplevel(root)
    win.title(f"Adaugă variabile - {name} ({city})")
    win.geometry("550x500")
    win.grab_set()
    
    tk.Label(win, text="Adaugă variabile personalizate pentru instituție", font=("Segoe UI", 10, "bold")).pack(pady=10)
    tk.Label(win, text="Variabilele RANK, ROLE și PUNCTAJ sunt deja incluse!", font=("Segoe UI", 9), fg="#2196F3").pack(pady=5)
    
    # ===== RANKURI - PRIMA ALEGERE =====
    tk.Label(win, text="Configurare RANK", font=("Segoe UI", 10, "bold"), fg="#FF9800").pack(pady=10)
    
    rank_frame = tk.Frame(win, relief="solid", borderwidth=1, bg="#fff3e0")
    rank_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(rank_frame, text="Câte rankuri ai? (ex: 3 pentru rankuri 1, 2, 3)", font=("Segoe UI", 9), bg="#fff3e0").pack(anchor="w", padx=10, pady=5)
    e_num_ranks = tk.Entry(rank_frame, width=10, font=("Segoe UI", 10))
    e_num_ranks.insert(0, "2")
    e_num_ranks.pack(anchor="w", padx=10, pady=5)
    
    # Frame pentru definire rankuri (inițial gol, se completează după input)
    ranks_defs = tk.Frame(win)
    ranks_defs.pack(fill="both", expand=True, padx=10, pady=5)
    
    canvas_defs = tk.Canvas(ranks_defs)
    scrollbar_defs = tk.Scrollbar(ranks_defs, orient="vertical", command=canvas_defs.yview)
    scroll_defs = tk.Frame(canvas_defs)
    
    scroll_defs.bind("<Configure>", lambda e: canvas_defs.configure(scrollregion=canvas_defs.bbox("all")))
    canvas_defs.create_window((0, 0), window=scroll_defs, anchor="nw")
    canvas_defs.configure(yscrollcommand=scrollbar_defs.set)
    
    canvas_defs.pack(side="left", fill="both", expand=True)
    scrollbar_defs.pack(side="right", fill="y")
    
    rank_entries = {}
    
    def update_rank_fields(*args):
        """Actualizează câmpurile de rank când se schimbă numărul"""
        try:
            num = int(e_num_ranks.get())
            if num < 1:
                num = 1
        except ValueError:
            return
        
        # Curăță frame-urile anterioare
        for widget in scroll_defs.winfo_children():
            widget.destroy()
        rank_entries.clear()
        
        tk.Label(scroll_defs, text="Definește rolul pentru fiecare rank:", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=5, pady=(5, 10))
        
        for rank_num in range(1, num + 1):
            rank_row = tk.Frame(scroll_defs, relief="solid", borderwidth=1)
            rank_row.pack(fill="x", pady=5, padx=5)
            
            tk.Label(rank_row, text=f"Rank {rank_num} →", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5, pady=5)
            e_rol = tk.Entry(rank_row, width=30, font=("Segoe UI", 10))
            e_rol.pack(side="left", padx=5, pady=5, fill="x", expand=True)
            
            # Setează roluri implicite
            if rank_num == 1:
                e_rol.insert(0, "User")
            elif rank_num == 2:
                e_rol.insert(0, "Admin")
            
            rank_entries[rank_num] = e_rol
    
    e_num_ranks.bind("<KeyRelease>", update_rank_fields)
    update_rank_fields()  # Inițializează cu 2 rankuri
    
    # ===== VARIABILE PERSONALIZATE =====
    tk.Label(win, text="Variabile personalizate", font=("Segoe UI", 10, "bold"), fg="#FF9800").pack(pady=10)
    
    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, padx=10, pady=5)
    
    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)
    
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    extra_columns = []
    
    def add_column():
        col_frame = tk.Frame(scroll_frame, relief="solid", borderwidth=1)
        col_frame.pack(fill="x", pady=5, padx=5)
        
        tk.Label(col_frame, text="Variabilă:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        e_col = tk.Entry(col_frame, width=30, font=("Segoe UI", 10))
        e_col.grid(row=0, column=1, padx=5, pady=5)
        
        def remove_col():
            col_frame.destroy()
            if e_col in extra_columns:
                extra_columns.remove(e_col)
        
        tk.Button(col_frame, text="✕ Șterge", command=remove_col, width=8, bg="#F44336", fg="white").grid(row=0, column=2, padx=5, pady=5)
        
        extra_columns.append(e_col)
    
    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", pady=10)
    
    tk.Button(btn_frame, text="➕ Adaugă variabilă", command=add_column, width=30, bg="#2196F3", fg="white").pack(side="left", padx=5)
    
    def save_structure():
        # Validează numărul de rankuri
        try:
            num_ranks = int(e_num_ranks.get())
            if num_ranks < 1:
                messagebox.showerror("Eroare", "Trebuie să ai cel puțin 1 rank!")
                return
        except ValueError:
            messagebox.showerror("Eroare", "Introduceți un număr valid pentru rankuri!")
            return
        
        # Validează roluri pentru fiecare rank
        ranks_data = {}
        for rank_num in range(1, num_ranks + 1):
            rol = rank_entries[rank_num].get().strip()
            if not rol:
                messagebox.showerror("Eroare", f"Introduceți un rol pentru rank {rank_num}!")
                return
            ranks_data[str(rank_num)] = rol
        
        # Variabile custom
        col_names = [e.get().strip().upper() for e in extra_columns]
        col_names = [c for c in col_names if c]
        
        # Verifică duplicate
        if len(col_names) != len(set(col_names)):
            messagebox.showerror("Eroare", "Nu pot exista două variabile cu același nume!")
            return
        
        # Structura finală: Variabile custom + RANK + ROLE + PUNCTAJ
        final_cols = col_names + ["RANK", "ROLE", "PUNCTAJ"]
        
        ensure_institution(city, name)
        
        # Crea o descriere ușor de citit a rankurilor
        ranks_description = "\n".join([f"Rank {rank_num}: {ranks_data[str(rank_num)]}" for rank_num in sorted([int(k) for k in ranks_data.keys()])])
        
        data = {
            "columns": final_cols,
            "ranks": ranks_data,
            "rankuri_desc": ranks_description,
            "rows": []
        }
        
        # Salvează în JSON local
        inst_path = institution_path(city, name)
        with open(inst_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        # Sincronizează cu Supabase (creează tabelul în police_data)
        if SUPABASE_SYNC and SUPABASE_SYNC.enabled:
            try:
                result = supabase_upload(city, name, data, inst_path)
                if result.get("status") == "success":
                    print(f"✓ Instituție '{name}' sincronizată cu Supabase")
                else:
                    print(f"⚠️ Instituție salvată local, dar sincronizare Supabase eșuată")
            except Exception as e:
                print(f"⚠️ Eroare sincronizare instituție: {e}")
                messagebox.showwarning(
                    "Sincronizare",
                    f"Instituția '{name}' a fost creată local, dar nu s-a putut sincroniza cu Supabase.\n\nEroare: {e}"
                )
        
        win.destroy()
        create_institution_tab(city, name)
    
    tk.Button(btn_frame, text="✓ Creează tabel", command=save_structure, bg="#4CAF50", fg="white", width=30, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)


def edit_institution(city):
    inst_nb = tabs.get(city, {}).get("nb")
    if not inst_nb:
        messagebox.showinfo("Info", "Nu există instituții de editat!")
        return

    current = inst_nb.select()
    if not current:
        messagebox.showinfo("Info", "Selectează o instituție din tab-urile orașului!")
        return

    old_inst = inst_nb.tab(current, "text")
    new_inst = simpledialog.askstring("Editează instituție", "Nume nou:", initialvalue=old_inst)
    if not new_inst:
        return
    new_inst = new_inst.strip().replace(" ", "_")

    if new_inst == old_inst:
        return
    if new_inst in tabs[city]["trees"]:
        messagebox.showerror("Eroare", "Există deja o instituție cu acest nume!")
        return

    try:
        os.rename(institution_path(city, old_inst), institution_path(city, new_inst))
    except Exception as e:
        messagebox.showerror("Eroare", f"Nu pot redenumi instituția: {e}")
        return

    # reconstruieste tab-ul instituției
    inst_nb.forget(current)
    tabs[city]["trees"].pop(old_inst, None)
    create_institution_tab(city, new_inst)


def delete_institution_ui(city):
    trees = tabs.get(city, {}).get("trees", {})
    if not trees:
        messagebox.showinfo("Info", "Nu există instituții de șters în acest oraș!")
        return

    win = tk.Toplevel(root)
    win.title(f"Șterge instituții - {city}")
    win.geometry("400x450")
    win.grab_set()

    frame_top = tk.Frame(win, bg="#ffe8e8", pady=10)
    frame_top.pack(fill="x")
    tk.Label(frame_top, text="Selectează instituțiile de șters", font=("Segoe UI", 10, "bold"), bg="#ffe8e8").pack(pady=5)

    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, pady=10)

    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_inst = []
    for inst in sorted(trees.keys()):
        var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(scroll_frame, text=inst, variable=var, anchor="w", font=("Segoe UI", 10))
        chk.pack(fill="x", padx=10, pady=3)
        vars_inst.append((inst, var))

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    def select_all():
        for _, var in vars_inst:
            var.set(True)

    tk.Button(btn_frame, text="✓ Selectează toate", command=select_all, width=18).pack(side="left", padx=5)

    def deselect_all():
        for _, var in vars_inst:
            var.set(False)

    tk.Button(btn_frame, text="✗ Deselectează toate", command=deselect_all, width=18).pack(side="left", padx=5)

    def aplica():
        selectate = [inst for inst, var in vars_inst if var.get()]
        if not selectate:
            messagebox.showwarning("Nicio selecție", "Nu ai selectat nicio instituție!")
            return
        if not messagebox.askyesno("Confirmare", f"Ștergi {len(selectate)} instituție(i) din {city}?"):
            return

        inst_nb = tabs[city]["nb"]
        for inst in selectate:
            # șterge tab-ul
            for tab_id in inst_nb.tabs():
                if inst_nb.tab(tab_id, "text") == inst:
                    inst_nb.forget(tab_id)
                    break
            delete_institution(city, inst)
            tabs[city]["trees"].pop(inst, None)

        win.destroy()
        messagebox.showinfo("Succes", "Instituțiile au fost șterse.")

    tk.Button(win, text="🗑️ ȘTERGE INSTITUȚII", bg="#F44336", fg="white", font=("Segoe UI", 10, "bold"), width=25, height=2, command=aplica).pack(pady=15)


def add_member(tree, city, institution):
    data = load_institution(city, institution)
    ranks_map = data.get("ranks", {})
    
    win = tk.Toplevel(root)
    win.title(f"Adaugă angajat - {institution} ({city})")
    win.geometry("500x600")
    win.resizable(True, True)
    win.grab_set()

    columns = tree.columns
    entries = {}
    
    # Creează frame cu scroll pentru entries
    frame_main = tk.Frame(win)
    frame_main.pack(fill="both", expand=True, padx=10, pady=10)
    
    canvas = tk.Canvas(frame_main, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(frame_main, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="white")
    
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Enable mouse wheel scroll
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Creează mai întâi toate entry-urile
    for i, col in enumerate(columns):
        label_frame = tk.Frame(scroll_frame, bg="white")
        label_frame.pack(fill="x", pady=5)
        
        tk.Label(label_frame, text=f"{col}:", bg="white", font=("Segoe UI", 9)).pack(anchor="w", padx=10)
        
        if col == "RANK":
            # Entry pentru RANK (user intră manual numărul)
            e_rank = tk.Entry(label_frame, justify="center", width=40)
            e_rank.pack(fill="x", padx=20)
            entries[col] = e_rank
        
        elif col == "ROLE":
            # ROLE este read-only, se completează automat
            e = tk.Entry(label_frame, justify="center", width=40, state="readonly")
            e.pack(fill="x", padx=20)
            entries[col] = e
        
        elif col == "PUNCTAJ":
            # PUNCTAJ defaultează la 0
            e = tk.Entry(label_frame, justify="center", width=40)
            e.insert(0, "0")
            e.pack(fill="x", padx=20)
            entries[col] = e
        
        else:
            e = tk.Entry(label_frame, justify="center", width=40)
            e.pack(fill="x", padx=20)
            entries[col] = e
    
    # Acum configură bind-urile și completările
    if "RANK" in entries:
        def on_rank_change(event=None):
            if "ROLE" in entries:
                rank_val = entries["RANK"].get().strip()
                if rank_val in ranks_map:
                    entries["ROLE"].config(state="normal")
                    entries["ROLE"].delete(0, tk.END)
                    entries["ROLE"].insert(0, ranks_map[rank_val])
                    entries["ROLE"].config(state="readonly")
        
        entries["RANK"].bind("<KeyRelease>", on_rank_change)
        # Apelează la început în caz că RANK are deja valoare (edit)
        on_rank_change()

    def save():
        # Asigură că ROLE este completat înainte de a salva
        if "RANK" in entries and "ROLE" in entries:
            rank_val = entries["RANK"].get().strip()
            if rank_val in ranks_map:
                entries["ROLE"].config(state="normal")
                entries["ROLE"].delete(0, tk.END)
                entries["ROLE"].insert(0, ranks_map[rank_val])
                entries["ROLE"].config(state="readonly")
        
        values = []
        for col in columns:
            if col == "ROLE":
                rank_val = str(entries["RANK"].get())
                values.append(ranks_map.get(rank_val, ""))
            else:
                values.append(entries[col].get().strip())
        
        if not any(values):
            messagebox.showwarning("Eroare", "Adaugă cel puțin o valoare!")
            return
        
        new_item = tree.insert("", tk.END, values=tuple(values))
        has_punctaj = "PUNCTAJ" in columns
        save_institution(city, institution, tree, update_timestamp=has_punctaj, updated_items=[new_item], skip_logging=True)
        
        # ===== SUPABASE SYNC =====
        if SUPABASE_EMPLOYEE_MANAGER_AVAILABLE and data.get("source") == "supabase":
            try:
                employee_data = dict(zip(columns, values))
                supabase_emp_data = SUPABASE_EMPLOYEE_MANAGER.format_employee_for_supabase(employee_data)
                
                # Add to Supabase
                SUPABASE_EMPLOYEE_MANAGER.add_employee(data["institution_id"], supabase_emp_data)
                print(f"✓ Employee synced to Supabase: {employee_data.get('NUME IC', 'Unknown')}")
            except Exception as e:
                print(f"⚠️ Error syncing to Supabase: {e}")
        
        # ===== ACTION LOGGING =====
        if ACTION_LOGGER:
            try:
                employee_name = values[0] if values else "Unknown"
                employee_data = dict(zip(columns, values))
                discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else "unknown"
                discord_username = DISCORD_AUTH.user_info.get('username', discord_id) if DISCORD_AUTH else "unknown"
                print(f"📝 ADD_EMPLOYEE LOG: user={discord_username} ({discord_id}), employee={employee_name}, city={city}, inst={institution}")
                ACTION_LOGGER.log_add_employee(
                    discord_id,
                    city,
                    institution,
                    employee_name,
                    employee_data,
                    discord_username=discord_username
                )
            except Exception as e:
                print(f"⚠️ Error logging add_employee action: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️ ACTION_LOGGER is None - cannot log add_employee")
        
        # Adaug ULTIMA_MOD la treeview dacă nu e acolo
        if "ULTIMA_MOD" not in tree.columns:
            tree.columns = list(tree.columns) + ["ULTIMA_MOD"]
            tree.heading("ULTIMA_MOD", text="ULTIMA_MOD", anchor="center")
            tree.column("ULTIMA_MOD", anchor="center", width=200)
            tree.delete(*tree.get_children())
            inst_data = load_institution(city, institution)
            rows = inst_data.get("rows", [])
            for row in rows:
                if isinstance(row, dict):
                    values = tuple(row.get(col, "") for col in tree.columns)
                else:
                    values = tuple(row) if isinstance(row, (list, tuple)) else (row,)
                tree.insert("", tk.END, values=values)
        
        update_info_label(city, institution)
        sort_tree_by_punctaj(tree)
        win.destroy()
    
    # Pack scroll components
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Buton de salvare
    button_frame = tk.Frame(win)
    button_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Button(button_frame, text="✓ Salvează", command=save, bg="#4CAF50", fg="white", 
              font=("Segoe UI", 10, "bold"), width=25, height=2).pack(pady=5)
    tk.Button(button_frame, text="✕ Anulează", command=win.destroy, bg="#f44336", fg="white",
              font=("Segoe UI", 10, "bold"), width=25, height=2).pack(pady=5)

def delete_members(tree, city, institution):
    data = load_institution(city, institution)
    
    win = tk.Toplevel(root)
    win.title("Șterge angajat")
    win.geometry("500x550")
    win.grab_set()

    # ---------- HEADER ----------
    frame_top = tk.Frame(win, bg="#ffe8e8", pady=10)
    frame_top.pack(fill="x")

    tk.Label(
        frame_top, 
        text="Selectează angajații pe care vrei să-i ștergi", 
        font=("Segoe UI", 10, "bold"),
        bg="#ffe8e8"
    ).pack(pady=5)
    
    sync_label = "☁️ Supabase" if data.get("source") == "supabase" else "📁 Local"
    tk.Label(
        frame_top, 
        text=f"⚠️ Ștergerea va fi sincronizată imediat în cloud ({sync_label})", 
        font=("Segoe UI", 8),
        fg="#d32f2f",
        bg="#ffe8e8"
    ).pack(pady=2)

    # ---------- LISTĂ CU CHECKBOX ----------
    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, pady=10)

    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_items = []
    item_to_supabase_id = {}  # Map tree items to Supabase IDs

    rows = data.get("rows", [])
    
    for i, item in enumerate(tree.get_children()):
        values = tree.item(item, "values")
        # Arată primele 3 coloane pentru identificare
        display = " | ".join(str(v) for v in values[:3])
        var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(
            scroll_frame,
            text=display,
            variable=var,
            anchor="w"
        )
        chk.pack(fill="x", padx=10, pady=2)
        vars_items.append((item, var))
        
        # Store Supabase ID if available
        if i < len(rows) and isinstance(rows[i], dict) and "id" in rows[i]:
            item_to_supabase_id[item] = rows[i]["id"]

    # ---------- BUTOANE CONTROL ----------
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    def select_all():
        for _, var in vars_items:
            var.set(True)

    tk.Button(btn_frame, text="✓ Selectează toți", command=select_all, width=18).pack(side="left", padx=5)

    def deselect_all():
        for _, var in vars_items:
            var.set(False)

    tk.Button(btn_frame, text="✗ Deselectează toți", command=deselect_all, width=18).pack(side="left", padx=5)

    # ---------- CONFIRMARE ----------
    def aplica():
        selectati = [item for item, var in vars_items if var.get()]

        if not selectati:
            messagebox.showwarning(
                "Nicio selecție",
                "Nu ai selectat niciun angajat pentru ștergere!"
            )
            return

        if not messagebox.askyesno(
            "Confirmare ștergere",
            f"Sigur vrei să ștergi {len(selectati)} angajat/angajați?\n\n" +
            f"✅ Vor fi șterși LOCAL\n" +
            f"☁️ Vor fi sincronizați IMEDIAT în cloud\n\n" +
            f"Continuă?"
        ):
            return

        # 1. ȘTERGE LOCAL
        deleted_names = []
        deleted_data = []
        deleted_supabase_ids = []
        
        for item in selectati:
            values = tree.item(item, "values")
            if values:
                deleted_names.append(str(values[0])[:50])
                deleted_data.append(dict(zip(tree.columns, values)))
                if item in item_to_supabase_id:
                    deleted_supabase_ids.append(item_to_supabase_id[item])
            tree.delete(item)

        # 2. SALVEAZĂ LOCAL ÎN JSON
        save_institution(city, institution, tree)
        
        # ===== SUPABASE SYNC =====
        if SUPABASE_EMPLOYEE_MANAGER_AVAILABLE and data.get("source") == "supabase":
            try:
                for supabase_id in deleted_supabase_ids:
                    SUPABASE_EMPLOYEE_MANAGER.delete_employee(supabase_id)
                    print(f"✓ Employee deleted from Supabase (ID: {supabase_id})")
            except Exception as e:
                print(f"⚠️ Error syncing delete to Supabase: {e}")
        
        # ===== ACTION LOGGING =====
        if ACTION_LOGGER:
            try:
                discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else "unknown"
                discord_username = DISCORD_AUTH.user_info.get('username', discord_id) if DISCORD_AUTH else "unknown"
                for name, del_data in zip(deleted_names, deleted_data):
                    print(f"📝 DELETE_EMPLOYEE LOG: user={discord_username} ({discord_id}), employee={name}, city={city}, inst={institution}")
                    ACTION_LOGGER.log_delete_employee(
                        discord_id,
                        city,
                        institution,
                        name,
                        del_data,
                        discord_username=discord_username
                    )
            except Exception as e:
                print(f"⚠️ Error logging delete_employee action: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️ ACTION_LOGGER is None - cannot log delete_employee")
        
        update_info_label(city, institution)
        sort_tree_by_punctaj(tree)
        win.destroy()

    tk.Button(
        win,
        text="🗑️ ȘTERGE SELECTAȚI",
        bg="#F44336",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=25,
        height=2,
        command=aplica
    ).pack(pady=15)


def edit_member(tree, city, institution):
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Eroare", "Selectează un angajat!")
        return
    if len(sel) > 1:
        messagebox.showwarning("Eroare", "Selectează un singur angajat pentru editare!")
        return

    item = sel[0]
    old_values = tree.item(item, "values")
    columns = tree.columns
    
    data = load_institution(city, institution)
    ranks_map = data.get("ranks", {})

    win = tk.Toplevel(root)
    win.title(f"Editează angajat - {institution} ({city})")
    win.geometry("550x700")
    win.resizable(False, False)
    win.grab_set()

    # ===== BARĂ SUPERIOR CU TITLU =====
    header_frame = tk.Frame(win, bg="#1565c0", height=50)
    header_frame.pack(fill="x", padx=0, pady=0)
    header_frame.pack_propagate(False)
    
    tk.Label(
        header_frame,
        text=f"📝 Editare angajat",
        font=("Segoe UI", 12, "bold"),
        bg="#1565c0",
        fg="white"
    ).pack(pady=10)

    # ===== FRAME PRINCIPAL CU SCROLL =====
    main_frame = tk.Frame(win)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    entries = {}
    
    # Creează toate entry-urile
    for i, col in enumerate(columns):
        label = tk.Label(main_frame, text=f"{col}:", font=("Segoe UI", 10, "bold"))
        label.pack(pady=(12, 3), anchor="w")
        
        if col == "RANK":
            e_rank = tk.Entry(main_frame, justify="center", width=30, font=("Segoe UI", 10))
            e_rank.insert(0, old_values[i] if i < len(old_values) else "")
            e_rank.pack(pady=(0, 0), ipady=6, fill="x")
            entries[col] = e_rank
        
        elif col == "ROLE":
            e = tk.Entry(main_frame, justify="center", width=30, font=("Segoe UI", 10), state="readonly", bg="#f0f0f0")
            e.insert(0, old_values[i] if i < len(old_values) else "")
            e.pack(pady=(0, 0), ipady=6, fill="x")
            entries[col] = e
        
        else:
            e = tk.Entry(main_frame, justify="center", width=30, font=("Segoe UI", 10))
            e.insert(0, old_values[i] if i < len(old_values) else "")
            e.pack(pady=(0, 0), ipady=6, fill="x")
            entries[col] = e
    
    # Acum configură bind-urile și completările
    if "RANK" in entries:
        def on_rank_change(event=None):
            if "ROLE" in entries:
                rank_val = entries["RANK"].get().strip()
                if rank_val in ranks_map:
                    entries["ROLE"].config(state="normal")
                    entries["ROLE"].delete(0, tk.END)
                    entries["ROLE"].insert(0, ranks_map[rank_val])
                    entries["ROLE"].config(state="readonly")
        
        entries["RANK"].bind("<KeyRelease>", on_rank_change)
        # Apelează la început în caz că RANK are deja valoare (edit)
        on_rank_change()

    def save():
        # Asigură că ROLE este completat înainte de a salva
        if "RANK" in entries and "ROLE" in entries:
            rank_val = entries["RANK"].get().strip()
            if rank_val in ranks_map:
                entries["ROLE"].config(state="normal")
                entries["ROLE"].delete(0, tk.END)
                entries["ROLE"].insert(0, ranks_map[rank_val])
                entries["ROLE"].config(state="readonly")
        
        values = []
        for col in columns:
            if col == "ROLE":
                rank_val = str(entries["RANK"].get())
                values.append(ranks_map.get(rank_val, ""))
            else:
                values.append(entries[col].get().strip())
        
        if not any(values):
            messagebox.showwarning("Eroare", "Adaugă cel puțin o valoare!")
            return
        
        # Verifică dacă PUNCTAJ s-a modificat
        punctaj_changed = False
        if "PUNCTAJ" in columns:
            punctaj_idx = columns.index("PUNCTAJ")
            old_punctaj = str(old_values[punctaj_idx]) if punctaj_idx < len(old_values) else ""
            new_punctaj = str(values[punctaj_idx])
            punctaj_changed = old_punctaj != new_punctaj
        
        tree.item(item, values=tuple(values))
        # Marchează rândul ca updatat dacă PUNCTAJ s-a modificat
        save_institution(city, institution, tree, update_timestamp=punctaj_changed, updated_items=[item] if punctaj_changed else None, skip_logging=True)
        
        # ===== ACTION LOGGING =====
        if ACTION_LOGGER:
            try:
                # Colectează modificări
                changed_fields = {}
                for col_idx, col in enumerate(columns):
                    old_val = str(old_values[col_idx]) if col_idx < len(old_values) else ""
                    new_val = str(values[col_idx])
                    if old_val != new_val:
                        changed_fields[col] = (old_val, new_val)
                
                if changed_fields:
                    employee_name = values[0] if values else "Unknown"
                    changes_str = "; ".join([f"{field}: {old_val} → {new_val}" 
                                           for field, (old_val, new_val) in changed_fields.items()])
                    
                    discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else "unknown"
                    discord_username = DISCORD_AUTH.user_info.get('username', discord_id) if DISCORD_AUTH else "unknown"
                    
                    # Build row_dict from values and columns
                    row_dict = dict(zip(columns, values))
                    entity_id = row_dict.get("NUME IC", "") or row_dict.get("NOME_IC", "")
                    
                    print(f"📝 EDIT_EMPLOYEE LOG: user={discord_username} ({discord_id}), employee={employee_name}, city={city}, inst={institution}")
                    
                    # Use safe logging method
                    if hasattr(ACTION_LOGGER, 'log_edit_employee_safe'):
                        ACTION_LOGGER.log_edit_employee_safe(
                            discord_id,
                            city,
                            institution,
                            employee_name,
                            changes_str,
                            discord_username=discord_username,
                            entity_id=entity_id
                        )
                    else:
                        print(f"✓ Editare angajat: {changes_str}")
            except Exception as e:
                print(f"⚠️ Error logging edit_employee action: {e}")
        
        update_info_label(city, institution)
        sort_tree_by_punctaj(tree)
        win.destroy()

    def cancel():
        win.destroy()

    # ===== BARĂ DE BUTOANE (FIX LA JOS) =====
    button_frame = tk.Frame(win, bg="#ffffff", relief="raised", borderwidth=1)
    button_frame.pack(fill="x", side="bottom", padx=0, pady=0)
    
    btn_save = tk.Button(
        button_frame, 
        text="✅ SALVEAZĂ", 
        command=save, 
        font=("Segoe UI", 11, "bold"),
        bg="#27ae60", 
        fg="white",
        width=20,
        padx=15,
        pady=12
    )
    btn_save.pack(side="left", padx=8, pady=10)
    
    btn_cancel = tk.Button(
        button_frame,
        text="❌ ANULEAZĂ",
        command=cancel,
        font=("Segoe UI", 11, "bold"),
        bg="#e74c3c",
        fg="white",
        width=20,
        padx=15,
        pady=12
    )
    btn_cancel.pack(side="left", padx=8, pady=10)

def add_points(tree, city, institution):
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Eroare", "Selectează cel puțin o persoană!")
        return

    value = simpledialog.askinteger("Adaugă punctaj", "Număr puncte:", minvalue=1)
    if value is None:
        return

    columns = tree.columns
    for item in sel:
        old_values = tree.item(item, "values")
        values = list(old_values)
        
        # Găsește indexul PUNCTAJ
        if "PUNCTAJ" in columns:
            punctaj_idx = columns.index("PUNCTAJ")
            old_points = int(values[punctaj_idx]) if punctaj_idx < len(values) else 0
            new_points = old_points + value
            values[punctaj_idx] = str(new_points)
            
            tree.item(item, values=tuple(values))
            
            # ===== ACTION LOGGING =====
            if ACTION_LOGGER:
                try:
                    employee_name = str(values[0]) if values else "Unknown"
                    discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else "unknown"
                    discord_username = DISCORD_AUTH.user_info.get('username', discord_id) if DISCORD_AUTH else "unknown"
                    entity_id = values[len(values)-1] if len(values) > 0 else ""  # Get NUME_IC if available
                    print(f"📝 ADD_POINTS LOG: user={discord_username} ({discord_id}), employee={employee_name}, city={city}, inst={institution}, points={old_points}→{new_points}")
                    ACTION_LOGGER.log_edit_points(
                        discord_id,
                        city,
                        institution,
                        employee_name,
                        old_points,
                        new_points,
                        "add",
                        discord_username=discord_username,
                        entity_id=entity_id
                    )
                except Exception as e:
                    print(f"⚠️ Error logging add_points action: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"⚠️ ACTION_LOGGER is None - cannot log add_points")

    save_institution(city, institution, tree, update_timestamp=True, updated_items=list(sel), skip_logging=True)

def remove_points(tree, city, institution):
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Eroare", "Selectează cel puțin o persoană!")
        return

    value = simpledialog.askinteger("Șterge punctaj", "Număr puncte:", minvalue=1)
    if value is None:
        return

    columns = tree.columns
    for item in sel:
        old_values = tree.item(item, "values")
        values = list(old_values)
        
        # Găsește indexul PUNCTAJ
        if "PUNCTAJ" in columns:
            punctaj_idx = columns.index("PUNCTAJ")
            old_points = int(values[punctaj_idx]) if punctaj_idx < len(values) else 0
            new_points = max(0, old_points - value)
            values[punctaj_idx] = str(new_points)
            
            tree.item(item, values=tuple(values))
            
            # ===== ACTION LOGGING =====
            if ACTION_LOGGER:
                try:
                    employee_name = str(values[0]) if values else "Unknown"
                    discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else "unknown"
                    discord_username = DISCORD_AUTH.user_info.get('username', discord_id) if DISCORD_AUTH else "unknown"
                    entity_id = values[len(values)-1] if len(values) > 0 else ""  # Get NUME_IC if available
                    print(f"📝 REMOVE_POINTS LOG: user={discord_username} ({discord_id}), employee={employee_name}, city={city}, inst={institution}, points={old_points}→{new_points}")
                    ACTION_LOGGER.log_edit_points(
                        discord_id,
                        city,
                        institution,
                        employee_name,
                        old_points,
                        new_points,
                        "remove",
                        discord_username=discord_username,
                        entity_id=entity_id
                    )
                except Exception as e:
                    print(f"⚠️ Error logging remove_points action: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"⚠️ ACTION_LOGGER is None - cannot log remove_points")

    save_institution(city, institution, tree, update_timestamp=True, updated_items=list(sel), skip_logging=True)

# ================== LEGARE BUTOANE ==================
btn_add_tab.config(command=add_tab)
btn_edit_tab.config(command=edit_tab)
btn_del_tab.config(command=delete_tab)

# ================== HELPER: CONSTRUIȚI STRUCTURA PENTRU ORGANIZATION VIEW ==================
def build_structure_for_view():
    """
    Construiește structura {city: {institution: [employees]}} din Supabase sau JSON.
    Returnează structura gata pentru create_city_institution_view().
    """
    structure = {}
    
    if not os.path.exists(DATA_DIR):
        return structure
    
    # Iterează prin foldere de orașe
    for city in sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(city_dir(d))]):
        # Verificare permisiuni pe oraș
        can_view_city = True
        if DISCORD_AUTH and SUPABASE_SYNC:
            try:
                city_perms = SUPABASE_SYNC.get_city_permissions(DISCORD_AUTH.get_discord_id())
                if city_perms and city in city_perms:
                    can_view_city = city_perms[city].get('can_view', False)
                    if not can_view_city:
                        print(f"⚠️ No permission to view city: {city}")
                        continue
            except Exception as e:
                print(f"⚠️ Error checking city permissions: {e}")
        
        if not can_view_city:
            continue
        
        structure[city] = {}
        
        # Iterează prin instituții (fișiere JSON)
        institution_dir = city_dir(city)
        if os.path.exists(institution_dir):
            for json_file in sorted([f for f in os.listdir(institution_dir) if f.endswith('.json')]):
                institution = json_file[:-5]  # Remove .json
                
                # Verificare permisiuni pe instituție
                can_view_inst = True
                if DISCORD_AUTH and SUPABASE_SYNC:
                    try:
                        inst_perms = SUPABASE_SYNC.get_institution_permissions(
                            DISCORD_AUTH.get_discord_id(), 
                            city
                        )
                        if inst_perms and institution in inst_perms:
                            can_view_inst = inst_perms[institution].get('can_view', False)
                            if not can_view_inst:
                                print(f"⚠️ No permission to view institution: {city}/{institution}")
                                continue
                    except Exception as e:
                        print(f"⚠️ Error checking institution permissions: {e}")
                
                if not can_view_inst:
                    continue
                
                # Încarc angajații din Supabase sau JSON
                employees_data = load_institution(city, institution)
                if employees_data:
                    structure[city][institution] = employees_data.get("data", [])
                else:
                    structure[city][institution] = []
    
    return structure

# ================== AUTO-ÎNCĂRCARE ORAȘE / INSTITUȚII ==================
def load_existing_tables():
    """Încarcă automat toate orașele și instituțiile cu noua vizualizare organizată"""
    if not os.path.exists(DATA_DIR):
        return
    
    # CLEAR OLD TABS - Șterge tab-urile vechi pentru a evita duplicate

    for tab_id in city_notebook.tabs():
        city_notebook.forget(tab_id)
    tabs.clear()
    
    # === VERIFICARE PERMISIUNI GLOBALE - PAGINĂ GOALĂ DACĂ ZERO ACCES ===
    if DISCORD_AUTH and not DISCORD_AUTH.can_view() and not DISCORD_AUTH.is_admin():
        print("⚠️ Utilizator fără permisiune can_view - orașele nu vor fi încărcate (pagină goală)")
        return  # NU încarcă NIMIC - interfața rămâne goală

    # === VERIFICARE PERMISIUNI GRANULARE PE ORAȘ ===
    for city in sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(city_dir(d))]):
        # Verificăm dacă există permisiuni granulare per oraș
        can_view_city = True
        
        if DISCORD_AUTH and SUPABASE_SYNC:
            try:
                city_perms = SUPABASE_SYNC.get_city_permissions(DISCORD_AUTH.get_discord_id())
                if city_perms and city in city_perms:
                    # Verificăm permisiunea can_view pentru orașul specific
                    can_view_city = city_perms[city].get('can_view', False)
                    if not can_view_city:
                        print(f"⚠️ Utilizator fără permisiune can_view pentru orașul: {city}")
                        continue  # Sare peste acest oraș
            except Exception as e:
                print(f"⚠️ Eroare la verificare permisiuni granulare pentru {city}: {e}")
                # Fallback la permisiuni globale dacă eroare
        
        # Încarcă orașul doar dacă are permisiune
        if can_view_city:
            frame = create_city_ui(city)
            city_notebook.select(frame)


def punctaj_cu_selectie(tree, city, institution, mode="add"):
    win = tk.Toplevel(root)
    win.title("Adaugă/Șterge valori" if mode == "add" else "Șterge valori")
    win.geometry("400x500")
    win.grab_set()

    # Detectează coloana PUNCTAJ (obligatorie)
    numeric_col = None
    columns = tree.columns
    
    # Caută exact "PUNCTAJ"
    if "PUNCTAJ" in columns:
        numeric_col = "PUNCTAJ"
    else:
        # Fallback pe alte coloane numerice
        for col in columns:
            if col.upper() in ["PUNCTAJ", "VALOARE", "SCOR"]:
                numeric_col = col
                break
    
    if not numeric_col:
        messagebox.showwarning("Eroare", "Nu găsesc coloana PUNCTAJ!")
        return

    frame_top = tk.Frame(win, bg="#e8f4f8" if mode == "add" else "#ffe8e8", pady=10)
    frame_top.pack(fill="x")

    tk.Label(
        frame_top, 
        text=f"PASUL 1: Introdu valoarea pentru {numeric_col}", 
        font=("Segoe UI", 10, "bold"),
        bg="#e8f4f8" if mode == "add" else "#ffe8e8"
    ).pack(pady=5)

    entry = tk.Entry(frame_top, justify="center", font=("Segoe UI", 12), width=15)
    entry.pack(pady=5)
    entry.focus()

    tk.Label(
        win, 
        text="PASUL 2: Selectează rândurile din lista de mai jos", 
        font=("Segoe UI", 9),
        fg="#555"
    ).pack(pady=10)

    frame_list = tk.Frame(win)
    frame_list.pack(fill="both", expand=True, pady=5)

    canvas = tk.Canvas(frame_list)
    scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_items = []

    for item in tree.get_children():
        values = tree.item(item, "values")
        var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(
            scroll_frame,
            text=" | ".join(str(v) for v in values[:3]),
            variable=var,
            anchor="w"
        )
        chk.pack(fill="x", padx=10, pady=2)
        vars_items.append((item, var))

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=5)

    def select_all():
        for _, var in vars_items:
            var.set(True)

    tk.Button(btn_frame, text="✓ Selectează toate", command=select_all, width=18).pack(side="left", padx=5)

    def deselect_all():
        for _, var in vars_items:
            var.set(False)

    tk.Button(btn_frame, text="✗ Deselectează toate", command=deselect_all, width=18).pack(side="left", padx=5)

    def aplica():
        try:
            valoare = int(entry.get())
            if valoare <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Eroare", "Introdu un număr valid!")
            return

        selectati = [item for item, var in vars_items if var.get()]

        if not selectati:
            messagebox.showwarning(
                "Nicio selecție",
                "Nu ai selectat niciun rând!"
            )
            return

        col_idx = columns.index(numeric_col)
        for item in selectati:
            values = list(tree.item(item, "values"))
            try:
                current = int(values[col_idx]) if col_idx < len(values) else 0
            except (ValueError, IndexError):
                current = 0
            
            if mode == "add":
                nou = current + valoare
            else:
                nou = max(0, current - valoare)

            values[col_idx] = str(nou)
            tree.item(item, values=tuple(values))

        save_institution(city, institution, tree, update_timestamp=True, updated_items=selectati, skip_logging=True)
        
        # ===== ACTION LOGGING for punctaj_cu_selectie =====
        if ACTION_LOGGER and selectati:
            try:
                discord_id = DISCORD_AUTH.get_discord_id() if DISCORD_AUTH else "unknown"
                discord_username = DISCORD_AUTH.user_info.get('username', discord_id) if DISCORD_AUTH else "unknown"
                
                for item in selectati:
                    values = list(tree.item(item, "values"))
                    employee_name = values[0] if values else "Unknown"
                    col_idx = columns.index(numeric_col)
                    
                    # Get current value (after edit)
                    current_val = str(values[col_idx]) if col_idx < len(values) else "0"
                    # Calculate old value
                    if mode == "add":
                        old_val = str(int(current_val) - valoare) if current_val.isdigit() else "0"
                    else:
                        old_val = str(int(current_val) + valoare) if current_val.isdigit() else "0"
                    
                    entity_id = values[-1] if values else ""  # Get DISCORD column
                    
                    ACTION_LOGGER.log_edit_points(
                        discord_id,
                        city,
                        institution,
                        employee_name,
                        old_val,
                        current_val,
                        mode,
                        discord_username=discord_username,
                        entity_id=entity_id
                    )
            except Exception as e:
                print(f"⚠️ Error logging punctaj_cu_selectie: {e}")
                import traceback
                traceback.print_exc()
        
        update_info_label(city, institution)
        sort_tree_by_punctaj(tree)
        
        tree.selection_set(selectati)
        if selectati:
            tree.see(selectati[0])
        
        win.destroy()

    tk.Button(
        win,
        text="✓ CONFIRMĂ ȘI APLICĂ",
        bg="#4CAF50" if mode == "add" else "#F44336",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=25,
        height=2,
        command=aplica
    ).pack(pady=15)


# ================== CLOUD SYNC MANAGER (FORCED SYNC) ==================
CLOUD_SYNC = None
sync_notification_window = None
sync_in_progress = False
ui_locked = False

def initialize_cloud_sync():
    """Initialize cloud sync manager with polling"""
    global CLOUD_SYNC, sync_notification_window, ui_locked
    
    if not CLOUD_SYNC_AVAILABLE or not SUPABASE_SYNC:
        return
    
    try:
        CLOUD_SYNC = CloudSyncManager(SUPABASE_SYNC, BASE_DIR)
        
        # Set up callbacks
        CLOUD_SYNC.on_sync_required = on_cloud_sync_required
        CLOUD_SYNC.on_sync_start = on_sync_start
        CLOUD_SYNC.on_sync_complete = on_sync_complete
        CLOUD_SYNC.on_sync_error = on_sync_error
        
        # Start polling every 1 second
        CLOUD_SYNC.start_polling(interval=1)
        print("☁️ Cloud sync manager initialized with 1-second polling")
        
    except Exception as e:
        print(f"❌ Error initializing cloud sync: {e}")

def on_cloud_sync_required(cloud_version, local_version):
    """Callback when cloud has newer version"""
    global sync_notification_window, ui_locked
    
    if ui_locked:
        return  # Already showing notification
    
    ui_locked = True
    
    # Block UI and show notification
    disable_all_ui()
    
    if sync_notification_window:
        try:
            sync_notification_window.destroy()
        except:
            pass
    
    sync_notification_window = tk.Toplevel(root)
    sync_notification_window.title("☁️ Sincronizare Cloud")
    sync_notification_window.geometry("600x250")
    sync_notification_window.grab_set()
    sync_notification_window.resizable(False, False)
    
    # Center window
    sync_notification_window.update_idletasks()
    x = (sync_notification_window.winfo_screenwidth() // 2) - (600 // 2)
    y = (sync_notification_window.winfo_screenheight() // 2) - (250 // 2)
    sync_notification_window.geometry(f"+{x}+{y}")
    
    # Header with warning color
    header = tk.Frame(sync_notification_window, bg="#ff9800", height=80)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    tk.Label(
        header,
        text="🔔 Au apărut modificări în cloud!",
        font=("Segoe UI", 14, "bold"),
        bg="#ff9800",
        fg="white"
    ).pack(pady=15)
    
    tk.Label(
        header,
        text=f"Versiunea cloud: v{cloud_version} | Versiunea locală: v{local_version}",
        font=("Segoe UI", 10),
        bg="#ff9800",
        fg="white"
    ).pack()
    
    # Content
    content = tk.Frame(sync_notification_window, bg="white")
    content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    tk.Label(
        content,
        text="⚠️ Aplicația este BLOCATĂ.",
        font=("Segoe UI", 11, "bold"),
        bg="white"
    ).pack(pady=5)
    
    tk.Label(
        content,
        text="Trebuie să descarci modificările din cloud pentru a continua.",
        font=("Segoe UI", 10),
        bg="white"
    ).pack(pady=5)
    
    tk.Label(
        content,
        text="Apasă butonul de mai jos pentru a descărca.",
        font=("Segoe UI", 10),
        bg="white"
    ).pack(pady=5)
    
    # Progress label
    progress_label = tk.Label(content, text="", font=("Segoe UI", 9), fg="#666", bg="white")
    progress_label.pack(pady=10)
    
    # Download button (ONLY button available)
    def do_download():
        def download_thread():
            global ui_locked
            try:
                progress_label.config(text="Se descarcă modificări din cloud...")
                sync_notification_window.update()
                
                if CLOUD_SYNC.download_all_changes(lambda msg: progress_label.config(text=msg)):
                    progress_label.config(text="✅ Descărcare completă!", fg="#4CAF50")
                    sync_notification_window.update()
                    time.sleep(1)
                    
                    # Reload data
                    root.after(500, load_existing_tables)
                    
                    sync_notification_window.destroy()
                    ui_locked = False
                    enable_all_ui()
                else:
                    progress_label.config(text="❌ Eroare la descărcare!", fg="#f44336")
                    sync_notification_window.update()
                    time.sleep(2)
                    ui_locked = False
                    enable_all_ui()
            except Exception as e:
                progress_label.config(text=f"❌ Eroare: {str(e)}", fg="#f44336")
                sync_notification_window.update()
                time.sleep(2)
                ui_locked = False
                enable_all_ui()
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    download_btn = tk.Button(
        content,
        text="📥 DESCARCĂ SINCRONIZARE",
        font=("Segoe UI", 11, "bold"),
        bg="#2196F3",
        fg="white",
        command=do_download,
        relief=tk.FLAT,
        cursor="hand2",
        padx=30,
        pady=10
    )
    download_btn.pack(pady=15)

def disable_all_ui():
    """Disable all UI elements except sync download button"""
    try:
        # Disable all widgets in root
        for widget in root.winfo_children():
            if widget.winfo_class() != 'Toplevel':
                widget.config(state=tk.DISABLED)
    except:
        pass

def enable_all_ui():
    """Enable all UI elements"""
    try:
        # Enable all widgets in root
        for widget in root.winfo_children():
            if widget.winfo_class() != 'Toplevel':
                try:
                    widget.config(state=tk.NORMAL)
                except:
                    pass
    except:
        pass

def on_sync_start():
    """Called when sync starts"""
    print("🔄 Sincronizare în progres...")

def on_sync_complete():
    """Called when sync completes"""
    print("✅ Sincronizare finalizată")

def on_sync_error(error_msg):
    """Called when sync errors"""
    print(f"❌ Sync error: {error_msg}")
    messagebox.showerror("Eroare Sincronizare", f"Eroare: {error_msg}")

def force_cloud_sync_button():
    """Force immediate cloud synchronization from button"""
    if not CLOUD_SYNC:
        messagebox.showwarning("Sincronizare Cloud", "Cloud sync not available")
        return
    
    if messagebox.askyesno(
        "Forțează Sincronizare Cloud",
        "Vei forța o sincronizare completă a tuturor datelor din cloud.\n\n"
        "⚠️ Toți utilizatorii conectați vor fi notificați.\n"
        "✓ După apăsare, butoanele vor fi blocate până descărcă.\n\n"
        "Continuă?"
    ):
        # Update cloud version to force all clients to sync
        CLOUD_SYNC.update_cloud_version()
        messagebox.showinfo(
            "Sincronizare Forțată",
            "✅ Sincronizare forțată inițiată!\n\n"
            "Toți utilizatorii vor fi notificați\n"
            "și vor trebui să descarce modificările."
        )

# ================== SINCRONIZARE LA PORNIRE ==================
def startup_sync():
    """Sincronizează datele din cloud la pornirea aplicației"""
    if SUPABASE_SYNC and SUPABASE_SYNC.enabled:
        print("🔄 Sincronizare date din cloud...")
        result = supabase_sync_all()
        
        if result.get("status") == "success":
            downloaded = result.get("downloaded", 0)
            if downloaded > 0:
                messagebox.showinfo(
                    "Sincronizare Cloud", 
                    f"✓ Au fost descărcate {downloaded} fișiere din cloud\n\n"
                    f"Orașele sincronizate: {', '.join(result.get('cities', []))}"
                )
                print(f"✓ Sincronizare completă: {downloaded} fișiere")
            else:
                print("ℹ️ Nu există date noi în cloud")
        elif result.get("status") == "error":
            print(f"⚠️ Eroare sincronizare: {result.get('message')}")
            messagebox.showwarning(
                "Sincronizare Cloud",
                f"⚠️ Nu s-au putut descărca datele din cloud\n\n"
                f"Aplicația va lucra cu datele locale.\n"
                f"Eroare: {result.get('message', 'Unknown')}"
            )
    else:
        print("ℹ️ Sincronizare cloud dezactivată")

# Autentificare Discord
if not discord_login():
    print("❌ Aplicația a fost închisă - autentificare anulată")
    sys.exit(0)

# Refresh admin buttons și secțiunea Discord după autentificare
refresh_admin_buttons()
refresh_discord_section()

# Rulează sincronizarea la pornire
startup_sync()

# Initialize cloud sync manager with polling (1-second interval)
initialize_cloud_sync()

# Încarcă orașele după sincronizare și după ce Discord section e actualizat
root.after(1000, load_existing_tables)

root.mainloop()
