# PUNCTAJ MANAGER - INSTALLER BUILD GUIDE

## 🚀 Quick Start

Creează installerul în 2 pași simpli:

### Option 1: Using PowerShell (RECOMMENDED)
```powershell
cd d:\punctaj
.\BUILD_INSTALLER.ps1
```

### Option 2: Using Command Prompt
```batch
cd d:\punctaj
BUILD_INSTALLER.bat
```

### Option 3: Direct Python
```bash
python BUILD_INSTALLER_COMPLETE.py
```

---

## 📋 Requirements

Before building, ensure you have:

1. **Python 3.8+** installed
   ```bash
   python --version
   ```

2. **Required Python packages** (automatically installed):
   - PyInstaller
   - tkinter (usually included with Python)
   - requests
   - supabase
   - schedule

3. **NSIS** (for creating the installer):
   - Download from: https://nsis.sourceforge.io/Download
   - Or install via: `choco install nsis -y`

4. **Application files** in `d:\punctaj`:
   - `punctaj.py` (main application)
   - `discord_config.ini`
   - `supabase_config.ini`
   - Other required modules

---

## 🔧 Build Process

The installer builder performs these steps:

### 1. Check Python Packages ✓
- Verifies and installs PyInstaller
- Checks for required dependencies

### 2. Create Spec File ✓
- Generates PyInstaller configuration
- Includes data files and hidden imports

### 3. Build Executable ✓
- Compiles Python code to executable
- Creates `Punctaj.exe` in `dist/` directory
- Size: ~40-60 MB

### 4. Create Installer Directory ✓
- Organizes files for installation
- Copies configuration files
- Prepares installer package

### 5. Create NSIS Script ✓
- Generates Windows installer script
- Configures shortcuts and registry entries
- Sets up uninstaller

### 6. Build NSIS Installer ✓
- Creates `Punctaj_Manager_Setup.exe`
- Adds registry entries
- Enables Add/Remove Programs

### 7. Create Manifest ✓
- Documents build information
- Lists requirements and features

### 8. Create README ✓
- Generates installation guide
- Provides system requirements

---

## 📁 Output Files

After successful build, you'll find:

```
installer_output/
├── Punctaj/
│   ├── Punctaj.exe          (Main executable)
│   ├── base_library.zip
│   ├── discord_config.ini
│   ├── supabase_config.ini
│   └── [other dependencies]
├── Punctaj_Installer.nsi    (NSIS script)
└── manifest.json            (Build information)

Punctaj_Manager_Setup.exe    (Final installer - ~100-150 MB)
INSTALLATION_README.txt      (User guide)
```

---

## ⚙️ Configuration

### Before Building

1. **Update icon** (optional):
   - Place `icon.ico` in `d:\punctaj` directory
   - Size: 256x256 or 64x64 pixels

2. **Verify configuration files**:
   - `discord_config.ini` - Discord OAuth2 settings
   - `supabase_config.ini` - Supabase connection

3. **Update version** in `BUILD_INSTALLER_COMPLETE.py`:
   ```python
   "version": "2.0.0",  # Change this
   ```

### After Building

1. **Test the installer**:
   ```bash
   Punctaj_Manager_Setup.exe
   ```

2. **Verify installation**:
   - Check Start Menu shortcut
   - Check Desktop shortcut
   - Verify registry entries
   - Test application launch

---

## 🐛 Troubleshooting

### PyInstaller fails
```
Solution: Install latest version
python -m pip install --upgrade pyinstaller
```

### NSIS not found
```
Solution: Install NSIS
- Download: https://nsis.sourceforge.io/Download
- Or: choco install nsis -y
```

### Missing icon
```
Solution: Create icon.ico or build without it
- The script will skip icon if not found
```

### Large executable size
```
This is normal! PyInstaller includes:
- Python runtime (~50 MB)
- All dependencies
- Application code

Size: 100-150 MB is expected
```

### Antivirus warnings
```
Some antivirus software may flag PyInstaller executables
This is normal and harmless. You can:
1. Add to whitelist
2. Use signed executable (paid certificate)
3. Test with multiple antivirus engines
```

---

## 📦 Distribution

### Package for Distribution

1. **Create ZIP package**:
   ```powershell
   Compress-Archive -Path "Punctaj_Manager_Setup.exe" `
     -DestinationPath "Punctaj_Manager_v2.0.0.zip"
   ```

2. **Create documentation**:
   - Include `INSTALLATION_README.txt`
   - Add `QUICK_START.md`
   - Include changelog

3. **Upload to server**:
   - Host on: GitHub Releases, Google Drive, Dropbox, etc.
   - Provide checksum for verification

### Verify Before Distribution

```powershell
# Get file hash
Get-FileHash "Punctaj_Manager_Setup.exe" -Algorithm SHA256

# File information
Get-Item "Punctaj_Manager_Setup.exe" | 
  Select-Object Name, Length, LastWriteTime
```

---

## 🔐 Security

### Code Signing (Optional)

For production releases, consider code signing:

```powershell
# Requires: Code signing certificate
signtool sign /f "certificate.pfx" /p "password" `
  /t "http://timestamp.server.com" `
  "Punctaj_Manager_Setup.exe"
```

### Virus Scanning

Before distribution, scan with:
- VirusTotal.com
- Windows Defender
- Your preferred antivirus

---

## 📊 Build Customization

### Modify Installer Look & Feel

Edit `BUILD_INSTALLER_COMPLETE.py`:

```python
# Change in create_nsis_script():
Name "Your App Name"
OutFile "YourApp_Setup.exe"
InstallDir "$PROGRAMFILES\Your App"
```

### Add More Data Files

Edit `create_spec_file()`:

```python
datas=[
    ('config_file.ini', '.'),
    ('data_folder', 'data'),
    ('licenses', 'licenses'),
],
```

### Customize Shortcuts

Edit `create_nsis_script()`:

```nsis
CreateDirectory "$SMPROGRAMS\Your App"
CreateShortcut "$SMPROGRAMS\Your App\App.lnk" "$INSTDIR\App.exe"
```

---

## ✅ Checklist Before Release

- [ ] All dependencies installed
- [ ] Application tested and working
- [ ] Configuration files prepared
- [ ] Icon created (optional)
- [ ] Version number updated
- [ ] Build completed without errors
- [ ] Installer tested on clean system
- [ ] Shortcuts created correctly
- [ ] Uninstaller works
- [ ] File size acceptable
- [ ] Antivirus scan passed
- [ ] Documentation complete

---

## 🎯 Next Steps

1. **Run the build script**:
   ```powershell
   .\BUILD_INSTALLER.ps1
   ```

2. **Wait for completion** (~5-10 minutes)

3. **Test the installer**:
   ```
   Double-click Punctaj_Manager_Setup.exe
   ```

4. **Verify everything works**:
   - Shortcuts created
   - Application launches
   - Configuration loads
   - Features functional

5. **Distribute**:
   - Create release package
   - Host online
   - Share with users

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review build logs
3. Check Python/PyInstaller documentation
4. Verify all requirements installed

---

**Version**: 1.0  
**Last Updated**: 2026-02-02  
**Status**: ✅ Ready to use
