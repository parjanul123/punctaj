# 🧪 TESTING AUTO-REGISTRATION

## Test Setup

**Prerequisite:**
- Supabase project configured
- `discord_users` table exists
- Internet connection working

## Test Case 1: New User Registration

### Steps:
1. **Open Application**
   - Start app fresh
   - No one logged in yet

2. **Click "Login cu Discord"**
   - Click login button
   - Browser opens Discord auth

3. **Authorize App**
   - Aproba permisiunile
   - Complete login flow

4. **Verify Console Output**
   - ✅ Should see: `🔍 Checking if Discord user exists`
   - ✅ Should see: `➕ User NOT found in Supabase - creating new account`
   - ✅ Should see: `✅ NEW USER CREATED IN SUPABASE`
   - ✅ Should see: `Initial Permissions: NONE (role: VIEWER)`

5. **Verify in Supabase**
   - Open Supabase dashboard
   - Go to `discord_users` table
   - Check: New row created with your Discord ID
   - Check: `discord_username` = your Discord username
   - Check: `is_superuser` = FALSE
   - Check: `is_admin` = FALSE
   - Check: `can_view` = FALSE

6. **Check Application Role**
   - In app sidebar, check your role
   - Should show: 👁️ **VIEWER** (read-only)

### Expected Result:
✅ **PASS** - User created automatically in Supabase

---

## Test Case 2: Existing User Login (Repeat)

### Steps:
1. **Close Application**
   - Exit the app completely

2. **Reopen Application**
   - Start app again

3. **Click "Login cu Discord"**
   - Same user (same Discord account)

4. **Verify Console Output**
   - ✅ Should see: `✅ User already exists in Supabase`
   - ✅ Should NOT see: `creating new account`
   - ✅ Should see: `✅ User last_login updated in Supabase`
   - ✅ Should see: role: USER (if admin gave you access) or VIEWER

5. **Verify in Supabase**
   - Open Supabase dashboard
   - Check `discord_users` table
   - Check: Only ONE row for your Discord ID (no duplicate!)
   - Check: `last_login` = current time (updated)
   - Check: `active` = TRUE

6. **Check Application**
   - Same permissions as before
   - Application loads normally

### Expected Result:
✅ **PASS** - Existing user updated (not duplicated)

---

## Test Case 3: Permission Assignment (Admin)

### Setup:
- User 1: Regular user (no permissions yet)
- User 2: Admin user

### Steps:

1. **User 1: Login with Discord**
   - New user auto-created
   - Role = VIEWER (no access)

2. **User 2: Login as Admin**
   - Use admin Discord account
   - Has access to Admin Panel

3. **Admin: Open Admin Panel**
   - Click "Admin" button
   - Navigate to "Permissions" tab

4. **Admin: Assign Permissions to User 1**
   - Find User 1 in users list
   - Check: `can_view = TRUE`
   - Check: `can_edit = TRUE`
   - Click "Save"

5. **User 1: Check Sidebar**
   - In next 5 seconds (auto-sync!)
   - Role should change from VIEWER → USER
   - Buttons should become enabled
   - Can now view and edit data

6. **Verify in Supabase**
   - Check `discord_users` for User 1
   - `can_view` = TRUE
   - `can_edit` = TRUE

### Expected Result:
✅ **PASS** - Permissions synced automatically (no restart needed)

---

## Test Case 4: Email Handling

### Scenario: User has email in Discord

### Steps:
1. **Login with Discord account that has email**
   - Should be auto-registered

2. **Check Console**
   - ✅ Should show: `Email: user@example.com`

3. **Verify in Supabase**
   - Check `discord_users`
   - `discord_email` should be populated

### Expected Result:
✅ **PASS** - Email captured correctly

---

## Test Case 5: Email Missing

### Scenario: User has no email in Discord

### Steps:
1. **Login with Discord account without email**
   - Should still register

2. **Check Console**
   - ✅ Should show: `Email: NOT PROVIDED`

3. **Verify in Supabase**
   - Check `discord_users`
   - `discord_email` should be empty string or NULL

### Expected Result:
✅ **PASS** - User created even without email

---

## Test Case 6: Supabase Offline (Error Handling)

### Setup:
- Disable internet or Supabase down

### Steps:
1. **Try to Login**
   - Click login button
   - Supabase is unreachable

2. **Check Console**
   - ✅ Should see: `❌ Connection error to Supabase`
   - ✅ Should see: `Check: Is Supabase online?`

3. **Application Behavior**
   - Should show error message
   - Should allow user to retry

4. **Recovery**
   - Re-enable internet
   - Click retry
   - User should be created normally

### Expected Result:
✅ **PASS** - Graceful error handling with retry

---

## Test Case 7: Timeout Handling

### Setup:
- Supabase very slow (simulate with network throttling)

### Steps:
1. **Try to Login**
   - Click login button
   - Supabase slow to respond

2. **Check Console**
   - ✅ Should see: `⚠️ Supabase timeout while checking user - retrying...`
   - ✅ Should see: `Sleep 1 second`
   - ✅ Should retry automatically
   - ✅ Should eventually succeed

3. **Application Behavior**
   - Should not crash
   - Should complete login eventually

### Expected Result:
✅ **PASS** - Automatic retry on timeout

---

## Test Case 8: Duplicate Prevention

### Scenario: Same user logs in twice simultaneously (edge case)

### Setup:
- Open 2 browser windows
- Same Discord account

### Steps:
1. **Window 1: Click Login**
   - Starting login flow

2. **Window 2: Click Login**
   - Same user, starting login flow

3. **Both: Complete Auth**
   - Both windows complete Discord auth

4. **Check Supabase**
   - ✅ Should have ONLY 1 row for this Discord ID
   - ✅ NOT 2 rows (no duplicate!)
   - ✅ `last_login` = latest time

### Expected Result:
✅ **PASS** - Duplicate prevention works (unique constraint)

---

## Troubleshooting

### User not showing in Supabase:
1. Check console for errors
2. Verify Supabase URL and API key correct
3. Verify `discord_users` table exists
4. Check table permissions in Supabase RLS

### User appears multiple times:
1. This shouldn't happen (unique constraint)
2. If it does: Check table schema - `discord_id` must be UNIQUE

### Permissions not syncing:
1. This is separate (check PERMISSION_SYNC_FIX.md)
2. Verify permission_sync_manager is running

### Supabase always offline:
1. Check internet connection
2. Check Supabase project status
3. Check API key validity

---

## Success Criteria

✅ All 8 test cases PASS
✅ No duplicate users created
✅ Permissions assigned correctly
✅ Auto-sync works within 5 seconds
✅ Error handling is graceful
✅ Retry logic works

**If all pass:** Ready for production! 🚀

---

**Tested:** Feb 3, 2026
**Status:** Ready for QA
