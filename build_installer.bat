@echo off
REM Installer script for Punctaj Application
REM Creates the final installer package

echo ========================================
echo Punctaj Application Build & Package
echo ========================================
echo.

REM Clean previous builds
if exist dist (
    echo Cleaning previous build...
    rmdir /s /q dist
)
if exist build (
    rmdir /s /q build
)
if exist installer_outputs (
    rmdir /s /q installer_outputs
)

REM Create installer output directory
mkdir installer_outputs
echo ✓ Created installer_outputs directory
echo.

REM Build executable with PyInstaller
echo Building executable...
pyinstaller punctaj.spec --distpath dist --buildpath build
if errorlevel 1 (
    echo ✗ PyInstaller build failed
    exit /b 1
)
echo ✓ Executable built successfully
echo.

REM Create necessary folders in dist/Punctaj/
echo Creating application directories...
mkdir "dist\Punctaj\data" 2>nul
mkdir "dist\Punctaj\arhiva" 2>nul
mkdir "dist\Punctaj\logs" 2>nul
echo ✓ Directories created
echo.

REM Copy initial data structure (if exists locally)
echo Copying data structure...
if exist "data" (
    xcopy data "dist\Punctaj\data" /E /I /Y >nul 2>&1
    echo ✓ Data directory copied
) else (
    echo ! Data directory not found (will be created on first run)
)
if exist "arhiva" (
    xcopy arhiva "dist\Punctaj\arhiva" /E /I /Y >nul 2>&1
    echo ✓ Archive directory copied
)
echo.

REM Copy config files
echo Copying configuration files...
if exist "discord_config.ini" (
    copy "discord_config.ini" "dist\Punctaj\" /Y >nul
    echo ✓ discord_config.ini copied
)
if exist "supabase_config.ini" (
    copy "supabase_config.ini" "dist\Punctaj\" /Y >nul
    echo ✓ supabase_config.ini copied
)
echo.

REM Create README for users
echo Creating README...
(
echo # Punctaj Application
echo.
echo ## Installation Instructions
echo.
echo 1. Extract the ZIP file to your desired location
echo 2. Run Punctaj.exe
echo 3. The app will create necessary folders automatically
echo.
echo ## Folders
echo.
echo - `data/` - Employee data by city and institution
echo - `arhiva/` - Archived punctaj records
echo - `logs/` - Application logs
echo.
echo ## Configuration
echo.
echo Before running:
echo - Edit `discord_config.ini` with your Discord credentials (optional^)
echo - Edit `supabase_config.ini` with your Supabase credentials
echo.
echo ## Support
echo.
echo For issues, check the logs folder for detailed error messages.
) > "dist\Punctaj\README.txt"
echo ✓ README created
echo.

REM Create a shortcut launcher script
echo Creating launcher script...
(
echo @echo off
echo cd /d "%%~dp0"
echo start Punctaj.exe
) > "dist\Punctaj\DESCHIDE.bat"
echo ✓ Launcher script created
echo.

REM Zip the application
echo.
echo Packaging into ZIP...
cd installer_outputs
cd ..
if exist "Punctaj.zip" (
    del "Punctaj.zip"
)

REM Use PowerShell to create ZIP (more reliable on Windows)
powershell -NoProfile -Command "Compress-Archive -Path 'dist\Punctaj' -DestinationPath 'installer_outputs\Punctaj.zip' -Force"
if errorlevel 1 (
    echo ✗ ZIP creation failed
    exit /b 1
)
echo ✓ ZIP created: installer_outputs\Punctaj.zip
echo.

REM Copy the built app to installer_outputs
echo Copying built application...
xcopy "dist\Punctaj" "installer_outputs\Punctaj" /E /I /Y >nul
echo ✓ Application copied to installer_outputs\Punctaj
echo.

REM Create a manifest file
echo Creating installation manifest...
(
echo Build Date: %date% %time%
echo Build Version: 1.0
echo Files Included:
echo - Punctaj.exe (Main application^)
echo - data/ (Employee data directory^)
echo - arhiva/ (Archive directory^)
echo - logs/ (Logs directory^)
echo - discord_config.ini (Discord configuration^)
echo - supabase_config.ini (Supabase configuration^)
echo - DESCHIDE.bat (Quick launcher^)
echo.
echo Installation Notes:
echo - Extract Punctaj.zip
echo - Run Punctaj.exe or DESCHIDE.bat
echo - Application is standalone and includes all dependencies
) > "installer_outputs\MANIFEST.txt"
echo ✓ Manifest created
echo.

REM Create install instructions
echo Creating installation guide...
(
echo # Punctaj Application - Installation Guide
echo.
echo ## Quick Start
echo.
echo 1. Download Punctaj.zip
echo 2. Right-click and select "Extract All..." or use 7-Zip, WinRAR
echo 3. Open the extracted folder
echo 4. Double-click DESCHIDE.bat or Punctaj.exe
echo.
echo ## Minimum Requirements
echo.
echo - Windows 7 or later
echo - No Python installation required ^(standalone executable^)
echo.
echo ## First Run
echo.
echo - Application will create necessary folders
echo - Configure Supabase in supabase_config.ini if needed
echo.
echo ## Support
echo.
echo Check logs/ folder for detailed information if issues occur.
) > "installer_outputs\INSTALLATION_GUIDE.txt"
echo ✓ Installation guide created
echo.

echo ========================================
echo ✓ Build Complete!
echo ========================================
echo.
echo Output location: installer_outputs\
echo - Punctaj.zip (Full packaged application^)
echo - Punctaj\ (Uncompressed application folder^)
echo - MANIFEST.txt (Installation manifest^)
echo - INSTALLATION_GUIDE.txt (Installation instructions^)
echo.
pause
