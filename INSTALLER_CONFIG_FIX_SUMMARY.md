# 🔧 Installer Configuration Discovery Fix - Session Summary

## Problem Identified
After running `punctaj_installer.exe` and installing the application to `C:\Program Files\Punctaj\`, the installed `punctaj.exe` could not authenticate with Discord because the `supabase_config.ini` file was not being found.

## Root Cause
The `discord_auth.py` module was searching for `supabase_config.ini` in these paths:
- Home directory (`~/.punctaj`)
- Linux config paths (`~/.config/punctaj`)
- Current working directory (`os.getcwd()`)
- Script directory

**What was missing**: The EXE's own installation directory (`C:\Program Files\Punctaj\`)

When `punctaj.exe` runs from `C:\Program Files\Punctaj\`, the `os.getcwd()` is typically the user's home directory or last working directory, NOT the installation directory. This caused the config file discovery to fail.

## Solution Implemented

### Changes to `discord_auth.py`

**Location 1: `_save_to_supabase()` method (lines 176-203)**
- Added `meipass = getattr(sys, '_MEIPASS', None)` for bundled app detection
- Added `exe_dir = os.path.dirname(sys.executable)` to find EXE directory
- Updated config search paths to include:
  1. `os.path.join(meipass, "supabase_config.ini")` - bundled location
  2. `os.path.join(exe_dir, "supabase_config.ini")` - **Installation directory** ✓ NEW
  3. `os.path.dirname(sys.executable)` - **EXE's directory** ✓ NEW
  4. `os.path.dirname(__file__)` - Script directory
  5. `os.getcwd()` - Current working directory
  6. Home documents folder
  7. `"supabase_config.ini"` - Relative path

**Location 2: `_fetch_user_role_from_supabase()` method (lines 229-256)**
- Applied identical changes for consistency
- Ensures both authentication paths use the same config discovery logic

### Key Addition
```python
exe_dir = os.path.dirname(sys.executable) if hasattr(sys, 'executable') else None
```
This ensures the config file is found in the same directory as the running `punctaj.exe`, which is where the installer copies it.

## Rebuild Process

### Step 1: Update discord_auth.py ✅
- Modified both config search locations in `discord_auth.py`
- Copied updated version to `setup_output/exe/discord_auth.py`

### Step 2: Rebuild punctaj.exe ✅
```bash
cd D:\punctaj
python -m PyInstaller --onefile --windowed --name punctaj --distpath dist --icon=NONE punctaj.py
```
- Result: `D:\punctaj\dist\punctaj.exe` (19.46 MB)
- Detects: discord_auth.py changed, rebuilds with new search logic

### Step 3: Rebuild punctaj_installer.exe ✅
```bash
python build_installer_final.py
```
- Result: `D:\punctaj\dist\punctaj_installer.exe` (30.88 MB)
- Packages updated punctaj.exe with all necessary config files

## Installation Flow (Now Fixed)

1. **User runs** `punctaj_installer.exe`
2. **Installer copies**:
   - `punctaj.exe` → `C:\Program Files\Punctaj\punctaj.exe`
   - `supabase_config.ini` → `C:\Program Files\Punctaj\supabase_config.ini`
   - Discord config → `C:\Program Files\Punctaj\discord_config.ini`
3. **User runs installed** `C:\Program Files\Punctaj\punctaj.exe`
4. **discord_auth.py searches** for configs in this order:
   - `sys._MEIPASS` (if bundled)
   - **`C:\Program Files\Punctaj\` ← NOW INCLUDED!** ✓
   - `os.path.dirname(__file__)`
   - Current directory
   - Home Documents
   - Relative path
5. **Config found** → Discord authentication succeeds ✅

## Files Modified

| File | Changes | Location |
|------|---------|----------|
| discord_auth.py | Added EXE dir to config search | Lines 176-203, 229-256 |
| setup_output/exe/discord_auth.py | Synced with main version | Updated |
| dist/punctaj.exe | Rebuilt with updated logic | 19.46 MB |
| dist/punctaj_installer.exe | Rebuilt with new EXE | 30.88 MB |

## Testing Instructions

1. **Run the installer**: `D:\punctaj\dist\punctaj_installer.exe`
2. **Choose installation path** (default: `C:\Program Files\Punctaj\`)
3. **Complete installation**
4. **Run installed EXE**: `C:\Program Files\Punctaj\punctaj.exe`
5. **Verify**: User should be able to login via Discord

## Expected Debug Output
When running the installed EXE, you should see in console:
```
[DEBUG] Found config at: C:\Program Files\Punctaj\supabase_config.ini
```

## Why This Works Now
- The search path `os.path.dirname(sys.executable)` directly points to where the EXE is located
- This is exactly where the installer copies the config file
- No matter where the user runs the EXE from, or what the current directory is, the config will be found in the same directory as the executable
- This is the same approach used in `punctaj.py` for loading `discord_config.ini` (see lines 88-89)

## Backwards Compatibility
✅ The fix maintains backwards compatibility:
- Still checks home directory for user-customized configs
- Still checks Documents folder
- Still accepts relative paths
- Just adds additional search paths specific to installation scenarios

## Related Files
- `build_installer_final.py` - Generates the installer
- `_setup_final.py` - Generated installer script with file copying logic
- `supabase_sync.py` - Database connection module
- `punctaj.py` - Main application (already had correct search paths)
