@echo off
REM ============================================================
REM PUNCTAJ MANAGER v2.5 - SIMPLE ONE-CLICK INSTALLER
REM ============================================================

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================
echo     PUNCTAJ MANAGER v2.5 - INSTALLER
echo ============================================================
echo.
echo Aceasta va instala aplicatia Punctaj Manager pe calculatorul tau.
echo.

REM Check Python
echo Verific Python...
where python >nul 2>&1
if !ERRORLEVEL! neq 0 (
    where python3 >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo.
        echo [EROARE] Python nu este instalat!
        echo.
        echo Descarca Python de la: https://www.python.org/
        echo.
        echo Cand instalezi, SIGUR bifeza: "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Python gasit
echo.

REM Install path
set INSTALL_PATH=%APPDATA%\PunctajManager

echo Caut locatia scriptului...
set SCRIPT_DIR=%~dp0
if not exist "%SCRIPT_DIR%punctaj.py" (
    echo [EROARE] punctaj.py nu gasit in: %SCRIPT_DIR%
    pause
    exit /b 1
)

echo [OK] Fise gasite
echo.

REM Check if already installed
if exist "%INSTALL_PATH%" (
    echo Aplicatia este deja instalata in: %INSTALL_PATH%
    echo.
    echo Optiuni:
    echo   1 = Reinstaleaza (va rescrie fisierele)
    echo   2 = Lanseaza aplicatia acum
    echo   3 = Anuleaza
    echo.
    set /p CHOICE="Alege (1/2/3): "
    
    if "!CHOICE!"=="2" (
        cd /d "%INSTALL_PATH%"
        echo Lansez aplicatia...
        timeout /t 2 >nul
        start "" python punctaj.py
        exit /b 0
    )
    if "!CHOICE!"=="3" (
        exit /b 0
    )
    if not "!CHOICE!"=="1" (
        echo Alegere invalida
        pause
        exit /b 1
    )
    
    echo Sterg versiunea anterioara...
    rmdir /s /q "%INSTALL_PATH%" >nul 2>&1
)

REM Create install directory
echo Creed directoare...
mkdir "%INSTALL_PATH%" >nul 2>&1
if not exist "%INSTALL_PATH%" (
    echo [EROARE] Nu pot crea directoare: %INSTALL_PATH%
    pause
    exit /b 1
)

echo [OK] Directoare creata
echo.

REM Copy all files
echo Copiez fisierele aplicatiei...
echo.

set COUNT=0
for %%F in (
    punctaj.py
    realtime_sync.py
    permission_sync_fix.py
    discord_auth.py
    supabase_sync.py
    admin_panel.py
    admin_permissions.py
    admin_ui.py
    action_logger.py
    config_resolver.py
    organization_view.py
    discord_config.ini
    supabase_config.ini
) do (
    if exist "%SCRIPT_DIR%%%F" (
        copy "%SCRIPT_DIR%%%F" "%INSTALL_PATH%\" >nul 2>&1
        set /a COUNT+=1
        echo   ✓ %%F
    )
)

echo.
echo [OK] !COUNT! fisiere copiate
echo.

REM Copy documentation
echo Copiez documentatia...
if exist "%SCRIPT_DIR%00_START_HERE_IMPLEMENTATION.md" (
    copy "%SCRIPT_DIR%00_*.md" "%INSTALL_PATH%\" >nul 2>&1
    echo   ✓ Documentatie
)

REM Create launcher
echo.
echo Creed launcher-ul...

set LAUNCHER=%INSTALL_PATH%\launch.bat
(
    echo @echo off
    echo title Punctaj Manager
    echo cd /d "%INSTALL_PATH%"
    echo python punctaj.py
) > "!LAUNCHER!"

echo [OK] Launcher creat: !LAUNCHER!
echo.

REM Create Windows Start Menu shortcut
echo Creed shortcut in Start Menu...

set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
if exist "%START_MENU%" (
    (
        echo [InternetShortcut]
        echo URL=
    ) > "%START_MENU%\Punctaj Manager.url"
    
    REM Better: Create a .bat shortcut
    (
        echo @echo off
        echo cd /d "%INSTALL_PATH%"
        echo start "" python punctaj.py
    ) > "%START_MENU%\Punctaj Manager.bat"
    
    echo [OK] Shortcut creat
)

echo.
echo ============================================================
echo INSTALARE COMPLETA!
echo ============================================================
echo.
echo Aplicatia instalata in: %INSTALL_PATH%
echo.
echo Pentru a lansa:
echo   1. Click pe "Punctaj Manager" in Start Menu
echo   2. Sau dublu-click pe: launch.bat
echo   3. Sau comando: python punctaj.py
echo.
echo Pentru a desinstala:
echo   Sterge mapa: %INSTALL_PATH%
echo.
echo Se lanseaza aplicatia acum...
echo.
timeout /t 3 >nul

cd /d "%INSTALL_PATH%"
start "" python punctaj.py

exit /b 0
