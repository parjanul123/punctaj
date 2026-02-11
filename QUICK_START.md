# Quick Start Guide - Discord Authentication

## 🚀 Fast Setup (5 minutes)

### Option 1: Interactive Setup Wizard (Recommended)

```bash
python discord_setup_wizard.py
```

This will:
1. Guide you through Discord app creation
2. Ask for your CLIENT_ID and CLIENT_SECRET
3. Save configuration automatically
4. Set up .gitignore for security

### Option 2: Manual Setup

1. **Create Discord App**
   - Visit: https://discord.com/developers/applications
   - Click "New Application"
   - Name it "Punctaj Manager"

2. **Get Credentials**
   - Go to OAuth2 → General
   - Copy: CLIENT_ID
   - Copy: CLIENT_SECRET

3. **Add Redirect URI**
   - In OAuth2 → General
   - Click "Add Redirect"
   - Add: `http://localhost:8888/callback`

4. **Configure File**
   - Edit `discord_config.ini`:
   ```ini
   [discord]
   CLIENT_ID = your_client_id_here
   CLIENT_SECRET = your_client_secret_here
   REDIRECT_URI = http://localhost:8888/callback
   WEBHOOK_URL = optional_webhook_url
   ```

5. **Secure File**
   - Add to `.gitignore`:
   ```
   discord_config.ini
   .discord_token
   ```

## 🔐 Using Discord Auth

### Login
1. Start Punctaj Manager
2. Click **"🔐 Login Discord"** button
3. Authorize in your browser
4. Username appears in sidebar

### Logout
- Click **"🚪 Logout"** button
- Token is deleted

### View Profile
- Click **"👁️ Profile"** button
- See your Discord info

## 🧪 Test Your Setup

```bash
python discord_auth_test.py
```

Interactive tool to:
- Validate configuration
- Test OAuth2 login
- Check stored tokens
- Test webhook notifications

## 📚 Documentation

| File | Purpose |
|------|---------|
| `discord_auth.py` | Main authentication module |
| `discord_config.ini` | Configuration file (create from template) |
| `DISCORD_AUTH_SETUP.md` | Detailed setup guide |
| `DISCORD_IMPLEMENTATION.md` | Technical implementation details |
| `discord_auth_test.py` | Diagnostic and testing tool |
| `discord_setup_wizard.py` | Interactive setup wizard |

## ❓ Troubleshooting

### "Discord configuration not configured"
→ Run `python discord_setup_wizard.py`

### Browser doesn't open
→ Manually visit authorization URL shown in console

### "Authentication failed"
→ Check CLIENT_ID and CLIENT_SECRET in discord_config.ini

### Need more help?
→ Read `DISCORD_AUTH_SETUP.md` for detailed troubleshooting

## 🎯 What's Included

✅ OAuth2 Authentication
✅ Token Management
✅ User Profile
✅ Webhook Support (optional)
✅ Secure Token Storage
✅ Automatic Token Refresh
✅ Beautiful Login UI
✅ Diagnostic Tools

## 📋 Requirements

- Python 3.7+
- `requests` library (will be installed)
- Discord account
- Modern web browser

## 🔒 Security Features

- HTTPS-only tokens from Discord
- CSRF protection with state validation
- No password handling
- Secure local token storage
- Automatic token expiry
- Environment variable support

---

**Need help?** Check the detailed guides or run the test tool!
