# 🎯 ACTIONABLE CHECKLIST - TODO LIST

Data: February 2026  
Task: Implementare Sistem Permisiuni Instituții

---

## 📋 FAZE

### 🔴 FAZA 1: SETUP (15 minute)

- [ ] **1.1 Citeste documentație intro** (5 min)
  - [ ] Deschide `GETTING_STARTED.md`
  - [ ] Citeste secțiunea "⏰ Timeline"
  - [ ] Citeste secțiunea "📋 CHECKLIST RAPID"

- [ ] **1.2 Setup Database** (5 min)
  - [ ] Mergi la https://supabase.com/dashboard
  - [ ] Selectează proiectul
  - [ ] Mergi la "SQL Editor"
  - [ ] Deschide `SETUP_INSTITUTION_PERMISSIONS.sql`
  - [ ] Copiaza primele linii (ALTER TABLE + CREATE INDEX)
  - [ ] Paste în Supabase SQL Editor
  - [ ] Click "RUN"
  - [ ] Verifică că nu sunt erori (Status: ✅)

- [ ] **1.3 Setup Python** (5 min)
  - [ ] Deschide `d:\punctaj\punctaj.py`
  - [ ] Găseste secțiunea de imports (linia ~80)
  - [ ] Adauga:
    ```python
    from admin_permissions import InstitutionPermissionManager
    from permission_decorators import PermissionChecker
    ```
  - [ ] Găseste secțiunea de inițializare supabase (linia ~150)
  - [ ] Adauga:
    ```python
    inst_perm_manager = InstitutionPermissionManager(
        supabase_sync,
        "d:/punctaj/data"  # SAU path-ul cotrect
    )
    ```

- [ ] **1.4 Verifica Setup** (2 min)
  - [ ] Deschide terminal
  - [ ] Navighează în `d:\punctaj`
  - [ ] Rulează: `python setup_permissions_tool.py`
  - [ ] Alege opțiunea 1 (Verifică)
  - [ ] Ar trebui să vizi: ✅ "Coloana granular_permissions EXISTĂ"
  - [ ] **Status**: ✅ SETUP COMPLET

---

### 🟡 FAZA 2: DOCUMENTARE (20 minute)

- [ ] **2.1 Citeste ghiduri** (20 min)
  - [ ] `PERMISSIONS_QUICK_REFERENCE.md` (2 min) - snippets
  - [ ] `IMPLEMENTATION_GUIDE.md` (10 min) - pași detaliat
  - [ ] `INSTITUTION_PERMISSIONS_GUIDE.md` (5 min) - concepte
  - [ ] `INTEGRATION_EXAMPLE.py` (3 min) - exemplu cod

- [ ] **2.2 Înțelege 3 permisiuni** (5 min)
  - [ ] `can_view` = Vede lista
  - [ ] `can_edit` = Adaugă/editează
  - [ ] `can_delete` = Șterge/reset
  - [ ] **Status**: ✅ ÎNȚELEG PERMISIUNILE

---

### 🔵 FAZA 3: IMPLEMENTARE (90 minute)

#### PASUL 1: Protejează Funcția Add (20 min)
- [ ] **3.1.1 Găseste funcția add_employee()**
  - [ ] Caut în cod: `def add_employee`
  - [ ] Notez linia unde incepe

- [ ] **3.1.2 Adauga verificare la inceput**
  ```python
  # LA INCEPUT FUNCȚIEI
  if not inst_perm_manager.check_user_institution_permission(
      self.current_user_id,  # Current user
      city,                  # Parameter
      institution,           # Parameter
      'can_edit'            # Permission type
  ):
      messagebox.showerror("Eroare", "❌ Nu ai acces!")
      return
  ```

- [ ] **3.1.3 Adauga logging** (opțional)
  ```python
  # DUPA SUCCES
  action_logger.log_event("add_employee_success", ...)
  ```

- [ ] **Status**: ✅ FUNCȚIA ADD PROTEJATĂ

#### PASUL 2: Protejează Funcția Edit (15 min)
- [ ] **3.2.1 Găseste funcția edit_employee()**

- [ ] **3.2.2 Adauga verificare**
  ```python
  if not inst_perm_manager.check_user_institution_permission(
      self.current_user_id, city, institution, 'can_edit'
  ):
      return
  ```

- [ ] **Status**: ✅ FUNCȚIA EDIT PROTEJATĂ

#### PASUL 3: Protejează Funcția Delete (15 min)
- [ ] **3.3.1 Găseste funcția delete_employee()**

- [ ] **3.3.2 Adauga verificare**
  ```python
  if not inst_perm_manager.check_user_institution_permission(
      self.current_user_id, city, institution, 'can_delete'
  ):
      return
  ```

- [ ] **Status**: ✅ FUNCȚIA DELETE PROTEJATĂ

#### PASUL 4: Protejează Reset Punctaj (10 min)
- [ ] **3.4.1 Găseste funcția reset_scores()**

- [ ] **3.4.2 Adauga verificare**
  ```python
  if not inst_perm_manager.check_user_institution_permission(
      self.current_user_id, city, institution, 'can_delete'
  ):
      return
  ```

- [ ] **Status**: ✅ FUNCȚIA RESET PROTEJATĂ

#### PASUL 5: Control Butoane UI (30 min)
- [ ] **3.5.1 Găseste pagina cu instituții**
  - [ ] Caut: `def on_institution_selected` sau similar

- [ ] **3.5.2 Adauga verificări permisiuni**
  ```python
  can_view = inst_perm_manager.check_user_institution_permission(
      self.current_user_id, city, institution, 'can_view'
  )
  can_edit = inst_perm_manager.check_user_institution_permission(
      self.current_user_id, city, institution, 'can_edit'
  )
  can_delete = inst_perm_manager.check_user_institution_permission(
      self.current_user_id, city, institution, 'can_delete'
  )
  ```

- [ ] **3.5.3 Control butoane**
  ```python
  self.add_button.config(state=tk.NORMAL if can_edit else tk.DISABLED)
  self.edit_button.config(state=tk.NORMAL if can_edit else tk.DISABLED)
  self.delete_button.config(state=tk.NORMAL if can_delete else tk.DISABLED)
  self.reset_button.config(state=tk.NORMAL if can_delete else tk.DISABLED)
  ```

- [ ] **3.5.4 Control vizibilitate**
  ```python
  if can_view:
      self.employee_tree.pack(fill=tk.BOTH, expand=True)
      self.load_employees(city, institution)
  else:
      self.employee_tree.pack_forget()
      messagebox.showerror("Acces", "❌ Nu ai acces!")
  ```

- [ ] **Status**: ✅ UI COMPLET CONTROLAT

---

### 🟢 FAZA 4: TESTING (20 minute)

- [ ] **4.1 Setup Utilizator Test** (5 min)
  ```bash
  python setup_permissions_tool.py
  Alege 4 (Setează permisiuni de test)
  Discord ID: [aleator sau cunoscut]
  → Se setează: Blackwater/Politie = acces complet
  ```

- [ ] **4.2 Verifică Permisiuni** (5 min)
  ```bash
  python setup_permissions_tool.py
  Alege 3 (Afișează permisiuni)
  Discord ID: [același din 4.1]
  → Ar trebui sa vizi permisiunile setate
  ```

- [ ] **4.3 Testează în Aplicație** (10 min)
  - [ ] Pornește `python punctaj.py`
  - [ ] Autentifică cu utilizatorul de test
  - [ ] Deschide Blackwater/Politie
    - [ ] ✅ Lista angajați e vizibilă
    - [ ] ✅ Butoane sunt active
  - [ ] Mergi la Saint-Denis (SAU altă instituție fără acces)
    - [ ] ✅ Lista e ascunsă/afișează "Acces refuzat"
    - [ ] ✅ Butoane sunt inactive

- [ ] **Status**: ✅ TESTING COMPLET

---

### 🟣 FAZA 5: ADMIN PANEL (10 minute)

- [ ] **5.1 Adauga Buton Admin** (5 min)
  - [ ] Deschide panelul admin în cod
  - [ ] Adauga buton:
    ```python
    ttk.Button(
        admin_frame,
        text="🏢 Permisiuni Instituții",
        command=lambda: open_granular_permissions_panel(
            root, supabase_sync, discord_auth, "d:/punctaj/data"
        )
    ).pack()
    ```

- [ ] **5.2 Testează Admin Panel** (5 min)
  - [ ] Pornește app
  - [ ] Deschide Admin Panel
  - [ ] Click pe "🏢 Permisiuni Instituții"
  - [ ] Ar trebui să vizi:
    - [ ] ✅ Dropdown cu utilizatori
    - [ ] ✅ Orașe cu instituții
    - [ ] ✅ Checkbox-uri pentru permisiuni
  - [ ] Selectează un utilizator
  - [ ] Bifează câteva permisiuni
  - [ ] Click "Salvează"
  - [ ] Verifică că s-au salvat

- [ ] **Status**: ✅ ADMIN PANEL FUNCTIONAL

---

## 📊 FINAL CHECKLIST

### Code Changes
- [ ] Import InstitutionPermissionManager
- [ ] Import PermissionChecker
- [ ] Inițializare inst_perm_manager
- [ ] Protecție add_employee
- [ ] Protecție edit_employee
- [ ] Protecție delete_employee
- [ ] Protecție reset_scores
- [ ] Control butoane în UI
- [ ] Filtrare instituții vizibile
- [ ] Buton admin panel

### Documentation Reviewed
- [ ] GETTING_STARTED.md
- [ ] PERMISSIONS_QUICK_REFERENCE.md
- [ ] IMPLEMENTATION_GUIDE.md
- [ ] INSTITUTION_PERMISSIONS_GUIDE.md

### Testing Done
- [ ] SQL setup verificat
- [ ] Python imports funcționează
- [ ] Setup tool rulează OK
- [ ] Permisiuni se salvează
- [ ] UI se comportă corect
- [ ] Admin panel deschide
- [ ] Test user are permisiuni
- [ ] Restricții funcționează

---

## 🎯 ESTIMATED TIME

```
Faza 1 (Setup):          15 min
Faza 2 (Documentare):    20 min
Faza 3 (Implementare):   90 min
Faza 4 (Testing):        20 min
Faza 5 (Admin Panel):    10 min
─────────────────────────────
TOTAL:                  155 min (~2.5 ore)
```

---

## 🚀 READY TO DEPLOY?

- [ ] All checklist items completed
- [ ] Testing passed
- [ ] Code reviewed
- [ ] Permission admin panel working
- [ ] Documentation read

**Status**: ✅ READY FOR PRODUCTION

---

## ❌ IF STUCK

1. **Database problem?**
   → Rulează `python setup_permissions_tool.py` → Alege 1

2. **Import error?**
   → Verifică că `admin_permissions.py` e în folder

3. **Permissions not saving?**
   → Check Supabase granular_permissions column

4. **UI not updating?**
   → Verifică că on_institution_selected e apelat

5. **Need help?**
   → PERMISSIONS_INDEX.md → Troubleshooting section

---

## 📞 CONTACT

Dacă ai probleme, mergi la:
- [PERMISSIONS_QUICK_REFERENCE.md](PERMISSIONS_QUICK_REFERENCE.md) - snippets
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - details
- `setup_permissions_tool.py` - debug

---

**Última Update**: February 2026  
**Status**: Ready for Implementation ✅
