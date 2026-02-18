# Test script for Supabase sync verification
# Run the EXE and capture debug output

$exe_dir = "d:\punctaj\PUNCTAJ_DIST"
$exe_path = "$exe_dir\Punctaj.exe"

if (-not (Test-Path $exe_path)) {
    Write-Host "[ERROR] EXE not found at $exe_path" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Starting Punctaj.exe for testing..." -ForegroundColor Cyan
Write-Host "[INFO] Using folder: $exe_dir" -ForegroundColor Cyan
Write-Host ""

# Check if config exists
$config_path = "$exe_dir\supabase_config.ini"
if (Test-Path $config_path) {
    Write-Host "[OK] supabase_config.ini found" -ForegroundColor Green
    $size = (Get-Item $config_path).Length
    Write-Host "[OK] Config file size: $size bytes"
} else {
    Write-Host "[ERROR] supabase_config.ini NOT FOUND" -ForegroundColor Red
}

Write-Host ""
Write-Host "Files in PUNCTAJ_DIST:" -ForegroundColor Yellow
Get-ChildItem -Path $exe_dir -File | Select-Object Name, @{Name='Size(KB)';Expression={[math]::Round($_.Length/1KB,2)}} | Format-Table -AutoSize

Write-Host ""
Write-Host "Starting application..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Run EXE - this will show debug output if running with console
& $exe_path

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "[DONE] Application test completed" -ForegroundColor Green
