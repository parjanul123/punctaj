@echo off
REM ========================================
REM  System Requirements Check
REM ========================================

echo.
echo ====================================
echo  Verificare Sistem pentru PunctajManager
echo ====================================
echo.

REM Verifică dacă există Visual C++ Redistributables
echo [1/2] Verificare Visual C++ Redistributables...
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>&1
if %errorlevel% == 0 (
    echo   ✓ Visual C++ Redistributables instalate
) else (
    echo   ✗ Visual C++ Redistributables lipsesc!
    echo.
    echo   IMPORTANT: Descarca si instaleaza:
    echo   https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
)

echo.
echo [2/2] Verificare Git (optional)...
where git >nul 2>&1
if %errorlevel% == 0 (
    echo   ✓ Git instalat - functionalitate completa
) else (
    echo   ℹ Git nu este instalat - aplicatia va functiona fara sincronizare Git
)

echo.
echo ====================================
echo  Verificare finalizata!
echo ====================================
echo.
echo Daca toate sunt OK, poti rula PunctajManager.exe
echo.

pause
