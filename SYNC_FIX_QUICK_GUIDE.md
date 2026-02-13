# ✅ Ghid Rapid: Fixare Sincronizare Supabase

## 🔴 Problema
- Adaugi/ștergător date local, dar nu se actualizează în Supabase
- sau se actualizează cu întârziere

## ✅ Soluție Rapidă (5 minute)

### 1️⃣ Verifica Status Sincronizarii
```bash
cd D:\punctaj
python test_sync_flow.py
```

**Output expected:**
```
✅ Found X records in police_data table
✅ Found X employees
✅ City/Institution - IN SUPABASE
```

**Dacă e gol** → salt la Step 2

### 2️⃣ Reinitializa Tabelele Supabase
```bash
python initialize_supabase_tables.py
```

**Output:**
```
✅ Success (HTTP 200)
```

### 3️⃣ Verifica Conexiunea Supabase
```bash
python debug_sync_connection.py
```

**Trebuie sa vede:**
```
✅ Connected successfully (HTTP 200)
✅ INSERT successful (HTTP 201)
✅ Cities table exists
✅ Employees table exists
```

### 4️⃣ Verifica RLS (Row Level Security)

❌ **RLS ENABLED** (linie roșie) = BLOCAT
✅ **RLS DISABLED** (linie verde) = OK

**Pași:**
1. Deschide https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai
2. Mergi la Database → Tables
3. Selectează tabelul `police_data`
4. Click pe butonul "RLS" din dreapta
   - Dacă e ROȘU → Click pe el ca să-l dezactivezi (turn GREEN)
   - Dacă e VERDE → OK ✅

## 🚀 Test Sincronizare Reală

### Pas 1: Deschide aplicația
```bash
py punctaj.py
```

### Pas 2: Adaugă o instituție nouă
1. Click ➕ Adaugă instituție
2. Introdu: "TEST_SYNC_2026"
3. Click ✓ Creează tabel

### Pas 3: Verifica în Supabase
1. Du-te la Dashboard
2. Click pe `police_data` table
3. Ar trebui să vezi NEW record cu "TEST_SYNC_2026"

**Dacă apare în 5 secunde → ✅ SYNC WORKS**
**Dacă nu apare → ❌ Check console for errors**

## 📊 Debugging

### 1. Vezi Console Output
Cand faci modificari, ar trebui sa vezi:
```
📡 SUPABASE_UPLOAD: Starting for City/Institution
   ✅ Synced X/X employees
   📡 Calling SUPABASE_SYNC.sync_data()...
   ✅ Institution data synced
```

Daca NU vedi asta → supabase_upload() nu se apeleaza

### 2. Verifica Permisiuni

Daca vedi mesaj cum ar fi:
```
🔐 SYNC_DATA: Starting for City/Institution
   ❌ SYNC BLOCKED: No permission
```

**Soluție:** Contact administrator - trebuie setate permisiuni granulare

### 3. Verifica RLS Policies

```sql
SELECT * FROM public.police_data LIMIT 5;
```

Dacă returează 0 rows → probabil RLS e activat incorect

## 🆘 Dacă tot nu merge

1. Deschide **Supabase Dashboard**
2. Mergi la SQL Editor
3. Run:
```sql
-- Disable RLS pentru testing
ALTER TABLE police_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE employees DISABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;
```

4. Cand e gata, restart aplicația
5. Fă din nou modificare si verifica Supabase

## ✅ Mesaje de Succes

Sync lucreaza corect daca vedi:
```
📡 SUPABASE_UPLOAD: Starting...
   ✅ Synced X/X employees
   📡 Calling SUPABASE_SYNC.sync_data()...
   ✅ Institution data synced
```

## 📞 Contacta Admin

Daca problema persista după toti pasii:
1. Salveaza console output (Ctrl+A, copy-paste in document)
2. Run `test_sync_flow.py` si salveaza output
3. Contact: @admin pe Discord cu informatiile acelea

## 🔗 Linkuri Utile

- **Supabase Dashboard:** https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai
- **SQL Editor:** https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/sql
- **police_data table:** https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/editor/21071
- **employees table:** https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/editor/21102
