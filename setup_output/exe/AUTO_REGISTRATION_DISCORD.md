# ✅ AUTO-REGISTRATION LA DISCORD LOGIN

## 📋 Funcționalitate

Atunci când clientul se conectează cu Discord, aplicația **automat**:

1. ✅ Caută utilizatorul în Supabase după Discord ID
2. ✅ Dacă **EXISTĂ** → Actualizează `last_login` și `active=true`
3. ✅ Dacă **NU EXISTĂ** → Crează utilizatorul AUTOMAT în tabelul `discord_users`

## 🔄 Flow Complet

```
┌─────────────────────────────────────┐
│ Cliente deschide aplicația           │
└──────────────┬──────────────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Click "Login cu Discord" │
    └──────────────┬───────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Deschide browser         │
    │ Aprobă permisiuni        │
    │ Discord autentificare OK │
    └──────────────┬───────────┘
               │
               ▼
    ┌──────────────────────────────────┐
    │ Aplicația primește Discord data: │
    │ - username                       │
    │ - id (Discord ID)                │
    │ - email                          │
    └──────────────┬────────────────────┘
               │
               ▼
    ┌──────────────────────────────────┐
    │ VERIFICA în Supabase            │
    │ discord_id = user.discord_id    │
    └──────────────┬────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
    ✅ EXISTA    ❌ NU EXISTA
        │             │
        │             ▼
        │      ┌─────────────────────┐
        │      │ CREEAZA user AUTOMAT│
        │      │                     │
        │      │ discord_username    │
        │      │ discord_id          │
        │      │ discord_email       │
        │      │ created_at          │
        │      │ is_superuser: FALSE │
        │      │ is_admin: FALSE     │
        │      │ can_view: FALSE     │
        │      │ can_edit: FALSE     │
        │      │ can_delete: FALSE   │
        │      │ granular_perm: {}   │
        │      │ active: TRUE        │
        │      └─────────────────────┘
        │             │
        │      ┌──────┴──────────────┐
        │      ▼                     │
        │   ✅ CREAT         ❌ EROARE
        │      │
        │      ▼
        ├──────────────────────┐
        │                      │
        └──────────┬───────────┘
                   │
                   ▼
    ┌──────────────────────────┐
    │ Actualizează:            │
    │ last_login = NOW()       │
    │ active = TRUE            │
    └──────────────┬───────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ ✅ AUTENTIFICARE COMPLETA│
    │ User logat în aplicație  │
    └──────────────────────────┘
```

## 📊 Database Behavior

### Scenarioil 1: User Nou (First Login)
```
SELECT * FROM discord_users WHERE discord_id = '123456789'
→ REZULTAT: EMPTY (nu există)

INSERT INTO discord_users VALUES:
{
  discord_username: 'JohnDoe',
  discord_id: '123456789',
  discord_email: 'john@example.com',
  created_at: '2026-02-03T10:30:00',
  last_login: '2026-02-03T10:30:00',
  active: TRUE,
  is_superuser: FALSE,
  is_admin: FALSE,
  can_view: FALSE,
  can_edit: FALSE,
  can_delete: FALSE,
  granular_permissions: '{}'
}

→ REZULTAT: ✅ USER CREAT
```

### Scenarioil 2: User Existent (Login repetat)
```
SELECT * FROM discord_users WHERE discord_id = '123456789'
→ REZULTAT: Gasit utilizator

UPDATE discord_users SET:
  last_login = NOW(),
  active = TRUE
WHERE discord_id = '123456789'

→ REZULTAT: ✅ USER UPDATED
```

## 🔐 Permisinuni Initiale

Cand se creeaza user NOU, are:
- ✅ `is_superuser: FALSE` - Nu e superuser
- ✅ `is_admin: FALSE` - Nu e admin
- ✅ `can_view: FALSE` - Nu poate vedea date
- ✅ `can_edit: FALSE` - Nu poate edita
- ✅ `can_delete: FALSE` - Nu poate sterge
- ✅ `granular_permissions: '{}'` - Fara permisiuni granulare

**Rolul initial:** 👁️ **VIEWER** (read-only, fara acces)

**Admin trebuie să aloce permisiuni manual** in Admin Panel!

## 🔍 Console Output

### Cand user EXISTA deja:
```
🔍 Checking if Discord user exists: JohnDoe (ID: 123456789)
✅ User already exists in Supabase: JohnDoe
   Discord ID: 123456789
   Status: True | Role: USER
✅ User last_login updated in Supabase
```

### Cand se CREEAZA user NOU:
```
🔍 Checking if Discord user exists: JaneDoe (ID: 987654321)
➕ User NOT found in Supabase - creating new account...
   Discord Username: JaneDoe
   Discord ID: 987654321
   Email: jane@example.com
✅ NEW USER CREATED IN SUPABASE
   Discord Username: JaneDoe
   Discord ID: 987654321
   Initial Permissions: NONE (role: VIEWER)
   Status: ✅ Ready - Admin can assign permissions
```

## 🛡️ Error Handling

### Daca Supabase e offline:
```
❌ Connection error to Supabase: ...
   Check: Is Supabase online? Is internet connected?
```

### Daca ceva se intampla gresit:
```
❌ Failed to create user in Supabase: HTTP 400
   Response: ...
   Error: Invalid data format - check table schema
```

## ⚙️ Configurare Tabel Supabase

Tabelul `discord_users` trebuie sa aiba coloane:

| Coloana | Tip | Required | Default |
|---------|-----|----------|---------|
| `id` | UUID | ✅ | auto |
| `discord_username` | VARCHAR | ✅ | - |
| `discord_id` | VARCHAR | ✅ | - |
| `discord_email` | VARCHAR | ❌ | NULL |
| `created_at` | TIMESTAMP | ✅ | NOW() |
| `last_login` | TIMESTAMP | ✅ | NOW() |
| `active` | BOOLEAN | ✅ | TRUE |
| `is_superuser` | BOOLEAN | ✅ | FALSE |
| `is_admin` | BOOLEAN | ✅ | FALSE |
| `can_view` | BOOLEAN | ✅ | FALSE |
| `can_edit` | BOOLEAN | ✅ | FALSE |
| `can_delete` | BOOLEAN | ✅ | FALSE |
| `granular_permissions` | JSON | ❌ | '{}' |

**Constraint:** `discord_id` trebuie sa fie **UNIQUE**!

```sql
ALTER TABLE discord_users 
ADD UNIQUE (discord_id);
```

## 🔄 Retry Logic

Daca Supabase timeout-ul:
1. Prima incercare - se face API call
2. Daca timeout → Asteapta 1 sec
3. Incercare #2 - se reface API call
4. Daca OK → User creat/updatat

## 📍 Locatii Code

### discord_auth.py
```python
def _fetch_user_info(self):
    # ...
    self._save_to_supabase()  # ◄─ Autoinvoke dupa Discord login

def _save_to_supabase(self):
    # ...
    supabase.register_user(username, user_id, email)  # ◄─ Creeaza/updatat user
```

### supabase_sync.py
```python
def register_user(self, discord_username, discord_id, discord_email):
    # 1. Check daca exista
    # 2. Daca exista -> UPDATE last_login
    # 3. Daca nu exista -> CREATE user nou cu NO PERMISSIONS
```

## ✅ Test Steps

1. **Logare ca user NOU:**
   - Click "Login cu Discord"
   - Completeaza autentificarea
   - Verifica console pentru "NEW USER CREATED"
   - Verifica in Supabase -> Utilizatorul e in tabel

2. **Logare repetata aceleasi user:**
   - Click "Login cu Discord"
   - Completeaza autentificarea
   - Verifica console pentru "User already exists"
   - Verifica in Supabase -> last_login e updatat

3. **Verifica role initial:**
   - User nou are role **VIEWER** (fara acces)
   - Admin trebuie sa-i dea permisiuni

## 🚀 Production Deployment

✅ Functionalitate **ACTIVE** pe producție
✅ Auto-registration **ENABLED** by default
✅ Retry logic **IMPLEMENTED**
✅ Error handling **COMPREHENSIVE**

---

**Status:** ✅ GATA & TESTAT
**Last Updated:** Feb 3, 2026
