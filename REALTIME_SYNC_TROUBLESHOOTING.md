# 🔴 REAL-TIME SYNC NOT WORKING - DIAGNOSTIC GUIDE

## ❌ Problema

Modificări în app (add/edit/delete) **NU se sincronizează** la Supabase în timp real:
- ❌ Adaug angajat → Nu apare în Supabase `employees` table
- ❌ Editez instituție → Nu se actualizează în `police_data`
- ❌ Șterg angajat → Nu se șterge din Supabase

---

## 🔍 Cauze Posibile

### 1. **RLS (Row Level Security) Blocheaza INSERT/UPDATE**
- Symptom: "HTTP 403 Forbidden" în console
- Fix: Disable RLS pentru testing

### 2. **WebSocket Token Expired (JWT 401)**
- Symptom: "WebSocket connection error: HTTP 401"
- Fix: Restart app pentru refresh token

### 3. **police_data Table Missing**
- Symptom: "HTTP 404" la sync
- Fix: Create table cu `initialize_supabase_tables.py`

### 4. **sync_data() Function Not Called**
- Symptom: No sync messages în console
- Fix: Verifica log messages "SUPABASE_UPLOAD"

### 5. **Permission Check Blocking Sync**
- Symptom: "Permission check error" messages
- Fix: User needs `can_edit` permission (superuser bypass)

---

## 🔧 QUICK FIX (3 Steps)

### Step 1: Run Complete Diagnostic
```bash
python FIX_REALTIME_SYNC_COMPLETE.py
```

Aceasta va:
- ✅ Verifica RLS status
- ✅ Dezactiveaza RLS dacă e necesar
- ✅ Verifica toate tabelele
- ✅ Testa sincronizarea

### Step 2: Restart App
```bash
python punctaj.py
```

### Step 3: Test Sync
1. Adauga un angajat nou
2. Salveaza
3. Check Supabase table `employees` - trebuie să apară acolo

---

## 📊 DETAILED DIAGNOSTIC FLOW

```
1. diagnose_realtime_sync.py
   ├─ Check police_data table exists
   ├─ Test RLS permissions (try INSERT)
   ├─ Check employees table
   ├─ Test manual sync with real data
   └─ Report findings

2. check_rls_status.py
   ├─ Verifica fiecare tabel
   ├─ Verifica SELECT/INSERT/UPDATE permissions
   └─ Identifica care tabele are RLS ENABLED

3. disable_rls_for_testing.py
   ├─ Dezactiveaza RLS pe police_data
   ├─ Dezactiveaza RLS pe employees
   └─ Permite sync să meargă

4. check_all_tables_sync.py
   ├─ Verifica ce date sunt în fiecare tabel
   ├─ Compara local vs cloud
   └─ Identifica gaps

5. monitor_realtime_sync.py
   ├─ Monitorizeaza police_data count
   ├─ Monitorizeaza employees count
   └─ Arata update-uri în timp real
```

---

## 📈 EXPECTED BEHAVIOR (après fix)

### Scenario: Add New Employee

```
1. Open app
2. Click "Adaugă angajat"
3. Enter data → Click Save
4. Console shows:
   📡 SUPABASE_UPLOAD: Starting for City/Institution
   ✅ Synced 1/1 employees
   ✅ Institution data synced

5. Supabase `employees` table appears immediately with new record
6. Supabase `police_data` updated with new employee data
```

### Timing
- **Local save**: ~0.1 seconds
- **Upload to Supabase**: ~1-2 seconds
- **Appears in dashboard**: ~0.5-1 second
- **Total**: 1.5-3 seconds

---

## 🔴 IF STILL NOT SYNCING

### 1. Check Console Output
Restart app and watch terminal for:

**Good signs:**
```
📡 SUPABASE_UPLOAD: Starting for BlackWater/Politie
   📊 Data: 5 rows, city_id=1, institution_id=2
   ✅ Synced 5/5 employees
   ✅ Institution data synced
```

**Bad signs:**
```
❌ SUPABASE_UPLOAD ERROR: [error message]
⚠️  sync_data returned False
❌ WebSocket connection error: HTTP 401
```

### 2. Check RLS Manually
1. Supabase Dashboard
2. Click Table → Select `employees`
3. Look for "RLS" button
   - 🟢 GREEN = RLS DISABLED (good)
   - 🔴 RED = RLS ENABLED (bad)

### 3. Check API Key
1. Supabase Dashboard → Project Settings → API
2. Copy `anon` / `public` key
3. Update `supabase_config.ini` key = [paste here]
4. Restart app

### 4. Manual Test Sync
```bash
python sync_all_cities_institutions.py
```

Should output:
```
✅ City created/exists
✅ Institution created/exists
✅ Synced to police_data
```

### 5. Check Supabase Permissions
1. Settings → Role Based Access Control (RBAC)
2. Verify `username` user has INSERT/UPDATE permissions
3. Or ensure policy allows your API key

---

## 📋 TROUBLESHOOTING TABLE

| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 Forbidden | RLS blocking | `python disable_rls_for_testing.py` |
| 404 Not Found | Table missing | `python initialize_supabase_tables.py` |
| 401 Unauthorized | JWT expired | Restart app: `python punctaj.py` |
| No sync messages | sync_data() not called | Check console for errors |
| WebSocket 401 | Token invalid | Check API key validity |
| Sync works local but not cloud | Network blocked | Check firewall/VPN |

---

## 📝 TECHNICAL DETAILS

### Sync Flow in Code

```python
# In punctaj.py - when user saves employee:

def save_institution(city, institution, tree):
    # Step 1: Save to local JSON
    with open(institution_path, 'w') as f:
        json.dump(data, f)
    
    # Step 2: Call supabase_upload()
    result = supabase_upload(city, institution, data)
    
    # Step 3: Inside supabase_upload():
    # 3a. Sync individual employees to `employees` table
    for emp in data['rows']:
        SUPABASE_EMPLOYEE_MANAGER.add_employee(inst_id, emp)
        # POST /rest/v1/employees
    
    # 3b. Sync institution JSON to `police_data` table
    SUPABASE_SYNC.sync_data(city, institution, data)
    # POST/PATCH /rest/v1/police_data
```

### Multiple Sync Paths

```
Add/Edit/Delete Employee
    ↓
save_institution() called
    ├─ supabase_upload()
    │  ├─ SUPABASE_EMPLOYEE_MANAGER.add_employee()
    │  │  → POST /rest/v1/employees
    │  │
    │  └─ SUPABASE_SYNC.sync_data()
    │     → POST/PATCH /rest/v1/police_data
    │
    └─ Success if BOTH succeed
```

---

## ✅ VERIFICATION CHECKLIST

After running fixes:

- [ ] Run `python FIX_REALTIME_SYNC_COMPLETE.py`
- [ ] All diagnostics passed
- [ ] RLS disabled for testing
- [ ] App restarted
- [ ] Made test change in app
- [ ] Checked Supabase table immediately
- [ ] Record appeared within 3 seconds
- [ ] Console shows "SUPABASE_UPLOAD" messages
- [ ] No errors in console

If all ✅:
**Real-time sync is working!**

---

## 🎯 NEXT: Test Other Scenarios

Once working, test:

1. **Add employee** → Should appear in `employees` table
2. **Edit employee** → Should UPDATE in `employees` table
3. **Delete employee** → Should DELETE from `employees` table
4. **Add institution** → Should appear in `institutions` table
5. **Add city** → Should appear in `cities` table

All should sync within 2-5 seconds.

---

## 📞 IF STILL STUCK

1. Share console output from `python FIX_REALTIME_SYNC_COMPLETE.py`
2. Share Supabase RLS settings for `employees` and `police_data` tables
3. Share API key settings
4. Run `python debug_sync_connection.py` and share output

---

**Last Updated:** February 13, 2026
**Status:** Diagnostic tools created and ready to use
