# Automation Machine - Project Recap

## Current Phase: 2.0 (Full Orchestration)

### Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1.0 | Initial research & planning | Completed |
| 1.5 | Local LLM integration (Ollama) | Completed |
| 2.0 | Full orchestration system | In Progress |
| 2.5 | Tool integrations (MCP) | Planned |
| 3.0 | Autonomous agents | Future |

---

## Architecture Overview

```
                    +------------------+
                    |  User Query      |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Automation Brain |
                    | (Task Analysis)  |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
     +--------+------+  +----+----+  +------+-------+
     | Local Models  |  | Cloud   |  | Specialized  |
     | (Free)        |  | (Paid)  |  | Tools        |
     +---------------+  +---------+  +--------------+
     | - DeepSeek R1 |  | Claude  |  | - Perplexity |
     | - Qwen 2.5    |  | Sonnet  |  | - ComfyUI    |
     +---------------+  +---------+  | - GitHub     |
                                     | - Supabase   |
                                     +--------------+
```

---

## Decision Tree: Task Routing

```
Query Received
    │
    ├─► Needs current web data?
    │       YES → Perplexity Pro (~$0.001/query)
    │       NO  ↓
    │
    ├─► Needs image generation?
    │       YES → ComfyUI (local, free)
    │       NO  ↓
    │
    ├─► Needs database operations?
    │       YES → Supabase (pending MCP)
    │       NO  ↓
    │
    ├─► Complexity level?
    │       SIMPLE → DeepSeek R1 (local, free)
    │       MEDIUM → Qwen 2.5 32B (local, free)
    │       COMPLEX → Claude Sonnet 4 (~$0.15/query)
    │
    └─► Fallback chain: Claude → Qwen → DeepSeek
```

---

## Tool Integration Status

| Tool | Status | Cost | Use Case |
|------|--------|------|----------|
| DeepSeek R1 | Active | Free | Simple queries, fast responses |
| Qwen 2.5 32B | Active | Free | Code, analysis, medium complexity |
| Perplexity Pro | Active | ~$0.001/query | Web research, current events |
| Claude Sonnet 4 | Active | ~$0.15/query | Complex/novel problems |
| ComfyUI | Placeholder | Free | Image generation (local GPU) |
| GitHub | Pending | Free | Repository ops (needs MCP) |
| Supabase | Pending | Free tier | Database ops (needs MCP) |
| Banana | Planned | Variable | GPU serverless overflow |

---

## Cost Estimates (Monthly)

### Conservative Usage (~100 queries/day)

| Tool | Queries | Cost |
|------|---------|------|
| DeepSeek R1 | 2000 | $0.00 |
| Qwen 2.5 | 500 | $0.00 |
| Perplexity | 300 | $0.30 |
| Claude | 50 | $7.50 |
| ComfyUI | 100 | $0.00 |
| **Total** | 2950 | **~$8/month** |

### Heavy Usage (~500 queries/day)

| Tool | Queries | Cost |
|------|---------|------|
| DeepSeek R1 | 10000 | $0.00 |
| Qwen 2.5 | 3000 | $0.00 |
| Perplexity | 1500 | $1.50 |
| Claude | 500 | $75.00 |
| ComfyUI | 500 | $0.00 |
| **Total** | 15500 | **~$77/month** |

**Key insight:** 90%+ of queries handled locally for free. Cloud costs only for truly complex/novel work.

---

## What's Working Now

1. **Local LLM Routing**
   - DeepSeek R1 for simple queries (fast, free)
   - Qwen 2.5 32B for code/analysis (powerful, free)
   - Automatic complexity detection
   - Fallback chain on errors

2. **Perplexity Integration**
   - Web research with current data
   - Automatic detection of "needs web" queries
   - Cost tracking per query

3. **Claude Fallback**
   - Complex task handling
   - Novel problem solving
   - Only used when necessary

4. **Knowledge Base**
   - Automatic context injection
   - Search across all markdown files
   - Conversation logging

5. **Cost Tracking**
   - Per-tool statistics
   - Daily/monthly summaries
   - Full query history

---

## Next Steps

### Phase 2A: Perplexity (Current)
- [x] API integration
- [x] Automatic web research detection
- [x] Cost tracking
- [ ] Citation extraction

### Phase 2B: ComfyUI
- [x] Placeholder delegation
- [ ] REST API integration
- [ ] Workflow execution
- [ ] Image result handling

### Phase 2C: GitHub MCP
- [ ] MCP server setup
- [ ] Repository operations
- [ ] Issue/PR automation
- [ ] Code search

### Phase 2D: Supabase MCP
- [ ] MCP server setup
- [ ] Query execution
- [ ] Data storage automation

---

## Files Reference

```
C:\automation-machine\
├── automation_brain.py    # Full orchestration system
├── brain.py               # Legacy simple router
├── config.yaml            # Model configurations
├── tools_config.json      # Tool integrations
├── usage_log.json         # Cost tracking
├── README.md              # Documentation
└── knowledge-base/
    ├── index.md
    ├── PROJECT-RECAP.md   # This file
    ├── DELEGATION-EXAMPLES.md
    ├── projects/
    ├── patterns/
    ├── research/
    └── decisions/
```

---

## Quick Commands

```bash
# Use new orchestration brain
python automation_brain.py "your query"

# Show available tools
python automation_brain.py --tools

# Force specific tool
python automation_brain.py --tool perplexity "latest AI news"
python automation_brain.py --tool local-qwen "write a function"

# Check costs
python automation_brain.py --stats

# Verbose mode (see routing decisions)
python automation_brain.py -v "your query"
```

---

*Last updated: 2026-01-18*
