# 📚 Ghid Complet - Implementare Permisiuni Instituții

## 🎯 Obiectiv Final

Fiecare utilizator (eg: Șerif din Blackwater) poate administra DOAR instituțiile pe care are acces:
- ✅ Adaugă angajați → doar cu `can_edit`
- ✅ Vizualizează → doar cu `can_view`
- ✅ Șterge/Reset → doar cu `can_delete`

---

## 🚀 Pasii de Implementare

### **PASUL 1: Setup Database (5 minute)**

#### 1.1 Deschide Supabase
- Mergi la https://supabase.com/dashboard
- Selectează proiectul tău
- Mergi la "SQL Editor"

#### 1.2 Rulează SQL-ul
Copiază și rulează comenzile din:
```
📄 d:\punctaj\SETUP_INSTITUTION_PERMISSIONS.sql
```

Comenzi importante:
```sql
-- Adaugă coloana
ALTER TABLE discord_users 
ADD COLUMN IF NOT EXISTS granular_permissions JSONB DEFAULT '{"institutions": {}}'::jsonb;

-- Index pentru performance
CREATE INDEX IF NOT EXISTS idx_discord_users_granular_perms 
ON discord_users USING gin(granular_permissions);
```

✅ **Status**: Coloana `granular_permissions` adăugată în Supabase

---

### **PASUL 2: Instalare Python (5 minute)**

#### 2.1 Importuri în `punctaj.py`

```python
# În secțiunea de imports
from admin_permissions import InstitutionPermissionManager, open_granular_permissions_panel
from permission_decorators import PermissionChecker, PermissionGuard

# După inițializare supabase_sync
inst_perm_manager = InstitutionPermissionManager(
    supabase_sync,
    data_dir="d:/punctaj/data"  # Calea unde sunt dosarele cu orașe
)

# Faci available pentru alte module
INSTITUTION_PERM_MANAGER = inst_perm_manager
```

#### 2.2 Adaugă buton admin
```python
# În panelul admin, adaugă:
ttk.Button(
    admin_frame,
    text="🏢 Permisiuni Instituții",
    command=lambda: open_granular_permissions_panel(
        root, supabase_sync, discord_auth, data_dir="d:/punctaj/data"
    )
).pack()
```

✅ **Status**: Modulele importate și disponibile

---

### **PASUL 3: Protejare Funcții (20 minute)**

#### 3.1 Funcția de Adaugă Angajat

```python
def add_employee_handler(self, city, institution):
    """Deschide dialog de adaugă cu verificare permisiuni"""
    
    # VERIFICARE
    if not inst_perm_manager.check_user_institution_permission(
        self.current_user_id, city, institution, 'can_edit'
    ):
        messagebox.showerror("Acces Refuzat", f"❌ Nu poți adăuga angajați la {city}/{institution}")
        log_action("add_employee_denied", f"User {self.current_user_id} tried unauthorized add")
        return
    
    # DIALOG de adaugă
    # ... deschide dialog ...
    
    # SALVARE
    try:
        supabase_sync.add_employee(city, institution, employee_data)
        messagebox.showinfo("Succes", "✅ Angajat adăugat!")
        log_action("add_employee_success", f"Added {employee_data.name}")
    except Exception as e:
        messagebox.showerror("Eroare", f"❌ {e}")
        log_action("add_employee_error", str(e))
```

#### 3.2 Funcția de Editare

```python
def edit_employee_handler(self, city, institution, employee_id):
    """Editează angajat cu verificare permisiuni"""
    
    # VERIFICARE
    if not inst_perm_manager.check_user_institution_permission(
        self.current_user_id, city, institution, 'can_edit'
    ):
        messagebox.showerror("Acces Refuzat", f"❌ Nu poți edita la {city}/{institution}")
        return
    
    # ... rest de cod ...
```

#### 3.3 Funcția de Ștergere

```python
def delete_employee_handler(self, city, institution, employee_id):
    """Șterge angajat cu verificare permisiuni"""
    
    # VERIFICARE
    if not inst_perm_manager.check_user_institution_permission(
        self.current_user_id, city, institution, 'can_delete'
    ):
        messagebox.showerror("Acces Refuzat", f"❌ Nu poți șterge la {city}/{institution}")
        return
    
    if messagebox.askyesno("Confirmare", "Ești sigur?"):
        supabase_sync.delete_employee(city, institution, employee_id)
        messagebox.showinfo("Succes", "✅ Angajat șters!")
```

#### 3.4 Funcția de Reset Punctaj

```python
def reset_scores_handler(self, city, institution):
    """Resetează punctajele cu verificare permisiuni"""
    
    # VERIFICARE - necesită delete permission
    if not inst_perm_manager.check_user_institution_permission(
        self.current_user_id, city, institution, 'can_delete'
    ):
        messagebox.showerror("Acces Refuzat", f"❌ Nu poți reseta la {city}/{institution}")
        return
    
    if messagebox.askyesno("Confirmare", "Reset punctaje pentru toți? ⚠️"):
        # ... reset logic ...
        messagebox.showinfo("Succes", "✅ Punctaje resetate!")
```

✅ **Status**: Toate funcțiile au verificări

---

### **PASUL 4: Control Butoane UI (15 minute)**

#### 4.1 Funcția de Actualizare UI

```python
def update_institution_ui(self, city, institution):
    """Actualizează starea butoanelor în funcție de permisiuni"""
    
    # Obține permisiuni
    checker = PermissionChecker(inst_perm_manager, self.current_user_id)
    states = checker.get_button_states(city, institution)
    
    # Actualizează butoane
    self.add_button.config(state=tk.NORMAL if states['can_add'] else tk.DISABLED)
    self.edit_button.config(state=tk.NORMAL if states['can_edit'] else tk.DISABLED)
    self.delete_button.config(state=tk.NORMAL if states['can_delete'] else tk.DISABLED)
    self.reset_button.config(state=tk.NORMAL if states['can_reset'] else tk.DISABLED)
    
    # Afișează/ascunde lista
    if states['can_view']:
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        self.load_employees(city, institution)
    else:
        self.employee_tree.pack_forget()
        ttk.Label(self.frame, text="❌ Nu ai acces").pack(pady=20)
```

#### 4.2 La Selecție Instituție

```python
def on_institution_selected(self, city, institution):
    """Se apelează când utilizatorul selectează o instituție"""
    
    self.current_city = city
    self.current_institution = institution
    
    # Actualizează UI
    self.update_institution_ui(city, institution)
```

#### 4.3 Filtrare Instituții Vizibile

```python
def load_institutions_list(self):
    """Încarcă DOAR instituțiile pe care utilizatorul are acces"""
    
    all_institutions = inst_perm_manager.get_all_institutions_by_city()
    checker = PermissionChecker(inst_perm_manager, self.current_user_id)
    
    # Filtrează
    accessible = checker.get_accessible_institutions(all_institutions)
    
    # Afișează în UI
    for city, institutions in accessible.items():
        for institution in institutions:
            self.add_city_institution_tab(city, institution)
```

✅ **Status**: UI complet controlat de permisiuni

---

### **PASUL 5: Testare (10 minute)**

#### 5.1 Tool de Setup

```bash
cd d:/punctaj
python setup_permissions_tool.py
```

Menu:
```
1. ✅ Verifică dacă Supabase e configurat
2. 👥 Afișează toți utilizatorii
3. 📋 Afișează permisiuni utilizator
4. ⚙️  Setează permisiuni de test
5. 🔄 Resetează permisiuni utilizator
6. ❌ Ieși
```

#### 5.2 Setează Permisiuni Test

```
Opțiune: 4
Discord ID: 123456
→ Se setează permisiuni de test:
   - Blackwater/Politie: can_view ✅, can_edit ✅, can_delete ✅
   - Blackwater/Medical: can_view ❌, can_edit ❌, can_delete ❌
   - Saint-Denis/Politie: can_view ✅, can_edit ❌, can_delete ❌
```

#### 5.3 Testează în Aplicație

1. Pornește `punctaj.py`
2. Autentifică cu utilizatorul de test
3. Mergi la admin → "Permisiuni Instituții"
4. Verifica permisiunile setate
5. Deschide o instituție:
   - ✅ Butoanele sunt active/inactive corect
   - ✅ Lista este vizibilă/ascunsă corect

✅ **Status**: Testare OK

---

## 📋 Checklist Completă

### Database
- [ ] SQL rulat în Supabase
- [ ] Coloana `granular_permissions` creată
- [ ] Index pentru performance creat

### Cod Python
- [ ] Import `InstitutionPermissionManager` în `punctaj.py`
- [ ] Init manager cu supabase_sync și data_dir
- [ ] Buton admin pentru panelul de permisiuni

### Protecție Funcții
- [ ] Verificare în `add_employee`
- [ ] Verificare în `edit_employee`
- [ ] Verificare în `delete_employee`
- [ ] Verificare în `reset_scores`

### Control UI
- [ ] Update funcție pentru butoane
- [ ] Filtrare instituții vizibile
- [ ] Afișare/ascundere liste

### Testing
- [ ] Setare permisiuni de test
- [ ] Verificare permisiuni în Supabase
- [ ] Test cu utilizator diferit
- [ ] Test cu permisiuni diferite

---

## 🔒 Securitate

### Client-side (Python)
✅ Faci verificări de permisiuni

### Server-side (Supabase) - OPTIONAL dar RECOMANDAT
```sql
-- Activează RLS
ALTER TABLE discord_users ENABLE ROW LEVEL SECURITY;

-- Policy: Superuser poate modifica
CREATE POLICY "superuser_can_manage" ON discord_users
FOR UPDATE
USING ((SELECT is_superuser FROM discord_users WHERE id = auth.uid()))
WITH CHECK ((SELECT is_superuser FROM discord_users WHERE id = auth.uid()));
```

---

## 🎓 Exemple Practici

### Exemplu 1: Șerif Blackwater - Acces Complet
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
      }
    }
  }
}
```
**Rezultat**: Vede DOAR Politie din Blackwater, poate adăuga/edita/șterge

### Exemplu 2: Manager Saint-Denis - Acces Limitat
```json
{
  "institutions": {
    "Saint-Denis": {
      "Administrație": {
        "can_view": true,
        "can_edit": true,
        "can_delete": false
      }
    }
  }
}
```
**Rezultat**: Vede și editează, dar NU poate șterge

### Exemplu 3: Viewer - Doar Vizualizare
```json
{
  "institutions": {
    "Blackwater": {
      "Politie": {
        "can_view": true,
        "can_edit": false,
        "can_delete": false
      }
    },
    "Saint-Denis": {
      "Polț": {
        "can_view": true,
        "can_edit": false,
        "can_delete": false
      }
    }
  }
}
```
**Rezultat**: Vede ambele instituții dar NU poate modifica nimic

---

## 🆘 Troubleshooting

### Problem: "Permisiunile nu se salvează"
**Soluție**:
1. Verifică dacă coloana `granular_permissions` există:
   ```bash
   python setup_permissions_tool.py
   Opțiune 1 (Verifică)
   ```
2. Rulează SQL din SETUP_INSTITUTION_PERMISSIONS.sql

### Problem: "Butoanele sunt întotdeauna active"
**Soluție**:
1. Verifică dacă permisiunile sunt setate pentru utilizator:
   ```bash
   python setup_permissions_tool.py
   Opțiune 3 (Afișează permisiuni)
   ```
2. Setează permisiuni de test:
   ```bash
   python setup_permissions_tool.py
   Opțiune 4 (Setează permisiuni de test)
   ```

### Problem: "Nici o instituție nu apare"
**Soluție**:
1. Verifică structura directoarelor:
   ```
   d:/punctaj/data/
   ├── Blackwater/
   │   └── Politie.json
   ├── Saint-Denis/
   │   └── Politie.json
   ```
2. Verifica în cod:
   ```python
   inst = inst_perm_manager.get_all_institutions_by_city()
   print(inst)  # Ar trebui să afișeze structura
   ```

---

## 📞 Suport

Pentru probleme:
1. Rulează `setup_permissions_tool.py`
2. Vezi log-urile în terminal
3. Verifică Supabase dashboard pentru structura datelor
4. Contactează cu informații din tool

---

## 📊 Status Implementare

```
┌─────────────────────────────────────────┐
│ ✅ SISTEM PERMISIUNI INSTITUȚII GATA    │
├─────────────────────────────────────────┤
│ ✅ Database Schema                      │
│ ✅ Python Classes                       │
│ ✅ Admin Panel                          │
│ ✅ Permission Decorators                │
│ ✅ UI Controls                          │
│ ✅ Testing Tool                         │
│ ✅ Documentation                        │
└─────────────────────────────────────────┘
```

**Gata pentru Production**: ✅ DA

---

**Creat**: February 2026  
**Versiune**: 1.0  
**Status**: Production Ready
