# ============================================
# Automation Machine - Easy Setup Script
# ============================================
# Run this ONCE to set up your workflow
# After setup: Double-click START.bat, then use brain/stats/eod commands
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTOMATION MACHINE - EASY SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Add functions to PowerShell profile
Write-Host "[1/3] Setting up PowerShell aliases..." -ForegroundColor Yellow

$profileContent = @'

# ============================================
# Automation Machine Commands
# ============================================
function brain { python C:\automation-machine\auto_doc.py $args }
function stats { python C:\automation-machine\auto_doc.py --status }
function eod { python C:\automation-machine\auto_doc.py --daily-update }
# ============================================

'@

# Create profile directory if it doesn't exist
$profileDir = Split-Path $PROFILE -Parent
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    Write-Host "  Created profile directory" -ForegroundColor Gray
}

# Check if profile exists and if aliases are already added
if (Test-Path $PROFILE) {
    $existingProfile = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
    if ($existingProfile -match "Automation Machine Commands") {
        Write-Host "  Aliases already in profile - skipping" -ForegroundColor Green
    } else {
        Add-Content -Path $PROFILE -Value $profileContent
        Write-Host "  Added aliases to existing profile" -ForegroundColor Green
    }
} else {
    Set-Content -Path $PROFILE -Value $profileContent
    Write-Host "  Created new profile with aliases" -ForegroundColor Green
}

Write-Host "  Profile location: $PROFILE" -ForegroundColor Gray

# Step 2: Create START.bat
Write-Host ""
Write-Host "[2/3] Creating START.bat launcher..." -ForegroundColor Yellow

$batContent = @'
@echo off
title Automation Machine Launcher
echo.
echo ========================================
echo   STARTING AUTOMATION MACHINE
echo ========================================
echo.

echo Starting Ollama server...
start "Ollama Server" powershell -NoExit -Command "Write-Host 'OLLAMA SERVER' -ForegroundColor Cyan; Write-Host '=============' -ForegroundColor Cyan; ollama serve"

echo Waiting for Ollama to initialize...
timeout /t 3 /nobreak > nul

echo Opening Automation Machine terminal...
start "Automation Machine" powershell -NoExit -Command "cd C:\automation-machine; Write-Host ''; Write-Host 'AUTOMATION MACHINE READY' -ForegroundColor Green; Write-Host '========================' -ForegroundColor Green; Write-Host ''; Write-Host 'Commands:' -ForegroundColor Yellow; Write-Host '  brain \"your question\"  - Ask anything' -ForegroundColor White; Write-Host '  stats                   - View documentation status' -ForegroundColor White; Write-Host '  eod                     - End of day summary' -ForegroundColor White; Write-Host ''"

echo.
echo Done! You can close this window.
timeout /t 2 > nul
exit
'@

$batPath = "C:\automation-machine\START.bat"
Set-Content -Path $batPath -Value $batContent
Write-Host "  Created: $batPath" -ForegroundColor Green

# Step 3: Test and show success
Write-Host ""
Write-Host "[3/3] Verifying setup..." -ForegroundColor Yellow

$allGood = $true

# Check profile
if (Test-Path $PROFILE) {
    $profileCheck = Get-Content $PROFILE -Raw
    if ($profileCheck -match "function brain") {
        Write-Host "  Profile aliases: OK" -ForegroundColor Green
    } else {
        Write-Host "  Profile aliases: MISSING" -ForegroundColor Red
        $allGood = $false
    }
} else {
    Write-Host "  Profile: NOT FOUND" -ForegroundColor Red
    $allGood = $false
}

# Check START.bat
if (Test-Path $batPath) {
    Write-Host "  START.bat: OK" -ForegroundColor Green
} else {
    Write-Host "  START.bat: MISSING" -ForegroundColor Red
    $allGood = $false
}

# Check auto_doc.py exists
if (Test-Path "C:\automation-machine\auto_doc.py") {
    Write-Host "  auto_doc.py: OK" -ForegroundColor Green
} else {
    Write-Host "  auto_doc.py: MISSING (create it first!)" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host ""
    Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "YOUR NEW WORKFLOW:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. Double-click START.bat" -ForegroundColor White
    Write-Host "     (Opens Ollama + terminal automatically)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Use these commands:" -ForegroundColor White
    Write-Host ""
    Write-Host '     brain "what does X do?"' -ForegroundColor Cyan
    Write-Host "     brain --learn C:\path\to\code" -ForegroundColor Cyan
    Write-Host "     stats" -ForegroundColor Cyan
    Write-Host "     eod" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NOTE: Restart PowerShell or run this to" -ForegroundColor Yellow
    Write-Host "      activate aliases in current session:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  . `$PROFILE" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "  SETUP INCOMPLETE - Check errors above" -ForegroundColor Red
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
}
