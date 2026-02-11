# ☁️ Cloud Sync Setup Instructions

## Step 1: Creează Tabela SQL în Supabase

1. Deschide Supabase Dashboard: https://supabase.com/dashboard/
2. Selectează projectul: **yzlkgifumrwqlfgimcai**
3. Mergi la **SQL Editor**
4. Click **+ New Query**
5. Copiază și rulează codul din `CREATE_SYNC_METADATA_TABLE.sql`:

```sql
-- Paste entire CREATE_SYNC_METADATA_TABLE.sql content here
```

✅ Rezultat așteptat:
```
✓ Created sync_metadata table
✓ Created sync_log table
✓ Created indexes
✓ Inserted global_version row
```

---

## Step 2: Creează 'arhiva' Bucket în Storage

1. Din Supabase Dashboard, mergi la **Storage**
2. Click **Create New Bucket**
3. Nume: `arhiva`
4. Privacy: **Public** (off) - citire require auth
5. Setări Permission:
   - Insert: **ON**
   - Select: **ON** (sau public read pentru download)
   - Update: **ON**
   - Delete: **ON**
6. Click **Create Bucket**

✅ Bucket ar trebui să apară în lista cu alte buckets

---

## Step 3: Verifica Python Requirements

Fișierul `requirements.txt` deja are `supabase>=1.0.0`.

Dacă nu, execută:
```bash
pip install supabase>=1.0.0
```

---

## Step 4: Verifica Fișierele Adăugate

Următoarele fișiere trebuie să existe în `d:\punctaj`:

✅ `cloud_sync_manager.py` - Managerul de sincronizare cloud
✅ `CREATE_SYNC_METADATA_TABLE.sql` - SQL script
✅ `CREATE_WEEKLY_REPORTS_TABLE.sql` - SQL script (din anterior)
✅ `CLOUD_SYNC_IMPLEMENTATION.md` - Documentație

---

## Step 5: Test Polling

### Test Manual:

1. Deschide aplicația:
```bash
cd d:\punctaj
python punctaj.py
```

2. Autentifică-te cu Discord

3. Deschide Terminal 2 și rulează:
```bash
cd d:\punctaj
python -c "
from supabase_sync import SupabaseSync
sync = SupabaseSync('supabase_config.ini')
# Actualizează versiunea
sync.table('sync_metadata').update({
    'version': 2
}).eq('sync_key', 'global_version').execute()
print('Version updated to 2')
"
```

4. **Așteptare:** ~1-2 secunde

5. **Rezultat așteptat în aplicație:**
   - ❌ Fereastra de notificare apare
   - ❌ "🔔 Au apărut modificări în cloud!"
   - ❌ Doar buton "📥 DESCARCĂ SINCRONIZARE" activ
   - ❌ Alte butoane dezactivate

✅ Test Passed dacă notificarea apare la 1-2 secunde!

---

## Step 6: Test Force Sync Button

1. Deschide aplicația (dacă nu e deschisă)

2. Mergi la **Sync menu** (buton în bara superioara)

3. Caută și click:
   ```
   "⚡ FORȚEAZĂ SINCRONIZARE CLOUD"
   ```

4. Apare dialog de confirmare:
   ```
   "Vei forța o sincronizare completă..."
   ```

5. Click **Yes**

6. Rezultat așteptat:
   - ✅ Info message: "Sincronizare forțată inițiată!"
   - ✅ În ~1-2 secunde, toți utilizatorii conectați vor vedea notificare

---

## Step 7: Test Archive Upload

1. Deschide aplicație

2. Selectează o instituție cu angajați

3. Click **🔴 RESET PUNCTAJ**

4. Confirmare: **Yes**

5. Check Supabase Storage:
   - Dashboard → **Storage**
   - Bucket **arhiva**
   - Ar trebui să vedea folder: `CityName/`
   - În folder, fișier: `InstitutionName_YYYY-MM-DD_HH-MM-SS.json`

✅ Test Passed dacă JSON apare în Storage!

---

## Step 8: Test Download Changes

1. Deschide Supabase Dashboard

2. SQL Editor → New Query

3. Rulează:
```sql
UPDATE sync_metadata 
SET version = version + 1 
WHERE sync_key = 'global_version';
```

4. În aplicație, **așteptă ~1 secund**

5. Ar trebui să apară fereastra de notificare

6. Click **📥 DESCARCĂ SINCRONIZARE**

7. Progres: "Descarcă datele de orașe și instituții..."

8. Rezultat așteptat:
   - ✅ Progres se deplasează
   - ✅ După ~5-10 secunde: "✅ Cloud download completed successfully"
   - ✅ Fereastra se închide
   - ✅ UI se deblochează
   - ✅ Datele se reîncarcă

✅ Test Passed dacă descărcarea se finalizează!

---

## Verificare Completare

### Checklist Final:

- [ ] SQL table `sync_metadata` creată
- [ ] SQL table `sync_log` creată
- [ ] Storage bucket `arhiva` creat
- [ ] `cloud_sync_manager.py` copiată în d:\punctaj
- [ ] `requirements.txt` are `supabase>=1.0.0`
- [ ] Polling detectează versiuni noi
- [ ] Buton "⚡ FORȚEAZĂ SINCRONIZARE" apare în Sync menu
- [ ] Notificare apare la 1-2 secunde după versiune updată
- [ ] Archive JSON se salvează în Storage la reset
- [ ] Download button deblochează UI după descărcare

---

## Troubleshooting

### Polling nu detectează schimbări

**Verificare:**
```python
# În terminal:
import threading
print(f"Active threads: {threading.enumerate()}")

# Caută "CloudSyncManager" thread
```

**Soluție:**
- Verifica dacă `initialize_cloud_sync()` se apelează în `punctaj.py`
- Verifica dacă `CLOUD_SYNC_AVAILABLE = True`

---

### Butoane nu se deblochează

**Verificare:**
```python
# În debug:
print(f"ui_locked = {ui_locked}")
print(f"CLOUD_SYNC = {CLOUD_SYNC}")
```

**Soluție:**
- Verifica dacă `enable_all_ui()` se apelează după download
- Verifica dacă exception nu se blocheaza

---

### Archive nu apare în Storage

**Verificare:**
```
Storage → arhiva bucket → List files
```

**Soluție:**
- Verifica bucket permissions (INSERT ON)
- Verifica Supabase storage configuration în `supabase_sync.py`
- Check console pentru error messages

---

## Status

**Implementare:** ✅ Complete
**Testing:** ⏳ În Progress

**Data Completare:** 1 februarie 2026
