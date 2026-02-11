# ====================================================================
# PUNCTAJ APPLICATION - COMPLETE INSTALLER BUILDER (PowerShell)
# ====================================================================
# Usage: .\BUILD_INSTALLER.ps1
# Creates: Punctaj_Manager_Setup.exe
# ====================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "   PUNCTAJ MANAGER v2.0 - INSTALLER BUILDER" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Check if Python is installed
Write-Host "[CHECK] Python installation..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8 or later from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] Found: $pythonCheck" -ForegroundColor Green

# Check if PyInstaller is installed
Write-Host "[CHECK] PyInstaller installation..." -ForegroundColor Yellow
$pipOutput = python -m pip show pyinstaller 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[1/3] Installing PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install PyInstaller" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] PyInstaller installed" -ForegroundColor Green
} else {
    Write-Host "[OK] PyInstaller already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/3] Building executable with PyInstaller..." -ForegroundColor Yellow
Write-Host ""

# Run the main builder script
python BUILD_INSTALLER_COMPLETE.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Installer build failed" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "   BUILD COMPLETE" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host ""

$installDir = "$(Get-Location)\installer_output"
Write-Host "Location: $installDir" -ForegroundColor Cyan

if (Test-Path "$installDir\Punctaj_Installer.nsi") {
    Write-Host "Files created:" -ForegroundColor Yellow
    Get-ChildItem "$installDir" -Recurse | 
        Where-Object {$_.PSIsContainer -eq $false} | 
        ForEach-Object {
            $size = if ($_.Length -gt 1MB) { 
                "{0:N2} MB" -f ($_.Length / 1MB) 
            } else { 
                "{0:N2} KB" -f ($_.Length / 1KB) 
            }
            Write-Host "  ✓ $($_.Name) ($size)" -ForegroundColor Green
        }
}

Write-Host ""
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Check installer_output directory" -ForegroundColor White
Write-Host "  2. Look for Punctaj_Manager_Setup.exe" -ForegroundColor White
Write-Host "  3. Run the installer to test it" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
exit 0
