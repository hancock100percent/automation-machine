# Automation Machine - Universal Handoff Protocol

**Works with ANY LLM: Claude, ChatGPT, Gemini, Llama, etc.**

---

## IMPORTANT: LLM Role

**YOU ARE ADVISORY ONLY.** You cannot execute commands directly.

Your role:
- Analyze the system state
- Suggest next steps
- Help write code/scripts
- Answer questions about the codebase

The USER must:
- Run all commands manually
- Copy-paste your code suggestions
- Execute scripts themselves
- Report results back to you

---

## Quick Start for ANY LLM

### Step 1: Understand What This System Does

The **Automation Machine** is a multi-LLM orchestration system that:
- Routes queries to the best LLM (Claude, Perplexity, local Ollama models)
- Tracks costs and usage
- Auto-documents decisions and patterns
- Manages knowledge base

**Main files:**
| File | Purpose |
|------|---------|
| `automation_brain.py` | Main orchestrator - routes queries to tools |
| `auto_doc.py` | Auto-documentation system |
| `tools_config.json` | Tool configurations and API keys |

### Step 2: Read State Files

Ask the user to share contents of:

```
C:\automation-machine\auto_doc_state.json    <- System state, patterns
C:\automation-machine\usage_log.json         <- Usage history, costs
```

### Step 3: Read Active Projects

Ask the user to share:

```
C:\automation-machine\knowledge-base\ACTIVE-PROJECTS.md
```

This tells you:
- Current project status
- What's already done
- What's next in priority order
- Critical constraints

### Step 4: Provide Guidance

Based on the state files, help the user:
- Understand where they left off
- Plan next steps
- Write code if needed
- Debug issues

---

## System Architecture

```
C:\automation-machine\
├── HANDOFF.md                  # This file
├── auto_doc_state.json         # System state
├── usage_log.json              # Usage tracking
├── automation_brain.py         # Main orchestration
├── auto_doc.py                 # Auto-documentation
├── tools_config.json           # Tool configs
├── emergency-handoff.bat       # Quick handoff script
└── knowledge-base/
    ├── ACTIVE-PROJECTS.md      # Current work
    ├── PROJECT-RECAP.md        # Architecture overview
    ├── DELEGATION-EXAMPLES.md  # How to use tools
    ├── decisions/              # Past decisions
    ├── research/               # Research findings
    └── patterns/               # Query patterns
```

## Machine Topology

| Machine | IP/Access | Role |
|---------|-----------|------|
| Gaming PC | localhost | Primary dev, local LLMs (Ollama) |
| The Machine | 100.64.130.71 | Server, ComfyUI, heavy compute |
| Laptop | Tailscale | Mobile access |

---

## Core Commands

```bash
# Check system state
python auto_doc.py --status

# Run query through orchestrator
python automation_brain.py "your query here"

# Force specific tool
python automation_brain.py --tool perplexity "web research"
python automation_brain.py --tool local-qwen "code question"

# Standalone mode (no external LLM needed)
python auto_doc.py --standalone-mode

# Update project status
python auto_doc.py --update-projects --eod "summary of work done"
```

---

## Rules - Non-Negotiable

### 1. NO Duplication
- Check if tool/script exists before creating new ones
- Search: `dir C:\automation-machine\*.py`

### 2. NO Rebuilding Existing Tools
- `automation_brain.py` - Working, don't replace
- `auto_doc.py` - Working, don't replace
- Add to existing files, don't recreate them

### 3. NO Over-Engineering
- Ship fast, iterate
- Don't build features not needed yet

### 4. NO Token Waste
- Read small state files first
- Ask clarifying questions before big changes

---

## For Claude Instances

When resuming work, your FIRST message should be:

```
STATE ACKNOWLEDGED:
- Last activity: [date from auto_doc_state.json]
- Active project: [from ACTIVE-PROJECTS.md]
- Current phase: [from PROJECT-RECAP.md]

CONFIRMED NEXT ACTION:
- [specific task from ACTIVE-PROJECTS.md]

EXECUTING:
[begin work]
```

---

## For ChatGPT/Gemini/Other LLMs

When the user pastes this handoff, respond with:

```
HANDOFF RECEIVED.

I understand this is the Automation Machine project.
I am in ADVISORY mode - I cannot execute commands.

To help you, please share:
1. Contents of auto_doc_state.json
2. Contents of ACTIVE-PROJECTS.md
3. What you're trying to accomplish

I'll analyze and provide guidance.
```

---

## Emergency Handoff Procedure

If Claude is rate-limited, the user should:

1. Run: `emergency-handoff.bat`
2. Copy the output
3. Paste into ChatGPT/Gemini
4. Continue working with advisory help

The batch file outputs everything the new LLM needs to understand the project.

---

## Standalone Mode

If no external LLM is available:

```bash
python auto_doc.py --standalone-mode
```

This provides:
- Current project status
- Suggested next steps
- Interactive prompts
- Basic guidance without needing another LLM

---

*Last updated: 2026-01-24*
