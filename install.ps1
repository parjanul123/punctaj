#Requires -RunAsAdministrator
# Punctaj Manager v2.0.0 - Professional Installer (PowerShell)

param(
    [switch]$Silent = $false
)

# Configuration
$ProductName = "Punctaj Manager"
$Version = "2.0.0"
$InstallPath = "C:\Program Files\Punctaj"
$AppDataPath = "$env:APPDATA\Punctaj"
$SourceExe = "dist\punctaj.exe"
$SourceConfigs = @("discord_config.ini", "supabase_config.ini", ".secure_key", "json_encryptor.py")

function Write-Header {
    Clear-Host
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "║         PUNCTAJ MANAGER v2.0.0 - PROFESSIONAL INSTALLER                 ║" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "║         Cloud-Enabled Employee Attendance Tracking System               ║" -ForegroundColor Cyan
    Write-Host "║              with Discord Authentication & Data Protection              ║" -ForegroundColor Cyan
    Write-Host "║                                                                           ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Administrator {
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object System.Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Application {
    Write-Header
    
    # Check admin rights
    if (-not (Test-Administrator)) {
        Write-Host "❌ ERROR: Administrator privileges required!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please run this script as Administrator (right-click PowerShell, 'Run as Administrator')"
        Write-Host ""
        pause
        exit 1
    }
    
    Write-Host "✓ Administrator privileges verified" -ForegroundColor Green
    Write-Host ""
    
    # Check if source exe exists
    if (-not (Test-Path $SourceExe)) {
        Write-Host "❌ ERROR: $SourceExe not found!" -ForegroundColor Red
        Write-Host "Please ensure dist\punctaj.exe exists before running this installer."
        Write-Host ""
        pause
        exit 1
    }
    
    # Display installation info
    Write-Host "📁 Installation Information:" -ForegroundColor Yellow
    Write-Host "   • Program folder: $InstallPath" -ForegroundColor White
    Write-Host "   • User data:      $AppDataPath" -ForegroundColor White
    Write-Host ""
    
    # Create directories
    Write-Host "📂 Creating directories..." -ForegroundColor Yellow
    @($InstallPath, "$InstallPath\data", "$InstallPath\logs", "$InstallPath\arhiva", $AppDataPath) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
        }
    }
    Write-Host "   ✓ Directories created" -ForegroundColor Green
    Write-Host ""
    
    # Copy executable
    Write-Host "📦 Installing application files..." -ForegroundColor Yellow
    Copy-Item -Path $SourceExe -Destination "$InstallPath\Punctaj_Manager.exe" -Force
    Write-Host "   ✓ Punctaj_Manager.exe" -ForegroundColor Green
    
    # Copy configuration files
    foreach ($config in $SourceConfigs) {
        if (Test-Path $config) {
            Copy-Item -Path $config -Destination "$InstallPath\$config" -Force
            Copy-Item -Path $config -Destination "$AppDataPath\$config" -Force
            
            # Hide sensitive files
            if ($config -eq ".secure_key" -or $config -eq ".env") {
                (Get-Item "$InstallPath\$config" -Force).Attributes = "Hidden"
                (Get-Item "$AppDataPath\$config" -Force).Attributes = "Hidden"
            }
            
            Write-Host "   ✓ $config" -ForegroundColor Green
        }
    }
    Write-Host ""
    
    # Register in Windows registry
    Write-Host "🔧 Registering application in Windows..." -ForegroundColor Yellow
    
    $regPath = "HKLM:\Software\Punctaj"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    
    Set-ItemProperty -Path $regPath -Name "Install_Dir" -Value $InstallPath -Force
    Set-ItemProperty -Path $regPath -Name "Version" -Value $Version -Force
    
    # Add to Add/Remove Programs
    $uninstallPath = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj"
    if (-not (Test-Path $uninstallPath)) {
        New-Item -Path $uninstallPath -Force | Out-Null
    }
    
    Set-ItemProperty -Path $uninstallPath -Name "DisplayName" -Value "$ProductName $Version" -Force
    Set-ItemProperty -Path $uninstallPath -Name "UninstallString" -Value "$InstallPath\uninstall.bat" -Force
    Set-ItemProperty -Path $uninstallPath -Name "DisplayVersion" -Value $Version -Force
    Set-ItemProperty -Path $uninstallPath -Name "Publisher" -Value "Punctaj Team" -Force
    
    Write-Host "   ✓ Registry configured" -ForegroundColor Green
    Write-Host ""
    
    # Create shortcuts
    Write-Host "🎯 Creating shortcuts..." -ForegroundColor Yellow
    
    $WshShell = New-Object -ComObject WScript.Shell
    
    # Desktop shortcut
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $desktopShortcut = Join-Path $desktopPath "Punctaj Manager.lnk"
    $shortcut = $WshShell.CreateShortcut($desktopShortcut)
    $shortcut.TargetPath = "$InstallPath\Punctaj_Manager.exe"
    $shortcut.Description = "Punctaj Manager - Employee Attendance System"
    $shortcut.IconLocation = "$InstallPath\Punctaj_Manager.exe,0"
    $shortcut.Save()
    Write-Host "   ✓ Desktop shortcut" -ForegroundColor Green
    
    # Start Menu shortcut
    $startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
    $startMenuShortcut = Join-Path $startMenuPath "Punctaj Manager.lnk"
    $shortcut = $WshShell.CreateShortcut($startMenuShortcut)
    $shortcut.TargetPath = "$InstallPath\Punctaj_Manager.exe"
    $shortcut.Description = "Punctaj Manager - Employee Attendance System"
    $shortcut.IconLocation = "$InstallPath\Punctaj_Manager.exe,0"
    $shortcut.Save()
    Write-Host "   ✓ Start Menu shortcut" -ForegroundColor Green
    Write-Host ""
    
    # Create uninstaller
    Write-Host "🧹 Creating uninstaller..." -ForegroundColor Yellow
    $uninstallerContent = @'
@echo off
echo Uninstalling Punctaj Manager...
del /F /Q "{0}\Punctaj_Manager.exe" 2>nul
del /F /Q "{0}\discord_config.ini" 2>nul
del /F /Q "{0}\supabase_config.ini" 2>nul
del /F /Q "{0}\.secure_key" 2>nul
del /F /Q "{0}\json_encryptor.py" 2>nul
rmdir /S /Q "{0}\logs" 2>nul
rmdir /S /Q "{0}\arhiva" 2>nul
rmdir "{0}" 2>nul
del "%USERPROFILE%\Desktop\Punctaj Manager.lnk" 2>nul
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Punctaj Manager.lnk" 2>nul
reg delete "HKLM\Software\Punctaj" /f 2>nul
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj" /f 2>nul
echo Punctaj Manager has been uninstalled.
pause
'@ -f $InstallPath
    
    Set-Content -Path "$InstallPath\uninstall.bat" -Value $uninstallerContent -Force
    Write-Host "   ✓ Uninstaller created" -ForegroundColor Green
    Write-Host ""
    
    # Show completion message
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                    INSTALLATION COMPLETE!                                ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Punctaj Manager $Version has been successfully installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Installation Details:" -ForegroundColor Yellow
    Write-Host "   • Application: $InstallPath\Punctaj_Manager.exe" -ForegroundColor White
    Write-Host "   • User Data:   $AppDataPath" -ForegroundColor White
    Write-Host "   • Shortcuts:   Desktop & Start Menu" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 What's Next:" -ForegroundColor Yellow
    Write-Host "   1. A shortcut has been created on your Desktop" -ForegroundColor White
    Write-Host "   2. You can also find it in Start Menu > Punctaj Manager" -ForegroundColor White
    Write-Host "   3. Click to launch the application" -ForegroundColor White
    Write-Host ""
    Write-Host "🔐 Security Features:" -ForegroundColor Yellow
    Write-Host "   • Discord Authentication enabled" -ForegroundColor White
    Write-Host "   • Supabase cloud sync configured" -ForegroundColor White
    Write-Host "   • Log files encrypted with AES-256" -ForegroundColor White
    Write-Host "   • Data protection: Files cannot be modified outside the app" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 Configuration Files:" -ForegroundColor Yellow
    Write-Host "   • discord_config.ini - Discord OAuth2 settings" -ForegroundColor White
    Write-Host "   • supabase_config.ini - Cloud database settings" -ForegroundColor White
    Write-Host "   • .secure_key - Encryption key (hidden, auto-generated)" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Important:" -ForegroundColor Yellow
    Write-Host "   • Do NOT delete configuration files" -ForegroundColor White
    Write-Host "   • Do NOT modify .secure_key" -ForegroundColor White
    Write-Host "   • Data is protected and encrypted" -ForegroundColor White
    Write-Host ""
    Write-Host "✨ Installation folder: $InstallPath" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not $Silent) {
        pause
    }
}

# Run installer
Install-Application
