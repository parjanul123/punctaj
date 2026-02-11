@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM   PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER
REM   Installs application with Discord & Supabase configuration
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║         PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER                 ║
echo ║                                                                           ║
echo ║         Cloud-Enabled Employee Attendance Tracking System               ║
echo ║              with Discord Authentication & Data Protection              ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

REM Check Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  ERROR: Administrator privileges required!
    echo.
    echo This installer needs Administrator access to:
    echo   • Install to Program Files
    echo   • Create system shortcuts
    echo   • Configure system integration
    echo.
    echo Please run this installer as Administrator.
    echo.
    pause
    exit /b 1
)

echo ✓ Administrator privileges verified
echo.

REM Define installation paths
set INSTALL_PATH=%ProgramFiles%\Punctaj
set APP_DATA_PATH=%APPDATA%\Punctaj

echo 📁 Installation Information:
echo   • Program folder: %INSTALL_PATH%
echo   • User data:      %APP_DATA_PATH%
echo.

REM Create directories
echo 📂 Creating directories...
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"
if not exist "%INSTALL_PATH%\data" mkdir "%INSTALL_PATH%\data"
if not exist "%INSTALL_PATH%\logs" mkdir "%INSTALL_PATH%\logs"
if not exist "%INSTALL_PATH%\arhiva" mkdir "%INSTALL_PATH%\arhiva"
if not exist "%APP_DATA_PATH%" mkdir "%APP_DATA_PATH%"

REM Copy main executable
echo.
echo 📦 Installing application files...
if exist "dist\punctaj.exe" (
    copy /Y "dist\punctaj.exe" "%INSTALL_PATH%\Punctaj_Manager.exe" >nul
    echo   ✓ Punctaj_Manager.exe
) else (
    echo   ❌ ERROR: dist\punctaj.exe not found
    pause
    exit /b 1
)

REM Copy configuration files
if exist "discord_config.ini" (
    copy /Y "discord_config.ini" "%INSTALL_PATH%\discord_config.ini" >nul
    copy /Y "discord_config.ini" "%APP_DATA_PATH%\discord_config.ini" >nul
    echo   ✓ discord_config.ini
) else (
    echo   ⚠️  discord_config.ini not found (will use defaults)
)

if exist "supabase_config.ini" (
    copy /Y "supabase_config.ini" "%INSTALL_PATH%\supabase_config.ini" >nul
    copy /Y "supabase_config.ini" "%APP_DATA_PATH%\supabase_config.ini" >nul
    echo   ✓ supabase_config.ini
) else (
    echo   ⚠️  supabase_config.ini not found (will use defaults)
)

REM Copy encryption key if exists
if exist ".secure_key" (
    copy /Y ".secure_key" "%INSTALL_PATH%\.secure_key" >nul
    copy /Y ".secure_key" "%APP_DATA_PATH%\.secure_key" >nul
    attrib +h "%INSTALL_PATH%\.secure_key"
    attrib +h "%APP_DATA_PATH%\.secure_key"
    echo   ✓ .secure_key (hidden)
)

REM Copy JSON encryptor module
if exist "json_encryptor.py" (
    copy /Y "json_encryptor.py" "%INSTALL_PATH%\json_encryptor.py" >nul
    echo   ✓ json_encryptor.py
)

REM Register application in Windows
echo.
echo 🔧 Registering application in Windows...
reg add "HKLM\Software\Punctaj" /v "Install_Dir" /d "%INSTALL_PATH%" /f >nul 2>&1
reg add "HKLM\Software\Punctaj" /v "Version" /d "2.0.0" /f >nul 2>&1

REM Add to Add/Remove Programs
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" /v "DisplayName" /d "Punctaj Manager 2.0.0" /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" /v "UninstallString" /d "%INSTALL_PATH%\uninstall.bat" /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" /v "DisplayVersion" /d "2.0.0" /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" /v "Publisher" /d "Punctaj Team" /f >nul 2>&1

echo   ✓ Registry configured

REM Create shortcuts
echo.
echo 🎯 Creating shortcuts...

REM Desktop shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Punctaj Manager.lnk'); $Shortcut.TargetPath = '%INSTALL_PATH%\Punctaj_Manager.exe'; $Shortcut.Description = 'Punctaj Manager - Employee Attendance System'; $Shortcut.Save()"
echo   ✓ Desktop shortcut

REM Start Menu shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $StartMenu = '%APPDATA%\Microsoft\Windows\Start Menu\Programs'; $Shortcut = $WshShell.CreateShortcut('$StartMenu\Punctaj Manager.lnk'); $Shortcut.TargetPath = '%INSTALL_PATH%\Punctaj_Manager.exe'; $Shortcut.Description = 'Punctaj Manager - Employee Attendance System'; $Shortcut.Save()"
echo   ✓ Start Menu shortcut

REM Create uninstaller batch file
echo.
echo 🧹 Creating uninstaller...
(
    echo @echo off
    echo setlocal enabledelayedexpansion
    echo.
    echo REM Check admin privileges
    echo net session ^>nul 2^>^&1
    echo if %%errorlevel%% neq 0 ^(
    echo     echo Administrator privileges required!
    echo     pause
    echo     exit /b 1
    echo ^)
    echo.
    echo echo Uninstalling Punctaj Manager...
    echo del /F /Q "%INSTALL_PATH%\Punctaj_Manager.exe" ^>nul 2^>^&1
    echo del /F /Q "%INSTALL_PATH%\discord_config.ini" ^>nul 2^>^&1
    echo del /F /Q "%INSTALL_PATH%\supabase_config.ini" ^>nul 2^>^&1
    echo del /F /Q "%INSTALL_PATH%\.secure_key" ^>nul 2^>^&1
    echo del /F /Q "%INSTALL_PATH%\json_encryptor.py" ^>nul 2^>^&1
    echo rmdir /S /Q "%INSTALL_PATH%\logs" ^>nul 2^>^&1
    echo rmdir /S /Q "%INSTALL_PATH%\arhiva" ^>nul 2^>^&1
    echo rmdir "%INSTALL_PATH%" ^>nul 2^>^&1
    echo.
    echo del "%%USERPROFILE%%\Desktop\Punctaj Manager.lnk" ^>nul 2^>^&1
    echo del "%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Punctaj Manager.lnk" ^>nul 2^>^&1
    echo.
    echo reg delete "HKLM\Software\Punctaj" /f ^>nul 2^>^&1
    echo reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" /f ^>nul 2^>^&1
    echo.
    echo echo Punctaj Manager has been uninstalled.
    echo pause
) > "%INSTALL_PATH%\uninstall.bat"
echo   ✓ Uninstaller created

REM Installation summary
echo.
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                    INSTALLATION COMPLETE!                                ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo ✅ Punctaj Manager 2.0.0 has been successfully installed!
echo.
echo 📋 Installation Details:
echo   • Application: %INSTALL_PATH%\Punctaj_Manager.exe
echo   • User Data:   %APP_DATA_PATH%
echo   • Shortcuts:   Desktop ^& Start Menu
echo.
echo 🚀 What's Next:
echo   1. A shortcut has been created on your Desktop
echo   2. You can also find it in Start Menu ^> Punctaj Manager
echo   3. Click to launch the application
echo.
echo 🔐 Security Features:
echo   • Discord Authentication enabled
echo   • Supabase cloud sync configured
echo   • Log files encrypted with AES-256
echo   • Data protection: Files cannot be modified outside the app
echo.
echo 📝 Configuration Files:
echo   • discord_config.ini - Discord OAuth2 settings
echo   • supabase_config.ini - Cloud database settings
echo   • .secure_key - Encryption key (hidden, auto-generated)
echo.
echo 💡 Important:
echo   • Do NOT delete configuration files
echo   • Do NOT modify .secure_key
echo   • Data is protected and encrypted
echo.
echo ✨ Installation folder: %INSTALL_PATH%
echo.
pause
