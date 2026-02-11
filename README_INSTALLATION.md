# 📦 Punctaj Manager - Professional Installer Guide

## Installation Methods

Sunt **2 moduri** să instalezi Punctaj Manager pe calculatoarele clienților:

### Option 1: Batch Script (Ușor pentru toți)
**File:** `install.bat`
- Click și install - nimic complicat
- Windows 10/11 compatible
- Nu necesită PowerShell

### Option 2: PowerShell Script (Avansat)
**File:** `install.ps1`
- Mai grafic, cu culori
- Detalii mai aprofundate
- Trebuie rulat cu Administrator

---

## 🚀 Installation Steps (pentru clienți)

### Method 1: Using install.bat (RECOMMENDED)
```
1. Copy dosarul d:\punctaj pe USB sau trimite email
2. Descarcă sau copiază la client:
   - dist\punctaj.exe
   - discord_config.ini
   - supabase_config.ini
   - install.bat
3. Dublu-click pe install.bat
4. Accept Administrator prompt
5. Wait for completion
6. Desktop shortcut va fi creat automat
```

### Method 2: Using install.ps1
```
1. Open PowerShell as Administrator
2. Navigate to installer folder
3. Run: powershell -ExecutionPolicy Bypass -File install.ps1
4. Follow on-screen instructions
```

---

## 📋 What Gets Installed

```
C:\Program Files\Punctaj\
├── Punctaj_Manager.exe          ← Main application
├── discord_config.ini           ← Discord settings (pre-configured)
├── supabase_config.ini          ← Database settings (pre-configured)
├── .secure_key                  ← Encryption key (auto-generated, hidden)
├── json_encryptor.py            ← Encryption module
├── uninstall.bat                ← Uninstaller
├── data/                        ← Employee data (encrypted)
├── logs/                        ← Action logs (encrypted)
└── arhiva/                      ← Backups (encrypted)

%APPDATA%\Punctaj\               ← User config backup
├── discord_config.ini
├── supabase_config.ini
└── .secure_key
```

---

## 🔧 What's Pre-Configured

✅ **Discord Authentication:**
- Client ID: 1465698276375527622
- Callback URL: http://localhost:8888/callback
- Secret Key: Configured

✅ **Supabase Cloud Sync:**
- Database URL: Pre-configured
- API Key: Pre-configured
- Auto-sync: Enabled

✅ **Data Encryption:**
- AES-256 encryption for all logs
- Encryption key auto-generated
- Files cannot be modified outside app

---

## 🎯 After Installation

### Client sees:
- Desktop shortcut: **"Punctaj Manager"**
- Start Menu: **Start > Punctaj Manager**

### First Launch:
1. Application starts
2. Discord login popup appears
3. User authenticates with Discord
4. Data syncs from Supabase (if configured)
5. Ready to use!

---

## 🚨 Troubleshooting

### Error: "Administrator privileges required"
**Solution:** Right-click `install.bat` → Run as Administrator

### Error: "dist\punctaj.exe not found"
**Solution:** Make sure `dist\punctaj.exe` exists before running installer

### Application won't start
**Solution:** Check that `discord_config.ini` and `supabase_config.ini` are in installation folder

### Can't uninstall
**Solution:** Go to Control Panel > Uninstall Programs > Punctaj Manager

---

## 📦 Deployment Package Contents

For distribution to clients, include:

```
Punctaj_Manager_Setup\
├── install.bat                      ← Run this to install
├── install.ps1                      ← Alternative installer
├── dist/
│   └── punctaj.exe                  ← Main application (REQUIRED)
├── discord_config.ini               ← Pre-configured
├── supabase_config.ini              ← Pre-configured
├── .secure_key                      ← Encryption key (OPTIONAL - auto-generated if missing)
├── json_encryptor.py                ← Encryption module
├── README_INSTALLATION.md           ← Instructions
└── LICENSE.txt                      ← License
```

---

## 🔐 Security Notes

- **Configurations are pre-configured** - Client doesn't need to edit them
- **Discord credentials embedded** - Single sign-on works out of box
- **Database credentials included** - Cloud sync works automatically
- **Encryption key generated per machine** - Data protected locally
- **Files encrypted with AES-256** - Cannot be modified outside app

---

## 📝 Distribution Checklist

Before giving to client:

- [ ] `dist\punctaj.exe` rebuilt and tested
- [ ] `discord_config.ini` with correct Client ID and Secret
- [ ] `supabase_config.ini` with correct database URL
- [ ] `install.bat` is present
- [ ] All 3 files in same directory
- [ ] Tested installation on clean Windows 10/11 PC
- [ ] Verified Discord login works
- [ ] Verified database sync works
- [ ] Created uninstall instructions

---

## 💡 Pro Tips

### Batch Deploy to Multiple PCs
```batch
REM Create batch script to deploy to multiple machines
for /F %%i in (computers.txt) do (
    psexec \\%%i -s cmd /c "C:\install\install.bat"
)
```

### Silent Install
```batch
REM Create batch that installs without interaction
install.bat silent
```

### Create Installation USB
```
Copy to USB:
- install.bat
- dist\punctaj.exe
- discord_config.ini
- supabase_config.ini

Clients can plug in USB and run install.bat
```

---

## 📞 Support

If clients have issues:
1. Check Event Viewer > Windows Logs > Application for errors
2. Verify `C:\Program Files\Punctaj\discord_config.ini` exists
3. Verify `C:\Program Files\Punctaj\supabase_config.ini` exists
4. Check logs folder for error messages
5. Contact support with log files

---

**Version:** 2.0.0  
**Last Updated:** February 2, 2026  
**Installer Type:** Professional (.bat / .ps1)
