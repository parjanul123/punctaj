-- 🔧 INSTALLER SETUP CHECKLIST

## Inainte sa Distribui Instalerele

### ✅ Checklist Pre-Distributie

1. **Copiaza acesti fisieri in folder-ul de bundle**:
   - [ ] `config_resolver.py`
   - [ ] `SETUP_SUPABASE_WIZARD.py`
   - [ ] `DATABASE_CONNECTION_DIAGNOSTIC.py`
   - [ ] `QUICK_TEST_DATABASE.py`
   - [ ] `INSTALLER_README.txt`
   - [ ] `INSTALLER_DATABASE_TROUBLESHOOTING_GUIDE.md`

2. **Verifica ca instalerele au aceste fishiere**:
   - [ ] `installer_gui.py` (UPDATED - cu setup wizard auto)
   - [ ] `installer_app.py` (original - simple setup)
   - [ ] `Punctaj.exe` (compiled main app)

3. **Test instalare pe dispozitiv curat**:
   - [ ] Sterge toate folder-urile Punctaj
   - [ ] Sterge supabase_config.ini
   - [ ] Ruleaza instalerele
   - [ ] Verifica ca Setup Wizard apare
   - [ ] Completeaza configurare
   - [ ] Ruleaza `QUICK_TEST_DATABASE.py`
   - [ ] Verifica ca Punctaj.exe se lanseaza

4. **Copiaza fisierul de configurare**:
   - [ ] Gaseste supabase_config.ini dupa instalare
   - [ ] Verifica ca contine URL si API key corecte
   - [ ] Salveaza-l ca template pentru alte dispozitive

---

## Pentru Utilizatori - Instructiuni Simplificate

**INAINTE de a executa instalerele, du-te la**: `INSTALLER_README.txt`

**DUPA instalare, ruleaza**:
```batch
python QUICK_TEST_DATABASE.py
```

**DACA ceva nu functioneaza**:
```batch
python DATABASE_CONNECTION_DIAGNOSTIC.py
```

---

## Troubleshooting - Dispozitiv Nou

### Simptom 1: "Cannot find supabase_config.ini"

**Reparatie**:
```batch
python SETUP_SUPABASE_WIZARD.py
```

### Simptom 2: "Connection Failed - HTTP 401"

**Reparatie**:
1. Verifica API key in Supabase
2. Re-ruleaza Setup Wizard
3. Re-testeaza cu QUICK_TEST_DATABASE.py

### Simptom 3: "Connection Timeout"

**Reparatie**:
1. Verifica internet connection
2. Verifica firewall
3. Verifica daca Supabase URL e corect

---

## Fisierele Importante

### Pentru Instalare
- `installer_gui.py` - GUI installer (recommended)
- `installer_app.py` - CLI installer (legacy)
- `Punctaj_Installer.nsi` - NSIS installer script

### Pentru Setup Post-Instalare
- `SETUP_SUPABASE_WIZARD.py` - Configuration wizard
- `config_resolver.py` - Auto-find configuration files

### Pentru Diagnostic
- `DATABASE_CONNECTION_DIAGNOSTIC.py` - Full diagnostic
- `QUICK_TEST_DATABASE.py` - Quick test after install

### Documentatie
- `INSTALLER_README.txt` - Quick start guide
- `INSTALLER_DATABASE_TROUBLESHOOTING_GUIDE.md` - Complete guide

---

## Versioning

- v1.0: Initial installer without config resolution
- v2.0: Added config resolver, setup wizard, and diagnostics
- **Current**: v2.0 (PRODUCTION READY)

---

## Testing Scenarios

### Scenario 1: Fresh Install on New Computer
1. Run installer
2. Auto-lanseaza Setup Wizard
3. Introdu Supabase details
4. Run QUICK_TEST_DATABASE.py
5. Launch Punctaj.exe

### Scenario 2: Transfer Config from Old Computer
1. Copy supabase_config.ini from old computer
2. Run installer on new computer
3. Setup Wizard "Load from File"
4. Select the copied config file
5. Run QUICK_TEST_DATABASE.py
6. Launch Punctaj.exe

### Scenario 3: Troubleshooting Connection Issues
1. Run DATABASE_CONNECTION_DIAGNOSTIC.py
2. Review report
3. Follow recommendations
4. Re-run diagnostic

---

## Environment Variables (Optional Setup)

Can be used by installers to find config paths:

```batch
setx PUNCTAJ_CONFIG_PATH "C:\Path\To\Config"
setx PUNCTAJ_APP_PATH "C:\Path\To\App"
```

But normally not needed - auto-discovery handles it.

---

## Build Instructions

### Creating Installer EXE

1. **Compile with PyInstaller**:
```batch
pyinstaller installer_gui.py --onefile --windowed --icon=icon.ico
```

2. **Include data files** in `--collect-all` or `--add-data`

3. **Test exe** before distributing

4. **Sign exe** (optional, recommended for production)

---

**Status**: ✅ Ready for Distribution  
**Last Updated**: 1 Februarie 2026  
**Tested On**: Windows 7, 8, 10, 11
