@echo off
REM ==========================================
REM Punctaj Application Build & Package v2.0
REM Includes config resolver and setup wizard
REM ==========================================

echo.
echo ==========================================
echo  Punctaj Application Build v2.0
echo  with Config Resolver & Setup Wizard
echo ==========================================
echo.

setlocal enabledelayedexpansion

REM Colors
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "CYAN=[96m"
set "RESET=[0m"

REM Paths
set "DIST_DIR=dist\Punctaj"
set "INSTALLER_OUT=installer_outputs"
set "BUILD_LOG=build.log"

echo [INFO] Starting build process...
echo.

REM ========================================
REM STEP 1: Clean previous builds
REM ========================================
echo [STEP 1] Cleaning previous builds...
if exist dist (
    echo   Removing dist directory...
    rmdir /s /q dist >nul 2>&1
)
if exist build (
    echo   Removing build directory...
    rmdir /s /q build >nul 2>&1
)
if exist "%INSTALLER_OUT%" (
    echo   Removing installer_outputs directory...
    rmdir /s /q "%INSTALLER_OUT%" >nul 2>&1
)
mkdir "%INSTALLER_OUT%"
echo [OK] Clean complete
echo.

REM ========================================
REM STEP 2: Build main executable
REM ========================================
echo [STEP 2] Building main executable with PyInstaller...
echo   This may take a few minutes...

if exist "punctaj.spec" (
    pyinstaller punctaj.spec --distpath dist --buildpath build >"%BUILD_LOG%" 2>&1
) else (
    echo [ERROR] punctaj.spec not found
    exit /b 1
)

if not exist "dist\Punctaj\Punctaj.exe" (
    echo [ERROR] Build failed - Punctaj.exe not created
    echo   Check build.log for details
    exit /b 1
)
echo [OK] Punctaj.exe created successfully
echo.

REM ========================================
REM STEP 3: Create application directories
REM ========================================
echo [STEP 3] Creating application directories...
mkdir "%DIST_DIR%\data" 2>nul
mkdir "%DIST_DIR%\arhiva" 2>nul
mkdir "%DIST_DIR%\logs" 2>nul
echo [OK] Directories created
echo.

REM ========================================
REM STEP 4: Copy NEW files (Config Resolver + Wizard)
REM ========================================
echo [STEP 4] Copying NEW support files...

set "NEW_FILES=^
    config_resolver.py ^
    SETUP_SUPABASE_WIZARD.py ^
    DATABASE_CONNECTION_DIAGNOSTIC.py ^
    QUICK_TEST_DATABASE.py ^
    INSTALLER_README.txt ^
    INSTALLER_DATABASE_TROUBLESHOOTING_GUIDE.md"

for %%F in (%NEW_FILES%) do (
    if exist "%%F" (
        copy "%%F" "%DIST_DIR%\" /Y >nul 2>&1
        echo   [+] %%F
    ) else (
        echo   [!] %%F NOT FOUND - will be missing!
    )
)
echo [OK] Support files copied
echo.

REM ========================================
REM STEP 5: Copy configuration files
REM ========================================
echo [STEP 5] Copying configuration templates...

if exist "discord_config.ini" (
    copy "discord_config.ini" "%DIST_DIR%\" /Y >nul 2>&1
    echo [OK] discord_config.ini copied
) else (
    echo [!] discord_config.ini not found
)

if exist "supabase_config.ini" (
    copy "supabase_config.ini" "%DIST_DIR%\" /Y >nul 2>&1
    echo [OK] supabase_config.ini copied
) else (
    echo [!] supabase_config.ini not found (will need to be created)
)
echo.

REM ========================================
REM STEP 6: Copy installer scripts
REM ========================================
echo [STEP 6] Copying installer scripts...

set "INSTALLER_FILES=^
    installer_gui.py ^
    installer_app.py"

for %%F in (%INSTALLER_FILES%) do (
    if exist "%%F" (
        copy "%%F" "%DIST_DIR%\" /Y >nul 2>&1
        echo [OK] %%F copied
    )
)
echo.

REM ========================================
REM STEP 7: Copy data structure if exists
REM ========================================
echo [STEP 7] Copying initial data...

if exist "data" (
    echo   Copying data directory...
    xcopy data "%DIST_DIR%\data" /E /I /Y >nul 2>&1
    echo [OK] Data directory copied
) else (
    echo [!] Data directory not found (will be created on first run)
)

if exist "arhiva" (
    echo   Copying archive directory...
    xcopy arhiva "%DIST_DIR%\arhiva" /E /I /Y >nul 2>&1
    echo [OK] Archive directory copied
)
echo.

REM ========================================
REM STEP 8: Create documentation files
REM ========================================
echo [STEP 8] Creating documentation...

(
echo # Punctaj Application v2.0 - Installer Package
echo.
echo ## Quick Start (Setup Wizard)
echo.
echo After installation, the Setup Wizard will automatically appear:
echo 1. Load configuration from file (if you have one from another device)
echo 2. OR enter Supabase URL and API key manually
echo 3. Test connection
echo 4. Save configuration
echo.
echo ## Manual Setup (if needed^)
echo.
echo Run: python SETUP_SUPABASE_WIZARD.py
echo.
echo ## Verify Installation
echo.
echo Run: python QUICK_TEST_DATABASE.py
echo.
echo This will test:
echo - Configuration file found
echo - Configuration valid
echo - Database connection working
echo.
echo ## Troubleshooting
echo.
echo Run: python DATABASE_CONNECTION_DIAGNOSTIC.py
echo.
echo This will:
echo - Search for configuration in multiple locations
echo - Validate configuration
echo - Test database connection
echo - Provide detailed diagnostics
echo.
echo ## Configuration Files
echo.
echo - supabase_config.ini - Supabase connection settings
echo - discord_config.ini - Discord OAuth settings (optional^)
echo.
echo ## Folders
echo.
echo - data/ - Employee records by city/institution
echo - arhiva/ - Archived punctaj records
echo - logs/ - Application logs
echo.
echo ## System Requirements
echo.
echo - Windows 7 or later
echo - 100 MB free disk space
echo - Internet connection (for cloud sync^)
echo.
echo ## Version
echo.
echo Version: 2.0
echo Date: 1 February 2026
echo Status: Production Ready
) > "%DIST_DIR%\SETUP_INSTRUCTIONS.txt"
echo [OK] Documentation created
echo.

REM ========================================
REM STEP 9: Create installer packages
REM ========================================
echo [STEP 9] Creating installer packages...

REM Create simple ZIP installer
echo   Creating ZIP package...
powershell -Command "Compress-Archive -Path dist\Punctaj -DestinationPath '%INSTALLER_OUT%\Punctaj_Portable.zip' -Force" >nul 2>&1

if exist "%INSTALLER_OUT%\Punctaj_Portable.zip" (
    for /f "delims=" %%A in ('powershell -Command "[math]::Round((Get-Item '%INSTALLER_OUT%\Punctaj_Portable.zip').Length / 1MB, 2)"') do (
        set "ZIP_SIZE=%%A"
    )
    echo [OK] Punctaj_Portable.zip created (!ZIP_SIZE! MB^)
) else (
    echo [!] ZIP creation failed
)
echo.

REM ========================================
REM STEP 10: Create standalone executable
REM ========================================
echo [STEP 10] Creating standalone installer...
echo   Note: This requires NSIS to be installed
echo.

if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo   Compiling NSIS installer...
    "C:\Program Files (x86)\NSIS\makensis.exe" "Punctaj_Installer.nsi" /DOUTDIR="%INSTALLER_OUT%" >nul 2>&1
    
    if exist "%INSTALLER_OUT%\Punctaj_Installer.exe" (
        for /f "delims=" %%A in ('powershell -Command "[math]::Round((Get-Item '%INSTALLER_OUT%\Punctaj_Installer.exe').Length / 1MB, 2)"') do (
            set "EXE_SIZE=%%A"
        )
        echo [OK] Punctaj_Installer.exe created (!EXE_SIZE! MB^)
    ) else (
        echo [!] NSIS installer creation failed
    )
) else (
    echo [!] NSIS not found - skipping .exe installer
    echo    Install NSIS for standalone executable: https://nsis.sourceforge.io/
)
echo.

REM ========================================
REM STEP 11: Generate build summary
REM ========================================
echo [STEP 11] Generating build summary...

(
echo ===========================================
echo   PUNCTAJ BUILD SUMMARY
echo ===========================================
echo.
echo BUILD INFORMATION:
echo   Date: %date% %time%
echo   Version: 2.0
echo   Build Type: Full Application + Installers
echo.
echo EXECUTABLE:
echo   Location: dist\Punctaj\Punctaj.exe
echo   Status: Created
echo.
echo NEW FEATURES INCLUDED:
echo   - config_resolver.py (auto-config discovery^)
echo   - SETUP_SUPABASE_WIZARD.py (GUI setup wizard^)
echo   - DATABASE_CONNECTION_DIAGNOSTIC.py (diagnostics^)
echo   - QUICK_TEST_DATABASE.py (quick verification^)
echo.
echo INSTALLER PACKAGES:
) > "%INSTALLER_OUT%\BUILD_SUMMARY.txt"

if exist "%INSTALLER_OUT%\Punctaj_Portable.zip" (
    echo   - Punctaj_Portable.zip (ZIP archive - portable^) >> "%INSTALLER_OUT%\BUILD_SUMMARY.txt"
)

if exist "%INSTALLER_OUT%\Punctaj_Installer.exe" (
    echo   - Punctaj_Installer.exe (Windows installer - recommended^) >> "%INSTALLER_OUT%\BUILD_SUMMARY.txt"
)

(
echo.
echo FILES IN PACKAGE:
echo   - Punctaj.exe (main application^)
echo   - config_resolver.py
echo   - SETUP_SUPABASE_WIZARD.py
echo   - DATABASE_CONNECTION_DIAGNOSTIC.py
echo   - QUICK_TEST_DATABASE.py
echo   - installer_gui.py
echo   - installer_app.py
echo   - supabase_config.ini (template^)
echo   - discord_config.ini (template^)
echo   - SETUP_INSTRUCTIONS.txt
echo.
echo USAGE:
echo   1. Run Punctaj_Installer.exe OR extract Punctaj_Portable.zip
echo   2. Setup Wizard will appear automatically
echo   3. Follow wizard to configure Supabase
echo   4. Run QUICK_TEST_DATABASE.py to verify
echo   5. Launch Punctaj.exe
echo.
echo BUILD STATUS: SUCCESS
echo ===========================================
) >> "%INSTALLER_OUT%\BUILD_SUMMARY.txt"

type "%INSTALLER_OUT%\BUILD_SUMMARY.txt"
echo.

REM ========================================
REM FINAL SUMMARY
REM ========================================
echo.
echo ==========================================
echo  BUILD COMPLETE!
echo ==========================================
echo.
echo Installer packages ready in: %INSTALLER_OUT%
echo.
echo Files created:
if exist "%INSTALLER_OUT%\Punctaj_Portable.zip" (
    echo   ✓ Punctaj_Portable.zip
)
if exist "%INSTALLER_OUT%\Punctaj_Installer.exe" (
    echo   ✓ Punctaj_Installer.exe
)
echo   ✓ BUILD_SUMMARY.txt
echo.
echo Next steps:
echo   1. Copy installers to USB or share online
echo   2. Run on target device
echo   3. Setup Wizard will guide configuration
echo.
echo ==========================================
echo.

REM Cleanup
if exist "%BUILD_LOG%" del "%BUILD_LOG%"

endlocal
