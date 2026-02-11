# ☁️ Cloud Synchronization Implementation Guide

**Data: 1 februarie 2026**

## Overview

S-a implementat un sistem complet de **sincronizare forțată cu cloud** cu următoarele caracteristici:

### Features Implementate

✅ **Polling Automат (1 secundă)**
- Thread separat care verifică la fiecare 1 secundă dacă s-au schimbat date în cloud
- Detectează versiuni mai noi și hash-uri diferite din Supabase

✅ **Notificare cu Blocare UI**
- Când se detectează modificări în cloud, interfața se blochează
- Doar butonul "📥 DESCARCĂ SINCRONIZARE" rămâne activ
- Celelalte butoane și controale sunt dezactivate

✅ **Download Forțat**
- Descarcă TOATE datele din cloud:
  - Orașe și instituții
  - Angajați și scoruri
  - Toată arhiva JSON din Supabase Storage
- Cu progres real-time

✅ **Upload Arhiva**
- JSON-urile din `arhiva` se salvează automat în Supabase Storage când se resetează punctajul
- Folosește structura: `arhiva/CityName/Institution_YYYY-MM-DD_HH-MM-SS.json`

✅ **Buton Forțare Sincronizare**
- Oricine poate apăsa butonul "⚡ FORȚEAZĂ SINCRONIZARE CLOUD" din Sync menu
- Notifică toți utilizatorii conectați să descarce
- Toți vor fi blocați până descarcă

---

## Fișiere Modificate/Adăugate

### 1. **cloud_sync_manager.py** (NOU)
```python
class CloudSyncManager:
    """Manages 1-second polling and forced synchronization"""
    
    - start_polling(interval=1)  # Inițiază polling automitic
    - download_all_changes()      # Descarcă toate modificările
    - upload_archive_to_storage() # Incarcă arhiva în cloud
    - force_sync_from_cloud()     # Forțează sincronizare
    - log_sync_activity()         # Înregistrează activitatea
```

**Funcții cheie:**
- `_polling_loop()` - Ruleaza continuu în background, verifica daca cloud se updateraza
- `_get_cloud_version()` - Citeste versiunea din Supabase sync_metadata table
- `_download_archive_from_storage()` - Descarca intreg folderul arhiva din cloud storage

### 2. **CREATE_SYNC_METADATA_TABLE.sql** (NOU)
Tabel Supabase pentru tracking versiunilor:

```sql
CREATE TABLE sync_metadata (
    id BIGSERIAL PRIMARY KEY,
    sync_key VARCHAR(255) UNIQUE,  -- 'global_version'
    version BIGINT,                 -- Versiune curenta
    data_hash VARCHAR(64),          -- SHA256 hash pentru detectie schimbari
    last_modified_by VARCHAR(255),
    last_modified_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE sync_log (
    id BIGSERIAL PRIMARY KEY,
    discord_id VARCHAR(50),
    sync_type VARCHAR(50),          -- 'upload', 'download', 'force_sync'
    status VARCHAR(50),             -- 'success', 'failed'
    items_synced INTEGER,
    synced_at TIMESTAMP
);
```

### 3. **punctaj.py** (MODIFICAT)

#### Noi Funcții:
```python
# Linia ~3980
initialize_cloud_sync()           # Inițiază cloud sync la pornire
on_cloud_sync_required()          # Callback când cloud se updateraza
on_sync_start()                   # Callback inceput sync
on_sync_complete()                # Callback sync terminat
on_sync_error()                   # Callback eroare sync
disable_all_ui()                  # Blochează interfața
enable_all_ui()                   # Deblochează interfața
force_cloud_sync_button()         # Handler buton forțare sync

# Modificat: reset_punctaj() - Linia ~2320
# Acum salvează JSON și în Supabase Storage
```

#### Noi Butoane UI:
```python
# Linia ~1600 - În Sync menu
"⚡ FORȚEAZĂ SINCRONIZARE CLOUD" - apelează force_cloud_sync_button()
"📥 DESCARCĂ SINCRONIZARE"       - descarcă din cloud cand se detecta schimbari
```

#### Inițializare (Linia ~4250):
```python
# Pornire la start-up
initialize_cloud_sync()  # Incepe polling la 1 secundă
```

---

## Flux de Funcționare

### Scenario 1: Detectare Schimbări în Cloud

```
1. Cloud Sync Manager polls (1 sec interval)
   ↓
2. Detectează versiune nouă în sync_metadata tabel
   ↓
3. Apelează on_cloud_sync_required() callback
   ↓
4. UI se blochează - disable_all_ui()
   ↓
5. Apare Toplevel window cu notificare
   ↓
6. Doar buton "📥 DESCARCĂ SINCRONIZARE" activ
   ↓
7. Utilizator apasă buton
   ↓
8. download_all_changes() descarcă din cloud
   ↓
9. load_existing_tables() reîncarcă datele
   ↓
10. UI se deblochează - enable_all_ui()
```

### Scenario 2: Admin Forțează Sincronizare

```
1. Admin deschide Sync menu
   ↓
2. Apasă "⚡ FORȚEAZĂ SINCRONIZARE CLOUD"
   ↓
3. force_cloud_sync_button() apelează CLOUD_SYNC.update_cloud_version()
   ↓
4. Versiunea în sync_metadata table se incrementează
   ↓
5. Toți alți utilizatori detectează versiune nouă (la următorul poll la 1 sec)
   ↓
6. Toți primesc notificare și sunt blocați până descarcă
```

### Scenario 3: Reset Punctaj cu Upload Arhiva

```
1. Utilizator apasă "🔴 RESET PUNCTAJ"
   ↓
2. reset_punctaj() salvează JSON local în arhiva/
   ↓
3. CLOUD_SYNC.upload_archive_to_storage() 
   ↓
4. Supabase Storage primește JSON la arhiva/CityName/Institution_YYYY-MM-DD_HH-MM-SS.json
```

---

## Variabile Globale

```python
CLOUD_SYNC = None              # CloudSyncManager instance
sync_notification_window = None # Fereastra notificare
sync_in_progress = False       # Flag pentru sync în curs
ui_locked = False              # Flag pentru UI blocat
```

---

## Constantele

```python
# cloud_sync_manager.py
POLLING_INTERVAL = 1  # secunde (verificare la 1 secunda)
ARCHIVE_BUCKET = 'arhiva'  # Supabase Storage bucket
```

---

## Cerințe

### Python Packages
```
supabase>=1.0.0  # Pentru Storage access
```

### Supabase Setup
```sql
-- 1. Ruleaza CREATE_SYNC_METADATA_TABLE.sql în Supabase SQL Editor
-- 2. Creează bucket 'arhiva' în Supabase Storage
--    Setari: Public read OFF, Allow insert ON, Allow update ON, Allow delete ON
```

---

## Testing

### Test 1: Polling Detection
```python
# În Supabase:
# UPDATE sync_metadata SET version = 2 WHERE sync_key = 'global_version';

# Rezultat: După 1 secund, utilizatorul va vedea notificare și va fi blocat
```

### Test 2: Force Sync Button
```
1. Deschide Sync menu
2. Click "⚡ FORȚEAZĂ SINCRONIZARE CLOUD"
3. Toți utilizatorii ar trebui blocați în ~1 secund
```

### Test 3: Archive Upload
```
1. Click "🔴 RESET PUNCTAJ"
2. Check Supabase Storage → arhiva folder
3. Ar trebui să apară JSON cu timestamp
```

---

## Troubleshooting

### "Cloud sync not available"
```
Verifica:
- CLOUD_SYNC_AVAILABLE = True în imports
- cloud_sync_manager.py este în folder
- SUPABASE_SYNC este initialized
```

### Polling nu detectează schimbări
```
Verifica:
- CLOUD_SYNC.polling_active = True
- sync_metadata tabel în Supabase are versiunea schimbată
- Thread este active
```

### UI nu se blochează
```
Verifica:
- on_cloud_sync_required callback este setată
- disable_all_ui() apelează widget.config(state=DISABLED)
```

### Archive nu se salvează în Storage
```
Verifica:
- arhiva bucket există în Supabase Storage
- Bucket are permisiuni INSERT/UPDATE
- SUPABASE_SYNC.storage este configurată corect
```

---

## Viitori Îmbunătățiri

- [ ] Conflict resolution dacă 2 utilizatori editează simultan
- [ ] Selective sync (doar anumite orașe/instituții)
- [ ] Compression pentru archive mari
- [ ] Delta sync (doar fișierele modificate)
- [ ] Automatic daily backups la miezul nopții
- [ ] Notification sound/bell cand apar modificari
- [ ] Heartbeat check pentru server health

---

## Status

✅ **Implementare Completă**
- [x] Cloud sync manager creat
- [x] SQL tables create
- [x] Polling implementat
- [x] Notificare și blocare UI implementate
- [x] Upload arhiva implementat
- [x] Butoane UI adăugate
- [x] Funcții callback setate

⏳ **Testare Necesară**
- [ ] Test polling cu versiuni noi
- [ ] Test force sync
- [ ] Test archive upload
- [ ] Test UI blocare/delocare

**Data Implementare:** 1 februarie 2026
**Versiune:** 1.0
