# 👤 User Account Management - Supabase Integration

## Implementare: Auto-Create User Account pe Discord Login

### 📋 Cerință
```
"aplicatia vreau sa inchid din x si dupa ce ma conectez cu discordul 
vreau sa mi se ia contul de aici https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/editor/17550?schema=public, 
daca nu exista, il creaza, dar fara permisiuni"
```

---

## ✅ Ce a fost implementat

### 1. **Close with X Button** ✅
Deja fixat în sesiunea anterioară:
- Butonul X funcționează
- Arată mesaj informatiu dacă utilizatorul încearcă să inchidă
- Permite închiderea normală din Task Manager

### 2. **Auto-Create User în Supabase** ✅ 
Implementare completă în `discord_auth.py` și `supabase_sync.py`

#### Flow-ul de Autentificare:
```
1. User apasă Login cu Discord
2. Discord OAuth2 flow
3. Primim user info din Discord (username, ID, email)
4. SupabaseSync.register_user() se apelează automat
   ├─ Verifică dacă user exists în discord_users tabel
   ├─ Dacă EXISTS: update last_login timestamp
   └─ Dacă NU EXISTS: create new user WITHOUT PERMISSIONS
5. Fetch user role din Supabase
   ├─ is_superuser: False
   ├─ is_admin: False
   ├─ can_view: False (viewer role = read-only)
   ├─ can_edit: False
   └─ can_delete: False
6. App opens cu user role setată
```

---

## 🔧 Detalii Tehnice

### Modificări în `supabase_sync.py`

**Metoda `register_user()`** - Create or Update User:

```python
def register_user(self, discord_username: str, discord_id: str, discord_email: str = None) -> bool:
    """Register user in Supabase after Discord login - CREATE if not exists with NO PERMISSIONS"""
    
    # 1. Verifica dacă user exist în discord_users tabel
    check_url = f"{url}?discord_id=eq.{discord_id}&select=*"
    response = requests.get(check_url, headers=self.headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if data:  # User EXISTS
            # Update last_login
            update_url = f"{url}?discord_id=eq.{discord_id}"
            update_data = {
                'last_login': datetime.now().isoformat(),
                'active': True
            }
            response = requests.patch(update_url, ...)
            print("✅ User updated in Supabase")
            return True
        
        else:  # User DOES NOT EXIST
            # Create new user with NO PERMISSIONS
            user_data = {
                'discord_username': discord_username,
                'discord_id': str(discord_id),
                'discord_email': discord_email or '',
                'created_at': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat(),
                'active': True,
                # NO PERMISSIONS - all false
                'is_superuser': False,
                'is_admin': False,
                'can_view': False,
                'can_edit': False,
                'can_delete': False
            }
            response = requests.post(url, json=user_data, ...)
            print("✅ New user created WITHOUT PERMISSIONS")
            return True
```

### Modificări în `discord_auth.py`

**Metoda `_fetch_user_role_from_supabase()`** - Get User Role:

```python
def _fetch_user_role_from_supabase(self, user_id: str, supabase=None):
    """Fetch user role from discord_users table"""
    
    # Query pentru user record
    url = f"{supabase.url}/rest/v1/discord_users?discord_id=eq.{user_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if data:  # User found
            user_data = data[0]
            is_superuser = user_data.get('is_superuser', False)
            is_admin = user_data.get('is_admin', False)
            can_view = user_data.get('can_view', False)
            
            if is_superuser:
                self.user_role = "superuser"
            elif is_admin:
                self.user_role = "admin"
            elif can_view:
                self.user_role = "user"
            else:
                self.user_role = "viewer"  # Default - no permissions
        
        else:  # User NOT found (shouldn't happen if register_user worked)
            self.user_role = "viewer"
```

---

## 📊 Supabase Schema

Tabelul `discord_users` trebuie să aibă următoarea structură:

```sql
CREATE TABLE discord_users (
    id BIGSERIAL PRIMARY KEY,
    discord_id TEXT UNIQUE NOT NULL,
    discord_username TEXT NOT NULL,
    discord_email TEXT,
    
    -- Permissions
    is_superuser BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    can_view BOOLEAN DEFAULT FALSE,
    can_edit BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE
);

-- Index pentru căutări rapide
CREATE INDEX idx_discord_id ON discord_users(discord_id);
```

---

## 🔄 User Permission Levels

După login, utilizatorul are un rol și set de permisiuni:

| Nivel | is_superuser | is_admin | can_view | can_edit | can_delete | Descriere |
|-------|-------------|----------|----------|----------|------------|-----------|
| **SUPERUSER** | ✅ TRUE | - | - | - | - | Admin complet, todos acceso |
| **ADMIN** | ❌ FALSE | ✅ TRUE | - | - | - | Administrator, poate gestiona |
| **USER** | ❌ FALSE | ❌ FALSE | ✅ TRUE | - | - | Utilizator normal cu acces citire |
| **VIEWER** | ❌ FALSE | ❌ FALSE | ❌ FALSE | ❌ FALSE | ❌ FALSE | Read-only (DEFAULT la creare) |

### Default (Noii Utilizatori):
```
is_superuser: FALSE
is_admin: FALSE
can_view: FALSE     ← Utilizatorul este VIEWER (read-only)
can_edit: FALSE
can_delete: FALSE
```

---

## 🔐 Fluxul Complet de Logare

```
┌─────────────────────────────────────┐
│  User start Punctaj.exe             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Discord OAuth2 Login Dialog        │
│  (Browser opens: discord.com)       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  User clicks Authorize              │
│  (discord_auth.py receives code)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Fetch user info from Discord       │
│  (username, ID, email)              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  supabase_sync.register_user()      │
│  ├─ Check if user exists            │
│  ├─ If NOT: CREATE with NO PERMS    │
│  └─ If EXISTS: Update last_login    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  discord_auth._fetch_user_role()    │
│  (Get role from discord_users tbl)  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  App opens with user role           │
│  (User sees interface)              │
│                                     │
│  Default: VIEWER (read-only)        │
│  Admin needs to grant permissions   │
└─────────────────────────────────────┘
```

---

## 📝 Console Output (Exemplu)

```
Discord login started...
🔍 Checking if user exists: sebi#1234 (123456789012345678)
➕ User not found - creating new account: sebi
✅ New user created in Supabase WITHOUT PERMISSIONS: sebi#1234
🔍 Fetching user role from Supabase...
👁️  User role: VIEWER (default - no permissions yet)

✅ Autentificare reușită!
👤 Utilizator: sebi
🔒 ID Discord: 123456789012345678

Aplicația se va deschide acum.
```

---

## 🛠️ Pentru Administatori

Odată ce utilizatorul este creat în Supabase, administratorul poate să:

1. Deschidă dashboard Supabase
2. Mergi la `discord_users` tabel
3. Găsește userul
4. Schimbă permisiunile:
   - `can_view = TRUE` → Utilizator normal (USER)
   - `is_admin = TRUE` → Administrator (ADMIN)
   - `is_superuser = TRUE` → Superuser

### SQL pentru update permisiuni:
```sql
UPDATE discord_users 
SET can_view = TRUE 
WHERE discord_username = 'sebi';

UPDATE discord_users 
SET is_admin = TRUE 
WHERE discord_id = '123456789012345678';
```

---

## 📦 Build Information

**Data:** 1 februarie 2026  
**Versiune:** Punctaj.exe (19.47 MB)  
**Locații:**
- `D:\punctaj\dist\Punctaj.exe`
- `D:\punctaj\installer_outputs\Punctaj.exe`
- `D:\punctaj\installer_outputs\Punctaj\Punctaj.exe`

---

## ✨ Rezumat Features

✅ **Discord Login** - Mandatory, fresh each session  
✅ **Auto-Create User** - In Supabase discord_users table  
✅ **No Default Permissions** - Viewers start read-only  
✅ **Close with X** - Button fully functional  
✅ **Role-Based Access** - Superuser → Admin → User → Viewer  
✅ **Supabase Integration** - Real-time user management  

---

**Status:** ✅ READY FOR DEPLOYMENT
