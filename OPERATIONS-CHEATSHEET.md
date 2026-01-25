# Automation Machine - Operations Cheat Sheet

**Last Updated:** January 25, 2026

Quick reference for daily operations. Copy-paste ready commands.

**Repo:** https://github.com/hancock100percent/automation-machine

---

## 1. DAILY STARTUP

```powershell
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags

# Check loaded models
ollama list

# Pull models if missing
ollama pull deepseek-r1:latest
ollama pull qwen2.5:32b
```

---

## 2. COMMON COMMANDS

```powershell
# Basic query (auto-routes to best tool)
python C:\automation-machine\automation_brain.py "your question here"

# Check usage/costs
python C:\automation-machine\automation_brain.py --stats

# List available tools
python C:\automation-machine\automation_brain.py --tools

# Force specific tool
python C:\automation-machine\automation_brain.py --tool perplexity "search query"
python C:\automation-machine\automation_brain.py --tool local-qwen "code question"
python C:\automation-machine\automation_brain.py --tool claude "complex task"

# Verbose mode (see routing decisions)
python C:\automation-machine\automation_brain.py -v "your question"

# Interactive mode
python C:\automation-machine\automation_brain.py
```

---

## 3. TROUBLESHOOTING

### Ollama Not Responding
```powershell
# Check if running
tasklist | findstr ollama

# Restart it
taskkill /IM ollama.exe /F
ollama serve
```

### Perplexity 400 Error
**Cause:** Wrong model name (old names deprecated)

**Valid models:** `sonar`, `sonar-pro`, `sonar-reasoning-pro`

```powershell
# Test Perplexity
python C:\automation-machine\perplexity-debug.py
```

### Model Not Found
```powershell
# List available models
ollama list

# Pull missing model
ollama pull deepseek-r1:latest
ollama pull qwen2.5:32b
```

### API Key Issues
```powershell
# Check if keys are set
echo %PERPLEXITY_API_KEY%
echo %ANTHROPIC_API_KEY%

# Set temporarily (current session)
set PERPLEXITY_API_KEY=pplx-xxxx
set ANTHROPIC_API_KEY=sk-ant-xxxx
```

---

## 4. CHECKING STATUS

```powershell
# Ollama running?
curl http://localhost:11434/api/tags

# Models loaded?
ollama list

# API keys set?
echo %PERPLEXITY_API_KEY%
echo %ANTHROPIC_API_KEY%

# Usage stats
python C:\automation-machine\automation_brain.py --stats

# Available tools
python C:\automation-machine\automation_brain.py --tools
```

---

## 5. ENVIRONMENT VARIABLES

### Required Variables
| Variable | Purpose |
|----------|---------|
| `PERPLEXITY_API_KEY` | Perplexity API (web search) |
| `ANTHROPIC_API_KEY` | Claude API (complex tasks) |

### Optional Variables
| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | GitHub API (not needed - gh CLI uses own auth) |
| `SUPABASE_URL` | Supabase database |
| `SUPABASE_KEY` | Supabase auth |

### Check If Set
```powershell
echo %PERPLEXITY_API_KEY%
echo %ANTHROPIC_API_KEY%
```

### Set Permanently (Windows)
```powershell
# User environment (persists across sessions)
setx PERPLEXITY_API_KEY "pplx-xxxx"
setx ANTHROPIC_API_KEY "sk-ant-xxxx"

# Then restart terminal
```

---

## 6. FILE LOCATIONS

| File | Path |
|------|------|
| Main brain | `C:\automation-machine\automation_brain.py` |
| Tools config | `C:\automation-machine\tools_config.json` |
| Main config | `C:\automation-machine\config.yaml` |
| Usage log | `C:\automation-machine\usage_log.json` |
| Knowledge base | `C:\automation-machine\knowledge-base\` |
| Conversation log | `C:\automation-machine\knowledge-base\research\conversation-log.md` |
| Debug script | `C:\automation-machine\perplexity-debug.py` |

---

## 7. QUICK TESTS

### Test Local Models
```powershell
# Test DeepSeek
python C:\automation-machine\automation_brain.py --tool local-deepseek "What is 2+2?"

# Test Qwen
python C:\automation-machine\automation_brain.py --tool local-qwen "Write a hello world function"
```

### Test Perplexity
```powershell
# Quick test
python C:\automation-machine\perplexity-debug.py

# Via brain
python C:\automation-machine\automation_brain.py --tool perplexity "What day is today?"
```

### Test Routing Logic
```powershell
# Should route to Perplexity (web research)
python C:\automation-machine\automation_brain.py -v "What are the latest news headlines?"

# Should route to local (simple)
python C:\automation-machine\automation_brain.py -v "Explain what a variable is"

# Should route to Claude (complex)
python C:\automation-machine\automation_brain.py -v "Design a microservices architecture"
```

---

## 8. GITHUB INTEGRATION (COMPLETED)

### Status: WORKING
- GitHub CLI installed: `C:\Program Files\GitHub CLI\gh.exe`
- Authenticated as: `hancock100percent`
- Repo: https://github.com/hancock100percent/automation-machine

### Common Commands
```powershell
# Check auth status
gh auth status

# List your repos
gh repo list

# View repo details
gh repo view hancock100percent/automation-machine

# Clone a repo
gh repo clone hancock100percent/automation-machine

# Create issue
gh issue create --title "Bug" --body "Description"

# List issues
gh issue list

# Create pull request
gh pr create --title "Feature" --body "Description"

# List PRs
gh pr list

# Search code across repos
gh search code "pattern"
```

### Git Workflow
```powershell
# Check status
git status

# Stage changes
git add filename.py
git add -A                    # Stage all

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push

# Pull latest
git pull
```

### Quick Sync (after making changes)
```powershell
cd C:\automation-machine
git add -A && git commit -m "Update" && git push
```

---

## QUICK REFERENCE

### Tool Priority
1. **Local** (free) - Simple/medium tasks
2. **Perplexity** (~$3/1M) - Web research
3. **Claude** (~$3-15/1M) - Complex/novel tasks

### Perplexity Models
| Model | Cost | Use Case |
|-------|------|----------|
| `sonar` | $1/1M | Fast, simple searches |
| `sonar-pro` | $3/1M | Quality searches (default) |
| `sonar-reasoning-pro` | $5/1M | Complex reasoning |

### Local Models
| Model | Best For |
|-------|----------|
| `deepseek-r1` | Fast reasoning |
| `qwen2.5:32b` | Code, analysis |
