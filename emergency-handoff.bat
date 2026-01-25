@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo                    AUTOMATION MACHINE - EMERGENCY HANDOFF
echo ================================================================================
echo.
echo Copy ALL output below this line and paste into ChatGPT, Gemini, or any LLM.
echo.
echo ================================================================================
echo                              BEGIN HANDOFF CONTENT
echo ================================================================================
echo.
echo # EMERGENCY HANDOFF - Automation Machine Project
echo.
echo ## CRITICAL: You are in ADVISORY MODE
echo You CANNOT execute commands. The user must run everything manually.
echo Your job: Analyze state, suggest next steps, help write code.
echo.
echo ---
echo.
echo ## Project Overview
echo.
echo The Automation Machine is a multi-LLM orchestration system that:
echo - Routes queries to the best LLM (Claude, Perplexity, local Ollama)
echo - Tracks costs and usage
echo - Auto-documents decisions and patterns
echo.
echo Location: C:\automation-machine
echo.
echo ---
echo.
echo ## Current System State
echo.

if exist "C:\automation-machine\auto_doc_state.json" (
    echo ### auto_doc_state.json:
    echo ```json
    type "C:\automation-machine\auto_doc_state.json"
    echo ```
    echo.
) else (
    echo [auto_doc_state.json not found]
    echo.
)

echo ---
echo.
echo ## Active Projects
echo.

if exist "C:\automation-machine\knowledge-base\ACTIVE-PROJECTS.md" (
    echo ### ACTIVE-PROJECTS.md:
    echo.
    type "C:\automation-machine\knowledge-base\ACTIVE-PROJECTS.md"
    echo.
) else (
    echo [ACTIVE-PROJECTS.md not found]
    echo.
)

echo ---
echo.
echo ## Recent Usage (last entries)
echo.

if exist "C:\automation-machine\usage_log.json" (
    echo ### usage_log.json (summary):
    echo ```json
    type "C:\automation-machine\usage_log.json"
    echo ```
    echo.
) else (
    echo [usage_log.json not found]
    echo.
)

echo ---
echo.
echo ## Key Files Reference
echo.
echo - automation_brain.py  : Main orchestrator
echo - auto_doc.py          : Documentation system
echo - tools_config.json    : Tool configurations
echo - HANDOFF.md           : Full handoff protocol
echo.
echo ## Commands the User Can Run
echo.
echo ```bash
echo # Check status
echo python auto_doc.py --status
echo.
echo # Run a query
echo python automation_brain.py "your query"
echo.
echo # Standalone mode (no LLM needed)
echo python auto_doc.py --standalone-mode
echo ```
echo.
echo ---
echo.
echo ## Your Response Should Be
echo.
echo 1. Acknowledge you received the handoff
echo 2. Confirm you're in ADVISORY mode only
echo 3. Summarize current project status
echo 4. Ask what the user needs help with
echo.
echo ================================================================================
echo                               END HANDOFF CONTENT
echo ================================================================================
echo.
echo.
echo ================================================================================
echo INSTRUCTIONS:
echo 1. Select all text above (Ctrl+A in terminal or scroll and select)
echo 2. Copy to clipboard (Ctrl+C or right-click copy)
echo 3. Open ChatGPT, Gemini, or any LLM
echo 4. Paste and send
echo 5. Continue working with advisory help
echo ================================================================================
echo.
pause
