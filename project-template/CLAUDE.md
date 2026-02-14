# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## Owner Intent

**Goal:** {{PROJECT_GOAL}}

**Business context:** {{BUSINESS_CONTEXT}}

## Architecture

{{ARCHITECTURE_NOTES}}

### Infrastructure

- Gaming PC (localhost) -- Ollama + primary dev
- The Machine (100.64.130.71) -- ComfyUI + RTX 5060 Ti 16GB
- Routing: local-first, cloud as fallback

## Quick Commands

```bash
# (populated as project develops)
```

## Current Focus

{{CURRENT_FOCUS}}

### Checklist

{{CHECKLIST}}

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | This file -- project bible |
| `SESSION-LOG.md` | CHECK FIRST every session |
| `HANDOFF.md` | Cross-LLM handoff protocol |
| `config.yaml` | Model routing config |
| `tools_config.json` | Tool integrations |
| `usage_log.json` | Cost tracking |
| `knowledge-base/ACTIVE-PROJECTS.md` | Current status |
| `agents/BULLETIN.md` | Multi-agent status board |
| `state/` | Resumable state files |

## Session Protocol

**When starting a new session**, check status first:
1. Read `SESSION-LOG.md` (what happened last)
2. Read `knowledge-base/ACTIVE-PROJECTS.md` (current status)
3. Check `agents/BULLETIN.md` (agent status, if using agents)

## Code Conventions

- Configuration in YAML/JSON, never hardcoded
- Log all API costs to `usage_log.json`
- Local-first, cloud as fallback
- Verbose mode (`-v`) for debugging

## Multi-Agent System (Optional)

Uses file-based coordination with Ralph Wiggum loops.

### Quick Start

```powershell
# Run one agent interactively (testing)
.\agents\agent-runner.ps1 -AgentName <name> -MaxIterations 1

# Run agent autonomously
.\agents\agent-runner.ps1 -AgentName <name>

# Budget check
python agents/cost-guardian.py --check
```

### Adding an Agent

1. Copy `agents/_template/` to `agents/<agent-name>/`
2. Edit PROMPT.md with role, owned dirs, and task list
3. Edit state.json with task definitions
4. Add agent row to BULLETIN.md
5. Run: `.\agents\agent-runner.ps1 -AgentName <agent-name> -MaxIterations 1`

### Coordination

- `agents/BULLETIN.md` -- shared status board (all agents read/write)
- `agents/<name>/state.json` -- per-agent resume state
- `agents/<name>/HEARTBEAT.md` -- last-alive timestamp
- `agents/cost-guardian.py` -- budget watchdog (zero token cost)

## Budget Limits

- Daily warning: ${{DAILY_BUDGET}}
- Monthly hard stop: ${{MONTHLY_BUDGET}}
- Tracked in `usage_log.json`

## Do Not Modify

- `usage_log.json` -- append-only cost tracking
