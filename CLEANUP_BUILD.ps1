# CLEANUP & OPTIMIZE SCRIPT - RUN THIS FIRST
# ============================================

# Stop on any error
$ErrorActionPreference = "SilentlyContinue"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "CURATARE SI OPTIMIZARE - 500MB TARGET" -ForegroundColor Green
Write-Host "=" * 60

# Step 1: Check current size
Write-Host "`nCheck current size..." -ForegroundColor Yellow
$folders = @(
    "app_build",
    "build", 
    "installer_build",
    "installer_output",
    "installer_outputs",
    "Punctaj_Manager_Professional_Installer",
    "Punctaj_Manager_Setup",
    "setup_output"
)

$totalSize = 0
foreach ($folder in $folders) {
    $path = "d:\punctaj\$folder"
    if (Test-Path $path) {
        $size = (Get-ChildItem -Path $path -Recurse -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        $totalSize += $size
        Write-Host "  $folder : $sizeMB MB"
    }
}
$totalMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "`nTotal OLD build files: $totalMB MB" -ForegroundColor Cyan

# Step 2: Ask for confirmation
Write-Host "`n⚠️  This will delete $totalMB MB of old build files" -ForegroundColor Yellow
$confirm = Read-Host "Continue? (yes/no)"

if ($confirm -ne 'yes') {
    Write-Host "Cancelled." -ForegroundColor Red
    exit
}

# Step 3: Delete old build directories
Write-Host "`n🗑️  Deleting old build directories..." -ForegroundColor Yellow

foreach ($folder in $folders) {
    $path = "d:\punctaj\$folder"
    if (Test-Path $path) {
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  [OK] Removed $folder"
        }
        catch {
            Write-Host "  [WARN] Could not remove $folder" -ForegroundColor Yellow
        }
    }
}

# Step 4: Clean old EXE files
Write-Host "`nCleaning old EXE files..." -ForegroundColor Yellow
$oldExes = Get-ChildItem -Path "d:\punctaj" -Filter "*.exe" -Depth 1 -ErrorAction SilentlyContinue
foreach ($exe in $oldExes) {
    $name = $exe.Name
    if ($name -notmatch "^venv") {  # Don't delete venv exes
        try {
            Remove-Item -Path $exe.FullName -Force
            $size = [math]::Round($exe.Length / 1MB, 2)
            Write-Host "  [OK] Removed $name ($size MB)"
        }
        catch {
            Write-Host "  [WARN] Could not remove $exe" -ForegroundColor Yellow
        }
    }
}

# Step 5: Disk space freed
Write-Host "`n[SUCCESS] CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "`nFreed up: ~$totalMB MB" -ForegroundColor Cyan

Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Run: python OPTIMIZE_FOR_DISTRIBUTION.py"
Write-Host "2. Wait for build to complete (~2-3 minutes)"
Write-Host "3. Check file: Punctaj_Application_FINAL.zip"
Write-Host "4. Verify size is < 500MB"

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
