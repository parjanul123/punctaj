# Punctaj Manager - Professional Installer Generator
# Genereaza installerul profesional cu NSIS

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Punctaj Manager - Installer Generator" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# =======================
# 1. VERIFICA NSIS
# =======================

Write-Host "1️⃣  Verificare NSIS..." -ForegroundColor Yellow

$NSIS_Paths = @(
    "C:\Program Files (x86)\NSIS\makensis.exe",
    "C:\Program Files\NSIS\makensis.exe"
)

$NSIS_Found = $false
foreach ($path in $NSIS_Paths) {
    if (Test-Path $path) {
        $NSIS_Found = $true
        $NSIS_Exe = $path
        Write-Host "   ✅ NSIS găsit: $path" -ForegroundColor Green
        break
    }
}

if (-not $NSIS_Found) {
    Write-Host "`n❌ NSIS nu este instalat!" -ForegroundColor Red
    Write-Host "`nDescarcă și instalează NSIS de la:" -ForegroundColor Yellow
    Write-Host "   https://nsis.sourceforge.io/" -ForegroundColor Cyan
    Write-Host "`nDupă instalare, rulează din nou acest script.`n" -ForegroundColor Yellow
    pause
    exit 1
}

# =======================
# 2. VERIFICA FISIERE
# =======================

Write-Host "`n2️⃣  Verificare fișiere..." -ForegroundColor Yellow

$required_files = @(
    "dist\Punctaj.exe",
    "discord_config.ini",
    "supabase_config.ini"
)

$all_files_exist = $true
foreach ($file in $required_files) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $file - NU GĂSIT" -ForegroundColor Yellow
        if ($file -eq "dist\Punctaj.exe") {
            $all_files_exist = $false
        }
    }
}

if (-not $all_files_exist) {
    Write-Host "`n❌ Punctaj.exe nu găsit! Rulează PyInstaller mai întâi." -ForegroundColor Red
    pause
    exit 1
}

# =======================
# 3. CREARE NSIS SCRIPT
# =======================

Write-Host "`n3️⃣  Generare script NSIS..." -ForegroundColor Yellow

$NSI_Content = @"
; Punctaj Manager Installer
; Creat cu NSIS

!include "MUI2.nsh"

Name "Punctaj Manager v2.0"
OutFile "installer_outputs\Punctaj_Installer.exe"
InstallDir "`$PROGRAMFILES\Punctaj Manager"
RequestExecutionLevel admin

SetCompressor /SOLID lzma

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Romanian"

Section "Instaleaza Punctaj Manager"
  SetOutPath "`$INSTDIR"
  
  File "dist\Punctaj.exe"
  File "discord_config.ini"
  File "supabase_config.ini"
  
  CreateDirectory "`$INSTDIR\data"
  CreateDirectory "`$INSTDIR\arhiva"
  CreateDirectory "`$INSTDIR\logs"
  
  CreateDirectory "`$SMPROGRAMS\Punctaj Manager"
  CreateShortCut "`$SMPROGRAMS\Punctaj Manager\Punctaj Manager.lnk" "`$INSTDIR\Punctaj.exe"
  CreateShortCut "`$SMPROGRAMS\Punctaj Manager\Dezinstaleaza.lnk" "`$INSTDIR\Uninstall.exe"
  CreateShortCut "`$DESKTOP\Punctaj Manager.lnk" "`$INSTDIR\Punctaj.exe"
  
  WriteUninstaller "`$INSTDIR\Uninstall.exe"
  
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" "DisplayName" "Punctaj Manager v2.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" "UninstallString" "`$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" "InstallLocation" "`$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager" "DisplayVersion" "2.0"
  
  MessageBox MB_OK "✅ Punctaj Manager a fost instalat cu succes!"
SectionEnd

Section "Uninstall"
  Delete "`$SMPROGRAMS\Punctaj Manager\Punctaj Manager.lnk"
  Delete "`$SMPROGRAMS\Punctaj Manager\Dezinstaleaza.lnk"
  RMDir "`$SMPROGRAMS\Punctaj Manager"
  Delete "`$DESKTOP\Punctaj Manager.lnk"
  
  Delete "`$INSTDIR\Punctaj.exe"
  Delete "`$INSTDIR\Uninstall.exe"
  RMDir "`$INSTDIR"
  
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Punctaj Manager"
  
  MessageBox MB_OK "✅ Dezinstalaree completă!"
SectionEnd
"@

$NSI_Content | Out-File -FilePath "Punctaj_Installer_Temp.nsi" -Encoding UTF8
Write-Host "   ✅ Script NSIS creat" -ForegroundColor Green

# =======================
# 4. COMPILE NSIS
# =======================

Write-Host "`n4️⃣  Compilare installer cu NSIS..." -ForegroundColor Yellow
Write-Host "   ⏳ Se asteaptă... (poate dura 10-30 secunde)`n" -ForegroundColor Cyan

& $NSIS_Exe /V2 "Punctaj_Installer_Temp.nsi"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ NSIS compilare reușită!" -ForegroundColor Green
    
    # Șterge fișierul temp
    Remove-Item "Punctaj_Installer_Temp.nsi" -Force
    
    # =======================
    # 5. VERIFICA OUTPUT
    # =======================
    
    Write-Host "`n5️⃣  Verificare output..." -ForegroundColor Yellow
    
    if (Test-Path "installer_outputs\Punctaj_Installer.exe") {
        $file_size = (Get-Item "installer_outputs\Punctaj_Installer.exe").Length / 1MB
        Write-Host "   ✅ Installer creat cu succes!" -ForegroundColor Green
        Write-Host "   📦 Mărime: $([Math]::Round($file_size, 2)) MB" -ForegroundColor Cyan
        
        # =======================
        # 6. SUMMARY
        # =======================
        
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "✅ INSTALLERUL A FOST GENERAT CU SUCCES!" -ForegroundColor Green
        Write-Host "========================================`n" -ForegroundColor Cyan
        
        Write-Host "📦 Locație installer:" -ForegroundColor Yellow
        Write-Host "   $(Get-Location)\installer_outputs\Punctaj_Installer.exe`n" -ForegroundColor Cyan
        
        Write-Host "📋 Ce include installerul:" -ForegroundColor Yellow
        Write-Host "   ✓ Punctaj.exe (aplicația)" -ForegroundColor White
        Write-Host "   ✓ discord_config.ini (configurare)" -ForegroundColor White
        Write-Host "   ✓ supabase_config.ini (configurare)" -ForegroundColor White
        Write-Host "   ✓ Directoare pentru data (data, arhiva, logs)" -ForegroundColor White
        Write-Host "   ✓ Shortcuts pe Desktop și Start Menu" -ForegroundColor White
        Write-Host "   ✓ Dezinstalare cu Remove Programs`n" -ForegroundColor White
        
        Write-Host "🚀 Pentru distribuire:" -ForegroundColor Yellow
        Write-Host "   1. Copiază: installer_outputs\Punctaj_Installer.exe" -ForegroundColor White
        Write-Host "   2. Trimite utilizatorilor" -ForegroundColor White
        Write-Host "   3. Ei rulează EXE-ul pentru a instala`n" -ForegroundColor White
        
        Write-Host "Deschidere folder... " -ForegroundColor Cyan
        Start-Process "explorer.exe" -ArgumentList "installer_outputs"
        
    } else {
        Write-Host "   ❌ Installer nu a fost creat!" -ForegroundColor Red
    }
} else {
    Write-Host "`n❌ EROARE LA COMPILARE NSIS!" -ForegroundColor Red
    Write-Host "   Codul de eroare: $LASTEXITCODE`n" -ForegroundColor Red
}

Write-Host "`nApasă Enter pentru a inchide..." -ForegroundColor Cyan
Read-Host
