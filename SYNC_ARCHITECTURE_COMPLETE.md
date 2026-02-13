# 🏗️ SUPABASE SYNC ARCHITECTURE

## 📊 The 5 Tables and What They Store

| Table ID | Table Name | Purpose | What Gets Synced |
|----------|-----------|---------|------------------|
| 21071 | `police_data` | **Main City/Institution Data** | All institution employees as JSON |
| 17550 | `users` | User accounts & permissions | User Discord info + role/permissions |
| 21102 | `employees` | Individual employees | Each employee record |
| 21084 | `institutions` | Individual institutions | Institution details |
| 22330 | `weekly_reports` | Weekly scoring reports | Weekly report data |

---

## 🔄 CURRENT SYNC FLOW (How Data Actually Moves)

### When User Adds/Edits/Deletes Employee:

```
1. Save Locally (JSON File)
   ↓
2. supabase_upload() function called
   ├─ Attempts Employee Manager Sync
   │  ├─ Find city by name
   │  ├─ Find institution by city
   │  ├─ For each employee:
   │  │  ├─ Format employee for Supabase
   │  │  ├─ Check if employee exists
   │  │  └─ POST/PATCH to /rest/v1/employees
   │  │     → Goes to TABLE 21102 (employees)
   │  └─ Result: ✅ Employee synced individually
   │
   └─ Attempts Institution Manager Sync
      ├─ Format entire institution as JSON
      ├─ Check if police_data record exists
      └─ POST/PATCH to /rest/v1/police_data
         → Goes to TABLE 21071 (police_data)
         → Result: ✅ Institution JSON synced
```

### Result After Save:
- ✅ Individual employee(s) synced to `employees` table (21102)
- ✅ Institution JSON synced to `police_data` table (21071)
- ❓ `institutions` table (21084) - NOT updated individually
- ❓ `weekly_reports` table (22330) - NOT synced
- ❓ `users` table (17550) - Updated manually on login only

---

## ⚠️ Known Limitations

### 1. **RLS (Row Level Security) Blocking**
If RLS is enabled on ANY table:
- ❌ INSERT to `employees` fails
- ❌ INSERT to `police_data` fails
- ❌ UPDATE operations fail

**Solution:** Disable RLS for testing
```bash
python disable_rls_for_testing.py
```

### 2. **Permission Check Blocking** (FIXED in v2)
Old code would block sync if user permissions weren't set
- ✅ NOW: Fail-safe mode allows sync if permissions unknown

### 3. **Individual Institution Table Not Synced**
- Current: Only institution JSON goes to `police_data`
- Missing: No individual records in `institutions` table

### 4. **Weekly Reports Not Auto-Synced**
- Current: No automatic sync to `weekly_reports` table
- Manual: Must be uploaded separately

---

## 🔍 How to Debug

### 1. Check What's Actually Synced
```bash
python check_all_tables_sync.py
```

This will show:
- ✅/❌ Status for each table
- 📊 Sample records from each table
- 📈 What's working and what's not

### 2. Check Specific Sync Operation
```bash
python debug_sync_connection.py
```

Tests:
- ✅ Connection to Supabase
- ✅ Can INSERT to `police_data`
- ✅ Can INSERT to `employees`
- ✅ All required tables exist

### 3. Compare Local vs Cloud
```bash
python test_sync_flow.py
```

Shows:
- Local institutions and employees
- Cloud institutions and employees
- Differences (what's missing where)

---

## ✅ Verification Checklist

After you make a change in the app:

- [ ] 1. Make a change (add employee, save)
- [ ] 2. Run `python check_all_tables_sync.py`
- [ ] 3. Check that `employees` table has new record
- [ ] 4. Check that `police_data` has updated JSON

Expected:
```
✅ police_data has X rows
✅ employees has Y rows
✅ New employee appears in both tables
```

---

## 🚨 If Data NOT Syncing

### Diagnosis Order:
1. **First:** Disable RLS
   ```bash
   python disable_rls_for_testing.py
   ```

2. **Then:** Verify connection
   ```bash
   python debug_sync_connection.py
   ```

3. **Then:** Check all tables
   ```bash
   python check_all_tables_sync.py
   ```

4. **Finally:** Make a test change and verify

### Common Issues:

| Symptom | Cause | Fix |
|---------|-------|-----|
| No rows in any table | RLS blocking all | Run disable_rls_for_testing.py |
| employees empty but police_data has data | Employee manager disabled | Check SUPABASE_EMPLOYEE_MANAGER_AVAILABLE |
| Both tables empty | Connection error | Run debug_sync_connection.py |
| Data 10+ seconds late | Network slow or polling interval | Check sync_interval in config |

---

## 🔧 Configuration

In `supabase_config.ini`:

```ini
[supabase]
url = https://yzlkgifumrwqlfgimcai.supabase.co
key = sb_publishable_...
table_sync = police_data          # Where institution JSON goes
table_logs = audit_logs            # Where action logs go
table_users = users                # User permissions table

[sync]
enabled = true
auto_sync = true
sync_interval = 30                 # Seconds between syncs
```

---

## 📈 Expected Behavior After Fixes

### ✅ Works:
- Add employee → Syncs to `employees` immediately
- Delete employee → Deletes from `employees` immediately
- Edit employee → Updates in `employees` immediately
- Save institution → Syncs JSON to `police_data` immediately

### ⏳ Not Yet Implemented:
- Sync individual records to `institutions` table
- Sync weekly reports to `weekly_reports` table
- Sync users to `users` table

---

## 🔐 Permission System

User permissions checked in this order:
1. **Superuser?** → Allow all sync
2. **Admin?** → Allow all sync
3. **Can edit institution?** → Allow if yes
4. **Unknown?** → Allow anyway (fail-safe mode)

Changes made in v2:
- ✅ Changed from BLOCKING to FAIL-SAFE
- ✅ Allows sync even if permissions uncertai

---

## Last Updated
February 13, 2026 - Complete sync architecture documented

**Version:** 2.0 (Fail-safe mode active)
