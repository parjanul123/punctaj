# PowerShell script to create ZIP package
# Creaza un pachet ZIP complet cu aplicatia

param(
    [string]$SourceDir = "d:\punctaj",
    [string]$OutputDir = "d:\punctaj\package_output"
)

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗"
Write-Host "║          CREATING ZIP PACKAGE - PUNCTAJ MANAGER v2.5          ║"
Write-Host "╚════════════════════════════════════════════════════════════════╝"
Write-Host ""

# Clean previous output
if (Test-Path $OutputDir) {
    Write-Host "Cleaning previous builds..."
    Remove-Item $OutputDir -Recurse -Force
}

New-Item $OutputDir -ItemType Directory -Force | Out-Null

# ZIP file path
$ZipFile = Join-Path $OutputDir "PunctajManager_v2.5.zip"

Write-Host "📦 Creating: $ZipFile"
Write-Host ""

# Files to include
$Files = @(
    # Core application
    "punctaj.py",
    "realtime_sync.py",
    "permission_sync_fix.py",
    "discord_auth.py",
    "supabase_sync.py",
    "admin_panel.py",
    "admin_permissions.py",
    "admin_ui.py",
    "action_logger.py",
    "config_resolver.py",
    "json_logger.py",
    "organization_view.py",
    
    # Setup & Build
    "SETUP_INSTALLER.py",
    "BUILD_SETUP_EXE.py",
    "CREATE_ZIP_PACKAGE.py",
    "DIAGNOSE_SYNC_ISSUE.py",
    
    # Configuration
    "discord_config.ini",
    "supabase_config.ini"
)

# Documentation files (with wildcards)
$DocFiles = @(
    "00_START_HERE_IMPLEMENTATION.md",
    "00_FINAL_SUMMARY.md",
    "00_SETUP_SOLUTION_COMPLETE.md",
    "00_FILES_MANIFEST.md",
    "00_WELCOME.txt",
    "00_COMPLETE.txt",
    "01_QUICK_START_BUILD_DISTRIBUTE.md",
    "02_ARCHITECTURE_COMPLETE.md",
    "PERMISSION_SYNC_FIX.md",
    "AUTO_REGISTRATION_DISCORD.md",
    "CLIENT_GUIDE_PERMISSIONS_FIX.md",
    "DEPLOYMENT_READY.md"
)

try {
    # Load compression assembly
    Add-Type -Assembly System.IO.Compression.FileSystem
    
    # Create ZIP file
    $Zip = [System.IO.Compression.ZipFile]::Open($ZipFile, [System.IO.Compression.ZipArchiveMode]::Create)
    
    $fileCount = 0
    
    # Add core files
    Write-Host "Adding application files:"
    foreach ($File in $Files) {
        $FilePath = Join-Path $SourceDir $File
        if (Test-Path $FilePath) {
            $EntryName = "PunctajManager_v2.5/Application/$File"
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($Zip, $FilePath, $EntryName) | Out-Null
            Write-Host "  ✓ $File"
            $fileCount++
        }
    }
    
    # Add documentation
    Write-Host ""
    Write-Host "Adding documentation:"
    foreach ($File in $DocFiles) {
        $FilePath = Join-Path $SourceDir $File
        if (Test-Path $FilePath) {
            $EntryName = "PunctajManager_v2.5/Documentation/$File"
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($Zip, $FilePath, $EntryName) | Out-Null
            Write-Host "  ✓ $File"
            $fileCount++
        }
    }
    
    # Add installer_source folder
    Write-Host ""
    Write-Host "Adding installer_source:"
    $InstallerSource = Join-Path $SourceDir "installer_source"
    if (Test-Path $InstallerSource) {
        Get-ChildItem $InstallerSource -File | ForEach-Object {
            $FilePath = $_.FullName
            $FileName = $_.Name
            $EntryName = "PunctajManager_v2.5/installer_source/$FileName"
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($Zip, $FilePath, $EntryName) | Out-Null
            Write-Host "  ✓ $FileName"
            $fileCount++
        }
    }
    
    # Add README
    Write-Host ""
    Write-Host "Adding README:"
    $ReadmeContent = @"
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║          PUNCTAJ MANAGER v2.5 - COMPLETE PACKAGE                    ║
║                                                                       ║
║                   Real-Time Cloud Synchronization                    ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

✅ COMPLETE REBUILD PACKAGE

This ZIP contains the entire Punctaj Manager application with:
  ✓ Real-Time Cloud Sync (every 30 seconds)
  ✓ Real-Time Permission Sync (every 5 seconds)
  ✓ Auto-User Registration
  ✓ Professional Setup Installer
  ✓ Complete Documentation
  ✓ Diagnostic Tools

📂 FOLDER STRUCTURE

/Application/              - All Python modules
/Documentation/            - Complete guides (8 files)
/installer_source/         - Files for building Setup.exe
/README.txt               - This file

🚀 QUICK START

1. Extract this ZIP to: d:\punctaj\

2. Read: Documentation/00_START_HERE_IMPLEMENTATION.md

3. Configure:
   - Edit discord_config.ini (Discord OAuth)
   - Edit supabase_config.ini (Supabase API)

4. Run Application:
   python Application/punctaj.py

5. Or Build Setup.exe:
   python Application/BUILD_SETUP_EXE.py
   Creates: setup_output\dist\PunctajManager_Setup.exe

📚 KEY DOCUMENTATION FILES

→ 00_START_HERE_IMPLEMENTATION.md    - Navigation guide
→ 01_QUICK_START_BUILD_DISTRIBUTE.md - How to build/distribute
→ 00_FINAL_SUMMARY.md                - Complete overview
→ 02_ARCHITECTURE_COMPLETE.md        - Technical design

🎯 FEATURES

✅ Real-Time Cloud Sync
   Database syncs every 30 seconds
   Changes from other users visible instantly
   No restart needed!

✅ Real-Time Permission Sync
   Permissions sync every 5 seconds
   Admin changes visible instantly
   No restart needed!

✅ Auto-User Registration
   First Discord login creates account
   No manual user creation
   Admin assigns permissions

✅ Professional Installer
   Single Setup.exe file
   Installs to %APPDATA%\PunctajManager
   Ready for distribution

═══════════════════════════════════════════════════════════════════════

Version: 2.5 with Real-Time Sync
Status: Production Ready
Date: 2026-02-03

Good luck with your deployment! 🚀

═══════════════════════════════════════════════════════════════════════
"@
    
    $ReadmeEntry = $Zip.CreateEntry("PunctajManager_v2.5/README.txt")
    $Writer = [System.IO.StreamWriter]$ReadmeEntry.Open()
    $Writer.Write($ReadmeContent)
    $Writer.Close()
    Write-Host "  ✓ README.txt"
    $fileCount++
    
    # Close ZIP
    $Zip.Dispose()
    
    # Get ZIP size
    $ZipSize = (Get-Item $ZipFile).Length / 1MB
    
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════════"
    Write-Host "✅ ZIP PACKAGE CREATED!"
    Write-Host "════════════════════════════════════════════════════════════════"
    Write-Host ""
    Write-Host "📦 File: PunctajManager_v2.5.zip"
    Write-Host "📍 Location: $OutputDir"
    Write-Host "📊 Size: $([Math]::Round($ZipSize, 1)) MB"
    Write-Host "📄 Files: $fileCount"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Extract ZIP to d:\punctaj\"
    Write-Host "2. Read: Documentation/00_START_HERE_IMPLEMENTATION.md"
    Write-Host "3. Configure Discord and Supabase credentials"
    Write-Host "4. Run: python Application/punctaj.py"
    Write-Host ""
    Write-Host "Ready to distribute! 🚀"
    Write-Host ""
    
}
catch {
    Write-Host "❌ Error creating ZIP: $_"
    exit 1
}
