# Punctaj Manager - Installation & Distribution Guide

## 🚀 Quick Start

### Pentru Utilisatori Finali (Pre-built EXE)
1. Descarcă `PunctajManager.exe` din folderul `dist/`
2. Dublu-click pe EXE pentru a rula
3. Aplicația va crea automat folderele necesare

### Pentru Dezvoltatori (Development)
1. Asigură-te că ai Python 3.8+ instalat
2. Rulează `installer.bat` - va instala totul automat
3. După, poți rula aplicația din Desktop shortcut

---

## 📦 Installation Process

### Automated Installation (Recomandat)
```bash
installer.bat
```

Aceasta va:
- ✅ Verifica dacă Python este instalat
- ✅ Crea virtual environment
- ✅ Instala toate dependențele
- ✅ Build-a EXE-ul
- ✅ Crea shortcut pe Desktop

### Manual Installation
```bash
# 1. Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build EXE
python setup.py

# 4. Run (opțional)
dist\PunctajManager.exe
```

---

## 🔧 Rebuild after Changes

Dacă modifici `punctaj.py` și vrei EXE nou:
```bash
build.bat
```

Sau manual:
```bash
call venv\Scripts\activate.bat
python setup.py
```

---

## 📋 Requirements

- **Python 3.8+** - [Descarcă de aici](https://www.python.org/downloads/)
- **Dependencies** (instalate automat):
  - `GitPython` - Git integration
  - `schedule` - Task scheduling
  - `pyinstaller` - Build to EXE

---

## 📂 File Structure

```
punctaj/
├── punctaj.py              # Main application
├── setup.py                # PyInstaller configuration
├── requirements.txt        # Dependencies list
├── installer.bat           # Automated installer
├── build.bat              # Quick rebuild script
├── README.md              # This file
├── data/                  # User data folder (created at runtime)
├── arhiva/                # Archive folder (created at runtime)
├── venv/                  # Virtual environment (created by installer)
└── dist/                  # Build output
    └── PunctajManager.exe # Final executable
```

---

## 🎯 Usage

### First Run
1. Click `PunctajManager.exe` in `dist/` folder
2. Add a city (e.g., "BlackWater")
3. Add institutions (e.g., "Politie")
4. Start managing scores!

### Git Integration
- Auto-commits every change to Git
- Auto-pulls every 5 minutes
- Setup remote: `git remote add origin <URL>`

### Auto-Reset
- Automatically resets scores on 1st of month at 00:00
- Archives old data in CSV
- Updates all timestamps

---

## 🐛 Troubleshooting

### Python not found
```
Error: Python not installed or not in PATH
```
**Solution:** 
- Download Python from python.org
- Check "Add Python to PATH" during installation
- Restart your computer

### PyInstaller errors
```
Error: Building failed
```
**Solution:**
```bash
pip install --upgrade pyinstaller
python setup.py
```

### Git errors
```
Error: Git not found
```
**Note:** Git sync is optional. Application works without it.

---

## 📝 Version Info

- **App Version:** 1.0
- **Python Required:** 3.8+
- **Build Tool:** PyInstaller 6.1.0
- **Last Updated:** January 2026

---

## 💾 Data Location

All user data is stored in:
- `data/` - JSON files with scores
- `arhiva/` - CSV archives of resets

Both folders are created automatically on first run.

---

## 🔐 Git Setup (Optional)

To enable Git sync with team:

```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit"

# Add remote repository
git remote add origin https://github.com/yourname/punctaj.git
git branch -M main
git push -u origin main
```

After this, changes auto-sync every 5 minutes!

---

## 📞 Support

For issues or questions:
1. Check the console output (if running from CMD)
2. Check data integrity (JSON files should be valid)
3. Ensure Python 3.8+ is installed

---

**Enjoy Punctaj Manager! 🎉**
"# punctaj" 
