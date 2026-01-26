@echo off
REM ========================================
REM  Test Git Synchronization
REM ========================================

echo.
echo ====================================
echo  Test Sincronizare Git
echo ====================================
echo.

cd /d "%~dp0"

REM Verifică dacă e Git repo
git rev-parse --is-inside-work-tree >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Acesta nu este un Git repository!
    echo.
    echo Pentru setup, vezi GIT_SYNC_GUIDE.md
    pause
    exit /b 1
)

echo [1/4] Verificare conexiune GitHub...
git ls-remote origin >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Nu pot conecta la GitHub!
    echo Verifică:
    echo   - Ai internet
    echo   - Ai acces la https://github.com/parjanul123/punctaj.git
    echo   - Credențialele Git sunt corecte
    pause
    exit /b 1
)
echo   ✓ Conectat la GitHub

echo.
echo [2/4] Verificare fișiere data/ în Git...
git ls-tree -r main --name-only | findstr "^data/" >nul
if %errorlevel% neq 0 (
    echo   ⚠ Nu există fișiere data/ în Git
) else (
    echo   ✓ Fișiere data/ sincronizate
)

echo.
echo [3/4] Verificare stare locală...
git status --porcelain >nul
if %errorlevel% neq 0 (
    echo   ⚠ Există modificări nesalvate
    git status --short
) else (
    echo   ✓ Tot sincronizat
)

echo.
echo [4/4] Verificare ultimele commit-uri...
echo.
git log --oneline -5 --graph --decorate
echo.

echo ====================================
echo  Test complet!
echo ====================================
echo.
echo Repository: https://github.com/parjanul123/punctaj
echo Branches:
git branch -a
echo.
echo Pentru mai multe detalii, vezi GIT_SYNC_GUIDE.md
echo.

pause
