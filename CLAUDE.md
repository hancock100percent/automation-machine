# Automation Machine

Local-first AI orchestration system for cost-optimized query routing across multiple LLMs.

**Repo:** https://github.com/hancock100percent/automation-machine

## Owner Intent

**Goal:** Become an expert in everything Claude has to offer - Claude Code, Claude API, MCP servers, integrations - and connect it with every possible tool to build and advertise automation expertise.

**Business context:** Building a Fiverr-based automation consultancy. Every feature learned and tool connected is a potential service offering.

**When assisting:** Proactively mention Claude features, MCP integrations, or capabilities that could enhance the automation-machine or expand service offerings.

## Architecture

```
Gaming PC (localhost)     → Ollama server + automation_brain.py (primary dev)
The Machine (100.64.130.71) → ComfyUI + RTX 5060 Ti 16GB (image generation)
Laptop                    → Mobile access via Tailscale
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

# Status
python automation_brain.py --stats              # View costs
python automation_brain.py --tools              # List available tools

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
- [x] Generate sample images (5 generated, 25 remaining)
- [ ] Video demos
- [ ] Publish gigs on Fiverr

## Key Files

| File | Purpose |
|------|---------|
| `automation_brain.py` | Main orchestration engine |
| `auto_doc.py` | Auto-documentation system |
| `config.yaml` | Model configs, routing thresholds |
| `tools_config.json` | Tool integrations (Perplexity, ComfyUI, Claude) |
| `usage_log.json` | Cost tracking database |
| `HANDOFF.md` | Cross-LLM handoff protocol |

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

## Knowledge Base Structure

```
knowledge-base/
├── ACTIVE-PROJECTS.md    # Current work status
├── PROJECT-RECAP.md      # Architecture overview
├── research/             # Query history, conversation logs
├── decisions/            # Past architectural decisions
└── patterns/             # Auto-detected reusable patterns
```

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

### Claude in Chrome (Browser Extension)
- Browser automation and navigation
- Form filling, multi-tab workflows
- Record & replay workflows
- Built-in: Gmail, Calendar, Docs, Slack, GitHub
- Install: https://claude.com/chrome

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
Needs browser?     → Claude in Chrome (step generation)
Needs GitHub?      → gh CLI (FREE, safe read ops)
Needs web data?    → Perplexity sonar-pro (~$0.001)
Needs images?      → ComfyUI (FREE, local GPU)
Needs database?    → Supabase (when enabled)
Simple query?      → DeepSeek R1 (FREE, local)
Code/analysis?     → Qwen 2.5 32B (FREE, local)
Complex/novel?     → Claude Sonnet (last resort, ~$0.15)
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

## Fiverr Service Expansion Ideas

Based on Claude ecosystem mastery:

| Gig Idea | Tools Used | Price Range |
|----------|------------|-------------|
| AI Marketing Automation | automation_brain + ComfyUI | $500 - $2,500 |
| AI Image Generation | ComfyUI + SDXL | $15 - $75 |
| Browser Automation Setup | Claude in Chrome | $200 - $800 |
| Custom MCP Development | MCP + Claude API | $500 - $2,000 |
| AI Workflow Consulting | Full ecosystem | $100 - $300/hr |
