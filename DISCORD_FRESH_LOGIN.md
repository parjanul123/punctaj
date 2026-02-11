# 🔐 Discord Fresh Login - Every Session

## Overview

**Discord authentication is NOW required EVERY TIME you start the application.**

- ❌ Token caching is DISABLED
- ✅ Fresh login required each session
- ✅ Always fresh permission verification
- ✅ Maximum security & permission accuracy

---

## What Changed

### Before (Token Cached)
```
Session 1: Login to Discord
Session 2: App reused saved token (no login)
Session 3: App reused saved token (no login)
Session N: Might use outdated permissions
```

### Now (Fresh Login Every Time) ⭐
```
Session 1: Login to Discord → Access
Session 2: Login to Discord again → Access
Session 3: Login to Discord again → Access
Session N: Always fresh login → Always correct permissions
```

---

## Benefits

### ✅ Always Fresh Permissions
- User roles updated immediately
- New role changes take effect instantly
- No stale permission caching

### ✅ Maximum Security
- No token files stored locally
- No token expiry issues
- No token refresh needed
- Complete session isolation

### ✅ Role Changes Instant
```
Scenario: Admin removes user's "admin" role
Before: User still had access until token expired
Now: Next login, user gets "viewer" role immediately
```

### ✅ Audit Trail
- Every session logged with fresh auth
- Clear login/logout boundaries
- Complete session tracking

---

## User Experience

### At Application Startup

```
1. Click Punctaj.exe
   ↓
2. "Discord Login" window appears
   ↓
3. Browser opens automatically
   ↓
4. User clicks "Authorize" in Discord
   ↓
5. Application starts with current permissions
   ↓
6. User works in app
   ↓
7. When user closes app OR restarts
   ↓
8. Complete login flow again (fresh)
```

**Time required:** 2-3 minutes (first time setup is done, subsequent are faster)

---

## Login Process Detail

### Step 1: Application Starts
```
❌ Check for saved token
   → NONE FOUND (caching disabled)
❌ Load cached session
   → SKIP (no cached sessions)
✅ Show Discord login window
   → "Discord Login - OBLIGATORIU"
```

### Step 2: Browser Opens
```
✅ Local server starts on port 8888
✅ Browser opens Discord OAuth page
✅ User sees "Authorize Punctaj application"
✅ User clicks "Authorize"
```

### Step 3: Authorization Code
```
✅ Discord sends authorization code
✅ Code captured by app's local server
✅ Code exchanged for access token
✅ User info fetched from Discord
```

### Step 4: Permission Check
```
✅ Check Supabase for user role
✅ Fetch latest permissions
✅ Load role: superuser/admin/user/viewer
✅ Apply permission restrictions
```

### Step 5: App Starts
```
✅ Login window closes
✅ Main application starts
✅ User can work with current permissions
✅ Token deleted from memory when app closes
```

---

## Technical Details

### What Happens to Tokens

```
Login:
  → OAuth2 flow with Discord
  → Access token created
  → STORED IN MEMORY ONLY (not on disk)

Working:
  → Token used for API calls
  → Token stored in RAM only

Logout/Close:
  → Token destroyed from memory
  → NO TOKEN FILE CREATED
  → Complete cleanup
```

### Why No Token File?

```
Token file disadvantages:
❌ Can be read by other users on system
❌ Susceptible to disk attacks
❌ Persists across sessions (stale)
❌ Renewal issues & complexity

Fresh login advantages:
✅ No files to protect
✅ Always current permissions
✅ Simple & secure
✅ No token expiry issues
```

---

## Permission Updates Example

### Scenario: User Role Change

```
Time: 9:00 AM
  → Admin removes user from "admin" role
  → Sets user to "user" role (lower permissions)

Old system (token cached):
  → User had admin token from yesterday
  → User could still do admin actions
  → ⚠️ SECURITY ISSUE - stale permissions

New system (fresh login):
  → User closes app
  → User reopens app
  → Fresh Discord login
  → Permission fetched: "user" (not admin)
  → User has restricted permissions immediately
  → ✅ SECURE - always current permissions
```

---

## FAQ

**Q: Do I have to login every time I start the app?**
A: Yes, exactly. Fresh login every session for security.

**Q: Why was token caching removed?**
A: To ensure permissions are always current and prevent stale permission issues.

**Q: How long does login take?**
A: Usually 2-3 minutes (browser opens, you click authorize, done).

**Q: What if I want to keep it open?**
A: App can stay open as long as you want. Login only happens when you START the app.

**Q: What happens if I close and restart the app?**
A: Same login process again - this is expected and secure.

**Q: Can I bypass the login?**
A: No. Discord login is mandatory. There's no way around it.

**Q: What if my internet goes down?**
A: You cannot login. Discord authentication requires internet connection.

**Q: Is my Discord password stored?**
A: No, never. We use Discord OAuth2 - you login to Discord, not our app.

**Q: Can an admin see my token?**
A: No token to see. Token exists in memory only during app session.

**Q: What if Discord servers are down?**
A: App cannot start. Discord is required for all sessions.

**Q: Does this affect performance?**
A: Login takes 2-3 minutes. Once logged in, app runs normally.

---

## Security Benefits Summary

| Aspect | Old (Cached) | New (Fresh) |
|--------|-------------|-----------|
| Token Storage | Disk file | Memory only |
| Token Lifespan | Days/weeks | Single session |
| Permission Updates | Delayed | Immediate |
| Security | Moderate | High |
| File Permissions | Restricted file | No file |
| Session Isolation | No | Complete |
| Role Changes | Delayed | Instant |

---

## Implementation Details

### Disabled Functions
```python
# DISABLED - no longer saves tokens
_save_token() → pass (does nothing)

# DISABLED - no longer loads cached tokens  
_load_stored_token() → pass (does nothing)

# DISABLED - no token refresh
refresh_access_token() → N/A
is_token_valid() → always False
```

### Every Session
```python
# Always executes
discord_login() → fresh OAuth2 flow
_exchange_code_for_token() → get new token
_fetch_user_info() → get current user data
_fetch_user_role_from_supabase() → get fresh permissions
```

### On App Close
```python
# Token deleted
access_token = None
user_info = None
# Everything cleaned up
# Next session = complete fresh start
```

---

## User Instructions

### For Users

1. **Start Application**
   ```
   Double-click: Punctaj.exe
   ```

2. **Authorize**
   ```
   Browser opens → Click "Authorize"
   ```

3. **Work**
   ```
   App starts → Do your work
   ```

4. **Stop**
   ```
   Close the app
   All session data deleted
   ```

5. **Next Time**
   ```
   Start again → Repeat from step 1
   ```

### For Admins

**Ensure users understand:**
- ✓ Fresh login each time is NORMAL
- ✓ No token caching = more secure
- ✓ Role changes take effect immediately
- ✓ Always requires Discord online

**Monitor:**
- Login attempts in logs
- Failed authentications
- Permission changes impact

---

## Migration Notes

### If You Had Previous Version
- ❌ Old token file (.discord_token) is IGNORED
- ❌ Cached sessions are NOT used
- ✅ Fresh login required on first start
- ✅ Clean state from now on

### No Setup Needed
- No cleanup required
- Old token files can be deleted (optional)
- App will work with fresh login

---

## Technical Architecture

```
Application Startup
    ↓
Discord Auth Check
    ├─ Is discord_config.ini configured?
    │  ├─ YES → Continue
    │  └─ NO → Exit (mandatory)
    ↓
Token Cache Check
    ├─ Is token cached?
    │  ├─ OLD: YES → Load & use
    │  ├─ NEW: NO → Skip (always false)
    ↓
OAuth2 Flow
    ├─ Start local server (port 8888)
    ├─ Open browser to Discord
    ├─ User authorizes
    ├─ Get authorization code
    ├─ Exchange for access token
    ├─ Fetch user info
    ├─ Fetch user role
    ↓
Token Storage
    ├─ OLD: Save to disk (.discord_token)
    ├─ NEW: Keep in memory only
    ↓
Application Runs
    └─ Token used for API calls
    └─ Token destroyed on close
```

---

## Contact

If users have questions about mandatory login:

**Explain:**
- "This is for security - ensures permissions are always current"
- "Process is same as any web service (like Gmail, Discord, etc.)"
- "Protects your data by preventing stale permission issues"
- "Only takes 2-3 minutes, then you can work normally"

---

**IMPLEMENTATION DATE:** February 1, 2026  
**STATUS:** ✅ Active (Token caching completely disabled)
