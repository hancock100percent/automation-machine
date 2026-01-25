# PERSONAL CHEAT SHEET
> Last Updated: January 2026

---

## 1. AUTOMATION MACHINE - DAILY WORKFLOW

### Morning Startup (The Easy Way)
```
Double-click: C:\automation-machine\START.bat
```
That's it. Opens Ollama server + ready terminal automatically.

### Commands
| Command | What it does |
|---------|--------------|
| `brain "question"` | Ask anything (auto-routes to best AI) |
| `brain --learn C:\path` | Learn a codebase |
| `stats` | View documentation status |
| `eod` | End of day summary + logging |

### Examples
```powershell
brain "what does the session manager do?"
brain "how do I use Tailscale?"
brain --tool perplexity "latest ComfyUI updates"
brain -v "complex question"              # Verbose - see routing decisions
```

### End of Day Routine
```powershell
eod                    # Generates daily summary, logs work done
```
Then close terminals.

---

## 2. THE MACHINE (REMOTE) - DAILY SOP

### START (3 Terminals Total)

**Terminal 1 - Session Manager:**
```powershell
ssh michael@100.64.130.71
powershell
cd C:\100Percent\ACTIVE\THE-MACHINE
python run-session.py --no-comfyui
# Leave OPEN
```

**Terminal 2 - ComfyUI Server:**
```powershell
ssh michael@100.64.130.71
powershell
cd C:\ComfyUI
.\venv\Scripts\Activate.ps1
python main.py --port 8189 --listen 0.0.0.0
# Leave OPEN
```

**Browser:**
```
http://100.64.130.71:8189
```

### WORK
- Generate images in browser
- Leave BOTH SSH terminals open
- Don't close anything yet

### STOP (In Order!)
1. **ComfyUI terminal:** `Ctrl+C` (wait for shutdown)
2. **Session manager terminal:** Press `Enter`
3. Answer the 4 prompts (keep it short)
4. Wait for "Session complete"
5. NOW close both SSH terminals

### Emergency Reset
```powershell
taskkill /F /IM python.exe
```

---

## 3. TAILSCALE FILE SHARING

### Your Machines
| Name | Machine |
|------|---------|
| `mike` | Laptop (Windows) |
| `gaming-pc` | Desktop PC (Windows) |
| `100percent` | Ubuntu Server (Linux) |

### Taildrop Folder
```
C:\Users\micha\Taildrop
```

### Send Files
```powershell
tailscale file cp filename.ext MACHINE-NAME:
```

**Examples:**
```powershell
tailscale file cp document.pdf gaming-pc:
tailscale file cp report.md mike:
tailscale file cp script.py 100percent:
```

### Receive Files
```powershell
tailscale file get C:\Users\micha\Taildrop
```
Or receive to current directory:
```powershell
tailscale file get .
```

### Check Status
```powershell
tailscale status                    # See all machines
ls C:\Users\micha\Taildrop          # Check received files
```

---

## 4. NAVIGATION & BASIC COMMANDS

### PowerShell Basics
| Command | What it does |
|---------|--------------|
| `pwd` | Where am I? |
| `dir` or `ls` | What's here? |
| `cd foldername` | Go into folder |
| `cd ..` | Go up one level |
| `cd C:\path` | Jump to exact location |
| `cls` | Clear screen |

### File Operations
| Command | What it does |
|---------|--------------|
| `python file.py` | Run a Python script |
| `copy file1 file2` | Copy a file |
| `move file1 folder\` | Move a file |
| `del file` | Delete a file |

### SSH Commands
| Command | What it does |
|---------|--------------|
| `ssh user@ip` | Connect to remote machine |
| `exit` | Disconnect from SSH |
| `scp file user@ip:path` | Copy file to remote |

### Tips
- **Tab** = autocomplete folder/file names
- **Up Arrow** = repeat last command
- **Ctrl+C** = stop running process

---

## 5. FILE LOCATIONS REFERENCE

### Automation Machine (Laptop)
```
C:\automation-machine\
├── auto_doc.py              ← Main brain script
├── START.bat                ← Double-click to start everything
├── setup_aliases.ps1        ← Run once to set up commands
├── tools_config.json        ← Tools configuration
├── config.yaml              ← Main config
├── usage_log.json           ← Usage tracking
└── knowledge-base\          ← Documentation & logs
    └── research\
        └── conversation-log.md
```

### The Machine (100.64.130.71)
```
C:\100Percent\ACTIVE\THE-MACHINE\
├── run-session.py           ← Session manager
└── portfolio\               ← Upload destination

C:\ComfyUI\
├── venv\                    ← Virtual environment
└── main.py                  ← ComfyUI server
```

### Laptop Workspace
```
C:\Users\micha\
├── fiverr-workspace\        ← Main working folder
│   ├── images\
│   ├── organized\
│   │   ├── airbnb\
│   │   └── comic\
│   ├── image-tagger.py
│   └── tags.json
│
├── Downloads\
│   └── comfyui-batch\       ← Old images
│
└── Taildrop\                ← Tailscale received files
```

---

## 6. TROUBLESHOOTING QUICK FIXES

### Ollama Not Responding
```powershell
# Check if running
tasklist | findstr ollama

# Restart it
taskkill /IM ollama.exe /F
ollama serve
```

### Perplexity 400 Error
**Cause:** Wrong model name

**Valid models:** `sonar`, `sonar-pro`, `sonar-reasoning-pro`

### Model Not Found
```powershell
ollama list                      # See what's installed
ollama pull deepseek-r1:latest   # Pull missing model
ollama pull qwen2.5:32b
```

### ComfyUI Issues
```powershell
# On The Machine, kill all Python
taskkill /F /IM python.exe

# Restart ComfyUI
cd C:\ComfyUI
.\venv\Scripts\Activate.ps1
python main.py --port 8189 --listen 0.0.0.0
```

### API Key Issues
```powershell
# Check if set
echo %PERPLEXITY_API_KEY%
echo %ANTHROPIC_API_KEY%

# If empty, see Section 7
```

### Emergency Resets
```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Kill Ollama
taskkill /IM ollama.exe /F

# Clear terminal
cls
```

---

## 7. ENVIRONMENT VARIABLES

### Required Keys
| Variable | Purpose |
|----------|---------|
| `PERPLEXITY_API_KEY` | Web search via Perplexity |
| `ANTHROPIC_API_KEY` | Claude API for complex tasks |

### Check If Set
```powershell
echo %PERPLEXITY_API_KEY%
echo %ANTHROPIC_API_KEY%
```

### Set Temporarily (Current Session)
```powershell
set PERPLEXITY_API_KEY=pplx-xxxx
set ANTHROPIC_API_KEY=sk-ant-xxxx
```

### Set Permanently (Persists After Restart)
```powershell
setx PERPLEXITY_API_KEY "pplx-your-key-here"
setx ANTHROPIC_API_KEY "sk-ant-your-key-here"
# Restart terminal after running these
```

### Optional Variables
| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | GitHub integration |
| `SUPABASE_URL` | Database URL |
| `SUPABASE_KEY` | Database auth |

---

## QUICK REFERENCE CARD

### Daily Workflow
```
START.bat → brain "question" → eod
```

### Tool Priority (Cost)
1. **Local** (free) → Simple tasks
2. **Perplexity** (~$3/1M) → Web research
3. **Claude** (~$15/1M) → Complex tasks

### Perplexity Models
| Model | Cost | Use |
|-------|------|-----|
| `sonar` | $1/1M | Fast searches |
| `sonar-pro` | $3/1M | Quality (default) |
| `sonar-reasoning-pro` | $5/1M | Complex reasoning |

### Local Models
| Model | Best For |
|-------|----------|
| `deepseek-r1` | Fast reasoning |
| `qwen2.5:32b` | Code, analysis |

### Key IPs & Ports
| Service | Address |
|---------|---------|
| The Machine | `100.64.130.71` |
| ComfyUI | `http://100.64.130.71:8189` |
| Ollama | `http://localhost:11434` |

---

*Run `brain "help"` anytime you forget a command.*
