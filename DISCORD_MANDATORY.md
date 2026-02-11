# 🔐 Discord Authentication - MANDATORY

## Overview

**Discord authentication is now REQUIRED** to use the Punctaj application. This ensures:

✅ **Identity Verification** - Each user is authenticated with their Discord account  
✅ **Role-Based Access Control** - Permissions based on Discord server roles  
✅ **Audit Trail** - All actions logged with Discord username for accountability  
✅ **Security** - No hardcoded passwords, uses secure OAuth2 protocol  

---

## What Has Changed?

### Before (Optional Discord)
- Application started even without Discord login
- Could use app anonymously
- No permission system based on roles

### Now (Mandatory Discord) ⭐
- **MUST authenticate with Discord at startup**
- **Cannot proceed without successful login**
- **Permissions enforced based on Discord role**
- **All actions logged with Discord user info**

---

## Setup Required

### 1. Create Discord Application

Go to: https://discord.com/developers/applications

**Steps:**
1. Click "New Application"
2. Give it a name: `Punctaj`
3. Go to "OAuth2" tab
4. Copy **CLIENT_ID**
5. Under "Client Secret", click "Reset Secret" and copy **CLIENT_SECRET**

### 2. Configure Redirect URI

In Discord Developer Portal:
- Go to "OAuth2" → "General"
- Scroll to "Redirects"
- Add: `http://localhost:8888/callback`
- Save changes

### 3. Configure Application

Edit `discord_config.ini`:

```ini
[discord]
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:8888/callback
WEBHOOK_URL=https://discordapp.com/api/webhooks/your_webhook_id/token
```

### 4. Set Discord Server Roles

Users need Discord roles assigned in your server for permissions:

- **superuser** - Full administrative access
- **admin** - Can manage institutions and employees
- **user** - Can edit employee data
- **viewer** - Read-only access

---

## Login Flow

### At Application Startup

```
1. Application starts
   ↓
2. Checks if discord_config.ini is configured
   ↓
3. If NOT configured → ❌ Application EXITS (Discord is MANDATORY)
   ↓
4. If configured → Shows Discord Login window
   ↓
5. Opens browser for Discord OAuth2 authentication
   ↓
6. User logs in with Discord account
   ↓
7. Browser redirects back to app
   ↓
8. Application reads Discord user info & role
   ↓
9. ✅ User gains access based on their role
```

### Error Handling

| Scenario | Result |
|----------|--------|
| discord_config.ini missing | ❌ App closes immediately |
| Invalid CLIENT_ID/SECRET | ❌ App closes immediately |
| Browser timeout during login | User can retry or close app |
| Invalid Discord role | ✅ User loads as "viewer" (read-only) |
| Successful authentication | ✅ Full access with role permissions |

---

## User Roles & Permissions

### SUPERUSER
```
✅ Full system access
✅ Can manage all institutions
✅ Can manage employees
✅ Can manage users & permissions
✅ Can see all logs
✅ Can access admin panel
```

### ADMIN
```
✅ Can manage institutions
✅ Can manage employees  
✅ Can upload/download from cloud
✅ Can see most logs
✅ Limited user management
```

### USER
```
✅ Can add/edit/delete employees
✅ Can upload/download from cloud
✅ Can reset punctaj scores
✅ Can manage their own data
❌ Cannot manage users
```

### VIEWER
```
✅ Can view all data (read-only)
❌ Cannot make any changes
❌ Cannot delete anything
❌ Cannot upload to cloud
```

---

## For Administrators

### Managing User Roles

Edit user Discord roles in your Discord server:

1. Open your Discord server
2. Go to Server Settings → Members
3. Find the user
4. Click "+" to add role
5. Select appropriate role: superuser, admin, user, viewer

### Revoking Access

Remove the user's role from Discord server:
- User will still be able to login
- But will be assigned "viewer" role (read-only)
- No sensitive changes possible

### Creating New Admin

1. Create Discord role "admin" in server
2. Add user to role
3. User logs in → automatically gets "admin" role
4. User gains admin permissions

---

## Troubleshooting

### "Discord authentication is required but not configured"

**Solution:**
1. Edit `discord_config.ini`
2. Add CLIENT_ID and CLIENT_SECRET
3. Restart application

### "Authentication failed or timed out"

**Possible causes:**
- Browser closed during authentication
- Internet connection lost
- Port 8888 already in use

**Solution:**
- Click "Retry" button in login dialog
- Check internet connection
- Close other apps using port 8888

### "Invalid CLIENT_ID or CLIENT_SECRET"

**Solution:**
1. Go to https://discord.com/developers/applications
2. Select your Punctaj application
3. Copy correct CLIENT_ID from "Application ID"
4. Copy correct CLIENT_SECRET from "Client Secret"
5. Update discord_config.ini
6. Restart application

### User cannot login

**Check:**
1. Does user have Discord account?
2. Is user in your Discord server?
3. Does user have a role (superuser/admin/user/viewer)?
4. Is port 8888 accessible on their machine?

---

## Security Notes

### What Discord Can See

Discord OAuth2 only reads:
- `username` - Public Discord username
- `id` - Public Discord user ID
- `email` - Email if user shares it
- `guilds` - List of servers user is in

### What Punctaj NEVER Shares

- User's Discord password
- User's email with Discord
- User's activity data to Discord
- Any application data to Discord
- Any financial information

### Token Security

- Access tokens are stored locally in: `~\Documents\PunctajManager\.discord_token`
- Tokens are encrypted (if available)
- Tokens auto-refresh automatically
- Tokens never sent to external servers (except Discord)

---

## For Developers

### Checking User Authentication

```python
if DISCORD_AUTH and DISCORD_AUTH.is_authenticated():
    username = DISCORD_AUTH.user_info.get('username')
    user_id = DISCORD_AUTH.user_info.get('id')
    role = DISCORD_AUTH.get_user_role()
    print(f"Logged in as: {username} ({role})")
```

### Checking Permissions

```python
if DISCORD_AUTH:
    if DISCORD_AUTH.is_superuser():
        print("User is superuser")
    elif DISCORD_AUTH.is_admin():
        print("User is admin")
    
    if DISCORD_AUTH.can_perform_action("can_upload_cloud"):
        print("User can upload to cloud")
```

### Force Re-authentication

```python
DISCORD_AUTH.logout()
# User will be prompted to login again at next app restart
```

---

## FAQ

**Q: Can I use the app without Discord?**
A: No. Discord authentication is now mandatory for all users.

**Q: What if I forget my Discord password?**
A: Use Discord's account recovery: https://discord.com/reset

**Q: Can multiple users use the same Discord account?**
A: Not recommended. Create separate Discord accounts for each user.

**Q: What if Discord is down?**
A: Application cannot start without Discord verification.

**Q: Can I have multiple Discord roles?**
A: Yes! User will have the HIGHEST permission level of all their roles.

**Q: Are logins cached offline?**
A: No. Login happens every session restart (security best practice).

**Q: How long does authentication take?**
A: Usually 2-3 minutes (opens browser, user clicks "Authorize").

---

## Contact Support

If you have issues with Discord authentication:

1. Check this guide
2. Verify discord_config.ini is correct
3. Check Discord server roles
4. Try restarting the application
5. Contact your administrator

**Admin Contact:** [Your Discord Server]
