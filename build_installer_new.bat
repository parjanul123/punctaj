@echo off
REM ====================================
REM Punctaj Manager - Build Installer
REM ====================================

echo.
echo ========================================
echo  Punctaj Manager - Professional Installer
echo ========================================
echo.

REM Check if NSIS is installed
if not exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    if not exist "C:\Program Files\NSIS\makensis.exe" (
        echo.
        echo ❌ NSIS nu este instalat!
        echo.
        echo Descarcă și instalează NSIS de la: https://nsis.sourceforge.io/
        echo.
        echo După instalare, rulează din nou acest script.
        echo.
        pause
        exit /b 1
    )
)

REM Find NSIS path
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    set "NSIS_PATH=C:\Program Files (x86)\NSIS"
) else (
    set "NSIS_PATH=C:\Program Files\NSIS"
)

echo ✓ NSIS găsit: %NSIS_PATH%
echo.

REM Check if EXE exists
if not exist "dist\Punctaj.exe" (
    echo ❌ Punctaj.exe nu găsit în folderul dist\
    echo.
    echo Asigură-te că ai rulat PyInstaller înainte de a genera installerul.
    echo.
    pause
    exit /b 1
)

echo ✓ Punctaj.exe găsit
echo.

REM Check if config files exist
if not exist "discord_config.ini" (
    echo ⚠️  discord_config.ini nu găsit - va fi includeaz doar EXE
)

if not exist "supabase_config.ini" (
    echo ⚠️  supabase_config.ini nu găsit - va fi includeaz doar EXE
)

echo.
echo 🔨 Se construiește installerul...
echo.

REM Build installer using NSIS
"%NSIS_PATH%\makensis.exe" /V2 "Punctaj_Installer.nsi"

echo.

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ INSTALLERUL A FOST GENERAT CU SUCCES!
    echo ========================================
    echo.
    echo 📦 Fișierul installerului:
    echo    %USERPROFILE%\Documents\Punctaj_Installer.exe
    echo.
    echo 📋 Pentru a distribui:
    echo    1. Copy %USERPROFILE%\Documents\Punctaj_Installer.exe
    echo    2. Trimite utilizatorilor pentru a instala
    echo.
    echo 🚀 Utilizatorii vor putea:
    echo    - Alege locația de instalare
    echo    - Crea shortcuts pe Desktop și Start Menu
    echo    - Dezinstala cu opțiunea "Add/Remove Programs"
    echo.
    REM Deschide folderul cu installerul
    start "" "%USERPROFILE%\Documents"
) else (
    echo.
    echo ========================================
    echo ❌ EROARE LA GENERAREA INSTALLERULUI
    echo ========================================
    echo.
)

echo.
pause
