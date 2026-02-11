# Quick Reference: Admin Panel & Permissions

## 🎯 What Was Done

### ✅ Task 1: Admin Panel Button
- **What:** Red "🛡️ Admin Panel" button in sidebar
- **Who can see:** Only admin users
- **What it does:** Opens admin interface for user management and logs
- **Where:** Look in sidebar below cloud sync button

### ✅ Task 3: Permission System
- **What:** Three role-based access levels
- **Roles:** Admin → User → Viewer
- **Enforcement:** Permission checks on all operations
- **Storage:** Roles in Supabase `discord_users` table

---

## 👤 User Roles

### ADMIN (Red Badge)
- **Full access** to everything
- Can manage users
- Can view action logs
- Can perform all operations

### USER (Blue Badge)
- Can **add/edit/delete** institutions and employees
- Can **view** all data
- Cannot manage users
- Cannot view logs

### VIEWER (Gray Badge)
- **Read-only** access
- Can **only view** data
- Cannot make any changes
- Cannot access Admin Panel

---

## 🛡️ Admin Panel Features

### Users Tab
- See all Discord users
- Update user roles
- Delete users
- View last login time

### Logs Tab
- View action history
- Filter by username
- Filter by action type
- See details of each action

### Stats Tab
- User count
- Log count
- Last sync time

---

## 🔐 How Permission Enforcement Works

```
User tries to edit data
        ↓
System checks: Is user read-only?
        ↓
NO: Allow action ✅
YES: Show error ❌
```

**Error message:** "Acces Interzis" (Access Denied)

---

## 📋 Role Management

### Change User's Role
1. Open Admin Panel (red button)
2. Go to Users tab
3. Select user
4. Click dropdown → select new role
5. Click "Update Role"
6. User gets new role on next login

### Check User's Current Role
1. User logs in
2. Look at badge next to username:
   - Red = Admin
   - Blue = User
   - Gray = Viewer

### Set Role (Direct in Supabase)
```sql
UPDATE discord_users 
SET role = 'admin' 
WHERE discord_id = 'USER_ID';
```

---

## 🎨 Visual Guide

### Sidebar for Admin
```
┌─────────────────┐
│ Miasta          │
│ ➕ Adaugă grad  │
│ ✏️  Editează    │
│ ❌ Șterge       │
│                 │
│ 👤 username     │
│ 📊 Role: Admin  │
│ [👁️] [🚪]       │
│                 │
│ ☁️ Cloud Sync   │
│                 │
│ 🛡️ ADMIN PANEL  │ ← Only for admin!
└─────────────────┘
```

### Sidebar for User
```
┌─────────────────┐
│ Miasta          │
│ ➕ Adaugă grad  │ ✅ Enabled
│ ✏️  Editează    │ ✅ Enabled
│ ❌ Șterge       │ ✅ Enabled
│                 │
│ 👤 username     │
│ 📊 Role: User   │
│ [👁️] [🚪]       │
│                 │
│ ☁️ Cloud Sync   │
│                 │
│ (no admin panel)│ ← Hidden for non-admin
└─────────────────┘
```

### Sidebar for Viewer
```
┌─────────────────┐
│ Miasta          │
│ ➕ Adaugă grad  │ ❌ DISABLED
│ ✏️  Editează    │ ❌ DISABLED
│ ❌ Șterge       │ ❌ DISABLED
│                 │
│ 👤 username     │
│ 📊 Role: Viewer │
│ [👁️] [🚪]       │
│                 │
│ ☁️ Cloud Sync   │ ❌ DISABLED
│                 │
│ (no admin panel)│ ← Hidden for non-admin
└─────────────────┘
```

---

## 💡 Common Tasks

### Create New Admin
1. Invite user to Discord
2. User logs in to app
3. Go to Admin Panel
4. Users tab → find user → set role to "admin"
5. User is now admin on next login

### Convert Admin to Viewer
1. Admin Panel → Users tab
2. Find user
3. Change role from "admin" to "viewer"
4. User loses admin access on next login

### Check Who's Admin
1. Admin Panel → Users tab
2. Look for users with admin role
3. Or check Supabase: `role = 'admin'`

### Remove User
1. Admin Panel → Users tab
2. Select user
3. Click "Delete User"
4. User cannot log in anymore

---

## ⚙️ Technical Details

### Permission Methods
```python
# Check if admin
if DISCORD_AUTH.is_admin():
    # User is admin

# Check if can edit
if not can_edit_city('CityName'):
    # User cannot edit

# Check if read-only
if is_read_only_user():
    # User is viewer (read-only)

# Get user's role
role = DISCORD_AUTH.get_user_role()
# Returns: 'admin', 'user', or 'viewer'
```

### Permission Matrix
| Action | Admin | User | Viewer |
|--------|-------|------|--------|
| View data | ✅ | ✅ | ✅ |
| Add city | ✅ | ❌ | ❌ |
| Edit city | ✅ | ✅ | ❌ |
| Delete city | ✅ | ✅ | ❌ |
| Admin Panel | ✅ | ❌ | ❌ |
| View logs | ✅ | ❌ | ❌ |

---

## 🆘 Troubleshooting

### Q: Admin Panel button not showing?
**A:** You're not admin. Check your role in Supabase.

### Q: Can't edit data?
**A:** You might have "viewer" role. Ask admin to change it to "user".

### Q: Role didn't change?
**A:** Logout and login again. Roles are loaded at login time.

### Q: Forgot admin password?
**A:** Can't forget Discord password. Use Discord login.

---

## 📞 Support

- **Admin Panel Help:** See USER_MANAGEMENT_GUIDE.md
- **Technical Details:** See PERMISSIONS_SYSTEM.md
- **Setup Issues:** See discord_config.ini or supabase_config.ini

---

## 🚀 Getting Started

1. **Login with Discord**
   - Click "🔐 Login Discord" button
   - Authorize in browser
   - You get default "viewer" role

2. **Get Admin to Change Your Role**
   - Ask existing admin
   - They open Admin Panel
   - Change your role to "user"
   - You can now edit data

3. **If You're First Admin**
   - Edit Supabase directly:
   - `UPDATE discord_users SET role = 'admin' WHERE discord_id = 'YOUR_ID'`
   - Logout and login
   - Admin Panel button appears

---

**That's all you need to know! 🎉**
