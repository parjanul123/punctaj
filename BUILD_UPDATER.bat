@echo off
echo ========================================
echo    🔨 BUILD GIT UPDATER EXE
echo ========================================
echo.
echo 🔄 Activând environment virtual...
call venv\Scripts\activate.bat
echo.
echo 🚀 Rulând build script...
python build_updater.py
echo.
echo ⏸️  Build completat - Apasă orice tastă...
pause