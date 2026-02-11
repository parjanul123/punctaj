
# SISTEM DE PERMISIUNI GRANULARE - INSTITUTII
============================================

## OVERVIEW

Aplicatia acum suporta permisiuni granulare la nivel de institutie. Fiecare utilizator poate avea:

1. PERMISIUNI GLOBALE (pentru toate orasele)
   - can_add_city: Poate adauga orase noi
   - can_edit_city: Poate edita orase existente
   - can_delete_city: Poate sterge orase

2. PERMISIUNI LA NIVEL DE INSTITUTIE (per institutie per oras)
   - can_view: Poate vizualiza datele institutiei
   - can_edit: Poate edita institutia
   - can_delete: Poate sterge institutia
   - can_add_employee: Poate adauga angajati
   - can_edit_employee: Poate edita angajati existenti
   - can_delete_employee: Poate sterge angajati
   - can_add_score: Poate adauga/edita punctaje (ADAUGAT NOU)


## FLUX DE SETARE A PERMISIUNILOR

### 1. ACCES LA PANOUL DE PERMISIUNI

- Doar SUPERUSER-i pot gestiona permisiunile
- Buton "⚙️ Admin" apare in sidebar-ul Discord dupa login
- Click pe buton deschide panelul de gestionare permisiuni


### 2. SETAREA PERMISIUNILOR PENTRU UN UTILIZATOR

1. Deschide Admin Panel (⚙️ Admin)
2. Cauta utilizatorul dupa Discord ID sau Username
3. Alege utilizatorul din lista
4. Bifeza permisiunile dorite:

   - ORASE (globale):
     ✓ Permite adaugare oras
     ✓ Permite editare oras
     ✓ Permite stergere oras

   - INSTITUTII (per institutie):
     ✓ can_view - vizualizare
     ✓ can_edit - editare
     ✓ can_delete - stergere
     ✓ can_add_employee - adaugare angajati
     ✓ can_edit_employee - editare angajati
     ✓ can_delete_employee - stergere angajati
     ✓ can_add_score - adaugare/editare punctaje

5. Salveaza permisiunile (click "Salveaza Permisiuni")


## VERIFICAREA PERMISIUNILOR IN APLICATIE

### Cand utilizatorul incearca sa:

#### 1. ADAUGĂ ORAŞ
- Sistema verifica `can_add_city` permisiunea globala
- Daca NU are permisiunea:
  ❌ Butonul "➕ Adaugă oraș" este DEZACTIVAT (gri)
  ❌ Apare mesaj de eroare daca incearca alt mod

#### 2. EDITEAZA ORAŞ
- Sistema verifica `can_edit_city` permisiunea globala
- Daca NU are permisiunea:
  ❌ Butonul "✏️ Editează oraș" este DEZACTIVAT
  ❌ Apare mesaj de eroare

#### 3. STERGE ORAŞ
- Sistema verifica `can_delete_city` permisiunea globala
- Daca NU are permisiunea:
  ❌ Butonul "❌ Șterge oraș" este DEZACTIVAT
  ❌ Apare mesaj de eroare

#### 4. ADAUGĂ ANGAJAT LA INSTITUTIE
- Sistema verifica `can_add_employee` permisiunea PER INSTITUTIE
- Daca NU are permisiunea LA ACEA INSTITUTIE SPECIFICA:
  ❌ Butonul de adaugare angajat este DEZACTIVAT DOAR PENTRU ACEA INSTITUTIE
  ❌ Mesaj: "❌ Nu ai permisiunea să adaugi angajați la [Institutie]"

#### 5. EDITEAZA ANGAJAT LA INSTITUTIE
- Sistema verifica `can_edit_employee` permisiunea PER INSTITUTIE
- Daca NU are permisiunea LA ACEA INSTITUTIE SPECIFICA:
  ❌ Editarea angajatului este blokata
  ❌ Mesaj: "❌ Nu ai permisiunea să editezi angajații la [Institutie]"

#### 6. STERGE ANGAJAT DE LA INSTITUTIE
- Sistema verifica `can_delete_employee` permisiunea PER INSTITUTIE
- Daca NU are permisiunea LA ACEA INSTITUTIE SPECIFICA:
  ❌ Stergerea angajatului este blokata
  ❌ Mesaj: "❌ Nu ai permisiunea să ștergi angajați de la [Institutie]"

#### 7. ADAUGĂ/EDITEAZA PUNCTAJ
- Sistema verifica `can_add_score` permisiunea PER INSTITUTIE
- Daca NU are permisiunea LA ACEA INSTITUTIE SPECIFICA:
  ❌ Adaugarea/editarea punctajului este blokata
  ❌ Mesaj: "❌ Nu ai permisiunea să adaugi punctaj la [Institutie]"


## EXEMPLU REAL - SETUP PERMISIUNI

Scenario: User "officer_alex" din BlackWater trebuie sa poata adauga angajati, dar NU le poate sterge

### Configurare:

1. Admin deschide Admin Panel
2. Cauta "officer_alex" in lista utilizatorilor
3. La INSTITUTII -> BlackWater -> Politie:
   ✓ can_view = BIFAT
   ✓ can_edit = BIFAT
   ✓ can_add_employee = BIFAT ← Poate adauga!
   ✓ can_edit_employee = BIFAT ← Poate edita
   ✗ can_delete_employee = NEBIFAT ← NU poate sterge!
   ✓ can_add_score = BIFAT ← Poate adauga punctaje

4. Salveaza permisiunile

### Rezultat:

- officer_alex vede BUTONUL "➕ Adaugă angajat" ACTIV
- officer_alex vede BUTONUL "❌ Șterge angajat" DEZACTIVAT (gri)
- Daca incearca sa stearga printr-alt mod, apare: "❌ Nu ai permisiunea să ștergi angajați..."


## ROLURI PREDEFINITE

### SUPERUSER (👑)
- Acces complet la ORICE
- Nu are nicio restrictie
- Vede TOATE institutiile din TOATE orasele
- Poate gestiona permisiunile altor utilizatori

### ADMIN (🛡️)
- Acces complet (similar superuser-ului dar fara gestiune permisiuni)
- Vede TOATE institutiile
- Poate adauga/edita/sterge ORICE

### USER (👤)
- Acces limitat la institutiile/orasele pentru care are permisiuni
- Trebuie sa aiba explicit bifata FIECARE permisiune
- Vede DOAR institutiile cu `can_view = true`

### VIEWER (👁️)
- Acces READ-ONLY
- NU poate adauga/edita/sterge NIMIC
- Poate doar sa VIZUALIZEZE datele


## SUPABASE STORAGE

Permisiunile sunt stocate in Supabase in tabelul `discord_users`:

Coloana: `granular_permissions` (JSON)

Structura:
```json
{
  "institutions": {
    "BlackWater": {
      "Politie": {
        "can_view": true,
        "can_edit": true,
        "can_delete": false,
        "can_add_employee": true,
        "can_edit_employee": true,
        "can_delete_employee": false,
        "can_add_score": true
      },
      "Pompieri": {
        "can_view": true,
        "can_edit": false,
        "can_delete": false,
        "can_add_employee": false,
        "can_edit_employee": false,
        "can_delete_employee": false,
        "can_add_score": false
      }
    }
  }
}
```

Coloana: `permissions` (JSON - permisiuni globale)

Structura:
```json
{
  "can_add_city": true,
  "can_edit_city": true,
  "can_delete_city": false
}
```


## VERSIUNE

- Versiunea sistemului de permisiuni: 2.5
- Data adaugarii permisiunilor granulare la institutii: Februarie 2026

✅ ➕ Adaugă instituție   - Can create new institutions
✅ ✏️  Editează instituție - Can modify institutions
✅ ❌ Șterge instituție    - Can delete institutions
```

### Angajați (Employees)
```
✅ ➕ Adaugă angajat   - Can add new employees
✅ ✏️  Editează angajat - Can modify employees
✅ ❌ Șterge angajat    - Can delete employees
```

### Cloud (Cloud Synchronization)
```
✅ 📤 Upload în cloud - Can upload data to cloud
✅ 📥 Download din cloud - Can download from cloud
```

### Admin (Administrator Features)
```
✅ 📋 Vizualizare logs - Can view action logs
✅ 👥 Gestiune utilizatori - Can manage users
✅ 🔐 Gestiune permisiuni - Can manage permissions
```

## Examples

### Example 1: Read-Only User (Viewer)
```
Orașe:          ❌ ❌ ❌ (no city operations)
Instituții:     ❌ ❌ ❌ (no institution operations)
Angajați:       ❌ ❌ ❌ (no employee operations)
Cloud:          ❌ ❌ (no cloud operations)
Admin:          ❌ ❌ ❌ (no admin features)
```

### Example 2: Data Entry User
```
Orașe:          ✅ ✅ ❌ (can add/edit cities, not delete)
Instituții:     ✅ ✅ ✅ (full institution control)
Angajați:       ✅ ✅ ✅ (full employee control)
Cloud:          ✅ ✅ (can upload/download)
Admin:          ❌ ❌ ❌ (no admin features)
```

### Example 3: Manager User
```
Orașe:          ✅ ✅ ✅ (full city control)
Instituții:     ✅ ✅ ✅ (full institution control)
Angajați:       ✅ ✅ ✅ (full employee control)
Cloud:          ✅ ✅ (can upload/download)
Admin:          ✅ ❌ ❌ (can view logs only)
```

### Example 4: Full Administrator
```
Orașe:          ✅ ✅ ✅ (full city control)
Instituții:     ✅ ✅ ✅ (full institution control)
Angajați:       ✅ ✅ ✅ (full employee control)
Cloud:          ✅ ✅ (can upload/download)
Admin:          ✅ ✅ ✅ (full admin access)
```

## Features

✅ **User-Friendly Interface**
- Simple checkbox selection
- Easy to understand categories
- Visual organization with tabs

✅ **Granular Control**
- Control each operation separately
- Set permissions per user
- No need for role changes

✅ **Automatic Storage**
- Permissions saved to Supabase
- Persistent across sessions
- Real-time updates

✅ **Immediate Effect**
- Changes visible after user login
- UI updates based on permissions
- Buttons hidden/disabled automatically

## Supabase Storage

Permissions are stored in the `discord_users` table:
- Column: `permissions` (JSON format)
- Format:
```json
{
  "add_city": true,
  "edit_city": true,
  "delete_city": false,
  "add_institution": true,
  "edit_institution": true,
  "delete_institution": true,
  "add_employee": true,
  "edit_employee": true,
  "delete_employee": true,
  "upload_cloud": true,
  "download_cloud": true,
  "view_logs": false,
  "manage_users": false,
  "manage_permissions": false
}
```

## Tips & Tricks

💡 **Quick Copy Permissions**
- Create one user with desired permissions
- Take note of the checkbox pattern
- Apply same pattern to other users

💡 **Default Permissions**
- New users get all permissions OFF by default
- Make sure to enable needed permissions

💡 **Test Permissions**
- Log out and log back in to see UI changes
- Buttons should hide/show based on permissions
- Error messages appear when trying denied actions

💡 **Admin Override**
- Admins always have full access
- Permissions don't apply to admin role
- Use "viewer" or "user" role for granular control

## Troubleshooting

### Q: Changes not taking effect?
**A:** Logout and login again. Permissions are loaded at login.

### Q: Can't find Granular Permissions tab?
**A:** Make sure you're:
1. Logged in with Discord
2. Have admin role
3. In the Admin Panel
4. Looking at 4th tab: "🔐 Permisiuni Granulare"

### Q: User dropdown is empty?
**A:** No users in system. Create users first:
1. Have someone login with Discord
2. Go back to Granular Permissions
3. Dropdown should now show users

### Q: Button disappeared but permission is checked?
**A:** Logout and login again. UI updates on login.

---

**For technical details, see:** admin_permissions.py
**For admin info, see:** USER_MANAGEMENT_GUIDE.md
