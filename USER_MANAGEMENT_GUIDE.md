# Managing User Permissions - Quick Guide

## Overview

The permission system uses three roles:
- **Admin** - Full access, can manage users and permissions
- **User** - Can add/edit/delete institutions and employees
- **Viewer** - Read-only access

## Admin Panel

### Accessing Admin Panel
1. Log in with Discord (user must have "admin" role)
2. Click "🛡️ Admin Panel" button in sidebar (red button, only visible for admins)
3. Admin panel window opens with 3 tabs

### Tab 1: Users Management
**Location:** Admin Panel → Users tab

**Features:**
- View all Discord users in system
- See user info: Discord ID, Username, Email, Current Role, Last Login
- Update user role (dropdown: admin → user → viewer)
- Delete users from system

**How to Change User Role:**
1. Open Admin Panel
2. Go to Users tab
3. Select user from list (click row)
4. Choose new role from "Role" dropdown
5. Click "Update Role" button
6. Confirmation message appears

**How to Delete User:**
1. Open Admin Panel
2. Go to Users tab
3. Select user from list
4. Click "Delete User" button
5. Confirmation required
6. User removed from discord_users table

### Tab 2: Logs
**Location:** Admin Panel → Logs tab

**Features:**
- View all action logs (add, edit, delete, upload, download)
- Filter by username
- Filter by action type
- See timestamp, affected city/institution, operation details

**How to Check Logs:**
1. Open Admin Panel
2. Go to Logs tab
3. (Optional) Filter by username or action
4. Click "Refresh Logs"
5. View activity history

### Tab 3: Statistics
**Location:** Admin Panel → Stats tab

**Features:**
- Total user count
- Total action logs
- Last sync timestamp
- System overview

---

## User Roles & Permissions

### ADMIN Role
**Badge Color:** Red (#e74c3c)

**Permissions:**
- ✅ View all data
- ✅ Add/Edit/Delete cities
- ✅ Add/Edit/Delete institutions
- ✅ Add/Edit/Delete employees
- ✅ Update ranks and scores
- ✅ Upload to cloud
- ✅ Download from cloud
- ✅ Access Admin Panel
- ✅ Manage users
- ✅ View logs

**When to Use:** System administrators, managers

---

### USER Role
**Badge Color:** Blue (#3498db)

**Permissions:**
- ✅ View all data
- ✅ Add/Edit/Delete institutions (can modify cities)
- ✅ Add/Edit/Delete employees
- ✅ Update ranks and scores
- ✅ Upload to cloud
- ✅ Download from cloud
- ❌ Access Admin Panel
- ❌ Manage users
- ❌ View logs

**When to Use:** Regular users, data entry staff

---

### VIEWER Role
**Badge Color:** Gray (#95a5a6)

**Permissions:**
- ✅ View all data
- ❌ Add/Edit/Delete cities
- ❌ Add/Edit/Delete institutions
- ❌ Add/Edit/Delete employees
- ❌ Update ranks and scores
- ❌ Upload to cloud
- ❌ Download from cloud
- ❌ Access Admin Panel
- ❌ Manage users
- ❌ View logs

**When to Use:** Read-only access, audit purposes, viewing only

---

## Setting Up New Users

### Manual Role Assignment (via Supabase)

If admin panel is not accessible, you can set roles directly in Supabase:

1. Go to Supabase Dashboard
2. Open `discord_users` table
3. Find user by discord_id or username
4. Edit the `role` column:
   - Set to `admin` for administrators
   - Set to `user` for regular users
   - Set to `viewer` for read-only access
5. Click Update

### Automatic Role Assignment

When a new user logs in:
1. User registers in `discord_users` table
2. Role defaults to `viewer`
3. Admin can change role in Admin Panel → Users tab
4. Change takes effect on next login

---

## Troubleshooting

### Issue: Admin Panel button not showing
**Possible Causes:**
- User does not have "admin" role
- Admin panel module not loaded
- user_role not set correctly

**Solution:**
1. Check user's role in Supabase `discord_users` table
2. Change role to "admin"
3. Logout and log back in
4. Admin Panel button should appear

### Issue: User can't edit data
**Possible Causes:**
- User has "viewer" role
- User has read-only permissions

**Solution:**
1. Open Admin Panel (if you're admin)
2. Go to Users tab
3. Select the user
4. Change role to "user" or "admin"
5. User can now make changes after next login

### Issue: User locked out of Admin Panel
**Possible Causes:**
- User role changed to "viewer" or "user"
- Supabase role query failed

**Solution:**
1. Use another admin account to access Admin Panel
2. Change the locked user's role back to "admin"
3. User can now access Admin Panel

---

## Database Query Reference

### Check user's current role
```sql
SELECT discord_id, username, email, role, created_at, last_login 
FROM discord_users 
WHERE discord_id = 'USER_ID';
```

### Update user role
```sql
UPDATE discord_users 
SET role = 'admin' 
WHERE discord_id = 'USER_ID';
```

### View all users and roles
```sql
SELECT discord_id, username, role, last_login 
FROM discord_users 
ORDER BY last_login DESC;
```

### Count users by role
```sql
SELECT role, COUNT(*) as count 
FROM discord_users 
GROUP BY role;
```

---

## Supabase Table Structure

### discord_users table
| Column | Type | Description |
|--------|------|-------------|
| id | int | Primary key |
| discord_id | text | Discord user ID (unique) |
| username | text | Discord username |
| email | text | User email |
| role | text | admin / user / viewer |
| created_at | timestamp | Account creation date |
| last_login | timestamp | Last login time |

---

## Best Practices

1. **Always have at least one admin** - Don't remove admin role from all users
2. **Use viewer role for read-only** - Give least privileges needed
3. **Regular review of permissions** - Check logs regularly
4. **Document changes** - Note why you changed a user's role
5. **Backup before major changes** - Keep backups of discord_users table
6. **Test permissions** - Verify role works as expected after assignment

---

## Contact & Support

For permission-related issues:
1. Check Admin Panel → Logs to see recent activity
2. Review Supabase discord_users table
3. Verify role is set correctly
4. Logout and log back in to refresh permissions
5. Check application logs for errors
