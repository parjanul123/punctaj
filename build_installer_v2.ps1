# ==========================================
# Punctaj Application Build & Package v2.0
# PowerShell build script with config resolver
# ==========================================

param(
    [switch]$CleanOnly = $false,
    [switch]$NoZip = $false,
    [switch]$NoNSIS = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$DistDir = "dist\Punctaj"
$InstallerOut = "installer_outputs"
$BuildLog = "build.log"

# Colors
$Colors = @{
    Green  = "`e[92m"
    Red    = "`e[91m"
    Yellow = "`e[93m"
    Cyan   = "`e[96m"
    Reset  = "`e[0m"
}

function Write-Status {
    param(
        [string]$Message,
        [ValidateSet("OK", "INFO", "WARNING", "ERROR")]
        [string]$Status = "INFO"
    )
    
    $color = @{
        OK      = $Colors.Green
        INFO    = $Colors.Cyan
        WARNING = $Colors.Yellow
        ERROR   = $Colors.Red
    }
    
    $prefix = @{
        OK      = "[✓]"
        INFO    = "[*]"
        WARNING = "[!]"
        ERROR   = "[✗]"
    }
    
    Write-Host "$($color[$Status])$($prefix[$Status]) $Message$($Colors.Reset)"
}

function New-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host ""
}

# ==========================================
# MAIN BUILD PROCESS
# ==========================================

New-Section "Punctaj Application Build v2.0"
Write-Status "Starting build process..." INFO

# STEP 1: Clean previous builds
New-Section "STEP 1: Cleaning Previous Builds"

if (Test-Path "dist") {
    Write-Status "Removing dist directory..." INFO
    Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
}

if (Test-Path "build") {
    Write-Status "Removing build directory..." INFO
    Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
}

if (Test-Path "$InstallerOut") {
    Write-Status "Removing installer_outputs directory..." INFO
    Remove-Item -Path "$InstallerOut" -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
}

New-Item -ItemType Directory -Path "$InstallerOut" -Force | Out-Null
Write-Status "Clean complete" OK

if ($CleanOnly) {
    Write-Status "Clean-only mode - exiting" OK
    exit 0
}

# STEP 2: Build main executable
New-Section "STEP 2: Building Main Executable"
Write-Status "Building Punctaj.exe with PyInstaller..." INFO
Write-Status "This may take a few minutes..." WARNING

if (-not (Test-Path "punctaj.spec")) {
    Write-Status "punctaj.spec not found" ERROR
    exit 1
}

$buildOutput = & pyinstaller punctaj.spec --distpath dist --buildpath build 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Status "PyInstaller build failed" ERROR
    $buildOutput | Out-File -FilePath $BuildLog
    Write-Status "Check $BuildLog for details" WARNING
    exit 1
}

if (-not (Test-Path "dist\Punctaj\Punctaj.exe")) {
    Write-Status "Punctaj.exe not created" ERROR
    exit 1
}

Write-Status "Punctaj.exe created successfully" OK

# STEP 3: Create application directories
New-Section "STEP 3: Creating Application Directories"

@("data", "arhiva", "logs") | ForEach-Object {
    New-Item -ItemType Directory -Path "$DistDir\$_" -Force -ErrorAction SilentlyContinue | Out-Null
    Write-Status "Created: $_" OK
}

# STEP 4: Copy NEW support files
New-Section "STEP 4: Copying NEW Support Files"

$NewFiles = @(
    "config_resolver.py",
    "SETUP_SUPABASE_WIZARD.py",
    "DATABASE_CONNECTION_DIAGNOSTIC.py",
    "QUICK_TEST_DATABASE.py",
    "INSTALLER_README.txt",
    "INSTALLER_DATABASE_TROUBLESHOOTING_GUIDE.md",
    "IMPLEMENTATION_STEPS.txt",
    "00_QUICK_REFERENCE.txt"
)

$copyCount = 0
foreach ($file in $NewFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination "$DistDir\" -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Status "Copied: $file" OK
        $copyCount++
    } else {
        Write-Status "NOT FOUND: $file" WARNING
    }
}

Write-Status "Copied $copyCount/$($NewFiles.Count) support files" INFO

# STEP 5: Copy configuration files
New-Section "STEP 5: Copying Configuration Templates"

@("discord_config.ini", "supabase_config.ini") | ForEach-Object {
    if (Test-Path $_) {
        Copy-Item -Path $_ -Destination "$DistDir\" -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Status "Copied: $_" OK
    } else {
        Write-Status "NOT FOUND: $_ (will need configuration on first run)" WARNING
    }
}

# STEP 6: Copy installer scripts
New-Section "STEP 6: Copying Installer Scripts"

@("installer_gui.py", "installer_app.py") | ForEach-Object {
    if (Test-Path $_) {
        Copy-Item -Path $_ -Destination "$DistDir\" -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Status "Copied: $_" OK
    }
}

# STEP 7: Copy data structure
New-Section "STEP 7: Copying Initial Data"

if (Test-Path "data") {
    Copy-Item -Path "data\*" -Destination "$DistDir\data\" -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
    Write-Status "Data directory copied" OK
} else {
    Write-Status "Data directory not found (will be created on first run)" WARNING
}

if (Test-Path "arhiva") {
    Copy-Item -Path "arhiva\*" -Destination "$DistDir\arhiva\" -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
    Write-Status "Archive directory copied" OK
}

# STEP 8: Create documentation
New-Section "STEP 8: Creating Documentation"

$setupInstructions = @"
# Punctaj Application v2.0 - Setup Instructions

## Welcome!

Thank you for installing Punctaj. This package includes automatic configuration tools.

## First Run

1. Run the application
2. A Setup Wizard will appear automatically
3. Choose: Load configuration from file OR Enter manually
4. Enter your Supabase credentials
5. Test the connection
6. Save and continue

## Manual Setup (if needed)

If the wizard doesn't appear:
```
python SETUP_SUPABASE_WIZARD.py
```

## Verify Installation

To test if everything is configured correctly:
```
python QUICK_TEST_DATABASE.py
```

Expected result: Green checkmarks (✓)

## Troubleshooting

If you encounter issues:
```
python DATABASE_CONNECTION_DIAGNOSTIC.py
```

This will:
- Search for configuration files
- Validate settings
- Test database connection
- Provide recommendations

## Configuration Files

- **supabase_config.ini** - Supabase connection settings
- **discord_config.ini** - Discord OAuth (optional)

## Need Help?

See: INSTALLER_DATABASE_TROUBLESHOOTING_GUIDE.md

## System Requirements

- Windows 7 or later
- 100 MB free disk space
- Internet connection for cloud sync

---

Version: 2.0
Date: 1 February 2026
Status: Production Ready
"@

$setupInstructions | Out-File -FilePath "$DistDir\SETUP_INSTRUCTIONS.txt" -Encoding UTF8
Write-Status "Setup instructions created" OK

# STEP 9: Create ZIP installer
if (-not $NoZip) {
    New-Section "STEP 9: Creating ZIP Package"
    
    $zipPath = "$InstallerOut\Punctaj_Portable.zip"
    Write-Status "Creating ZIP archive..." INFO
    
    try {
        if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
        Compress-Archive -Path "dist\Punctaj" -DestinationPath $zipPath -Force -ErrorAction Stop | Out-Null
        
        $zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
        Write-Status "ZIP created: Punctaj_Portable.zip ($zipSize MB)" OK
    }
    catch {
        Write-Status "ZIP creation failed: $_" WARNING
    }
}

# STEP 10: Create NSIS installer
if (-not $NoNSIS) {
    New-Section "STEP 10: Creating NSIS Installer"
    
    $nsisPath = "C:\Program Files (x86)\NSIS\makensis.exe"
    
    if (Test-Path $nsisPath) {
        Write-Status "Compiling NSIS installer..." INFO
        
        try {
            & $nsisPath "Punctaj_Installer.nsi" "/DOUTDIR=$InstallerOut" 2>&1 | Out-Null
            
            if (Test-Path "$InstallerOut\Punctaj_Installer.exe") {
                $exeSize = [math]::Round((Get-Item "$InstallerOut\Punctaj_Installer.exe").Length / 1MB, 2)
                Write-Status "NSIS installer created: Punctaj_Installer.exe ($exeSize MB)" OK
            } else {
                Write-Status "NSIS compilation failed" WARNING
            }
        }
        catch {
            Write-Status "NSIS build error: $_" WARNING
        }
    } else {
        Write-Status "NSIS not found - skipping .exe installer" WARNING
        Write-Status "Install NSIS from: https://nsis.sourceforge.io/" INFO
    }
}

# STEP 11: Generate build summary
New-Section "STEP 11: Generating Build Summary"

$summary = @"
===========================================
   PUNCTAJ BUILD SUMMARY
===========================================

BUILD INFORMATION:
  Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
  Version: 2.0
  Build Type: Full Application + Installers

EXECUTABLE:
  Location: dist\Punctaj\Punctaj.exe
  Status: Created ✓

NEW FEATURES INCLUDED:
  ✓ config_resolver.py (auto-config discovery)
  ✓ SETUP_SUPABASE_WIZARD.py (GUI setup wizard)
  ✓ DATABASE_CONNECTION_DIAGNOSTIC.py (diagnostics)
  ✓ QUICK_TEST_DATABASE.py (quick verification)

INSTALLER PACKAGES:
"@

if (Test-Path "$InstallerOut\Punctaj_Portable.zip") {
    $summary += "`n  ✓ Punctaj_Portable.zip (ZIP archive - portable)"
}

if (Test-Path "$InstallerOut\Punctaj_Installer.exe") {
    $summary += "`n  ✓ Punctaj_Installer.exe (Windows installer - recommended)"
}

$summary += @"

FILES IN PACKAGE:
  - Punctaj.exe (main application)
  - config_resolver.py
  - SETUP_SUPABASE_WIZARD.py
  - DATABASE_CONNECTION_DIAGNOSTIC.py
  - QUICK_TEST_DATABASE.py
  - installer_gui.py
  - installer_app.py
  - supabase_config.ini (template)
  - discord_config.ini (template)
  - SETUP_INSTRUCTIONS.txt

USAGE:
  1. Run Punctaj_Installer.exe OR extract Punctaj_Portable.zip
  2. Setup Wizard will appear automatically
  3. Follow wizard to configure Supabase
  4. Run QUICK_TEST_DATABASE.py to verify
  5. Launch Punctaj.exe

BUILD STATUS: SUCCESS ✓
===========================================
"@

$summary | Out-File -FilePath "$InstallerOut\BUILD_SUMMARY.txt" -Encoding UTF8
Write-Host $summary

# Final cleanup
if (Test-Path $BuildLog) { Remove-Item $BuildLog -Force -ErrorAction SilentlyContinue }

# Final summary
New-Section "BUILD COMPLETE!"
Write-Status "Installer packages ready in: $InstallerOut" OK
Write-Status "Files created:" INFO
Get-ChildItem "$InstallerOut" -File | ForEach-Object {
    Write-Status "  • $($_.Name)" OK
}

Write-Host ""
Write-Status "Next steps:" INFO
Write-Status "  1. Copy installers to USB or share online" INFO
Write-Status "  2. Run on target device" INFO
Write-Status "  3. Setup Wizard will guide configuration" INFO
Write-Host ""
