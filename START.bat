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
