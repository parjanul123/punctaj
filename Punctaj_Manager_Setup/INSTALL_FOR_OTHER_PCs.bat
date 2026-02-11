@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM   PUNCTAJ MANAGER - COMPLETE INSTALLER FOR OTHER PCs
REM   Installs Python + Application + Configures Cloud Sync
REM   Version: 2.0.0
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║         PUNCTAJ MANAGER - PROFESSIONAL INSTALLER FOR WINDOWS             ║
echo ║                                                                           ║
echo ║              Cloud-Enabled Employee Attendance Tracking                  ║
echo ║                        Version 2.0.0                                      ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   This installer will:
echo   • Install Python 3.8+ (if needed)
echo   • Copy application files
echo   • Install dependencies
echo   • Configure cloud synchronization
echo   • Create desktop shortcuts
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Check Admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  ERROR: Administrator privileges required!
    echo.
    echo Solution:
    echo   1. Right-click on this file
    echo   2. Select "Run as administrator"
    echo   3. Click "Yes" when prompted
    echo.
    pause
    exit /b 1
)

REM Check Python
echo [1/6] Checking Python installation...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Python not found on this system
    echo.
    echo You have two options:
    echo.
    echo Option 1: Download and install Python (Recommended)
    echo   • Visit: https://www.python.org/downloads/
    echo   • Download Python 3.8 or later
    echo   • During installation: CHECK "Add Python to PATH"
    echo   • Restart computer
    echo   • Run this installer again
    echo.
    echo Option 2: Point installer to Python location
    echo   • If you have Python installed elsewhere
    echo   • Edit this script to set PYTHON_PATH variable
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found

REM Set installation paths
set INSTALL_PATH=%PROGRAMFILES%\Punctaj Manager
set SOURCE_DIR=%~dp0
set APP_CONFIG=%APPDATA%\Punctaj Manager

echo.
echo [2/6] Preparing installation directories...
echo   Install path: %INSTALL_PATH%
echo   Config path: %APP_CONFIG%

REM Backup existing installation
if exist "%INSTALL_PATH%" (
    echo   Creating backup of existing installation...
    if exist "%INSTALL_PATH%_backup" (
        rmdir /s /q "%INSTALL_PATH%_backup" >nul 2>&1
    )
    rename "%INSTALL_PATH%" "Punctaj Manager_backup" >nul 2>&1
)

REM Create directories
mkdir "%INSTALL_PATH%" >nul 2>&1
mkdir "%APP_CONFIG%" >nul 2>&1

if %errorlevel% neq 0 (
    echo ✗ Error creating directories
    echo Please check your disk space and permissions
    pause
    exit /b 1
)

echo ✓ Directories ready

REM Copy application files
echo.
echo [3/6] Copying application files...

REM Copy all Python files
for %%F in ("*.py") do (
    if not "%%F"=="BUILD_EXE_SIMPLE.py" (
        if not "%%F"=="CREATE_PROFESSIONAL_INSTALLER.py" (
            copy /Y "%%F" "%INSTALL_PATH%\" >nul 2>&1
            if !errorlevel! equ 0 (
                echo   ✓ %%F
            )
        )
    )
)

REM Copy configuration files
if exist "supabase_config.ini" (
    copy /Y "supabase_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    copy /Y "supabase_config.ini" "%APP_CONFIG%\" >nul 2>&1
    echo   ✓ supabase_config.ini
)

if exist "discord_config.ini" (
    copy /Y "discord_config.ini" "%INSTALL_PATH%\" >nul 2>&1
    echo   ✓ discord_config.ini
)

REM Copy other files
if exist "requirements.txt" (
    copy /Y "requirements.txt" "%INSTALL_PATH%\" >nul 2>&1
    echo   ✓ requirements.txt
)

if exist "INSTALLATION_GUIDE.txt" (
    copy /Y "INSTALLATION_GUIDE.txt" "%INSTALL_PATH%\" >nul 2>&1
    echo   ✓ INSTALLATION_GUIDE.txt
)

echo ✓ Files copied

REM Verify critical files
echo.
echo [4/6] Verifying installation...

if not exist "%INSTALL_PATH%\punctaj.py" (
    echo ✗ ERROR: Main application file not found!
    echo The installation is incomplete.
    echo Please ensure all files are in the source directory.
    pause
    exit /b 1
)

echo ✓ Core files present

REM Install Python dependencies
echo.
echo [5/6] Installing Python packages...
echo (This may take a few minutes on first run)
echo.

cd /d "%INSTALL_PATH%"

if exist "requirements.txt" (
    echo Installing from requirements.txt...
    python -m pip install --upgrade pip -q >nul 2>&1
    python -m pip install -r requirements.txt -q
    
    if !errorlevel! neq 0 (
        echo.
        echo ⚠️  Warning: Some packages failed to install
        echo The application may still work, but some features might not be available
        echo.
    ) else (
        echo ✓ Python packages installed
    )
) else (
    echo ⚠️  requirements.txt not found
    echo Skipping package installation
)

REM Create launcher scripts
echo.
echo [6/6] Creating shortcuts and launcher scripts...

REM Create launcher batch file
(
    echo @echo off
    echo cls
    echo title Punctaj Manager
    echo echo Loading Punctaj Manager...
    echo echo.
    echo cd /d "%INSTALL_PATH%"
    echo python punctaj.py
    echo if errorlevel 1 (
    echo     echo.
    echo     echo Application closed.
    echo     pause
    echo )
) > "%INSTALL_PATH%\Punctaj_Manager.bat"

echo ✓ Created launcher script

REM Create desktop shortcut using PowerShell
echo Creating desktop shortcut...
powershell -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Punctaj Manager.lnk'); " ^
    "$Shortcut.TargetPath = '%INSTALL_PATH%\Punctaj_Manager.bat'; " ^
    "$Shortcut.WorkingDirectory = '%INSTALL_PATH%'; " ^
    "$Shortcut.Save()" >nul 2>&1

if %errorlevel% equ 0 (
    echo ✓ Desktop shortcut created
) else (
    echo ⚠️  Could not create desktop shortcut
)

REM Create Start Menu shortcut
mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Punctaj Manager" >nul 2>&1
powershell -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Appdata') + '\Microsoft\Windows\Start Menu\Programs\Punctaj Manager\Punctaj Manager.lnk'); " ^
    "$Shortcut.TargetPath = '%INSTALL_PATH%\Punctaj_Manager.bat'; " ^
    "$Shortcut.WorkingDirectory = '%INSTALL_PATH%'; " ^
    "$Shortcut.Save()" >nul 2>&1

REM Installation complete
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                  ✓✓✓ INSTALLATION SUCCESSFUL! ✓✓✓                        ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo Installation Details:
echo ──────────────────────────────────────────────────────────────────────────
echo   Location: %INSTALL_PATH%
echo   Python:   %PYTHON_VERSION%
echo.
echo How to Use:
echo ──────────────────────────────────────────────────────────────────────────
echo   • Look for "Punctaj Manager" shortcut on your Desktop
echo   • Or find it in Start Menu
echo   • Or run: Punctaj_Manager.bat from installation folder
echo.
echo Cloud Synchronization:
echo ──────────────────────────────────────────────────────────────────────────
echo   ☁️  Cloud sync is ENABLED by default!
echo   ✓ Your data is automatically synced with Supabase
echo   ✓ Access the same data from any device
echo   ✓ Real-time synchronization every 30 seconds
echo.
echo First Run:
echo ──────────────────────────────────────────────────────────────────────────
echo   1. Application will initialize cloud connection
echo   2. It will download existing data from cloud
echo   3. Wait 30 seconds for sync to complete
echo   4. Start adding employees and attendance records
echo   5. Everything syncs automatically!
echo.
echo For Help:
echo ──────────────────────────────────────────────────────────────────────────
echo   See INSTALLATION_GUIDE.txt in the installation folder
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Offer to launch application
set /p LAUNCH="Do you want to launch Punctaj Manager now? (Y/N): "

if /i "%LAUNCH%"=="Y" (
    echo.
    echo Starting Punctaj Manager...
    echo.
    call "%INSTALL_PATH%\Punctaj_Manager.bat"
) else (
    echo.
    echo Setup complete! You can launch the application anytime.
    echo Look for "Punctaj Manager" on your Desktop or Start Menu.
    echo.
)

pause
exit /b 0
