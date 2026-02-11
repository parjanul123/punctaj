@echo off
REM Build Complete ZIP Package
REM Creaza un pachet ZIP complet cu aplicatia

setlocal enabledelayedexpansion

cd /d "d:\punctaj"

echo.
echo ============================================================
echo   CREATING ZIP PACKAGE
echo ============================================================
echo.

REM Check if 7-Zip is installed
if exist "C:\Program Files\7-Zip\7z.exe" (
    echo Using 7-Zip for compression...
    
    set ZIP_FILE=PunctajManager_v2.5.zip
    set OUTPUT_DIR=package_output
    
    if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
    mkdir "%OUTPUT_DIR%"
    
    REM Create ZIP with all important files
    "C:\Program Files\7-Zip\7z.exe" a "%OUTPUT_DIR%\%ZIP_FILE%" ^
        punctaj.py ^
        realtime_sync.py ^
        permission_sync_fix.py ^
        discord_auth.py ^
        supabase_sync.py ^
        admin_panel.py ^
        admin_permissions.py ^
        admin_ui.py ^
        action_logger.py ^
        config_resolver.py ^
        json_logger.py ^
        organization_view.py ^
        SETUP_INSTALLER.py ^
        BUILD_SETUP_EXE.py ^
        CREATE_ZIP_PACKAGE.py ^
        DIAGNOSE_SYNC_ISSUE.py ^
        discord_config.ini ^
        supabase_config.ini ^
        "00_*.md" "00_*.txt" ^
        "01_*.md" ^
        "02_*.md" ^
        "PERMISSION_SYNC_FIX.md" ^
        "AUTO_REGISTRATION_DISCORD.md" ^
        "CLIENT_GUIDE_PERMISSIONS_FIX.md" ^
        "DEPLOYMENT_READY.md" ^
        installer_source
    
    echo.
    echo ============================================================
    echo ZIP PACKAGE CREATED
    echo ============================================================
    echo.
    echo Location: %OUTPUT_DIR%\%ZIP_FILE%
    echo.
    
) else (
    echo Error: 7-Zip not found!
    echo Install 7-Zip from: https://www.7-zip.org/
    echo.
    echo Alternatively, Windows can create ZIP natively:
    echo Using PowerShell instead...
    
    REM Use PowerShell to create ZIP
    powershell -Command "
    $source = 'd:\punctaj'
    $dest = 'd:\punctaj\package_output'
    $zipfile = Join-Path $dest 'PunctajManager_v2.5.zip'
    
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    New-Item $dest -ItemType Directory -Force | Out-Null
    
    Add-Type -Assembly System.IO.Compression.FileSystem
    
    `$files = @(
        'punctaj.py',
        'realtime_sync.py',
        'permission_sync_fix.py',
        'discord_auth.py',
        'supabase_sync.py',
        'admin_panel.py',
        'admin_permissions.py',
        'admin_ui.py',
        'action_logger.py',
        'config_resolver.py',
        'json_logger.py',
        'organization_view.py',
        'SETUP_INSTALLER.py',
        'BUILD_SETUP_EXE.py',
        'CREATE_ZIP_PACKAGE.py',
        'DIAGNOSE_SYNC_ISSUE.py',
        'discord_config.ini',
        'supabase_config.ini'
    )
    
    `$zip = [System.IO.Compression.ZipFile]::Open(`$zipfile, 'Create')
    
    foreach (`$file in `$files) {
        `$path = Join-Path `$source `$file
        if (Test-Path `$path) {
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(`$zip, `$path, `$file)
            Write-Host \"  ✓ Added: `$file\"
        }
    }
    
    `$zip.Dispose()
    
    Write-Host \"`n✅ ZIP created: `$zipfile\"
    "
)

echo.
echo Finished!
echo.

pause
