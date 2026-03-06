@echo off
echo ==========================================
echo    🛡️ BUILD PUNCTAJ UPDATE EXE
echo ==========================================
echo.
echo 🔄 Activând environment virtual...
call venv\Scripts\activate.bat
echo.
echo 🚀 Rulând build script pentru Punctaj Update...
python build_punctaj_update.py
echo.
echo ⏸️  Build completat - Apasă orice tastă...
pause