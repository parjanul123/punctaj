# Discord Authentication Setup

## Overview
Punctaj Manager now supports Discord OAuth2 authentication for secure user access and permission management.

## Features

✅ **Secure OAuth2 Authentication**
- Login with Discord credentials
- Token storage and automatic refresh
- No password management

✅ **User Identification**
- User ID and username tracking
- Email verification
- Discord guild/server access information

✅ **Session Management**
- Persistent authentication tokens
- Automatic token expiry handling
- One-click logout

✅ **Webhook Integration (Optional)**
- Send notifications to Discord channels
- Audit trail logging
- Real-time activity updates

## Setup Instructions

### Step 1: Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name it (e.g., "Punctaj Manager")
3. Go to "OAuth2" → "General" section
4. Copy your **CLIENT ID** and **CLIENT SECRET**
5. Save them in a secure location

### Step 2: Configure OAuth2 Redirects

1. In Developer Portal, go to OAuth2 → General
2. Click "Add Redirect" and add: `http://localhost:8888/callback`
3. Save changes

### Step 3: Configure discord_config.ini

Edit the `discord_config.ini` file in your project root:

```ini
[discord]
# Discord Application ID
CLIENT_ID = YOUR_CLIENT_ID_HERE

# Discord Application Secret (KEEP THIS PRIVATE!)
CLIENT_SECRET = YOUR_CLIENT_SECRET_HERE

# OAuth2 Redirect URI
REDIRECT_URI = http://localhost:8888/callback

# (Optional) Webhook URL for notifications
WEBHOOK_URL = https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

**Replace:**
- `YOUR_CLIENT_ID_HERE` with your actual Client ID
- `YOUR_CLIENT_SECRET_HERE` with your actual Client Secret
- `YOUR_WEBHOOK_ID` and `YOUR_WEBHOOK_TOKEN` (optional, for notifications)

### Step 4: Security

⚠️ **IMPORTANT:**
- Never commit `discord_config.ini` to Git with real credentials
- Add `discord_config.ini` to `.gitignore`
- Store secrets in environment variables for production
- Tokens are stored at: `~/Documents/PunctajManager/.discord_token`

## Usage

### Logging In

1. Start Punctaj Manager
2. Click **"🔐 Login Discord"** button
3. Your browser will open Discord login
4. Authorize the application
5. You'll be automatically authenticated

### User Profile

- Click **"👤 Profile"** to view your Discord information
- See your username, user ID, and email

### Logging Out

- Click **"🚪 Logout"** to end your session
- Your token will be deleted

## Webhook Integration (Optional)

To send notifications to a Discord channel:

1. Create a Webhook in your Discord server
   - Server Settings → Integrations → Webhooks → Create Webhook
   - Copy the webhook URL

2. Add to `discord_config.ini`:
```ini
WEBHOOK_URL = https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
```

3. Example usage in code:
```python
from discord_auth import DiscordWebhook

webhook = DiscordWebhook("YOUR_WEBHOOK_URL")
webhook.send_message("Data synchronized successfully!")
```

## Troubleshooting

### "Discord configuration not configured"
- Check if `discord_config.ini` exists
- Verify `CLIENT_ID` and `CLIENT_SECRET` are filled in
- Ensure file is in the project root or `~/Documents/PunctajManager/`

### "Authentication failed or timed out"
- Check browser popup blockers
- Verify localhost:8888 is not in use
- Ensure firewall allows local connections
- Try disabling VPN/proxy

### "Token refresh failed"
- Delete `~/Documents/PunctajManager/.discord_token`
- Log in again
- Check if CLIENT_SECRET is correct

### Browser doesn't open
- Manually open: `https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8888/callback&response_type=code&scope=identify+email+guilds`
- Replace YOUR_CLIENT_ID with your actual ID

## API Reference

### DiscordAuth Class

```python
from discord_auth import DiscordAuth

# Initialize
auth = DiscordAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="http://localhost:8888/callback"
)

# Check authentication
if auth.is_authenticated():
    user = auth.get_user_info()
    print(f"Logged in as: {user['username']}")

# Refresh token
auth.refresh_access_token()

# Logout
auth.logout()
```

### DiscordWebhook Class

```python
from discord_auth import DiscordWebhook

webhook = DiscordWebhook("YOUR_WEBHOOK_URL")

# Send simple message
webhook.send_message("Hello from Punctaj Manager!")

# Send embedded message
embed = {
    "title": "Data Sync Complete",
    "description": "5 files synchronized",
    "color": 3066993
}
webhook.send_embed(embed)
```

## Environment Variables (Production)

For production deployments, use environment variables:

```bash
export DISCORD_CLIENT_ID="your_client_id"
export DISCORD_CLIENT_SECRET="your_client_secret"
export DISCORD_WEBHOOK_URL="your_webhook_url"
```

Then update code to read from environment:

```python
import os

DISCORD_CONFIG = {
    'CLIENT_ID': os.getenv('DISCORD_CLIENT_ID'),
    'CLIENT_SECRET': os.getenv('DISCORD_CLIENT_SECRET'),
    'WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
}
```

## Support

For issues or questions:
1. Check this README
2. Review Discord Developer Documentation
3. Check application console for error messages
4. Contact system administrator

## Links

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord OAuth2 Documentation](https://discord.com/developers/docs/topics/oauth2)
- [Discord API Webhooks](https://discord.com/developers/docs/resources/webhook)
