# Discord Authentication Implementation Guide

## What Was Added

This document explains the Discord authentication system that has been integrated into Punctaj Manager.

## Files Created

### 1. `discord_auth.py` (Main Module)
The core Discord OAuth2 authentication module with two classes:

#### `DiscordAuth` Class
Handles Discord OAuth2 authentication with the following features:

- **OAuth2 Flow**: Implements complete authorization code grant flow
- **Token Management**: Automatic token storage, refresh, and expiry handling
- **User Info**: Fetches and stores user profile information
- **Session Persistence**: Stores tokens locally for seamless re-authentication
- **CSRF Protection**: State validation for security

**Key Methods**:
```python
# Check authentication status
auth.is_authenticated()

# Get user information
auth.get_user_info()  # Returns dict with username, email, etc.

# Start OAuth2 authentication server
auth.start_oauth_server(port=8888)

# Token management
auth.refresh_access_token()
auth.is_token_valid()

# Logout
auth.logout()
```

#### `DiscordWebhook` Class
Sends notifications to Discord channels via webhooks.

**Key Methods**:
```python
webhook = DiscordWebhook(webhook_url)
webhook.send_message("Message text")
webhook.send_embed({...})  # Send embedded message
```

### 2. `discord_config.ini`
Configuration file template for Discord credentials:

```ini
[discord]
CLIENT_ID = your_client_id_here
CLIENT_SECRET = your_client_secret_here
REDIRECT_URI = http://localhost:8888/callback
WEBHOOK_URL = your_webhook_url_here  # Optional
```

**IMPORTANT**: Never commit real credentials to Git!

### 3. `discord_auth_test.py`
Diagnostic tool to test and debug Discord authentication:

Features:
- Configuration validation
- OAuth2 login testing
- Token status checking
- Webhook notification testing
- Interactive menu interface

Run with: `python discord_auth_test.py`

### 4. `DISCORD_AUTH_SETUP.md`
Complete setup and troubleshooting guide for Discord authentication.

### 5. `requirements.txt`
Updated with necessary Python packages (especially `requests`)

## Changes to `punctaj.py`

### 1. Discord Configuration Loading (Lines ~25-55)
Added configuration file loading with multiple search paths:
- Project root
- User's Documents/PunctajManager folder
- Current directory

### 2. New Functions Added

#### `discord_login()`
Enhanced login function with:
- Beautiful login window UI
- Browser-based OAuth2 authentication
- Status feedback and progress indication
- Automatic token persistence
- Configuration wizard if not set up

#### `discord_logout()`
Handles user logout:
- Clears authentication tokens
- Removes stored token file
- Shows confirmation message

#### `show_discord_profile()`
Displays current user's Discord profile:
- Username
- User ID
- Email
- Token status

### 3. UI Integration (Lines ~664-705)
Added Discord authentication UI in sidebar:

**When Authenticated**:
- Shows Discord username with 👤 icon
- "👁️ Profile" button - view account info
- "🚪 Logout" button - end session

**When Not Authenticated**:
- "🔐 Login Discord" button - start OAuth2 flow

## How It Works

### Authentication Flow

1. **User Clicks "Login Discord"**
   ↓
2. **Local HTTP Server Starts** (port 8888)
   ↓
3. **Browser Opens Discord OAuth2 Page**
   ↓
4. **User Authorizes Application**
   ↓
5. **Discord Redirects to Callback URL** with authorization code
   ↓
6. **Local Server Receives Code** and exchanges for access token
   ↓
7. **Token and User Info Stored** locally
   ↓
8. **User Logged In** - username shown in sidebar

### Token Management

- **Storage Location**: `~/Documents/PunctajManager/.discord_token`
- **Format**: JSON file with encrypted-like appearance
- **Permissions**: File restricted to owner (mode 0o600)
- **Expiry**: Automatically refreshed 5 minutes before expiration
- **Persistence**: Reused across application restarts

## Security Considerations

### ✅ What We Do Right

1. **HTTPS-Only Tokens**: Discord sends tokens over HTTPS
2. **No Password Storage**: Never handle passwords directly
3. **CSRF Protection**: State validation prevents attacks
4. **Token Expiry**: Short-lived access tokens (1 hour)
5. **Refresh Tokens**: Secure way to get new access tokens
6. **Local Storage**: Tokens stored with restricted file permissions
7. **No Logging**: Sensitive data not logged

### ⚠️ Security Best Practices

1. **Never Hardcode Credentials**
   ```python
   # ❌ WRONG
   client_id = "1234567890"
   
   # ✅ RIGHT
   client_id = os.getenv('DISCORD_CLIENT_ID')
   ```

2. **Use Environment Variables in Production**
   ```bash
   export DISCORD_CLIENT_ID="xxx"
   export DISCORD_CLIENT_SECRET="yyy"
   ```

3. **Add to .gitignore**
   ```
   discord_config.ini
   .discord_token
   ```

4. **Secure Webhook URLs**
   - Don't share webhook URLs publicly
   - Rotate webhooks if exposed
   - Use environment variables for webhooks

5. **Token File Protection**
   - Linux/Mac: File is automatically 0o600 (owner only)
   - Windows: Use ACL to restrict access
   - Never include in backups unless encrypted

## Integration Examples

### Example 1: Basic Login

```python
# In your app initialization
if DISCORD_AUTH and DISCORD_AUTH.is_authenticated():
    user = DISCORD_AUTH.get_user_info()
    print(f"Welcome back, {user['username']}!")
else:
    # Show login window
    discord_login()
```

### Example 2: Permission Checking

```python
# Check if user is authenticated
if DISCORD_AUTH and DISCORD_AUTH.is_authenticated():
    # Allow certain actions
    enable_edit_button()
else:
    # Disable actions or require login
    disable_edit_button()
```

### Example 3: Send Notification

```python
from discord_auth import DiscordWebhook

webhook = DiscordWebhook(DISCORD_CONFIG.get('WEBHOOK_URL'))

webhook.send_message(
    f"User {username} synchronized {count} files",
    title="Sync Complete"
)
```

### Example 4: Check Token Validity

```python
if DISCORD_AUTH and DISCORD_AUTH.is_token_valid():
    # Token is fresh and valid
    fetch_user_data()
else:
    # Token expired or missing
    show_login_dialog()
```

## Testing

### Automatic Testing

Run the diagnostic tool:
```bash
python discord_auth_test.py
```

This will:
1. Load and validate configuration
2. Check for stored tokens
3. Offer to test OAuth2 login
4. Test webhook notifications
5. Display results

### Manual Testing

1. **Configuration**
   - Open `discord_config.ini`
   - Verify CLIENT_ID and CLIENT_SECRET are filled
   - Check paths exist

2. **OAuth2 Login**
   - Start application
   - Click "🔐 Login Discord"
   - Complete login in browser
   - Verify username appears in sidebar

3. **Token Persistence**
   - Logout from Discord
   - Restart application
   - Token should be reloaded automatically

4. **Webhook Notification**
   - Configure WEBHOOK_URL in discord_config.ini
   - Run test tool and select webhook test
   - Check Discord channel for test message

## Troubleshooting

### Issue: "Discord configuration not configured"

**Solutions**:
1. Create `discord_config.ini` in project root
2. Get credentials from Discord Developer Portal
3. Fill in CLIENT_ID and CLIENT_SECRET
4. Verify file paths are correct

### Issue: Browser doesn't open

**Solutions**:
1. Check browser is default
2. Disable popup blockers
3. Manually visit authorization URL shown in console
4. Ensure port 8888 is available

### Issue: "Token refresh failed"

**Solutions**:
1. Delete `~/.discord_token` file
2. Log in again
3. Check if CLIENT_SECRET is correct
4. Verify network connectivity

### Issue: "Authentication failed"

**Solutions**:
1. Check internet connection
2. Verify CLIENT_ID and CLIENT_SECRET match
3. Check REDIRECT_URI is `http://localhost:8888/callback`
4. Ensure same URL is set in Discord Developer Portal

## Future Enhancements

Potential improvements to consider:

1. **Permission Management**
   - Role-based access control
   - Guild/server membership verification
   - Fine-grained permissions per city/institution

2. **Audit Logging**
   - Log all user actions with Discord ID
   - Track data modifications
   - Create audit trail for compliance

3. **Multi-User Features**
   - Collaborative editing
   - User activity tracking
   - Conflict resolution for concurrent edits

4. **Advanced Webhooks**
   - Scheduled reports to Discord
   - Real-time sync notifications
   - Error alerts and warnings

5. **API Integration**
   - REST API with Discord token auth
   - Webhook events for external services
   - Discord bot commands for quick actions

## Documentation Links

- [Discord OAuth2](https://discord.com/developers/docs/topics/oauth2)
- [Discord API Webhooks](https://discord.com/developers/docs/resources/webhook)
- [Discord User Object](https://discord.com/developers/docs/resources/user)

## Support

For detailed setup instructions, see: [DISCORD_AUTH_SETUP.md](DISCORD_AUTH_SETUP.md)

For testing and debugging, use: `python discord_auth_test.py`
