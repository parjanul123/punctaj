# 🚀 GETTING STARTED - Primii 15 Minute

Dacă ești pe fugă, urmăreste asta! 15 minute și sistem e testat.

---

## ⏰ Timeline

```
Minutul 0-2:  Citeste asta
Minutul 2-4:  Citeste PERMISSIONS_QUICK_REFERENCE.md
Minutul 4-8:  Rulează SQL în Supabase
Minutul 8-11: Importa în Python
Minutul 11-15: Rulează setup_permissions_tool.py
```

---

## 📋 CHECKLIST RAPID

### ✅ Minute 0-2: TU ESTI AQUI
- [ ] Citesti PERMISSIONS_QUICK_REFERENCE.md DUPA ASTA

### ✅ Minute 2-4: SQL SETUP
```bash
1. Mergi la https://supabase.com/dashboard
2. Project → SQL Editor
3. Copiaza din: d:\punctaj\SETUP_INSTITUTION_PERMISSIONS.sql
4. Paste primele 10 linii (ALTER TABLE + CREATE INDEX)
5. Click RUN
```

### ✅ Minute 4-8: PYTHON SETUP
In `d:\punctaj\punctaj.py` adauga:

```python
# Lin ~80 (dupa ce se importa supabase_sync)
from admin_permissions import InstitutionPermissionManager

# Lin ~150 (dupa ce se inițializează supabase_sync)
inst_perm_manager = InstitutionPermissionManager(
    supabase_sync,
    "d:/punctaj/data"  # SAU o alta cale cu orașe
)
```

### ✅ Minute 8-11: VERIFY SETUP
```bash
cd d:\punctaj
python setup_permissions_tool.py
# Alege opțiunea 1 (Verifică dacă Supabase e configurat)
# Ar trebui sa vizi: ✅ Coloana granular_permissions EXISTĂ
```

### ✅ Minute 11-15: SET TEST PERMISSIONS
```bash
python setup_permissions_tool.py
# Alege opțiunea 2 (Afișează toți utilizatorii)
# Copie un discord_id din lista

# Alege opțiunea 4 (Setează permisiuni de test)
# Paste discord_id-ul
# → Va seta permisiuni de test (Blackwater/Politie acces complet)

# Alege opțiunea 3 (Afișează permisiuni)
# Paste același discord_id
# → Ar trebui sa vizi permisiunile setate
```

---

## 🎁 Cu Asta Termini

✅ Coloana în Supabase creată  
✅ Python manager importat  
✅ Setup tool testat și funcțional  
✅ Test permissions setate  

---

## 🚀 NEXT: IMPLEMENTARE

Acum citeste: **IMPLEMENTATION_GUIDE.md** pentru pasi detaliat

---

## 🆘 RAPID HELP

**Problem**: "Python error when importing"
→ Asigura-te ca ai copiat `admin_permissions.py` corect

**Problem**: "Coloana nu exista"
→ Rulează SQL din SETUP_INSTITUTION_PERMISSIONS.sql

**Problem**: "setup_permissions_tool.py nu merge"
→ Asigura-te ca esti in folder-ul d:\punctaj cu `python setup_permissions_tool.py`

---

## 📞 More Help?

See: **PERMISSIONS_QUICK_REFERENCE.md** (linia de comanda + troubleshooting)

---

**TIme estimated: 15 minutes**  
**Difficulty: Easy ✅**  
**Status: Ready! 🎉**
