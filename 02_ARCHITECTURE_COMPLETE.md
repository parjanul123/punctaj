# 🏗️ ARCHITECTURE - HOW EVERYTHING WORKS TOGETHER

## 📡 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERNET/CLOUD                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    SUPABASE (Cloud Database)                  │  │
│  │                                                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│  │  │ police_data │  │discord_users│  │ audit_logs  │          │  │
│  │  │             │  │             │  │             │          │  │
│  │  │ All records │  │ Users +     │  │ All changes │          │  │
│  │  │ with shift  │  │ Permissions │  │ Logged here │          │  │
│  │  │ info        │  │ granular    │  │             │          │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │  │
│  │          ▲              ▲                                     │  │
│  │          │              │                                     │  │
│  │    REST API (HTTP)     REST API                              │  │
│  │          │              │                                     │  │
│  └──────────┼──────────────┼─────────────────────────────────────┘  │
│             │              │                                        │
│             │              │                                        │
└─────────────┼──────────────┼────────────────────────────────────────┘
              │              │
              │              │ HTTPS
              │              │
  ┌───────────▼──────────────▼──────────────┐
  │                                          │
  │      LOCAL CLIENT MACHINE (User)        │
  │      (Windows PC with Punctaj Manager)  │
  │                                          │
  │  ┌──────────────────────────────────┐   │
  │  │   PUNCTAJ MANAGER APPLICATION    │   │
  │  │                                  │   │
  │  │  ┌────────────────────────────┐  │   │
  │  │  │  tkinter GUI (User Interface│  │   │
  │  │  │  Tables with employee data) │  │   │
  │  │  └────────────────────────────┘  │   │
  │  │             ▲                    │   │
  │  │             │                    │   │
  │  │         Updates UI               │   │
  │  │             │                    │   │
  │  │             ▼                    │   │
  │  │  ┌────────────────────────────┐  │   │
  │  │  │ RealTimeSyncManager        │  │   │
  │  │  │ (Real-Time Cloud Sync)     │  │   │
  │  │  │                            │  │   │
  │  │  │ ✅ Syncs every 30 seconds  │  │   │
  │  │  │ ✅ Fetches police_data     │  │   │
  │  │  │ ✅ Updates local .json     │  │   │
  │  │  │ ✅ Notifies UI via         │  │   │
  │  │  │    callbacks               │  │   │
  │  │  └────────────────────────────┘  │   │
  │  │             ▲                    │   │
  │  │             │                    │   │
  │  │  ┌────────────────────────────┐  │   │
  │  │  │ PermissionSyncManager      │  │   │
  │  │  │ (Permission Sync)          │  │   │
  │  │  │                            │  │   │
  │  │  │ ✅ Syncs every 5 seconds   │  │   │
  │  │  │ ✅ Fetches user perms from │  │   │
  │  │  │    discord_users table     │  │   │
  │  │  │ ✅ Updates local cache     │  │   │
  │  │  │ ✅ Enables/disables UI     │  │   │
  │  │  │    buttons based on perms  │  │   │
  │  │  └────────────────────────────┘  │   │
  │  │             ▲                    │   │
  │  │             │                    │   │
  │  │  ┌────────────────────────────┐  │   │
  │  │  │ DiscordAuth                │  │   │
  │  │  │ (Authentication + Perms)   │  │   │
  │  │  │                            │  │   │
  │  │  │ ✅ Handles Discord OAuth   │  │   │
  │  │  │ ✅ Gets user role          │  │   │
  │  │  │ ✅ Checks permissions      │  │   │
  │  │  │    (from cache first)      │  │   │
  │  │  │ ✅ Works with Permission   │  │   │
  │  │  │    Sync Manager            │  │   │
  │  │  └────────────────────────────┘  │   │
  │  │             ▲                    │   │
  │  │             │                    │   │
  │  │  ┌────────────────────────────┐  │   │
  │  │  │ SupabaseSync               │  │   │
  │  │  │ (Database Operations)      │  │   │
  │  │  │                            │  │   │
  │  │  │ ✅ Auto-registers users    │  │   │
  │  │  │ ✅ Syncs police_data       │  │   │
  │  │  │ ✅ Fetches permissions     │  │   │
  │  │  │ ✅ Logs actions            │  │   │
  │  │  │ ✅ Handles errors gracefully│ │   │
  │  │  └────────────────────────────┘  │   │
  │  │                                  │   │
  │  │  ┌────────────────────────────┐  │   │
  │  │  │ Local Data Storage         │  │   │
  │  │  │                            │  │   │
  │  │  │ %APPDATA%\PunctajManager\  │  │   │
  │  │  │ ├── data/                  │  │   │
  │  │  │ │   ├── City1/             │  │   │
  │  │  │ │   │   ├── Institution.json│ │   │
  │  │  │ │   │   └── ...            │  │   │
  │  │  │ │   └── City2/             │  │   │
  │  │  │ ├── arhiva/                │  │   │
  │  │  │ ├── logs/                  │  │   │
  │  │  │ └── config/                │  │   │
  │  │  │     ├── discord_config.ini │  │   │
  │  │  │     └── supabase_config.ini│  │   │
  │  │  └────────────────────────────┘  │   │
  │  │                                  │   │
  │  └──────────────────────────────────┘   │
  │                                          │
  │  ┌──────────────────────────────────┐   │
  │  │  Admin Panel (For Admins Only)   │   │
  │  │                                  │   │
  │  │  ✅ Assign permissions to users  │   │
  │  │  ✅ View user access levels      │   │
  │  │  ✅ Manage institutions          │   │
  │  │  ✅ Changes sync in < 5 seconds  │   │
  │  │                                  │   │
  │  └──────────────────────────────────┘   │
  │                                          │
  └──────────────────────────────────────────┘
```

## 🔄 Data Flow Diagrams

### Scenario 1: User Logs In
```
1. User Clicks "Login cu Discord"
   ↓
2. Browser opens Discord OAuth screen
   ↓
3. User approves permissions
   ↓
4. Redirects back to app with token
   ↓
5. DiscordAuth gets user info:
   - discord_id
   - discord_username  
   - discord_email
   ↓
6. SupabaseSync.register_user() called:
   - Checks if user exists in discord_users
   - If NOT: Creates user with VIEWER role + empty permissions
   - If YES: Updates last_login timestamp
   ↓
7. PermissionSyncManager initialized:
   - Starts background thread
   - Syncs every 5 seconds
   ↓
8. RealTimeSyncManager initialized:
   - Starts background thread
   - Syncs every 30 seconds
   ↓
9. Application UI loads:
   - Permissions checked from cache
   - Buttons enabled/disabled based on role
   ↓
10. ✅ User is logged in and ready to work!
```

### Scenario 2: Admin Changes User Permissions
```
ADMIN PANEL                          USER MACHINE
│                                    │
├─ Opens admin panel                 │
├─ Selects user                      │
├─ Checks "can_view"                 │
├─ Checks "can_edit"                 │
├─ Clicks "Save" 
│  └─► Updates Supabase              │
│      discord_users.granular_        │
│      permissions = JSON             │
│                                    │
│                                    │ Meanwhile on user machine:
│                                    │ PermissionSyncManager running...
│                                    │
│                      (< 5 seconds passes)
│                                    │
│                                    ├─ Sync timer triggers
│                                    ├─ Fetches permissions from
│                                    │  discord_users table
│                                    ├─ Updates local cache
│                                    ├─ DiscordAuth.has_granular_
│                                    │  permission() checks cache
│                                    ├─ UI buttons re-enable
│                                    │
                                    ✅ User can now edit!
                                       (no restart needed)
```

### Scenario 3: Another User Edits Data in Cloud
```
USER A                              USER B
│                                   │
├─ Opens Institution data           │
├─ Adds new employee                │
├─ Clicks "Save"                    │
├─ Data sent to Supabase
│  └─► police_data table
│      updated with new
│      employee record
│                                   │ Meanwhile on User B's machine:
│                                   │ RealTimeSyncManager running...
│                                   │
│                                   ├─ Every 30 seconds:
│                                   │  ├─ Calls sync_all_from_cloud()
│                                   │  ├─ Fetches latest police_data
│                                   │  ├─ Detects changes
│                                   │  ├─ Updates local .json files
│                                   │  ├─ Calls callbacks
│                                   │  └─ Reloads UI tables
│                                   │
                                   ✅ User B sees new employee!
                                      (automatically updated)
```

## 🔧 Component Details

### 1. **RealTimeSyncManager** (`realtime_sync.py`)
**Purpose**: Keep local data in sync with Supabase cloud

**How it works**:
- Runs on background thread (daemon)
- Wakes up every 30 seconds
- Calls `supabase_sync.sync_all_from_cloud()`
- Fetches latest police_data from Supabase
- Compares with local .json files
- Updates changed files
- Calls registered callbacks to update UI
- No blocking - runs in background

**Impact**:
- Data is maximum 30 seconds out of date
- Changes from other users appear automatically
- No restart needed

### 2. **PermissionSyncManager** (`permission_sync_fix.py`)
**Purpose**: Keep user permissions in sync with Supabase

**How it works**:
- Runs on background thread (daemon)
- Wakes up every 5 seconds
- Calls `supabase_sync.get_granular_permissions()`
- Fetches latest granular_permissions for logged-in user
- Updates local cache in DiscordAuth
- Enables/disables UI buttons based on new permissions

**Impact**:
- Permissions are maximum 5 seconds out of date
- Admin changes visible immediately
- No restart needed

### 3. **DiscordAuth** (`discord_auth.py`)
**Purpose**: Handle Discord OAuth and permission checking

**How it works**:
- OAuth flow via browser
- Gets user info from Discord
- Caches permissions locally
- PermissionSyncManager updates cache
- has_granular_permission() checks cache first, then API

**Impact**:
- Fast permission checks (from cache)
- Real-time updates via sync manager

### 4. **SupabaseSync** (`supabase_sync.py`)
**Purpose**: All Supabase database operations

**Key Methods**:
- `register_user()` - Auto-register new Discord users
- `sync_all_from_cloud()` - Fetch police_data from cloud
- `get_granular_permissions()` - Fetch user permissions
- `upload_data()` - Save changes to cloud

**Features**:
- Retry logic for timeouts
- Detailed logging
- Error categorization
- Connection error handling

### 5. **Main App** (`punctaj.py`)
**Purpose**: Orchestrate everything

**On startup**:
1. Load configuration
2. Show Discord login dialog
3. User logs in with Discord
4. Register user in Supabase (SupabaseSync.register_user)
5. Initialize PermissionSyncManager (5-sec syncs)
6. Initialize RealTimeSyncManager (30-sec syncs)
7. Load UI with correct permissions
8. Start monitoring thread (PermissionSyncManager)
9. Start data sync thread (RealTimeSyncManager)

**On shutdown**:
1. Stop PermissionSyncManager
2. Stop RealTimeSyncManager
3. Save any pending data
4. Close connections

## 🎯 Configuration

### `discord_config.ini`
```ini
[discord]
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
redirect_uri = http://localhost:8000/callback
```

### `supabase_config.ini`
```ini
[supabase]
url = https://your-project.supabase.co
key = YOUR_API_KEY
table_sync = police_data
table_logs = audit_logs
table_users = discord_users

[sync]
enabled = true
auto_sync = true
sync_interval = 30  # RealTimeSyncManager uses 30 sec
```

## 🚀 Installation & Distribution

### 1. Build Setup.exe
```bash
python BUILD_SETUP_EXE.py
```

Creates: `setup_output/dist/PunctajManager_Setup.exe`

### 2. Client runs Setup.exe
Installs to: `%APPDATA%\PunctajManager\`

### 3. Client adds config files
```
%APPDATA%\PunctajManager\config\
├── discord_config.ini
└── supabase_config.ini
```

### 4. Client launches app
Runs: `launch_punctaj.bat`

### 5. Both sync managers auto-start
- PermissionSyncManager: 5-second intervals
- RealTimeSyncManager: 30-second intervals

## 📊 Performance Characteristics

| Feature | Interval | Latency | Impact |
|---------|----------|---------|---------|
| Permission Sync | 5 sec | < 5 sec | Low (small data) |
| Data Sync | 30 sec | < 30 sec | Low (network only) |
| API Calls | 1 per interval | N/A | ~75% reduction vs old system |
| CPU Usage | Idle until sync | < 1% | Minimal |
| Memory | Constant | 50-100 MB | Normal for Python app |
| Disk | Cache only | 1-5 MB | Local copies of data |

## ✅ Reliability Features

- **Retry Logic**: Automatic retry on Supabase timeout
- **Error Handling**: Graceful handling of connection errors
- **Offline Support**: App works offline, syncs when online
- **Data Integrity**: Unique constraints prevent duplicates
- **Logging**: All changes logged to audit_logs table
- **Backup**: Cloud backup in Supabase + local copies

## 🔐 Security

- **Discord OAuth**: Standard OAuth2 flow, no passwords stored
- **API Key**: Stored in local config file (not in code)
- **Granular Permissions**: Fine-grained access control
- **Audit Trail**: All changes logged
- **Local Encryption**: Can be added if needed

---

**Version**: 2.5 with Real-Time Sync
**Date**: 2026-02-03
