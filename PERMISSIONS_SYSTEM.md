# Admin Panel & Permission System - Implementation Summary

## Status: ✅ COMPLETE - Version 2.0

### NEW FEATURE: Permisiuni Dinamice Grupate pe Orașe și Instituții

**Location:** [admin_permissions.py](admin_permissions.py#L131-L275)

#### Caracteristici

1. **Auto-Detection de Orașe și Instituții**
   - Sistemul scanează folderul `/data` și detectează automat toate orașele și instituțiile
   - Nu mai trebuie să adaugi manual permisiuni pentru noile instituții

2. **Inițializare Automată**
   - Când salvezi permisiuni pentru un utilizator, orice **noi orașe/instituții** sunt detectate
   - Sunt inițializate cu permisiuni **default FALSE** pentru toți permisioanele
   - Permisiunile existente sunt **păstrate**

3. **Structură Ierarhică**
   - Nivelul 1: **Orașe** (BlackWater, Saint_Denis, etc.)
   - Nivelul 2: **Instituții** (Politie, Pompieri, etc.)
   - Permisiuni: can_view, can_edit, can_delete

4. **Exemplu de Structură**
```
🏙️ BlackWater
  └─ 🏢 Politie
     ☑ 👁️ Vizualizare
     ☑ ✏️ Editare
     ☐ ❌ Ștergere
  └─ 🏢 Pompieri (NEW - auto-inițializat)
     ☐ 👁️ Vizualizare
     ☐ ✏️ Editare
     ☐ ❌ Ștergere

🏙️ Saint_Denis
  └─ 🏢 Politie
     ☑ 👁️ Vizualizare
     ☑ ✏️ Editare
     ☑ ❌ Ștergere
```

#### Metodele Principale

```python
# Obține toate orașele din /data
get_all_cities() → ['BlackWater', 'Saint_Denis']

# Obține instituții dintr-un oraș
get_all_institutions_for_city('BlackWater') → ['Politie', 'Pompieri']

# Obține structura completă
get_all_institutions_by_city() → {
    'BlackWater': ['Politie', 'Pompieri'],
    'Saint_Denis': ['Politie']
}

# Preiau permisiuni utilizator (auto-merge cu noi instituții)
save_user_institution_permissions(discord_id, permissions)
```

#### Avantaje

| Funcție | Înainte | Acum |
|---------|---------|------|
| Adăugare noi instituții | Manual pentru fiecare user | Auto-detectat ✅ |
| Organizare | Flat list | Ierarhie cu orașe 📊 |
| Noi utilizatori | Config manual | Default FALSE, gata |
| Schimbări de folder | Trebuie cod | Auto-detect 🔄 |

---

### 1. Admin Panel Button Integration ✅

**Location:** [punctaj.py](punctaj.py#L1205-L1212)

- Added "🛡️ Admin Panel" button in sidebar (visible only for admins)
- Button opens admin panel using `open_admin_panel()` from `admin_ui.py`
- Passes `root`, `SUPABASE_SYNC`, and `DISCORD_AUTH` to the admin panel
- Properly checks `is_admin()` before displaying

```python
if DISCORD_AUTH and DISCORD_AUTH.is_admin() and ADMIN_PANEL_AVAILABLE and open_admin_panel:
    btn_admin = tk.Button(
        sidebar,
        text="🛡️ Admin Panel",
        width=18,
        bg="#e74c3c",
        fg="white",
        font=("Segoe UI", 9, "bold"),
        command=lambda: open_admin_panel(root, SUPABASE_SYNC, DISCORD_AUTH)
    )
    btn_admin.pack(pady=8)
```

### 2. Role-Based Permission System ✅

**Enhanced Classes:**
- `DiscordAuth` in [discord_auth.py](discord_auth.py)
- Permission methods in [punctaj.py](punctaj.py)

**Three Role Levels:**
1. **admin** - Full access (manage users, view logs, perform all operations)
2. **user** - Read + Write access (edit cities, add/delete institutions and employees)
3. **viewer** - Read-only access (view data only, cannot make modifications)

**Permission Methods Implemented:**

| Method | Viewer | User | Admin |
|--------|--------|------|-------|
| `is_admin()` | ❌ | ❌ | ✅ |
| `can_view()` | ✅ | ✅ | ✅ |
| `can_view_city()` | ✅ | ✅ | ✅ |
| `can_edit_city_granular()` | ❌ | ✅ | ✅ |
| `can_perform_action()` | ❌ | ✅ | ✅ |
| `can_manage_institution_employees()` | ❌ | ✅ | ✅ |

### 3. Discord User Role Fetching ✅

**New Method:** `_fetch_user_role_from_supabase()` in [discord_auth.py](discord_auth.py#L196-L236)

- Automatically fetches user role from Supabase `discord_users` table after authentication
- Queries `discord_users` with filters: `discord_id=eq.{user_id}&select=role`
- Defaults to 'viewer' if role not found or table query fails
- Called automatically after user registration in `_save_to_supabase()`

```python
def _fetch_user_role_from_supabase(self, user_id: str, supabase=None):
    """Fetch user role from Supabase discord_users table"""
    # Queries Supabase REST API for user's role
    # Defaults to 'viewer' role for new users
```

### 4. User Interface Enhancements ✅

**Discord User Section** - [punctaj.py](punctaj.py#L923-L974)

Now displays:
- Username
- **Role badge with color coding:**
  - Red (#e74c3c) for **admin**
  - Blue (#3498db) for **user**
  - Gray (#95a5a6) for **viewer**
- Profile button (now shows role and permissions)
- Logout button

**Example Output:**
```
👤 username
📊 Role: Admin
[👁️ Profile] [🚪 Logout]
```

**Profile Dialog** - Updated to show:
- Username, User ID, Email
- Current Role (ADMIN/USER/VIEWER)
- **Permission Description:**
  - Admin: "Full access - can manage users and all operations"
  - User: "Can add, edit, and delete institutions and employees"
  - Viewer: "Read-only access - cannot make modifications"

### 5. Button Permission Enforcement ✅

**Sidebar Buttons** - [punctaj.py](punctaj.py#L901-L918)

City management buttons are now disabled for read-only users:
- ➕ Adaugă oraș (Add City)
- ✏️ Editează oraș (Edit City)
- ❌ Șterge oraș (Delete City)

Disabled when: `is_read_only_user()` returns True

**Protection Logic:**
1. Check user role before allowing modifications
2. Show error dialog: "Acces Interzis" (Access Denied)
3. Suggest contacting administrator for access

### 6. Enhanced Permission Checks ✅

**Implemented in** [punctaj.py](punctaj.py):

- `is_read_only_user()` - Checks if user has 'viewer' role
- `can_edit_city()` - Uses `can_edit_city_granular()` from DiscordAuth
- `can_perform_action()` - Delegates to DiscordAuth for action-specific checks

**Usage Examples:**
```python
# Check if user can edit
if is_read_only_user():
    messagebox.showerror("Acces Interzis", "Read-only access")
    return

# Check before saving
if not can_edit_city(city):
    messagebox.showerror("Acces Interzis", f"No permission for {city}")
    return

# Check action permissions
if not can_perform_action("add_employee"):
    messagebox.showerror("Acces Refuzat", "Action not allowed")
    return
```

### 7. Supabase Integration ✅

**Tables Used:**
- `discord_users` - User management with role column
  - `discord_id`: Discord user ID
  - `role`: admin/user/viewer
  - `username`: Discord username
  - `email`: User email

**Query Format:**
```
GET /rest/v1/discord_users?discord_id=eq.{user_id}&select=role
Authorization: Bearer {supabase_key}
```

### 8. Testing Results ✅

**Test Output (test_permissions.py):**
```
1. VIEWER role ✅
   - is_admin(): False
   - can_view(): True
   - can_perform_action('add_employee'): False

2. USER role ✅
   - is_admin(): False
   - can_view(): True
   - can_perform_action('add_employee'): True

3. ADMIN role ✅
   - is_admin(): True
   - can_view(): True
   - can_perform_action('add_employee'): True
   - can_manage_institution_employees(): True
```

## Files Modified

1. **discord_auth.py**
   - Added `user_role` attribute (default: 'viewer')
   - Added `get_user_role()` method
   - Added `_fetch_user_role_from_supabase()` method
   - Updated permission methods (is_admin, can_view, can_edit_city_granular, can_perform_action, can_manage_institution_employees)
   - Integrated role fetching in `_save_to_supabase()`

2. **punctaj.py**
   - Fixed Admin Panel import to include `open_admin_panel`
   - Fixed `is_read_only_user()` to use new `get_user_role()` method
   - Added role display in Discord user section with color badges
   - Updated button permission checks to use role-based system
   - Enhanced `show_discord_profile()` to display role and permissions

## Version 2.0 Updates - Per-Institution Permissions with City Grouping

### Changes in admin_permissions.py

**InstitutionPermissionManager - Enhanced Methods:**

1. **New: `get_all_cities()`**
   - Scanează `/data` folder pentru toate orașele
   - Returnează listă sortată

2. **New: `get_all_institutions_for_city(city: str)`**
   - Returnează instituții dintr-un oraș specific
   - Suportă orice structură de folder

3. **New: `get_all_institutions_by_city()`**
   - Returnează dicționar: `{city: [institution1, institution2]}`
   - Folosit pentru UI și auto-inițializare

4. **Enhanced: `get_all_institutions()`**
   - Păstrată pentru backward compatibility
   - Returnează flat list cu format "city/institution"

5. **Enhanced: `get_user_institution_permissions()`**
   - Returnează permisiuni grupate pe orașe
   - Structură: `{city: {institution: {can_view, can_edit, can_delete}}}`

6. **Enhanced: `save_user_institution_permissions()` - MAGIC METHOD** ⭐
   - ✅ Detectează automat **noi orașe și instituții**
   - ✅ Inițializează cu permisiuni **default FALSE**
   - ✅ Păstrează permisiunile existente
   - ✅ Merging inteligent cu Supabase

**UI Changes: `create_institution_permissions_ui()`**

- ✅ Afișează orașe sub formă de **LabelFrame** cu icon 🏙️
- ✅ Sub fiecare oraș, instituții cu icon 🏢
- ✅ Checkboxuri pentru: 👁️ Vizualizare, ✏️ Editare, ❌ Ștergere
- ✅ Scrollable canvas pentru ușă navigare
- ✅ Mesaj de succes cu notă despre auto-inițializare

### Flux de Utilizare

```
Admin deschide "Permisiuni Utilizatori"
    ↓
Selectează utilizator din dropdown
    ↓
Apare UI cu structura:
    🏙️ BlackWater
       └─ 🏢 Politie ☑☑☐
       └─ 🏢 Pompieri ☐☐☐
    🏙️ Saint_Denis
       └─ 🏢 Politie ☑☑☑
    ↓
Admin bifează permisiuni dorite
    ↓
Apasă "💾 Salvează Permisiuni"
    ↓
Sistem detectează noile instituții (ex. Pompieri dacă e noua)
    ↓
Inițializează cu FALSE pentru utilizatori noi
    ↓
Salveaza în Supabase
    ↓
✅ Mesaj: "Permisiuni salvate! Orice noi instituții/orașe vor fi salvate automat."
```

### Exemplu de Structură Salvată în Supabase

```json
{
  "institution_permissions": {
    "BlackWater": {
      "Politie": {
        "can_view": true,
        "can_edit": true,
        "can_delete": false
      },
      "Pompieri": {
        "can_view": false,
        "can_edit": false,
        "can_delete": false
      }
    },
    "Saint_Denis": {
      "Politie": {
        "can_view": true,
        "can_edit": true,
        "can_delete": true
      }
    }
  }
}
```

### Beneficii

- 🔄 **Dinamic:** Noi instituții/orașe detectate automat
- 🎯 **Precis:** Permisiuni la nivel de instituție, organizate pe orașe
- 🛡️ **Sigur:** Auto-inițializare cu FALSE, nicio permisiune neintenționată
- 📊 **Clar:** Ierahie vizuală ușor de urmărit
- ✅ **Compatibil:** Permisiunile existente sunt păstrate

   - Added sidebar button disable logic for read-only users

3. **admin_ui.py** (existing - no changes needed)
   - Already provides complete admin interface

4. **admin_panel.py** (existing - no changes needed)
   - Already provides backend services

## How It Works

### Login Flow
1. User logs in with Discord
2. `discord_login()` calls `start_oauth_server()`
3. After OAuth2 callback, `_fetch_user_info()` fetches user data
4. `_save_to_supabase()` registers user and fetches their role
5. `_fetch_user_role_from_supabase()` queries Supabase for role
6. User info + role cached in `DISCORD_AUTH` instance

### Permission Check Flow
1. UI element calls permission check (e.g., `is_read_only_user()`)
2. Check queries `DISCORD_AUTH.get_user_role()`
3. Role value ('admin'/'user'/'viewer') is compared
4. UI disables/enables features based on role

### Admin Access
1. User must have `role = 'admin'` in Supabase
2. `DISCORD_AUTH.is_admin()` returns True
3. "🛡️ Admin Panel" button appears in sidebar
4. Click button → `open_admin_panel()` opens admin interface

## Configuration

### Supabase
- Table: `discord_users` (ID: 17550 based on previous context)
- Key column: `discord_id` (unique identifier)
- Role column: `role` (admin/user/viewer values)

### Discord Config
- File: `discord_config.ini`
- Already configured with credentials

### Environment Variables
- None required - all config in INI files

## What's Next

**Optional Enhancements:**
1. ✅ **Automatic Action Logging** - Already implemented in `admin_panel.py` ActionLogger
2. ✅ **Admin Panel Button** - Implemented
3. ✅ **Permission Enforcement** - Implemented
4. Role-specific feature visibility (already works via permission checks)
5. Granular city/institution-level permissions (stub methods ready)
6. Audit logs in admin panel (already created in admin_ui.py)

---

## Summary

The permission system is now fully functional with:
- ✅ Three role levels (admin/user/viewer)
- ✅ Admin Panel button in sidebar (admin only)
- ✅ Role fetching from Supabase after login
- ✅ Permission checks on all modification operations
- ✅ UI feedback for denied actions
- ✅ User role display with color coding
- ✅ Comprehensive error messages

The application is ready for production use with role-based access control!
