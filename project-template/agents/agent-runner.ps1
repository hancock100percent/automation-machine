# Ralph Wiggum Loop -- Autonomous Claude Code agent runner.
# Usage:
#   .\agents\agent-runner.ps1 -AgentName trading -MaxIterations 1   # Test one iteration
#   .\agents\agent-runner.ps1 -AgentName fiverr                     # Run autonomously
#   .\agents\agent-runner.ps1 -AgentName dashboard -DryRun           # See prompt only

param(
    [Parameter(Mandatory = $true)]
    [string]$AgentName,

    [int]$MaxIterations = 20,
    [int]$TimeoutMinutes = 300,
    [int]$CooldownSeconds = 30,
    [int]$MaxStalls = 3,
    [switch]$DryRun
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$AgentDir = Join-Path (Join-Path $RepoRoot "agents") $AgentName
$PromptFile = Join-Path $AgentDir "PROMPT.md"
$StateFile = Join-Path $AgentDir "state.json"
$HeartbeatFile = Join-Path $AgentDir "HEARTBEAT.md"
$BulletinFile = Join-Path (Join-Path $RepoRoot "agents") "BULLETIN.md"

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

if (-not (Test-Path $AgentDir)) {
    Write-Error "Agent directory not found: $AgentDir"
    exit 1
}
if (-not (Test-Path $PromptFile)) {
    Write-Error "PROMPT.md not found: $PromptFile"
    exit 1
}
if (-not (Test-Path $StateFile)) {
    Write-Error "state.json not found: $StateFile"
    exit 1
}

# Check claude CLI is available
try {
    $null = Get-Command claude -ErrorAction Stop
} catch {
    Write-Error "Claude CLI not found. Install Claude Code first."
    exit 1
}

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

function Get-AgentState {
    return Get-Content $StateFile -Raw | ConvertFrom-Json
}

function Get-StateHash {
    <# Returns a hash of the state file for stall detection #>
    $content = Get-Content $StateFile -Raw
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    return [BitConverter]::ToString($hash) -replace "-", ""
}

function Update-Heartbeat {
    param([int]$Iteration, [string]$Status)
    $now = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    $content = @"
# Heartbeat: $AgentName

Last alive: $now
Iteration: $Iteration
Status: $Status
"@
    Set-Content -Path $HeartbeatFile -Value $content -Encoding UTF8
}

function Test-ExitSignal {
    $state = Get-AgentState
    return $state.exit_signal -eq $true
}

function Test-BulletinSignals {
    <# Check BULLETIN.md for PAUSE/STOP signals from cost guardian #>
    if (-not (Test-Path $BulletinFile)) { return $false }
    $content = Get-Content $BulletinFile -Raw
    if ($content -match "SIGNAL:\s*(PAUSE|STOP)") {
        Write-Host "[!] Bulletin signal detected: $($Matches[1])" -ForegroundColor Red
        return $true
    }
    return $false
}

function Build-Prompt {
    param([int]$Iteration)
    $promptContent = Get-Content $PromptFile -Raw
    $stateContent = Get-Content $StateFile -Raw
    $bulletinContent = ""
    if (Test-Path $BulletinFile) {
        $bulletinContent = Get-Content $BulletinFile -Raw
    }

    $fullPrompt = @"
You are running as an autonomous agent in iteration $Iteration.

## Your Instructions (from PROMPT.md):

$promptContent

## Your Current State (from state.json):

$stateContent

## Bulletin Board (from BULLETIN.md):

$bulletinContent

## Iteration Instructions:

1. Follow your Startup Checklist from PROMPT.md
2. Pick the highest-priority PENDING task from your state
3. Execute that ONE task
4. Update your state.json: set the task status to "completed" or "in_progress", increment iteration, update last_updated timestamp
5. Update your HEARTBEAT.md with current timestamp
6. If ALL tasks are complete, set exit_signal to true in state.json
7. If you encounter an error you cannot resolve, set exit_signal to true with exit_reason "error"

IMPORTANT: You must update agents/$AgentName/state.json before finishing. This is how progress is tracked.
"@
    return $fullPrompt
}

# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

$startTime = Get-Date
$stallCount = 0
$prevHash = Get-StateHash

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Ralph Wiggum Loop: $AgentName" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Max iterations: $MaxIterations"
Write-Host "Timeout: $TimeoutMinutes minutes"
Write-Host "Cooldown: $CooldownSeconds seconds"
Write-Host "Max stalls: $MaxStalls"
Write-Host "Repo root: $RepoRoot"
Write-Host ""

for ($i = 1; $i -le $MaxIterations; $i++) {
    $elapsed = (Get-Date) - $startTime
    Write-Host "--- Iteration $i / $MaxIterations (elapsed: $($elapsed.ToString('hh\:mm\:ss'))) ---" -ForegroundColor Yellow

    # Circuit breaker: timeout
    if ($elapsed.TotalMinutes -ge $TimeoutMinutes) {
        Write-Host "[X] Timeout reached ($TimeoutMinutes min). Stopping." -ForegroundColor Red
        Update-Heartbeat -Iteration $i -Status "timeout"
        break
    }

    # Circuit breaker: bulletin signals
    if (Test-BulletinSignals) {
        Write-Host "[X] PAUSE/STOP signal from cost guardian. Stopping." -ForegroundColor Red
        Update-Heartbeat -Iteration $i -Status "paused_by_guardian"
        break
    }

    # Circuit breaker: exit signal from agent
    if (Test-ExitSignal) {
        $state = Get-AgentState
        Write-Host "[OK] Agent set EXIT_SIGNAL. Reason: $($state.exit_reason)" -ForegroundColor Green
        Write-Host "     Message: $($state.exit_message)" -ForegroundColor Green
        Update-Heartbeat -Iteration $i -Status "exited"
        break
    }

    # Build prompt
    $prompt = Build-Prompt -Iteration $i

    if ($DryRun) {
        Write-Host "[DRY RUN] Would send to claude:" -ForegroundColor Magenta
        Write-Host $prompt.Substring(0, [Math]::Min(500, $prompt.Length))
        Write-Host "... (truncated)"
        break
    }

    # Update heartbeat
    Update-Heartbeat -Iteration $i -Status "running"

    # Run Claude Code (non-interactive, print mode)
    Write-Host "  Sending to Claude..." -ForegroundColor Gray
    try {
        $prompt | claude -p --allowedTools "Read,Write,Edit,Glob,Grep,Bash" 2>&1 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "  [ERROR] Claude execution failed: $_" -ForegroundColor Red
        Update-Heartbeat -Iteration $i -Status "error"
        # Don't break -- let stall detection handle persistent errors
    }

    # Stall detection
    $currentHash = Get-StateHash
    if ($currentHash -eq $prevHash) {
        $stallCount++
        Write-Host "  [!] No state change detected (stall $stallCount/$MaxStalls)" -ForegroundColor DarkYellow
        if ($stallCount -ge $MaxStalls) {
            Write-Host "[X] Max stalls reached ($MaxStalls). Agent appears stuck. Stopping." -ForegroundColor Red
            Update-Heartbeat -Iteration $i -Status "stalled"
            break
        }
    } else {
        $stallCount = 0
        $prevHash = $currentHash
    }

    # Cooldown between iterations
    if ($i -lt $MaxIterations) {
        Write-Host "  Cooling down for $CooldownSeconds seconds..." -ForegroundColor Gray
        Start-Sleep -Seconds $CooldownSeconds
    }
}

# Final status
$totalElapsed = (Get-Date) - $startTime
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Run complete: $AgentName" -ForegroundColor Cyan
Write-Host "  Total time: $($totalElapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Print final state summary
$finalState = Get-AgentState
$completedCount = ($finalState.completed_tasks | Measure-Object).Count
$pendingCount = ($finalState.tasks | Where-Object { $_.status -eq "pending" } | Measure-Object).Count
Write-Host "  Completed tasks: $completedCount"
Write-Host "  Pending tasks: $pendingCount"
Write-Host "  Exit signal: $($finalState.exit_signal)"
if ($finalState.exit_reason) {
    Write-Host "  Exit reason: $($finalState.exit_reason)"
}
