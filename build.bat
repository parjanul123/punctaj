@echo off
REM ========================================
REM  Rebuild EXE Script
REM ========================================

echo.
echo Rebuilding PunctajManager.exe...
echo.

REM Activează venv dacă există
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Șterge build-urile vechi
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build
python setup.py

echo.
echo Build complet! EXE: dist\PunctajManager.exe
echo.

pause
