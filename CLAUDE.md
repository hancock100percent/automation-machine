# Automation Machine

Local-first AI orchestration system for cost-optimized query routing across multiple LLMs.

**Repo:** https://github.com/hancock100percent/automation-machine

## Owner Intent

**Goal:** Become an expert in everything Claude has to offer - Claude Code, Claude API, MCP servers, integrations - and connect it with every possible tool to build and advertise automation expertise.

**Business context:** Building a Fiverr-based automation consultancy. Every feature learned and tool connected is a potential service offering.

**When assisting:** Proactively mention Claude features, MCP integrations, or capabilities that could enhance the automation-machine or expand service offerings.

## Architecture

```
Gaming PC (localhost)       → Ollama server + automation_brain.py (primary dev)
The Machine (100.64.130.71) → ComfyUI + RTX 5060 Ti 16GB (image generation)
S22 Ultra (100.115.120.118) → Mobile access via Termux + Tailscale SSH
Laptop                      → Mobile access via Tailscale
```

### Routing Logic
```
Query → Analyze complexity/needs
         ↓
Needs web data?    → Perplexity sonar-pro (~$0.001)
Needs images?      → ComfyUI (FREE, local GPU)
Simple query?      → DeepSeek R1 (FREE, local)
Code/analysis?     → Qwen 2.5 32B (FREE, local)
Complex/novel?     → Claude Sonnet (last resort, ~$0.15)
```

**Philosophy:** 90%+ of queries run locally for free. Cloud only when necessary.

## Quick Commands

```bash
# Queries
python automation_brain.py "your question"      # Auto-routed
python automation_brain.py -v "question"        # Verbose (see routing)
python automation_brain.py --tool perplexity "web search"
python automation_brain.py --tool local-qwen "code question"
python automation_brain.py --tool claude "complex problem"

# Image Generation
python automation_brain.py "generate image of luxury candle"

# Video Generation
python automation_brain.py "animate this candle image"
python automation_brain.py "create video from output/candle.png"
python automation_brain.py --tool comfyui-video "animate with flame motion"

# Talking Head (Avatar Videos)
python automation_brain.py "generate talking head photo: face.png audio: script.wav"
python automation_brain.py --tool comfyui-video-talking-head "avatar from photo.png with audio.wav"

# Status
python automation_brain.py --stats              # View costs
python automation_brain.py --tools              # List available tools

# Sprint Management
python automation_brain.py --sprint             # Show current sprint
python automation_brain.py --standup            # Generate standup report
python automation_brain.py --teams              # Show agent teams
python automation_brain.py --team "spawn video-production"  # Spawn team

# Knowledge Ingestion
python knowledge_ingest.py --youtube "URL"      # Ingest YouTube video
python knowledge_ingest.py --audio "file.mp3"   # Ingest podcast/audio
python knowledge_ingest.py --pdf "book.pdf"     # Ingest PDF document
python knowledge_ingest.py --web "URL"          # Ingest web article
python knowledge_ingest.py --list               # List training docs

# Documentation
python auto_doc.py --update-projects            # Update project docs
python auto_doc.py --eod "summary"              # End of day update
```

## Current Focus

**Fiverr Gig Launch: AI Marketing Automation**
- Primary: $500 / $1,200 / $2,500 tiers
- Secondary: AI Image Generation $15 / $35 / $75
- Demo client: `demo-clients/candle-co/`

### Checklist
- [x] ComfyUI integration working
- [x] Content generation (30-day calendar)
- [x] SDXL quality workflow (with refiner)
- [x] GitHub MCP integration
- [x] Browser detection routing
- [x] Analytics dashboard mockup (fiverr-assets/)
- [x] Case study documentation (demo-clients/candle-co/)
- [x] Gig descriptions (fiverr-assets/)
- [x] Generate sample images (14 generated)
- [ ] Video demos (IN PROGRESS - FantasyTalking + Wan2.1 GGUF)
  - [x] Wan2.1 video generation tested (i2v_wan_test_00001.mp4)
  - [x] TTS audio generated (edge-tts, 4 WAV files)
  - [x] FantasyTalking installed (WanVideoWrapper + model)
  - [x] FantasyTalking TESTED & APPROVED (2026-02-02, replaces SadTalker)
  - [x] Wan2.1 I2V GGUF downloaded (Q5_K_M quantized, 12.7GB)
  - [x] umt5-xxl GGUF encoder downloaded (Q5_K_M, 4.1GB)
  - [ ] Video 1: AI Marketing Automation (60-90s)
  - [ ] Video 2: AI Image Generation (45-60s)
  - [ ] Video 3: Analytics Dashboard (45-60s)
  - See: `fiverr-assets/VIDEO-PRODUCTION.md` for tracker
  - Scripts: `demo-clients/candle-co/video-scripts.md`
- [ ] Publish gigs on Fiverr

## Key Files

| File | Purpose |
|------|---------|
| `automation_brain.py` | Main orchestration engine |
| `comfyui_job.py` | Long-running ComfyUI job manager (fire-and-forget) |
| `knowledge_ingest.py` | Training document pipeline (YouTube, podcasts, PDFs) |
| `auto_doc.py` | Auto-documentation system |
| `config.yaml` | Model configs, routing thresholds |
| `tools_config.json` | Tool integrations (Perplexity, ComfyUI, Claude) |
| `usage_log.json` | Cost tracking database |
| `projects/registry.json` | Sprint tracking, agent teams, project domains |
| `HANDOFF.md` | Cross-LLM handoff protocol |
| `fiverr-assets/VIDEO-PRODUCTION.md` | Video production tracker |
| `demo-clients/candle-co/video-scripts.md` | Demo video scripts |
| `video-production/state/generation_progress.json` | **CHECK FIRST** - Resume state for video generation |
| `agents/BULLETIN.md` | Multi-agent shared status board |
| `agents/agent-runner.ps1` | Ralph Wiggum autonomous loop launcher |
| `agents/cost-guardian.py` | Budget watchdog (zero token cost) |
| `agents/*/PROMPT.md` | Per-agent instructions |
| `agents/*/state.json` | Per-agent progress state (resume-capable) |

## Resuming Video Generation

**When starting a new session**, check video progress first:
```bash
python video-production/scripts/generate_comfyui_assets.py --resume-status
```

The script auto-resumes: completed jobs/segments are skipped. Just re-run to continue:
```bash
# Resume all remaining FantasyTalking + I2V jobs
python video-production/scripts/generate_comfyui_assets.py

# Or run in a standalone terminal (survives Claude Code timeouts):
# Open PowerShell and run directly -- no Claude Code session needed
python video-production/scripts/generate_comfyui_assets.py --fantasy
```

**TIP:** For long generation runs (2+ hours), run the script directly in PowerShell instead of through Claude Code to avoid session timeouts.

## Code Conventions

- Configuration in YAML/JSON, never hardcoded
- Log all API costs to `usage_log.json`
- Local-first, cloud as fallback
- Verbose mode (`-v`) for debugging routing decisions

## Environment Variables Required

```
ANTHROPIC_API_KEY     # Claude API
PERPLEXITY_API_KEY    # Perplexity web research
```

## Do Not Modify

- `workflows/sdxl_basic.json` - Original ComfyUI workflow (reference)
- `output/` - Generated images directory
- `auto_doc_state.json` - Auto-doc internal state

## Workflows

| Workflow | Purpose |
|----------|---------|
| `sdxl_basic.json` | Original basic SDXL workflow |
| `sdxl_quality.json` | Enhanced with refiner + quality prompts |
| `image_to_video.json` | **Wan2.1 I2V fp8 (RECOMMENDED)** - ~42 min |
| `image_to_video_animatediff.json` | AnimateDiff for motion loops |
| `talking_head.json` | SadTalker for avatar videos (legacy) |
| `talking_head_fantasy.json` | **FantasyTalking (RECOMMENDED)** - primary avatar |
| `image_to_video_wan22.json` | Wan2.1 I2V GGUF (SLOWER - not recommended) |
| `lipsync_wav2lip.json` | Wav2Lip alternative lip sync |

## Knowledge Base Structure

```
knowledge-base/
├── ACTIVE-PROJECTS.md    # Current work status
├── PROJECT-RECAP.md      # Architecture overview
├── research/             # Query history, conversation logs
├── decisions/            # Past architectural decisions
├── patterns/             # Auto-detected reusable patterns
└── training/             # Ingested training documents (YouTube, podcasts, PDFs)
```

## Project Registry Structure

```
projects/
└── registry.json         # Sprint tracking, teams, domains, certifications
```

The registry contains:
- **domains** - Project areas (marketing, trading, ML, etc.)
- **certifications** - 10-cert roadmap with priorities
- **sprints** - Scrum-style sprint tracking
- **teams** - Multi-agent team configurations
- **agent_types** - Specialist agent definitions

## Budget Limits

- Daily warning: $5
- Monthly hard stop: $50
- Current spend tracked in `usage_log.json`

## Claude Ecosystem to Master

### Claude Code (CLI) - Current
- Terminal-based assistant
- File editing, code generation, git operations
- MCP server integrations
- Hooks for automation triggers

### Claude in Chrome (Browser Extension) - INSTALLED
- Browser automation and navigation
- Form filling, multi-tab workflows
- Record & replay workflows
- Built-in: Gmail, Calendar, Docs, Slack, GitHub

### Claude Desktop App - INSTALLED
- Native desktop AI assistant on Gaming PC

### Perplexity Comet Browser - INSTALLED
- AI-native browser with agentic browsing (free with Perplexity subscription)
- Multi-tab intelligence, form filling, web automation
- Use for: competitor research, data extraction, automated browsing workflows

### MCP Servers (Tool Integrations)
- Connect Claude to external services
- Databases, APIs, file systems, custom tools
- See: MCP configuration section below

### Claude API
- Build custom Claude-powered applications
- Integrate into automation_brain.py for advanced routing

## MCP Server Configuration

Model Context Protocol (MCP) extends Claude's capabilities by connecting to external services.

### Current MCP Integrations

| MCP Server | Status | Purpose |
|------------|--------|---------|
| GitHub | ENABLED | Code search, repo management, PR review |
| Supabase | PENDING | Database storage, analytics |
| Custom | PLANNED | automation-machine state access |

### GitHub MCP Setup

**Status:** INSTALLED & AUTHENTICATED (hancock100percent)

```bash
# Check auth status
gh auth status

# Common commands
gh repo list                    # List your repos
gh repo view                    # View current repo
gh issue list                   # List issues
gh pr list                      # List PRs
gh search code "pattern"        # Search code

# automation_brain.py auto-routes GitHub queries to gh CLI
python automation_brain.py "list my recent repos"
python automation_brain.py "search code for async patterns"
```

**Safe operations only:** list, view, search, status (no write operations without explicit flag)

### Supabase MCP Setup (Future)

```bash
# Set environment variables
set SUPABASE_URL=your-project-url
set SUPABASE_KEY=your-anon-key

# Enable in tools_config.json
# Migration: usage_log.json → Supabase for cross-machine sync
```

### Custom MCP Development Roadmap

1. **automation-machine-state** - Expose project state to Claude instances
2. **comfyui-orchestrator** - Better image generation management
3. **multi-machine-coordinator** - Unify Gaming PC + The Machine + Laptop

## ComfyUI Video Generation

Video production capabilities on The Machine (RTX 5060 Ti 16GB).

### Capabilities

| Feature | Model | VRAM | Status |
|---------|-------|------|--------|
| Image-to-Video | Wan2.1 I2V 480p fp8 | ~13GB | **RECOMMENDED** - ~42 min per clip |
| Image-to-Video GGUF | Wan2.1 I2V Q5_K_M | ~14GB | **SLOWER** - ~70 min (not recommended) |
| Talking Heads | FantasyTalking (Wan2.1) | ~14GB | **TESTED & APPROVED** 2026-02-02 |
| Talking Heads (legacy) | SadTalker | ~6GB | Superseded by FantasyTalking |
| Motion Loops | AnimateDiff | ~10GB | Nodes ready |
| Lip Sync | Wav2Lip | ~4GB | Nodes ready |
| TTS Audio | edge-tts (Microsoft) | CPU | **WORKING** - 4 audio files generated |

### Current Status (2026-02-02)

**ComfyUI:** v0.7.0 running at http://100.64.130.71:8188
**GPU:** RTX 5060 Ti 16GB (~13GB used during video gen)

| Component | Status |
|-----------|--------|
| VideoHelperSuite | INSTALLED (40 nodes) |
| Wan2.1 nodes | INSTALLED (27 nodes) |
| AnimateDiff | INSTALLED (30+ nodes) |
| SadTalker | INSTALLED (needs models downloaded) |
| ComfyUI-WanVideoWrapper | INSTALLED (FantasyTalking nodes) |
| ComfyUI-KJNodes | INSTALLED (image resize) |
| ComfyUI-GGUF | INSTALLED (GGUF model loaders) |
| Kling Lip Sync | AVAILABLE (API-based) |
| **Wan2.1 I2V 480p model** | WORKING (fp8, ~7GB) |
| **Wan2.1 I2V 720p model** | AVAILABLE (fp16, needs more RAM) |
| **umt5_xxl text encoder** | WORKING |
| **wan_2.1_vae** | WORKING |
| **CLIP-ViT-H vision** | WORKING |

### Models (Downloaded)

```
C:\ComfyUI\models\diffusion_models\Wan2.1\
  - wan2.1_i2v_480p_14B_fp8_e4m3fn.safetensors (WORKING)
  - wan2.1_i2v_720p_14B_fp16.safetensors (needs more paging file)

C:\ComfyUI\models\diffusion_models\WanVideo\
  - fantasytalking_fp16.safetensors (INSTALLED - FantasyTalking lip sync)

C:\ComfyUI\models\unet\
  - wan2.1-i2v-14b-480p-Q5_K_M.gguf (DOWNLOADING - GGUF quantized I2V)

C:\ComfyUI\models\text_encoders\
  - umt5_xxl_fp16.safetensors (required for Wan - NOT t5xxl)

C:\ComfyUI\models\clip\
  - umt5-xxl-encoder-Q5_K_M.gguf (DOWNLOADING - GGUF quantized encoder)

C:\ComfyUI\models\vae\
  - wan_2.1_vae.safetensors

C:\ComfyUI\models\clip_vision\
  - CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
```

**Performance (RTX 5060 Ti 16GB):**
- Wan2.1 fp8: 81 frames @ 30 steps = **~42 min** (RECOMMENDED)
- Wan2.1 GGUF Q5: 81 frames @ 30 steps = **~70 min** (slower, not recommended)
- FantasyTalking: ~20-45 min per clip

**GGUF Note:** Tested 2026-02-03. GGUF is slower on RTX 5060 Ti because it lacks specialized INT4/INT8 tensor cores. GGUF requires runtime dequantization which adds CPU overhead. Stick with fp8 for this hardware.

### Wan2.1 I2V Realism Tips

1. **Start from a strong still** -- Clean, well-lit, realistic source image (Flux/SDXL/WAN image model)
2. **Longer prompts (80-120 words)** -- Specify subject, environment, motion, camera (e.g. "soft natural lighting, shallow DOF, camera slowly dolly-in")
3. **Prompt motion, not redesign** -- Describe how the scene moves, don't re-describe the scene itself
4. **Keep motion simple** -- Small movements, gentle pans/zooms; complex actions = warped limbs
5. **Use negative prompts** -- "no distortion, no warped hands, no glitching, no flicker, no fast motion"

See `fiverr-assets/VIDEO-PRODUCTION.md` for full details.

### Restarting ComfyUI (The Machine)

ComfyUI runs as a **Windows Service** on The Machine. Do NOT use taskkill - the service auto-restarts.

```powershell
# SSH to The Machine
ssh michael@100.64.130.71

# Stop the service (proper way)
Stop-Service ComfyUI

# Do any maintenance (install deps, etc.)
pip install <package>

# Start the service
Start-Service ComfyUI

# Verify it's running
Get-Service ComfyUI
netstat -ano | findstr 8188
```

**Wrong way (will auto-restart immediately):**
```powershell
# DON'T DO THIS - service will respawn
taskkill /f /pid <PID>
```

**One-liner restart:**
```powershell
$pid = (netstat -ano | findstr "8188" | findstr "LISTENING" | ForEach-Object { $_.Split()[-1] } | Select-Object -First 1); if ($pid) { taskkill /f /pid $pid; Start-Sleep -Seconds 3 }; cd C:\ComfyUI; python main.py --listen
```

### Video Commands

```bash
# Image-to-video (auto-detected)
python automation_brain.py "animate this candle image with flame motion"
python automation_brain.py "create video from output/candle_001.png"

# Talking head (requires photo + audio)
python automation_brain.py "generate talking head photo: photos/avatar.png audio: audio/script.wav"

# Force specific tool
python automation_brain.py --tool comfyui-video "animate with subtle motion"
python automation_brain.py --tool comfyui-video-talking-head "avatar from files"
```

### Cost: $0 (100% local processing)

## Claude in Chrome Integration

Browser automation for tasks requiring web interaction.

### Setup

1. Install: https://claude.com/chrome
2. Enable in `tools_config.json`: set `"claude-in-chrome": { "enabled": true }`
3. Use via automation_brain.py: `python automation_brain.py "post to Fiverr"`

### Use Cases for Fiverr Consultancy

| Task | How It Helps |
|------|--------------|
| Gig management | Auto-fill descriptions, update pricing |
| Order tracking | Monitor inbox, respond to queries |
| Social posting | Multi-platform content distribution |
| Competitor research | Analyze competitor gigs |

### Workflow Pattern

```
User Request → automation_brain.py detects browser need
                    ↓
              Generates step-by-step browser instructions
                    ↓
              User executes in Claude in Chrome
                    ↓
              (Future: direct API integration)
```

## Extended Routing (Updated)

```
Query → Analyze complexity/needs
         ↓
Needs browser?       → Claude in Chrome (step generation)
Needs GitHub?        → gh CLI (FREE, safe read ops)
Needs web data?      → Perplexity sonar-pro (~$0.001)
Needs video?         → ComfyUI Video (FREE, Wan2.1/AnimateDiff)
Needs talking head?  → ComfyUI SadTalker (FREE, avatar videos)
Needs images?        → ComfyUI (FREE, local GPU)
Needs database?      → Supabase (when enabled)
Simple query?        → DeepSeek R1 (FREE, local)
Code/analysis?       → Qwen 2.5 32B (FREE, local)
Complex/novel?       → Claude Sonnet (last resort, ~$0.15)
```

## Environment Variables (Updated)

```bash
# Required
ANTHROPIC_API_KEY     # Claude API
PERPLEXITY_API_KEY    # Perplexity web research

# Optional (enable features)
GITHUB_TOKEN          # GitHub API (gh CLI uses its own auth)
SUPABASE_URL          # Supabase project URL
SUPABASE_KEY          # Supabase anon key
```

## Multi-Agent Orchestration (TeammateTool)

Claude Code v2.1.19+ includes native swarm orchestration via **TeammateTool**. This transforms Claude Code from a single assistant into a team orchestrator.

### How It Works

```
You (Leader) → spawns → [specialist-1, specialist-2, specialist-3]
                ↓
          Agents work in parallel
                ↓
          Coordinate via task board + mailbox
                ↓
          Report back to leader
```

### Core Operations

| Operation | Purpose |
|-----------|---------|
| `spawnTeam` | Create team, you become leader |
| `write` | Send targeted message to specific teammate |
| `broadcast` | Message all teammates (costly) |
| `requestShutdown` | Graceful termination |
| `cleanup` | Remove team resources |

### Built-In Agent Types

| Type | Tools | Use Case |
|------|-------|----------|
| **Bash** | Bash only | Command execution |
| **Explore** | Glob, Grep, Read, WebFetch | Read-only codebase exploration (fast, haiku) |
| **Plan** | All except Edit/Write | Architecture and planning |
| **general-purpose** | All tools | Multi-step implementation tasks |

### Spawn Backends

| Backend | Visibility | Use Case |
|---------|------------|----------|
| `in-process` | None | Fastest, no UI |
| **`tmux`** | Visible panes | Persistent, recommended |
| `iterm2` | Split panes | macOS only |

Set via: `CLAUDE_CODE_SPAWN_BACKEND=tmux`

### Pre-Configured Teams

View teams: `python automation_brain.py --teams`

| Team | Members | Purpose |
|------|---------|---------|
| `video-production` | video-researcher, asset-generator, editor | Demo video creation |
| `content-production` | researcher, writer, artist, editor | Marketing content |
| `certification-study` | curriculum-builder, quiz-generator, progress-tracker | Cert prep |
| `trading-analysis` | market-researcher, analyst, reporter | Market analysis |

### Spawning a Team

```bash
# View team config
python automation_brain.py --teams

# Spawn a team (generates instructions)
python automation_brain.py --team "spawn video-production"

# In Claude Code, use Task tool to spawn agents:
# subagent_type="Explore" for researchers
# subagent_type="general-purpose" for workers
```

### TeammateTool vs Claude-Flow

| Feature | TeammateTool (Native) | Claude-Flow V3 |
|---------|----------------------|----------------|
| Installation | Built-in | npm install |
| Consensus | Majority (simple) | 4 algorithms (Raft, Byzantine, etc.) |
| Learning | None | HNSW, LoRA, 9 RL algorithms |
| Best for | Claude Code workflows | Complex orchestration, research |

**Recommendation:** Start with native TeammateTool. Graduate to Claude-Flow if you need advanced consensus or learning systems.

### Resources

- [Claude Code Swarm Guide](https://gist.github.com/kieranklaassen/4f2aba89594a4aea4ad64d753984b2ea)
- [Claude Flow V3 vs TeammateTool](https://gist.github.com/ruvnet/18dc8d060194017b989d1f8993919ee4)

## Knowledge Ingestion Pipeline

Transform podcasts, YouTube videos, and PDFs into training documents.

### Pipeline Architecture

```
Source → Extraction → Chunking → Ollama Summary → Knowledge Base
```

### Supported Sources

| Source | Tool | Cost |
|--------|------|------|
| YouTube | yt-dlp + faster-whisper | $0 (local) |
| Podcast | faster-whisper | $0 (local) |
| PDF | pdfplumber | $0 (local) |
| Web | trafilatura | $0 (local) |

### Commands

```bash
# YouTube video
python knowledge_ingest.py --youtube "https://youtube.com/watch?v=..." -v

# Podcast episode
python knowledge_ingest.py --audio "podcast.mp3" --title "Episode Title"

# PDF book/document
python knowledge_ingest.py --pdf "book.pdf" --title "Book Title"

# Web article
python knowledge_ingest.py --web "https://example.com/article"

# List all training docs
python knowledge_ingest.py --list
```

### Output Format

Training documents are saved to `knowledge-base/training/` with:
- Key Takeaways (3-7 bullet points)
- Detailed Summary (2-4 paragraphs)
- Actionable Items (tasks extracted from content)
- Full transcript/content (collapsible)

### Dependencies

```bash
pip install yt-dlp faster-whisper pdfplumber trafilatura
```

### Recommended Podcasts for Training

| Podcast | Focus | Priority |
|---------|-------|----------|
| **The AI-Powered Project Manager** | AI + PM automation | High |
| **DrunkenPM Radio** | Agile + AI agents | High |
| **Scrum Master Toolbox** | Daily Scrum tips | Medium |
| **Agile Mentors** (Mountain Goat) | Scrum fundamentals | Medium |

## Sprint Management

Scrum-style project management integrated with automation_brain.py.

### Commands

```bash
# View current sprint
python automation_brain.py --sprint

# Generate standup report
python automation_brain.py --standup

# View all teams
python automation_brain.py --teams
```

### Sprint Structure (in registry.json)

```json
{
  "id": "2026-W06",
  "name": "Fiverr Launch Sprint",
  "start": "2026-02-03",
  "end": "2026-02-09",
  "status": "active",
  "goals": ["Complete 3 demo videos", "Publish gigs"],
  "tasks": [
    {"id": "video-1", "name": "Marketing Demo", "status": "in_progress"},
    {"id": "video-2", "name": "Image Gen Demo", "status": "pending"}
  ]
}
```

### Task Statuses

| Status | Icon | Meaning |
|--------|------|---------|
| `completed` | ✓ | Done |
| `in_progress` | → | Being worked on |
| `pending` | ○ | Ready to start |
| `blocked` | ✗ | Waiting on dependency |

## Mobile Access (S22 Ultra)

Claude Code from phone via Termux + Tailscale SSH. Setup completed 2026-02-07.

### Device Info

| Field | Value |
|-------|-------|
| Device | Samsung Galaxy S22 Ultra |
| Tailscale hostname | `michaels-s22-ultra` |
| Tailscale IP | `100.115.120.118` |
| Apps | Termux (F-Droid), Tailscale |

### Connect from Phone

```bash
# In Termux
ssh michael@100.64.130.71

# Then run Claude Code
claude
```

### Termux SSH Config (optional, for shortcut)

Create `~/.ssh/config` in Termux:
```
Host pc
    HostName 100.64.130.71
    User michael
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Then just: `ssh pc`

### SSH Key Auth (recommended)

```bash
# In Termux (one-time setup)
ssh-keygen -t ed25519
ssh-copy-id michael@100.64.130.71
```

### Tips

- All execution happens on the Gaming PC -- phone is just a terminal
- Close Termux anytime; nothing is lost on the PC side
- For long sessions, consider Mosh (`pkg install mosh`) for better network resilience

## SSH Persistence

Configured in `~/.ssh/config` for persistent connections.

```
Host the-machine
    HostName 100.64.130.71
    User michael
    ServerAliveInterval 30
    ServerAliveCountMax 10
```

### tmux for Long Tasks

```bash
# Start session (on The Machine)
tmux new -s claude

# Detach: Ctrl+B, D

# Reconnect later
tmux attach -t claude

# List sessions
tmux ls
```

## Long-Running ComfyUI Jobs

Video generation can take 1+ hours. Use `comfyui_job.py` for fire-and-forget job management.

### Commands

```bash
# Queue job (returns immediately with prompt_id)
python comfyui_job.py queue --workflow image_to_video_wan22 --image candle.png

# Check status anytime
python comfyui_job.py status <prompt_id>

# Wait for completion (RUN IN TMUX!)
python comfyui_job.py wait <prompt_id> --timeout 7200

# List recent jobs
python comfyui_job.py list

# Test GGUF speed (RUN IN TMUX!)
python comfyui_job.py test --image test.png
```

### Proper Workflow for Long Jobs

```bash
# 1. SSH to The Machine
ssh the-machine

# 2. Start tmux session
tmux new -s video-gen

# 3. Run the job
python C:/automation-machine/comfyui_job.py test

# 4. Detach from tmux (Ctrl+B, D)
# Session keeps running even if SSH drops!

# 5. Reconnect anytime to check progress
ssh the-machine
tmux attach -t video-gen
```

### Job Tracking

Jobs are logged to `comfyui_jobs.json` with:
- prompt_id, workflow, status
- queued_at, completed_at
- elapsed_seconds

## Multi-Agent Orchestration (File-Based)

Persistent, autonomous agent system using file-based coordination + Ralph Wiggum loops.

### Architecture

```
agents/
├── BULLETIN.md              # Shared status board (all agents read/write)
├── agent-runner.ps1         # Ralph Wiggum loop launcher (PowerShell)
├── cost-guardian.py         # Budget watchdog (plain Python, zero token cost)
├── fiverr/                  # Agent 1: Fiverr gig launch
│   ├── PROMPT.md            # Agent instructions
│   ├── state.json           # Progress state (resume-capable)
│   └── HEARTBEAT.md         # Last-alive timestamp
├── dashboard/               # Agent 2: Streamlit dashboard
├── trading/                 # Agent 3: Algorithmic trading research
├── aws-cert/                # Agent 4: AWS certification study
└── _template/               # Template for adding new agents
```

### Quick Commands

```powershell
# Run one agent interactively (testing)
.\agents\agent-runner.ps1 -AgentName trading -MaxIterations 1

# Run agent autonomously
.\agents\agent-runner.ps1 -AgentName fiverr

# Dry run (see prompt without executing)
.\agents\agent-runner.ps1 -AgentName dashboard -DryRun

# Budget check
python agents/cost-guardian.py --check

# Continuous budget monitoring
python agents/cost-guardian.py --watch

# Clear budget pause signal
python agents/cost-guardian.py --reset-signal
```

### File Ownership Rules

| Agent | Exclusive Write | Shared (lock required) |
|-------|----------------|----------------------|
| fiverr | `fiverr-assets/`, `demo-clients/`, `video-production/`, `workflows/` | `registry.json`, `BULLETIN.md` |
| dashboard | `dashboard/` | `BULLETIN.md` |
| trading | `trading/` | `BULLETIN.md` |
| aws-cert | `knowledge-base/training/aws/` | `registry.json`, `BULLETIN.md` |

### BULLETIN.md Protocol

- All agents read BULLETIN.md at startup
- Append-only updates for status changes
- File locks: check -> add lock -> write -> remove lock
- Stale locks (>30 min) can be broken
- Cost guardian writes PAUSE/STOP signals here

### Adding a New Agent

1. Copy `agents/_template/` to `agents/<new-name>/`
2. Edit PROMPT.md with role, owned dirs, and task list
3. Edit state.json with task definitions
4. Add agent row to BULLETIN.md
5. Run: `.\agents\agent-runner.ps1 -AgentName <new-name> -MaxIterations 1`

### Scaling Path

- **4 agents**: Single worktree, shared BULLETIN.md, file locks (current)
- **10 agents**: Git worktrees per agent, partitioned bulletins
- **25 agents**: Per-agent bulletin files + aggregator script
- **50 agents**: SQLite/Supabase for state, consider Claude Flow V3

## Fiverr Service Expansion Ideas

Based on Claude ecosystem mastery:

| Gig Idea | Tools Used | Price Range |
|----------|------------|-------------|
| AI Marketing Automation | automation_brain + ComfyUI | $500 - $2,500 |
| AI Image Generation | ComfyUI + SDXL | $15 - $75 |
| Browser Automation Setup | Claude in Chrome | $200 - $800 |
| Custom MCP Development | MCP + Claude API | $500 - $2,000 |
| AI Workflow Consulting | Full ecosystem | $100 - $300/hr |
| Multi-Agent Orchestration | TeammateTool + Claude Code | $1,000 - $5,000 |
