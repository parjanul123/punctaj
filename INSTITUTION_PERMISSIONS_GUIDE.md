# 🔐 Ghid Sistem Permisiuni Instituții - Granular pe Oraș și Instituție

## 📋 Rezumat

Sistem complet de permisiuni care permite controlul granular al accesului utilizatorilor **pentru fiecare instituție din fiecare oraș** separat.

## 🎯 Exemplu Practic: Șeriful din Blackwater

```
Șerif Blackwater (discord_id: 123456)
├── Blackwater/
│   ├── Politie
│   │   ├── can_view: ✅ true     (poate vedea angajații)
│   │   ├── can_edit: ✅ true     (poate adăuga/edita angajații)
│   │   └── can_delete: ✅ true   (poate șterge angajații)
│   └── Medical
│       ├── can_view: ❌ false
│       ├── can_edit: ❌ false
│       └── can_delete: ❌ false
└── Saint-Denis/
    └── (Fără acces la nimic)
```

## 🗄️ Structura Supabase - Tabelul `discord_users`

### Coloane Noi Necesare:

```sql
-- Adaugă coloanele în discord_users table
ALTER TABLE discord_users ADD COLUMN IF NOT EXISTS granular_permissions JSONB DEFAULT '{"institutions": {}}';
```

### Format JSONB - `granular_permissions`:

```json
{
  "institutions": {
    "Blackwater": {
      "Politie": {
        "can_view": true,
        "can_edit": true,
        "can_delete": true
      },
      "Medical": {
        "can_view": false,
        "can_edit": false,
        "can_delete": false
      },
      "Administrație": {
        "can_view": false,
        "can_edit": false,
        "can_delete": false
      }
    },
    "Saint-Denis": {
      "Politie": {
        "can_view": true,
        "can_edit": false,
        "can_delete": false
      },
      "Armată": {
        "can_view": false,
        "can_edit": false,
        "can_delete": false
      }
    },
    "New Hanover": {}
  }
}
```

## 🚀 Cum Se Folosește în Cod

### 1️⃣ Verificare Permisiuni Înainte de Acțiuni

```python
from admin_permissions import InstitutionPermissionManager

# Inițializare
inst_perm_manager = InstitutionPermissionManager(supabase_sync, data_dir)

# Verificare permisiuni
user_discord_id = "123456"
city = "Blackwater"
institution = "Politie"

# Poate vedea?
can_view = inst_perm_manager.check_user_institution_permission(
    user_discord_id, city, institution, 'can_view'
)

# Poate edita (adaugă/modifică)?
can_edit = inst_perm_manager.check_user_institution_permission(
    user_discord_id, city, institution, 'can_edit'
)

# Poate șterge?
can_delete = inst_perm_manager.check_user_institution_permission(
    user_discord_id, city, institution, 'can_delete'
)
```

### 2️⃣ Control Butoane în UI

```python
# În orice pagină care afișează angajații din o instituție:

if can_view:
    # Afișează lista angajați
    display_employees(employees)
else:
    # Ascunde lista
    label = ttk.Label(frame, text="❌ Nu ai acces la vizualizare")
    label.pack()

if can_edit:
    # Arată butonul de Adaugă/Editează
    add_button.pack()
else:
    add_button.pack_forget()

if can_delete:
    # Arată butonul de Șterge
    delete_button.pack()
else:
    delete_button.pack_forget()
```

### 3️⃣ Control Reset Punctaj

```python
# Doar dacă utilizatorul are can_edit pentru acea instituție
if inst_perm_manager.check_user_institution_permission(
    current_user_id, city, institution, 'can_edit'
):
    reset_button.config(state=tk.NORMAL)
else:
    reset_button.config(state=tk.DISABLED)
```

## 🎛️ Panelul de Administrare

### Deschidere:
```python
from admin_permissions import open_granular_permissions_panel

open_granular_permissions_panel(
    root=main_window,
    supabase_sync=supabase_sync,
    discord_auth=discord_auth,
    data_dir="path/to/data"  # Unde sunt dosarele cu orașe
)
```

### Interfață:
```
🔐 Gestiune Permisiuni Granulare
Selectează ce permisiuni au utilizatorii

Utilizatori: [👤 Șerif Blackwater (Admin) ▼]

🏢 Permisiuni Instituții
├── 🏙️ Blackwater
│   ├── 🏢 Politie
│   │   ☑ 👁️ Vizualizare
│   │   ☑ ✏️ Editare
│   │   ☑ ❌ Ștergere
│   └── 🏢 Medical
│       ☐ 👁️ Vizualizare
│       ☐ ✏️ Editare
│       ☐ ❌ Ștergere
└── 🏙️ Saint-Denis
    └── 🏢 Politie
        ☑ 👁️ Vizualizare
        ☐ ✏️ Editare
        ☐ ❌ Ștergere

[💾 Salvează Permisiuni]
```

## 🔧 Implementare Pas cu Pas

### Pasul 1: Adaugă Coloana în Supabase
```sql
ALTER TABLE discord_users 
ADD COLUMN IF NOT EXISTS granular_permissions JSONB DEFAULT '{"institutions": {}}';
```

### Pasul 2: Importă în `punctaj.py`
```python
from admin_permissions import InstitutionPermissionManager

# În zona de inițializare
inst_perm_manager = InstitutionPermissionManager(supabase_sync, data_dir)
```

### Pasul 3: Verifică Permisiuni Înainte de Acțiuni

Exemplu - în funcția de adaugă angajat:
```python
def add_employee_handler(city, institution, employee_data):
    # Verificare permisiuni
    if not inst_perm_manager.check_user_institution_permission(
        current_user_discord_id, city, institution, 'can_edit'
    ):
        messagebox.showerror("Eroare", "❌ Nu ai permisiuni pentru această acțiune!")
        return
    
    # Continuă cu adaugarea...
    add_employee_to_supabase(employee_data)
```

### Pasul 4: Control Butoane

```python
def update_button_states(city, institution):
    """Actualizează starea butoanelor în funcție de permisiuni"""
    
    can_view = inst_perm_manager.check_user_institution_permission(
        current_user_discord_id, city, institution, 'can_view'
    )
    can_edit = inst_perm_manager.check_user_institution_permission(
        current_user_discord_id, city, institution, 'can_edit'
    )
    can_delete = inst_perm_manager.check_user_institution_permission(
        current_user_discord_id, city, institution, 'can_delete'
    )
    
    # Actualizează UI
    add_button.config(state=tk.NORMAL if can_edit else tk.DISABLED)
    edit_button.config(state=tk.NORMAL if can_edit else tk.DISABLED)
    delete_button.config(state=tk.NORMAL if can_delete else tk.DISABLED)
    employee_frame.pack() if can_view else employee_frame.pack_forget()
```

## 📊 Tipuri de Permisiuni

| Permisiune | Descriere | Butoane Afectate |
|-----------|-----------|-----------------|
| `can_view` | Poate vedea angajații | Afișare listă |
| `can_edit` | Poate adăuga/modifica angajații | Buton Adaugă, Editează |
| `can_delete` | Poate șterge angajații | Buton Șterge, Reset Punctaj |

## 🔄 Flow Complet - Exemplu Practic

### Scenario: Șerif din Blackwater deschide aplicația

```python
# 1. Autentificare Discord
current_user_id = discord_auth.get_current_user()  # "123456"

# 2. Încarcă instituții disponibile
inst_manager = InstitutionPermissionManager(supabase_sync, data_dir)
institutions_by_city = inst_manager.get_all_institutions_by_city()
# Rezultat: {"Blackwater": ["Politie", "Medical"], "Saint-Denis": ["Politie", ...]}

# 3. Afișează doar instituțiile unde utilizatorul are can_view
for city, institutions in institutions_by_city.items():
    for institution in institutions:
        has_access = inst_manager.check_user_institution_permission(
            current_user_id, city, institution, 'can_view'
        )
        if has_access:
            add_tab(city, institution)  # Afișează tab-ul
        # altfel: nu afișează

# 4. La deschiderea unei instituții
def on_institution_selected(city, institution):
    can_view = inst_manager.check_user_institution_permission(
        current_user_id, city, institution, 'can_view'
    )
    can_edit = inst_manager.check_user_institution_permission(
        current_user_id, city, institution, 'can_edit'
    )
    can_delete = inst_manager.check_user_institution_permission(
        current_user_id, city, institution, 'can_delete'
    )
    
    if not can_view:
        show_error("❌ Nu ai acces la această instituție")
        return
    
    # Afișează angajații
    employees = load_employees(city, institution)
    display_employees(employees)
    
    # Afișează/ascunde butoane
    add_button.config(state=tk.NORMAL if can_edit else tk.DISABLED)
    delete_button.config(state=tk.NORMAL if can_delete else tk.DISABLED)
```

## 🛡️ Securitate

✅ Verificări se fac **și pe client ȘI pe server**
✅ Nu te baza DOAR pe UI (oricine poate dezactiva butoane)
✅ Supabase trbuie să aibă și RLS policies pentru siguranță completă

### RLS Policy Recomandată (pe Supabase):
```sql
-- Doar superuser poate schimba permisiuni
CREATE POLICY "Only superuser can manage permissions" ON discord_users
  FOR UPDATE
  USING (auth.uid() IN (
    SELECT id FROM discord_users WHERE is_superuser = true
  ))
  WITH CHECK (auth.uid() IN (
    SELECT id FROM discord_users WHERE is_superuser = true
  ));
```

## 📝 Checklist Implementare

- [ ] Adaugă coloana `granular_permissions` în Supabase
- [ ] Importă `InstitutionPermissionManager` în `punctaj.py`
- [ ] Inițializează managerul cu calea directoarelor
- [ ] Adaugă verificări permisiuni la fiecare acțiune (adaugă, editează, șterge)
- [ ] Control butoane în funcție de permisiuni
- [ ] Testează cu mai mulți utilizatori
- [ ] Setează permisiuni pentru fiecare utilizator în panelul admin

## 🎓 Răspunsuri la Întrebări Frecvente

### Q: Cum dau acces la o instituție nouă unui utilizator?
A: Deschizi panelul de permisiuni, selectezi utilizatorul, bifezi permisiunile dorite și salvezi.

### Q: Ce se întâmplă dacă adaug o instituție nouă?
A: Se inițializează automat în permisiuni cu toate valorile `false` pentru toți utilizatorii. Apoi le activezi manual pentru cine trebuie.

### Q: Pot restrânge accesul la nivel de angajat individual?
A: Nu în versiunea curentă. Permisiunile sunt doar pe instituție. Dacă vrei mai granular, putem adăuga și nivelul de angajat.

### Q: Cum resetez permisiile pentru un utilizator?
A: Panelul admin permite debitare/rebitare permisiunilor. Un superuser ar putea și șterge intreg JSON-ul.

---

**Status**: ✅ Gata de implementare
**Ultima actualizare**: Februar 2026
