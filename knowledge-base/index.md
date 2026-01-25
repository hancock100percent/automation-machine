# Automation Machine Knowledge Base

## Quick Navigation

| Area | Description | Path |
|------|-------------|------|
| [Projects](#projects) | Active automation projects | `projects/` |
| [Patterns](#patterns) | Reusable automation patterns | `patterns/` |
| [Research](#research) | Research notes and findings | `research/` |
| [Decisions](#decisions) | Architecture decision records | `decisions/` |

---

## Tool Integration Status

| Tool | Status | Cost | Primary Use |
|------|--------|------|-------------|
| DeepSeek R1 | Active | Free | Simple queries, fast responses |
| Qwen 2.5 32B | Active | Free | Code generation, analysis |
| Perplexity Pro | Active | ~$0.001/query | Web research, current events |
| Claude Sonnet 4 | Active | ~$0.15/query | Complex/novel problems |
| ComfyUI | Placeholder | Free | Image generation |
| GitHub | Pending | Free | Repository operations |
| Supabase | Pending | Free | Database operations |

See [PROJECT-RECAP.md](PROJECT-RECAP.md) for full status.

---

## Delegation Logic Reference

### Automatic Routing

The brain analyzes queries and routes based on:

1. **Web Data Needed?** → Perplexity
2. **Image Generation?** → ComfyUI
3. **Database Operations?** → Supabase
4. **Complexity:**
   - Simple → DeepSeek R1
   - Medium → Qwen 2.5 32B
   - Complex → Claude Sonnet 4

### Keyword Triggers

| Keywords | Routes To |
|----------|-----------|
| "latest", "current", "2026", "news", "price" | Perplexity |
| "generate image", "draw", "logo", "artwork" | ComfyUI |
| "database", "sql", "store", "query data" | Supabase |
| "quick", "simple", "what is", "list" | DeepSeek |
| "analyze", "code", "design", "implement" | Qwen |
| "complex", "novel", "architecture" | Claude |

See [DELEGATION-EXAMPLES.md](DELEGATION-EXAMPLES.md) for detailed examples.

---

## Cost Optimization Guidelines

### Do's
- Use local models (DeepSeek, Qwen) for 90%+ of queries
- Use Perplexity for web research instead of Claude
- Batch complex questions to minimize Claude calls
- Check `--stats` regularly to monitor costs

### Don'ts
- Don't use Claude for simple lookups
- Don't use Perplexity when you don't need current data
- Don't skip the free local models

### Monthly Budget Targets
- Conservative: < $10/month
- Normal: < $30/month
- Heavy: < $100/month

---

## Projects

### RSS Monitor
**Path:** `projects/rss-monitor/`
**Status:** Planning
**Description:** Automated RSS feed monitoring and alerting system.

### Token Monitor
**Path:** `projects/token-monitor/`
**Status:** Planning
**Description:** Cryptocurrency/API token monitoring and tracking.

### Image Generation
**Path:** `projects/image-generation/`
**Status:** Planning
**Description:** Automated image generation workflows via ComfyUI.

---

## Quick Commands

```bash
# New orchestration system (recommended)
python automation_brain.py "your question here"

# Show available tools
python automation_brain.py --tools

# Check usage stats
python automation_brain.py --stats

# Force specific tool
python automation_brain.py --tool local-deepseek "question"
python automation_brain.py --tool local-qwen "question"
python automation_brain.py --tool perplexity "web research"
python automation_brain.py --tool claude "complex question"

# Verbose mode (see routing)
python automation_brain.py -v "question"

# Legacy simple router
python brain.py "question"
```

---

## Patterns

Reusable patterns for automation tasks:
- *(Add patterns as they emerge)*

---

## Research

- [automation-machine-research.md](research/automation-machine-research.md) - Core research notes
- [conversation-log.md](research/conversation-log.md) - Query history

---

## Decisions

Architecture Decision Records (ADRs):
- [tools-integration-roadmap.md](decisions/tools-integration-roadmap.md) - Tool integration plan

---

*Last updated: 2026-01-18*
