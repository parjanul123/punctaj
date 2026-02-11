# 🚀 Quick Reference - Permisiuni Instituții

## ⚡ Setup Rapid (5 minute)

### 1. SQL - Adaugă coloana
```sql
ALTER TABLE discord_users 
ADD COLUMN IF NOT EXISTS granular_permissions JSONB DEFAULT '{"institutions": {}}';
```

### 2. Python - Import & Init
```python
from admin_permissions import InstitutionPermissionManager

perm_manager = InstitutionPermissionManager(supabase_sync, "d:/punctaj/data")
```

### 3. Python - Verificare Permisiuni
```python
# Înainte de orice acțiune
if not perm_manager.check_user_institution_permission(user_id, city, institution, 'can_edit'):
    messagebox.showerror("Eroare", "❌ Acces refuzat!")
    return
```

### 4. UI - Control Butoane
```python
can_view = perm_manager.check_user_institution_permission(user_id, city, inst, 'can_view')
can_edit = perm_manager.check_user_institution_permission(user_id, city, inst, 'can_edit')
can_delete = perm_manager.check_user_institution_permission(user_id, city, inst, 'can_delete')

add_button.config(state=tk.NORMAL if can_edit else tk.DISABLED)
delete_button.config(state=tk.NORMAL if can_delete else tk.DISABLED)
```

---

## 📋 3 Tipuri de Permisiuni

```
can_view    → Vede lista angajați
can_edit    → Adaugă/Editează angajați  
can_delete  → Șterge/Reset Punctaj
```

---

## 🎯 Deschidere Panelul Admin

```python
from admin_permissions import open_granular_permissions_panel

open_granular_permissions_panel(
    root=main_window,
    supabase_sync=supabase_sync,
    discord_auth=discord_auth,
    data_dir="d:/punctaj/data"
)
```

---

## 🔍 Verificări Obișnuite

### Înainte de Adaugă
```python
if not perm_manager.check_user_institution_permission(user_id, city, inst, 'can_edit'):
    return  # Refuz
add_employee_to_db(...)
```

### Înainte de Editează
```python
if not perm_manager.check_user_institution_permission(user_id, city, inst, 'can_edit'):
    return  # Refuz
edit_employee_in_db(...)
```

### Înainte de Șterge
```python
if not perm_manager.check_user_institution_permission(user_id, city, inst, 'can_delete'):
    return  # Refuz
delete_employee_from_db(...)
```

### Înainte de Reset Punctaj
```python
if not perm_manager.check_user_institution_permission(user_id, city, inst, 'can_delete'):
    return  # Refuz
reset_scores(...)
```

---

## 💾 Salvare Permisiuni (Auto în Admin Panel)

```python
# Manual - dacă vrei să salvezi din cod
permissions = {
    "Blackwater": {
        "Politie": {"can_view": True, "can_edit": True, "can_delete": True},
        "Medical": {"can_view": False, "can_edit": False, "can_delete": False}
    }
}

perm_manager.save_user_institution_permissions(user_id, permissions)
```

---

## 🗂️ Structura Directoare Asteptată

```
d:/punctaj/data/
├── Blackwater/
│   ├── Politie.json
│   ├── Medical.json
│   └── Adminsitratie.json
├── Saint-Denis/
│   ├── Politie.json
│   ├── Armata.json
│   └── Tribunal.json
└── New Hanover/
    └── Sherif.json
```

---

## 🧪 Test Rapid

```python
# 1. Verifică dacă manager e inițializat
perm_manager = InstitutionPermissionManager(supabase_sync, data_dir)

# 2. Vezi instituțiile
institutions_by_city = perm_manager.get_all_institutions_by_city()
print(institutions_by_city)

# 3. Verifică permisiuni unui user
perms = perm_manager.get_user_institution_permissions("123456")
print(perms)

# 4. Verifică o permisiune specifică
result = perm_manager.check_user_institution_permission("123456", "Blackwater", "Politie", "can_edit")
print(f"Can edit? {result}")
```

---

## ⚠️ Debugging

### Afișează permisiunile unui user
```python
perms = perm_manager.get_user_institution_permissions(user_id)
print(f"Permisiuni {user_id}: {json.dumps(perms, indent=2)}")
```

### Verifică instituțiile disponibile
```python
institutions = perm_manager.get_all_institutions_by_city()
print(f"Instituții disponibile: {institutions}")
```

### Simulează verificare
```python
can_view = perm_manager.check_user_institution_permission(user_id, "Blackwater", "Politie", "can_view")
print(f"Blackwater/Politie - can_view: {can_view}")
```

---

## 🔒 Siguranta

✅ **TREBUIE să faci verificarea și pe server (în SQL) prin RLS policies**  
✅ **TREBUIE să faci verificarea și pe client (în Python)**  
❌ **NU TE BAZA DOAR pe UI (oricine poate dezactiva butoane)**

---

## 📝 Checklist Integrare

- [ ] SQL: Rulează ALTER TABLE pentru granular_permissions
- [ ] Python: Import InstitutionPermissionManager
- [ ] Python: Init manager cu supabase_sync și data_dir
- [ ] Cod: Adaugă verificări înainte de fiecare acțiune (add/edit/delete)
- [ ] UI: Control butoane pe bază de permisiuni
- [ ] Test: Testează cu mai mulți utilizatori cu permisiuni diferite
- [ ] Admin: Setează permisiunile în panelul admin

---

## 🎓 Exemplu Complet - Adaugă Angajat

```python
def add_employee_handler(city, institution, name, position, salary):
    """Adaugă angajat cu verificare permisiuni"""
    
    # 1. Verificare permisiuni
    if not perm_manager.check_user_institution_permission(
        current_user_id, city, institution, 'can_edit'
    ):
        messagebox.showerror("Eroare", "❌ Nu ai permisiuni pentru această acțiune!")
        action_logger.log_event(
            user_id=current_user_id,
            action="add_employee_denied",
            details=f"Acces refuzat pentru {city}/{institution}"
        )
        return False
    
    # 2. Adaugă în baza de date
    try:
        result = supabase_sync.add_employee(city, institution, {
            "name": name,
            "position": position,
            "salary": salary
        })
        
        if result:
            messagebox.showinfo("Succes", f"✅ Angajat adăugat!")
            action_logger.log_event(
                user_id=current_user_id,
                action="add_employee_success",
                details=f"{name} la {city}/{institution}"
            )
            return True
    except Exception as e:
        messagebox.showerror("Eroare", f"❌ Eroare: {e}")
        action_logger.log_event(
            user_id=current_user_id,
            action="add_employee_error",
            details=f"Eroare: {str(e)}"
        )
    
    return False
```

---

## 🚨 Probleme Frecvente

### "Nu vede instituțiile"
- Verifică dacă data_dir-ul are structura corectă
- Verifică dacă dosarele cu orașe și JSON-urile sunt în locul corect

### "Permisiunile nu se salvează"
- Verifică dacă coloana granular_permissions există în Supabase
- Verifică API key și URL-ul
- Vezi log-urile în terminal (DEBUG messages)

### "Butoanele sunt întotdeauna active"
- Verifica if check_user_institution_permission returnează valori
- Verifica if permisiunile sunt setate pentru user în Supabase
- Adaugă print() statements pentru debugging

---

## 📚 Resurse

- [Ghid Complet](INSTITUTION_PERMISSIONS_GUIDE.md)
- [Exemplu Integrare](INTEGRATION_EXAMPLE.py)
- [SQL Setup](SETUP_INSTITUTION_PERMISSIONS.sql)
- [Admin Permissions Code](admin_permissions.py)

---

**Ultima actualizare**: February 2026  
**Status**: ✅ Production Ready
