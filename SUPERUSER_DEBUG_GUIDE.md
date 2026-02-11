# Superuser Authentication Debug Guide

## Overview

The EXE has been rebuilt with **file-based logging** to help diagnose why superuser status is not being applied despite correct data in Supabase.

## What Changed

All authentication logging in `discord_auth.py` now writes to a **persistent log file** in addition to console output. This ensures we can see the entire authentication flow even if the console window closes.

### File Logging Function

A new `_log_auth_debug()` function was added that:
1. Prints to console (visible while app is running)
2. Writes to file: `~/Documents/PunctajManager/discord_auth_debug.log`
3. Includes timestamps for each log entry

### Enhanced Logging in `_fetch_user_role_from_supabase()`

The most critical authentication method now logs:
- When the method is called
- The user ID being processed  
- Whether Supabase object exists
- **RAW values from Supabase** (is_superuser, is_admin, types)
- **Converted values** (after boolean conversion, with types)
- **Final role being set** (SUPERUSER, ADMIN, USER, VIEWER)
- Any errors during the process

## How to Test

### Step 1: Clear Old Logs

```bash
Remove-Item "$env:USERPROFILE\Documents\PunctajManager\discord_auth_debug.log" -ErrorAction SilentlyContinue
```

### Step 2: Run the Application

1. Launch the updated `punctaj.exe` from `d:\punctaj\dist\`
2. Go through the Discord OAuth2 login
3. Wait for the app to fully load
4. Close the application

### Step 3: Check the Log File

Open the log file with:

```bash
notepad "$env:USERPROFILE\Documents\PunctajManager\discord_auth_debug.log"
```

Or search the file:

```bash
Get-Content "$env:USERPROFILE\Documents\PunctajManager\discord_auth_debug.log" | Select-String "SUPERUSER|is_superuser"
```

## What to Look For

### Expected Log Output for Superuser

```
[2025-01-XX HH:MM:SS.mmm] [DEBUG] _fetch_user_role_from_supabase called with user_id=703316932232872016, supabase=<object>
[2025-01-XX HH:MM:SS.mmm] [DEBUG] Supabase object exists, URL=https://your-project.supabase.co
[2025-01-XX HH:MM:SS.mmm] [DEBUG] Requesting: https://your-project.supabase.co/rest/v1/discord_users?discord_id=eq.703316932232872016&select=...
[2025-01-XX HH:MM:SS.mmm] [DEBUG] Response status: 200
[2025-01-XX HH:MM:SS.mmm] [DEBUG] Response data: [{'discord_id': '703316932232872016', 'username': 'parjanu', 'is_superuser': True, 'is_admin': True, ...}]
[2025-01-XX HH:MM:SS.mmm] [DEBUG] Raw data from Supabase: is_superuser=True (type=bool), is_admin=True (type=bool)
[2025-01-XX HH:MM:SS.mmm] [DEBUG] Converted: self._is_superuser=True (type=bool), self._is_admin=True (type=bool)
[2025-01-XX HH:MM:SS.mmm] 👑 User role: SUPERUSER
```

### If There's an Issue

Look for:
- ❌ `[DEBUG] Supabase object is None/invalid`
- ❌ `[DEBUG] Response status: 404` or `401` or `500`
- ❌ `[DEBUG] No data returned from API`
- ❌ `[DEBUG] Request error: ...`
- ❌ Value conversion failures

## Critical Log Points

### 1. Method Called
```
[DEBUG] _fetch_user_role_from_supabase called with user_id=XXX
```
**If missing**: Method not being called during login

### 2. Supabase Configuration
```
[DEBUG] Supabase object exists, URL=...
```
**If says None/invalid**: Supabase config not found

### 3. API Response
```
[DEBUG] Response status: 200
```
**If not 200**: Check error code
- 401: Authentication failed
- 404: User not found
- 500: Server error

### 4. Raw Data Received
```
[DEBUG] Response data: [{'is_superuser': True, 'is_admin': True, ...}]
```
**If is_superuser=False**: Host not marked as superuser in Supabase

### 5. Conversion Result
```
[DEBUG] Converted: self._is_superuser=True (type=bool)
```
**If =False**: Conversion logic issue

### 6. Role Assignment
```
👑 User role: SUPERUSER
```
**If shows ADMIN or USER or VIEWER**: Role assignment conditional failed

## Troubleshooting Paths

### Path A: No Log File Created
- Log file path: `C:\Users\{YourUsername}\Documents\PunctajManager\discord_auth_debug.log`
- The directory might not exist yet - app should create it
- Check permissions on Documents folder

### Path B: Method Not Called
- Method only called during login (in `_fetch_user_info()`)
- Check if you're doing fresh login each time
- Verify you're logging out first, then back in

### Path C: Supabase Connection Fails
- Check supabase_config.ini exists in app directory
- Verify API key has correct permissions
- Check network connectivity

### Path D: is_superuser=False in Response
- Host not marked as superuser in Supabase database
- Need to check `discord_users` table directly:
  ```sql
  SELECT username, is_superuser, is_admin FROM discord_users WHERE discord_id = '703316932232872016'
  ```

## Next Steps After Identifying Issue

Once you have the log file:

1. **Share the log content** with detailed description of what you see
2. **Include Supabase status**: 
   - Is host marked as superuser in Supabase?
   - What do you see in the `discord_users` table?
3. **Describe behavior**:
   - Are admin buttons showing?
   - Does permissions panel open?
   - What role is displayed?

## Log File Locations

- **Main log**: `C:\Users\{YourUsername}\Documents\PunctajManager\discord_auth_debug.log`
- **.ini config**: Should be in same folder or EXE directory
- **Supabase logs**: Available in Supabase dashboard for API requests

## Important Notes

- Log file **appends** to existing file (doesn't overwrite)
- To start fresh: Delete the log file before testing
- Run `refresh_admin_buttons()` debug output shows: `_is_superuser={value}` - this should be `True`
- If role is set in logs but buttons don't show, issue is in UI, not authentication

---

**Created**: January 2025
**Purpose**: Diagnose superuser role assignment failure despite correct Supabase data
**File with changes**: `discord_auth.py` (all 4 versions)
