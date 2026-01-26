@echo off
REM ========================================
REM  Create Distribution Package
REM ========================================

echo.
echo ====================================
echo  Creeare Pachet Distributie
echo ====================================
echo.

REM Creează folderul pentru distribuție
if not exist "release" mkdir release
if exist "release\PunctajManager" rmdir /s /q "release\PunctajManager"
mkdir "release\PunctajManager"

REM Copiază exe-ul
echo [1/3] Copiez executabilul...
copy "dist\PunctajManager.exe" "release\PunctajManager\" >nul
if %errorlevel% neq 0 (
    echo   ✗ Eroare: Nu gasesc dist\PunctajManager.exe
    echo   Ruleaza build.bat mai intai!
    pause
    exit /b 1
)
echo   ✓ PunctajManager.exe copiat

REM Copiază documentația
echo [2/3] Copiez documentatia...
copy "DEPLOYMENT.md" "release\PunctajManager\CITESTE-MA.txt" >nul
copy "CHECK_SYSTEM.bat" "release\PunctajManager\" >nul
echo   ✓ Documentatie copiata

REM Creează README rapid
echo [3/3] Generez ghid rapid...
(
echo ========================================
echo  PUNCTAJ MANAGER - Ghid Rapid
echo ========================================
echo.
echo 1. Ruleaza CHECK_SYSTEM.bat pentru a verifica sistemul
echo 2. Instaleaza Visual C++ Redistributables daca lipsesc
echo 3. Dublu-click pe PunctajManager.exe
echo.
echo Pentru informatii complete, vezi CITESTE-MA.txt
echo.
echo ========================================
) > "release\PunctajManager\START_HERE.txt"
echo   ✓ Ghid rapid generat

echo.
echo ====================================
echo  Pachet creat cu succes!
echo ====================================
echo.
echo Locatie: release\PunctajManager\
echo.
echo Continut:
echo   - PunctajManager.exe      (Aplicatia)
echo   - CHECK_SYSTEM.bat        (Verificare sistem)
echo   - CITESTE-MA.txt          (Documentatie completa)
echo   - START_HERE.txt          (Ghid rapid)
echo.
echo Distribuie folderul "PunctajManager" catre utilizatori!
echo.

pause
