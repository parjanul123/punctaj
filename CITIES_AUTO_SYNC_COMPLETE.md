# 🌐 NEW CITIES AUTO-SYNC TO SUPABASE

## ✅ What Was Fixed

When you add a new city folder to `data/`, it now automatically:
1. **Detects** all cities in the local `data/` folder
2. **Creates** them in Supabase `cities` table (if not there)
3. **Creates** institutions in Supabase `institutions` table (if not there)
4. **Syncs** institution data to `police_data` table

## 🔄 How It Works

### Automatic (at app startup):
1. You restart `punctaj.py`
2. Discord login happens
3. **NEW**: Automatically syncs all cities & institutions to Supabase
4. Displays cities in the app UI

### Manual (if needed):
```bash
python sync_all_cities_institutions.py
```

---

## 📍 What Gets Synced

| Local | → | Supabase Table | Purpose |
|-------|---|---|---|
| `data/BlackWater/` | → | `cities` | City name |
| `data/BlackWater/Police.json` | → | `institutions` | Institution name |
| Institution JSON content | → | `police_data` | Full institution data as JSON |

---

## 🔧 Code Changes

### In punctaj.py:

**1. Added new function** `sync_all_local_cities_to_supabase()` (lines ~625-705)
   - Scans `data/` folder for all cities
   - Creates missing cities in Supabase `cities` table
   - Creates missing institutions in Supabase `institutions` table
   - Syncs institution JSON to `police_data` table

**2. Integrated into startup flow** (line ~2113)
   - Called automatically after Discord login
   - Syncs before UI tables are loaded
   - Runs in background without blocking UI

### Files Created:

**sync_all_cities_institutions.py** (standalone script)
   - Can be run manually anytime
   - Shows detailed sync progress
   - Creates missing cities/institutions

---

## ✨ Usage

### Scenario 1: New city added locally
```
Local data/:
  ✓ existed: BlackWater, Saint_Denis, Valentine
  ✓ NEW: Fort_Worth

1. Restart app
2. Authenticate Discord
3. App automatically:
   - Detects Fort_Worth
   - Creates "Fort_Worth" in Supabase cities table
   - Syncs all Fort_Worth institutions
4. Done! Check Supabase
```

### Scenario 2: Sync stuck or needs manual fix
```bash
python sync_all_cities_institutions.py
```

Output:
```
📍 Cities created: 1
🏢 Institutions created: 5
✅ Sync completed!
```

---

## 🔍 Verification

### Check if synced:
1. **In app**: New city should appear as a tab
2. **In Supabase**: Check these tables:
   - https://supabase.com/dashboard/.../project/.../cities
   - https://supabase.com/dashboard/.../project/.../institutions
   - https://supabase.com/dashboard/.../project/.../police_data

### Expected result:
```
✅ New city appears in cities table
✅ Institutions appear in institutions table
✅ Data appears in police_data table
```

---

## ⚡ Features

✅ Automatic sync at startup
✅ Detects new cities from data/ folder
✅ Creates missing cities & institutions
✅ Syncs institution JSON data
✅ Fail-safe (doesn't error if already exists)
✅ Detailed logging of sync progress
✅ Manual sync script if needed

---

## 🚀 Technical Details

**When it runs:**
- After Discord authentication
- Before UI tables are loaded
- Non-blocking (background)

**What it checks:**
- City exists in Supabase? If not, create
- Institution exists? If not, create
- Institution JSON? If yes, sync to police_data

**Handles:**
- RLS restrictions (via fail-safe sync)
- Missing Supabase managers
- File read errors
- Permission checks

---

## ✅ Status

**Implemented:** February 13, 2026

**Changes to punctaj.py:**
- Line ~2113: Added sync call to startup flow
- Lines ~625-705: Added `sync_all_local_cities_to_supabase()` function

**Files Added:**
- sync_all_cities_institutions.py

**Testing:** Ready to test!
