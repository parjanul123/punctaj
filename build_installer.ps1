# PowerShell script to build Punctaj installer

$nsiPath = "D:\punctaj\punctaj_installer.nsi"
$installerOutputDir = "D:\punctaj\installer_outputs"
$distDir = "D:\punctaj\dist"

Write-Host "Building Punctaj Manager Installer..." -ForegroundColor Cyan

# Check if NSIS is installed
$nsisPath = "C:\Program Files (x86)\NSIS\makensis.exe"
if (-not (Test-Path $nsisPath)) {
    Write-Host "NSIS not found. Installing..." -ForegroundColor Yellow
    choco install nsis -y --acceptLicense
}

Write-Host "NSIS found" -ForegroundColor Green

# Check if EXE exists
if (-not (Test-Path "$distDir\Punctaj.exe")) {
    Write-Host "Error: Punctaj.exe not found" -ForegroundColor Red
    exit 1
}

Write-Host "Found Punctaj.exe" -ForegroundColor Green

# Create installer_outputs directory
if (-not (Test-Path $installerOutputDir)) {
    New-Item -ItemType Directory -Path $installerOutputDir | Out-Null
}

# Compile NSIS script
Write-Host "Compiling NSIS installer..." -ForegroundColor Yellow
Push-Location $installerOutputDir
& $nsisPath $nsiPath
Pop-Location

# Check if installer was created
$installerFile = "$installerOutputDir\Punctaj_Installer.exe"
if (-not (Test-Path $installerFile)) {
    Write-Host "Error: Installer file not created" -ForegroundColor Red
    exit 1
}

$installerSize = [math]::Round((Get-Item $installerFile).Length / 1MB, 2)
Write-Host "Installer created: $installerFile ($installerSize MB)" -ForegroundColor Green

# Create ZIP file with installer
$zipPath = "$installerOutputDir\Punctaj_Installer.zip"
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem

# Create ZIP
[System.IO.Compression.ZipFile]::CreateFromDirectory($installerOutputDir, $zipPath, $true)

# Add just the installer and README to a clean ZIP
$zip = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')
[System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $installerFile, (Split-Path $installerFile -Leaf)) | Out-Null

# Add README
$readmeTempPath = "$env:TEMP\README_Punctaj.txt"
@"
Punctaj Manager Installer

INSTALLATION INSTRUCTIONS:
1. Extract this ZIP file
2. Double-click Punctaj_Installer.exe
3. Follow the installation wizard
4. Configure Discord and Supabase credentials
5. Launch from Start Menu

REQUIREMENTS:
- Windows 7 or later (64-bit)
- 100 MB free disk space
- Internet connection

VERSION: 1.0
"@ | Out-File -FilePath $readmeTempPath -Encoding UTF8

[System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $readmeTempPath, "README.txt") | Out-Null
$zip.Dispose()
Remove-Item $readmeTempPath -Force

$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Host "ZIP created: $zipPath ($zipSize MB)" -ForegroundColor Green

Write-Host ""
Write-Host "SUCCESS - Installer ready!" -ForegroundColor Green
Write-Host "Location: $zipPath" -ForegroundColor Green
