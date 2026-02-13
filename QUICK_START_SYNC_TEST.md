# 🚀 Quick Start: Test Your Bidirectional Sync

## Get Started in 5 Minutes

### Prerequisites (Do This First)
```bash
# Make sure tables exist
python initialize_supabase_tables.py

# If you're not using a production DB, disable RLS
python disable_rls_for_testing.py

# Start the app
python punctaj.py
```

---

## The 5 Tests

### Test 1: Add City ✅
```
1. Click: ➕ Adaugă oraș (Add City)
2. Enter: TestCity1
3. Check console for: ✓ Orașul sincronizat... (ID: XX)
```
**Expected:** City appears in Supabase within 2-5 seconds

---

### Test 2: Add Institution ✅
```
1. Select TestCity1
2. Click: ➕ Adaugă instituție
3. Enter: TestInst1
4. Setup ranks and click: ✓ Creează tabel
```
**Expected:** See in console:
```
✓ Instituție 'TestInst1' sincronizată cu Supabase
✅ Institution data synced to Supabase: TestCity1/TestInst1
```

---

### Test 3: Add Employee ✅
```
1. Select TestInst1 tab
2. Click: ➕ Adaugă angajat
3. Fill details: Name, Rank, Points
4. Click: ✓ Salvează
```
**Expected:** See in console:
```
✓ Employee synced to Supabase: [Name]
✅ Institution data synced to Supabase: TestCity1/TestInst1
```

---

### Test 4: Delete Employee ✅
```
1. Click: 🗑️ Șterge angajat
2. Select employee
3. Click: 🗑️ ȘTERGE
```
**Expected:** See in console:
```
✓ Employee deleted from Supabase (ID: XX)
```

---

### Test 5: Delete Institution ✅
```
1. Right-click institution tab
2. Select "Șterge instituție"
3. Click: 🗑️ ȘTERGE INSTITUȚII
```
**Expected:** See in console:
```
✓ Institution deleted from Supabase (ID: XX)
✅ Institution synced to Supabase: TestCity1/TestInst1
```

---

### Test 6: Delete City ✅
```
1. Click city tab dropdown
2. Select "Șterge oraș"
3. Click: 🗑️ ȘTERGE
```
**Expected:** See in console:
```
✓ City deleted from Supabase (ID: XX)
✅ City synced to Supabase: TestCity1
```

---

## Verification

### In Supabase Dashboard
After each test, check these tables:

| Test | Table | Should See |
|------|-------|-----------|
| Add City | cities | New row: TestCity1 |
| Add Institution | institutions | New row linked to TestCity1 |
| Add Employee | employees | New row linked to TestInst1 |
| Delete Employee | employees | Row GONE |
| Delete Institution | institutions | Row GONE |
| Delete City | cities | Row GONE |

---

## Console Output Reference

### ✅ Success Messages
```
✓ Város sincronizat cu Supabase (ID: 123)
✓ Employee synced to Supabase: John Doe
✓ Institution deleted from Supabase (ID: 456)
✓ City deleted from Supabase (ID: 789)
✅ Institution data synced to Supabase: TestCity/TestInst
✅ City synced to Supabase: TestCity
```

### ⚠️ Warning Messages (Still Works)
```
⚠️ Oraș creat local, dar nu s-a putut sincroniza
⚠️ Could not retrieve city ID from Supabase
```

### ❌ Error Messages (Check These)
```
❌ Error deleting institution
❌ Error deleting city
```

---

## What's New? 🎉

✅ **Cities now sync immediately** when created (was waiting for first institution)
✅ **Cities auto-delete from cloud** when deleted locally
✅ **Institutions auto-delete from cloud** when deleted locally
✅ **All operations logged** to console
✅ **Cascade delete** (deleting city removes all institutions & employees)

---

## Troubleshooting

### "No sync messages in console?"
1. Check if Supabase URL is correct in `supabase_config.ini`
2. Run: `python check_supabase_connection.py`
3. Check if RLS is blocking: `python check_rls_status.py`

### "Deleted locally but still in Supabase?"
1. Check RLS: `python check_rls_status.py`
2. Run: `python disable_rls_for_testing.py`
3. Restart app: `python punctaj.py`

### "Sync messages but data doesn't appear?"
1. Refresh Supabase Dashboard (browser)
2. Check if tables exist: `python check_all_tables_sync.py`
3. Run: `python initialize_supabase_tables.py` if tables missing

---

## Files Modified

- **supabase_employee_manager.py**: Added `delete_institution()` and `delete_city()` methods
- **punctaj.py**: Enhanced `add_tab()`, `delete_city()`, `delete_institution()` with auto-sync

---

## Timeline for Each Operation

| Operation | Time |
|-----------|------|
| Add City | ~800ms |
| Add Institution | ~1-2s |
| Add Employee | ~1s |
| Delete Employee | ~500ms |
| Delete Institution | ~900ms |
| Delete City | ~800ms |

---

## Full Documentation

For detailed info, see:
- `SYNC_IMPLEMENTATION_SUMMARY.md` - Complete overview
- `BEFORE_AFTER_COMPARISON.md` - Code changes explained
- `BIDIRECTIONAL_SYNC_COMPLETE.md` - Testing guide & architecture

---

## Ready? 🚀

1. ✅ Code changes: DONE
2. Run: `python initialize_supabase_tables.py`
3. Run: `python disable_rls_for_testing.py` (if needed)
4. Run: `python punctaj.py`
5. Follow the 5 tests above
6. Check console logs and Supabase Dashboard

**Status: Ready for Testing!** ✅
