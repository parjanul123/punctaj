# 🔐 Granular Permissions Access Control

## Overview
Only **Superusers** and **Admins** can see and access the "⚙️ Admin" button that opens the granular permissions management panel.

## How It Works

### Permission Hierarchy
The button visibility is controlled by the `can_manage_granular_permissions()` method in `discord_auth.py`:

```python
def can_manage_granular_permissions(self) -> bool:
    """Check if user can manage granular permissions - only superusers and admins"""
    if not self.is_authenticated():
        return False
    
    return self._is_superuser or self._is_admin
```

### Who Can See the Button?
- ✅ **Superusers** (`is_superuser = True`) → Full access
- ✅ **Admins** (`is_admin = True`) → Full access
- ❌ **Users** → NO access
- ❌ **Viewers** → NO access

## Setting User Permissions in Supabase

The permission is controlled by the `is_admin` and `is_superuser` columns in the `discord_users` table:

| Column | Type | Default | Meaning |
|--------|------|---------|---------|
| `is_admin` | BOOLEAN | false | User can manage granular permissions |
| `is_superuser` | BOOLEAN | false | User has full superuser access |

### Example: Grant Access to User
To allow user "john_doe" to manage granular permissions:

1. Open your Supabase dashboard
2. Go to `discord_users` table
3. Find the user row
4. Set `is_admin = true` OR `is_superuser = true`
5. Save

The user will see the button on their next session.

## Two Button Locations

The granular permissions button appears in two places:

### 1. Main Sidebar (If Admin)
Location: Bottom of the sidebar
- Button: "⚙️ Admin"
- Shows if user has `can_manage_granular_permissions()` permission

### 2. Admin Panel
Location: Admin section (bottom toolbar)
- Button: "🔐 Permisiuni Utilizatori"
- Shows if user has `can_manage_granular_permissions()` permission

## What Can Be Done in Granular Permissions Panel?

Users with access can manage:

### Admin Level
- ✅ can_manage_user_permissions
- ✅ can_revoke_user_permissions

### Global Level
- ✅ can_add_cities
- ✅ can_edit_cities
- ✅ can_delete_cities

### City Level (per city)
- ✅ can_add_institutions
- ✅ can_edit_institutions
- ✅ can_delete_institutions

### Institution Level (per institution)
- ✅ can_view
- ✅ can_edit
- ✅ can_delete
- ✅ can_reset_scores
- ✅ can_deduct_scores

## Debug Information

To verify if a user has permission:
```python
# Check in code:
if DISCORD_AUTH.can_manage_granular_permissions():
    print("User can access granular permissions panel")
else:
    print("User does NOT have access")
```

## Notes
- User role is fetched from Supabase when they log in
- Permissions are checked in real-time when the button is clicked
- No additional column needs to be added - uses existing `is_admin` and `is_superuser` fields
