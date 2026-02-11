# PUNCTAJ MANAGER v2.5 - SIMPLE INSTALLER
# Run: powershell -ExecutionPolicy Bypass -File "Install-PunctajManager.ps1"

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   PUNCTAJ MANAGER v2.5 - INSTALLER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Verific Python..." -ForegroundColor Yellow
$pythonCheck = & cmd /c "where python 2>nul" 2>&1 | Select-Object -First 1
if (-not $pythonCheck) {
    $pythonCheck = & cmd /c "where python3 2>nul" 2>&1 | Select-Object -First 1
}

if (-not $pythonCheck) {
    Write-Host "[EROARE] Python nu este instalat!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Descarca Python de la: https://www.python.org/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "IMPORTANT: Cand instalezi, bifeza: 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Apasa Enter pentru a inchide"
    exit 1
}

Write-Host "[OK] Python gasit" -ForegroundColor Green
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$punctajPy = Join-Path -Path $scriptDir -ChildPath "punctaj.py"

if (-not (Test-Path $punctajPy)) {
    Write-Host "[EROARE] punctaj.py nu gasit in: $scriptDir" -ForegroundColor Red
    Read-Host "Apasa Enter pentru a inchide"
    exit 1
}

Write-Host "[OK] Fisiere gasite in: $scriptDir" -ForegroundColor Green
Write-Host ""

# Install path
$installPath = Join-Path $env:APPDATA "PunctajManager"

# Check if already installed
if (Test-Path $installPath) {
    Write-Host "Aplicatia este deja instalata in: $installPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Optiuni:"
    Write-Host "  1 = Reinstaleaza"
    Write-Host "  2 = Lanseaza aplicatia acum"
    Write-Host "  3 = Anuleaza"
    Write-Host ""
    
    $choice = Read-Host "Alege (1/2/3)"
    
    if ($choice -eq "2") {
        Write-Host "Lansez aplicatia..." -ForegroundColor Green
        Set-Location $installPath
        & python punctaj.py
        exit 0
    }
    elseif ($choice -eq "3") {
        exit 0
    }
    elseif ($choice -ne "1") {
        Write-Host "Alegere invalida" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Sterg versiunea anterioara..." -ForegroundColor Yellow
    Remove-Item -Path $installPath -Recurse -Force -ErrorAction SilentlyContinue
}

# Create install directory
Write-Host "Creed directoare..." -ForegroundColor Yellow
New-Item -Path $installPath -ItemType Directory -Force | Out-Null
Write-Host "[OK] Directoare creata" -ForegroundColor Green
Write-Host ""

# Copy all necessary files
Write-Host "Copiez fisierele aplicatiei..." -ForegroundColor Yellow
Write-Host ""

$files = @(
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
    "organization_view.py",
    "discord_config.ini",
    "supabase_config.ini"
)

$copiedCount = 0
foreach ($file in $files) {
    $sourcePath = Join-Path $scriptDir $file
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $installPath -Force
        Write-Host "   ✓ $file" -ForegroundColor Green
        $copiedCount++
    }
}

Write-Host ""
Write-Host "[OK] $copiedCount fisiere copiate" -ForegroundColor Green
Write-Host ""

# Copy documentation
Write-Host "Copiez documentatia..." -ForegroundColor Yellow
$docFiles = Get-ChildItem -Path $scriptDir -Filter "00_*.md" -ErrorAction SilentlyContinue
foreach ($doc in $docFiles) {
    Copy-Item -Path $doc.FullName -Destination $installPath -Force
}
Write-Host "[OK] Documentatie copiata" -ForegroundColor Green
Write-Host ""

# Create launcher batch file
Write-Host "Creed launcher-ul..." -ForegroundColor Yellow
$launcherPath = Join-Path $installPath "launch.bat"
@"
@echo off
title Punctaj Manager
cd /d "$installPath"
python punctaj.py
"@ | Out-File -FilePath $launcherPath -Encoding ASCII

Write-Host "[OK] Launcher creat" -ForegroundColor Green
Write-Host ""

# Create Start Menu shortcut
Write-Host "Creed shortcut in Start Menu..." -ForegroundColor Yellow
$startMenuPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
if (Test-Path $startMenuPath) {
    $shortcutBat = Join-Path $startMenuPath "Punctaj Manager.bat"
    @"
@echo off
cd /d "$installPath"
start "" python punctaj.py
"@ | Out-File -FilePath $shortcutBat -Encoding ASCII
    
    Write-Host "[OK] Shortcut creat in Start Menu" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "INSTALARE COMPLETA!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Aplicatia instalata in: $installPath" -ForegroundColor Green
Write-Host ""
Write-Host "Pentru a lansa:" -ForegroundColor Yellow
Write-Host "  1. Click pe 'Punctaj Manager' in Start Menu" -ForegroundColor Yellow
Write-Host "  2. Sau dublu-click pe: launch.bat" -ForegroundColor Yellow
Write-Host "  3. Sau comando: python punctaj.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Se lanseaza aplicatia acum..." -ForegroundColor Green
Write-Host ""

Start-Sleep -Seconds 2
Set-Location $installPath
& python punctaj.py

exit 0
