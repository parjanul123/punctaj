# Create ZIP package - simple version
Add-Type -Assembly System.IO.Compression.FileSystem

$SourceDir = "d:\punctaj"
$OutputDir = "d:\punctaj\package_output"
$ZipFile = "$OutputDir\PunctajManager_v2.5.zip"

Write-Host ""
Write-Host "Creating ZIP package..."
Write-Host ""

if (Test-Path $OutputDir) {
    Remove-Item $OutputDir -Recurse -Force
}

New-Item $OutputDir -ItemType Directory -Force | Out-Null

$Files = @(
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
    "SETUP_INSTALLER.py",
    "BUILD_SETUP_EXE.py",
    "CREATE_ZIP_PACKAGE.py",
    "DIAGNOSE_SYNC_ISSUE.py",
    "discord_config.ini",
    "supabase_config.ini",
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

$Zip = [System.IO.Compression.ZipFile]::Open($ZipFile, [System.IO.Compression.ZipArchiveMode]::Create)

foreach ($File in $Files) {
    $FilePath = Join-Path $SourceDir $File
    if (Test-Path $FilePath) {
        $EntryName = "PunctajManager_v2.5/$File"
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($Zip, $FilePath, $EntryName) | Out-Null
        Write-Host "  ✓ $File"
    }
}

$Zip.Dispose()

$ZipSize = (Get-Item $ZipFile).Length / 1MB

Write-Host ""
Write-Host "======================================================"
Write-Host "ZIP PACKAGE CREATED!"
Write-Host "======================================================"
Write-Host ""
Write-Host "File: PunctajManager_v2.5.zip"
Write-Host "Location: $OutputDir"
Write-Host "Size: $([Math]::Round($ZipSize, 1)) MB"
Write-Host ""
Write-Host "Ready to distribute! :)"
Write-Host ""
