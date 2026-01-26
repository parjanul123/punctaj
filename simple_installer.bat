@echo off
REM ========================================
REM  Auto-Installer pentru PunctajManager
REM  Rulează acest fișier pe PC-ul țintă
REM ========================================

title Punctaj Manager - Installer
color 0A

echo.
echo ============================================
echo   PUNCTAJ MANAGER - INSTALLER
echo ============================================
echo.
echo Acest script va instala Punctaj Manager
echo pe acest calculator.
echo.
pause

REM Verifică privilegii admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ATENTIE] Este recomandat sa rulezi ca Administrator
    echo pentru instalare in Program Files.
    echo.
    echo Apasa Enter pentru a continua oricum...
    pause >nul
)

REM Setează directorul de instalare
set "INSTALL_DIR=%ProgramFiles%\PunctajManager"
echo.
echo Locatie instalare: %INSTALL_DIR%
echo.
echo Vrei sa schimbi locatia? (N pentru default)
set /p "CUSTOM_DIR=Introdu path (sau apasa Enter): "

if not "%CUSTOM_DIR%"=="" (
    set "INSTALL_DIR=%CUSTOM_DIR%"
)

echo.
echo [1/5] Creare director de instalare...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%" 2>nul
    if errorlevel 1 (
        echo [ERROR] Nu pot crea directorul!
        echo Incearca sa rulezi ca Administrator.
        pause
        exit /b 1
    )
)
echo   OK: %INSTALL_DIR%

echo.
echo [2/5] Copiere fisiere...
REM Presupunem că acest script e în același folder cu fișierele
copy /Y "PunctajManager.exe" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "*.txt" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "*.bat" "%INSTALL_DIR%\" >nul 2>&1

if not exist "%INSTALL_DIR%\PunctajManager.exe" (
    echo [ERROR] Fisierele nu au fost copiate!
    pause
    exit /b 1
)
echo   OK: Fisiere copiate

REM Copiază datele inițiale în Documents\PunctajManager
echo.
echo [3/5] Configurare date in Documents...
set "DATA_DIR=%USERPROFILE%\Documents\PunctajManager"

if not exist "%DATA_DIR%" (
    mkdir "%DATA_DIR%" 2>nul
)

REM Copiază datele și arhiva dacă există în pachet
if exist "data" (
    xcopy /E /I /Y "data" "%DATA_DIR%\data\" >nul 2>&1
    echo   OK: Date initiale copiate in %DATA_DIR%\data
) else (
    echo   INFO: Nu exista date initiale de copiat
)

if exist "arhiva" (
    xcopy /E /I /Y "arhiva" "%DATA_DIR%\arhiva\" >nul 2>&1
    echo   OK: Arhiva copiata in %DATA_DIR%\arhiva
) else (
    echo   INFO: Nu exista arhiva de copiat
)

echo.
echo [4/5] Verificare Visual C++ Redistributables...
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ATENTIE] Visual C++ Redistributables lipsesc!
    echo.
    echo Acestea sunt NECESARE pentru functionare!
    echo.
    echo Vrei sa deschid pagina de download? (Y/N)
    set /p "DOWNLOAD_VC=Raspuns: "
    
    if /i "%DOWNLOAD_VC%"=="Y" (
        start https://aka.ms/vs/17/release/vc_redist.x64.exe
        echo.
        echo Dupa instalare, apasa Enter pentru a continua...
        pause >nul
    )
) else (
    echo   OK: VC++ Redistributables instalate
)

echo.
echo [5/5] Creare shortcut-uri...

REM Desktop shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Punctaj Manager.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\PunctajManager.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" 2>nul
if %errorlevel% equ 0 (
    echo   OK: Shortcut Desktop
)

REM Start Menu shortcut  
if not exist "%ProgramData%\Microsoft\Windows\Start Menu\Programs\PunctajManager" (
    mkdir "%ProgramData%\Microsoft\Windows\Start Menu\Programs\PunctajManager" 2>nul
)
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\PunctajManager\Punctaj Manager.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\PunctajManager.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" 2>nul
if %errorlevel% equ 0 (
    echo   OK: Shortcut Start Menu
)

echo.
echo [6/6] Finalizare...

REM Creează uninstaller
(
echo @echo off
echo title Dezinstalare Punctaj Manager
echo echo.
echo echo Dezinstalare Punctaj Manager...
echo echo.
echo del /q "%%USERPROFILE%%\Desktop\Punctaj Manager.lnk" 2^>nul
echo rmdir /s /q "%%ProgramData%%\Microsoft\Windows\Start Menu\Programs\PunctajManager" 2^>nul
echo cd /d "%%TEMP%%"
echo rmdir /s /q "%INSTALL_DIR%"
echo echo.
echo echo Dezinstalare completa!
echo pause
) > "%INSTALL_DIR%\Uninstall.bat"
echo   OK: Uninstaller creat

echo.
echo ============================================
echo   INSTALARE COMPLETA!
echo ============================================
echo.
echo Aplicatia a fost instalata in:
echo   %INSTALL_DIR%
echo.
echo Shortcut-uri create:
echo   - Desktop: "Punctaj Manager"
echo   - Start Menu: PunctajManager
echo.
echo Pentru dezinstalare:
echo   %INSTALL_DIR%\Uninstall.bat
echo.
echo ============================================
echo.
echo Vrei sa pornesti aplicatia acum? (Y/N)
set /p "START_NOW=Raspuns: "

if /i "%START_NOW%"=="Y" (
    start "" "%INSTALL_DIR%\PunctajManager.exe"
)

echo.
echo Instalare finalizata! Apasa Enter pentru a inchide...
pause >nul
