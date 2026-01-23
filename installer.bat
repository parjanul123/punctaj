@echo off
REM ========================================
REM  Punctaj Manager - Installer Script
REM ========================================

echo.
echo ================================================
echo   Punctaj Manager - Installation Script
echo ================================================
echo.

REM Verifică dacă Python este instalat
python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python nu e in PATH, caut instalări locale...
    
    REM Caută Python în locații standard
    set "PYTHON_PATH="
    
    REM Verifică AppData\Local\Programs\Python
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_PATH=%%i"
            goto :found_python
        )
    )
    
    REM Verifică Program Files
    for /d %%i in ("C:\Program Files\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_PATH=%%i"
            goto :found_python
        )
    )
    
    :found_python
    if not defined PYTHON_PATH (
        echo [ERROR] Python nu a fost găsit!
        echo         Descarcă Python de la: https://www.python.org/downloads/
        echo         Asigură-te că bifezi "Add Python to PATH"
        pause
        exit /b 1
    )
    
    echo [OK] Python găsit în: %PYTHON_PATH%
    set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%"
)

echo [OK] Python detectat
python --version

REM Crează virtual environment (opțional, dar recomandat)
echo.
echo [1/5] Creez virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Instalează dependențele
echo.
echo [2/5] Instalez dependențele...
pip install -r requirements.txt --upgrade
if errorlevel 1 (
    echo [ERROR] Instalarea dependențelor a eșuat!
    pause
    exit /b 1
)

echo [OK] Dependențele instalate cu succes

REM Build-ează EXE
echo.
echo [3/5] Construiesc EXE-ul (aceasta poate dura 1-2 minute)...
python setup.py
if errorlevel 1 (
    echo [ERROR] Build-ul a eșuat!
    pause
    exit /b 1
)

echo [OK] Build finalizat

REM Crează shortcut (opțional)
echo.
echo [4/5] Crează shortcut pe desktop...
if exist "dist\PunctajManager.exe" (
    REM Crează shortcut pe desktop (necesită Powershell)
    powershell -Command "if (Test-Path '$env:USERPROFILE\Desktop\PunctajManager.lnk') { Remove-Item '$env:USERPROFILE\Desktop\PunctajManager.lnk' }; $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('$env:USERPROFILE\Desktop\PunctajManager.lnk'); $Shortcut.TargetPath = '%cd%\dist\PunctajManager.exe'; $Shortcut.WorkingDirectory = '%cd%\dist'; $Shortcut.Save()" 2>nul
    
    if errorlevel 0 (
        echo [OK] Shortcut creat pe Desktop
    )
)

REM Afișează instrucțiuni finale
echo.
echo [5/5] Instalare completă!
echo.
echo ================================================
echo   Installation Summary
echo ================================================
echo.
echo [✓] Dependențele instalate în: %cd%\venv
echo [✓] Executable creat în: %cd%\dist\PunctajManager.exe
echo [✓] Shortcut pe Desktop: PunctajManager
echo.
echo ================================================
echo   How to Run
echo ================================================
echo.
echo OPȚIUNEA 1: Direct pe Desktop
echo   - Dublu-click pe "PunctajManager" shortcut
echo.
echo OPȚIUNEA 2: Command Line
echo   - cd dist
echo   - PunctajManager.exe
echo.
echo OPȚIUNEA 3: Development Mode
echo   - call venv\Scripts\activate.bat
echo   - python punctaj.py
echo.
echo ================================================
echo.

pause
