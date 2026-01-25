# Automation Machine

Local-first AI orchestration system with intelligent task routing across multiple tools.

## Quick Start

```bash
# Single query (auto-routes to best tool)
python automation_brain.py "your question here"

# Interactive mode
python automation_brain.py

# Check usage stats
python automation_brain.py --stats

# Show available tools
python automation_brain.py --tools
```

## How It Works

The Automation Brain analyzes each query and routes it to the optimal tool based on:
- **Task type** (research, code, image, database, general)
- **Complexity** (simple, medium, complex)
- **Cost optimization** (local free → cheap cloud → expensive cloud)

## Task Routing Logic

```
Query → Analyze → Route → Execute → Log

1. ANALYZE: Detect keywords, complexity, requirements
2. ROUTE:   Match to optimal tool
3. EXECUTE: Call appropriate API
4. LOG:     Track cost, tokens, category
```

### Routing Decision Tree

| Condition | Tool | Cost |
|-----------|------|------|
| Needs current web data | Perplexity | ~$0.001 |
| Needs image generation | ComfyUI | Free |
| Needs database ops | Supabase | Free |
| Simple query | DeepSeek R1 | Free |
| Medium complexity | Qwen 2.5 32B | Free |
| Complex/novel | Claude Sonnet 4 | ~$0.15 |

## Available Tools & Status

| Tool | Status | Description |
|------|--------|-------------|
| DeepSeek R1 | Active | Fast local reasoning (free) |
| Qwen 2.5 32B | Active | Powerful local code/analysis (free) |
| Perplexity Pro | Active | Web research with current data |
| Claude Sonnet 4 | Active | Complex task fallback |
| ComfyUI | Placeholder | Local image generation |
| GitHub | Pending | Repository operations (MCP) |
| Supabase | Pending | Database operations (MCP) |

## Cost Breakdown by Tool

| Tool | Cost Model | Typical Query |
|------|------------|---------------|
| DeepSeek R1 | $0.00 | Free (local) |
| Qwen 2.5 32B | $0.00 | Free (local) |
| Perplexity | ~$1/1M tokens | ~$0.001/query |
| Claude Sonnet 4 | $3/$15 per 1M in/out | ~$0.15/query |
| ComfyUI | $0.00 | Free (local GPU) |

**Monthly estimate:** ~$8-80 depending on Claude usage (90%+ handled locally for free)

## Delegation Examples

### Simple Tasks → DeepSeek R1 (Free)
```bash
python automation_brain.py "What is 2+2?"
python automation_brain.py "Explain Python lists"
python automation_brain.py "List common HTTP status codes"
```

### Medium Tasks → Qwen 2.5 32B (Free)
```bash
python automation_brain.py "Refactor this code for better performance"
python automation_brain.py "Design a database schema for user auth"
python automation_brain.py "Explain the trade-offs of microservices"
```

### Web Research → Perplexity (~$0.001)
```bash
python automation_brain.py "What are the latest AI releases in 2026?"
python automation_brain.py "Compare current GPU prices"
python automation_brain.py "Find best Python RSS libraries in 2026"
```

### Complex Tasks → Claude Sonnet 4 (~$0.15)
```bash
python automation_brain.py "Design a distributed architecture for real-time data"
python automation_brain.py "Debug this complex async race condition"
python automation_brain.py "Create a comprehensive migration strategy"
```

### Image Generation → ComfyUI (Free)
```bash
python automation_brain.py "Generate an image of a futuristic city"
python automation_brain.py "Create a logo for my app"
```

## Forcing Specific Tools

```bash
# Force local models
python automation_brain.py --tool local-deepseek "question"
python automation_brain.py --tool local-qwen "question"

# Force Perplexity for web research
python automation_brain.py --tool perplexity "question"

# Force Claude for complex work
python automation_brain.py --tool claude "question"
```

## Enabling New Tools

Edit `tools_config.json`:

```json
{
  "github": {
    "enabled": true,    // Change to true
    "token_env": "GITHUB_TOKEN"
  }
}
```

Then set the environment variable:
```bash
set GITHUB_TOKEN=your_token_here
```

## Environment Variables

| Variable | Required For | Description |
|----------|--------------|-------------|
| `ANTHROPIC_API_KEY` | Claude | Anthropic API key |
| `PERPLEXITY_API_KEY` | Perplexity | Perplexity API key |
| `GITHUB_TOKEN` | GitHub | Personal access token |
| `SUPABASE_URL` | Supabase | Project URL |
| `SUPABASE_KEY` | Supabase | Anon/service key |

## File Structure

```
C:\automation-machine\
├── automation_brain.py    # Full orchestration (use this)
├── brain.py               # Legacy simple router
├── config.yaml            # Model configurations
├── tools_config.json      # Tool integrations
├── usage_log.json         # Cost tracking
├── test_brain.py          # Test suite
└── knowledge-base/
    ├── index.md           # KB index
    ├── PROJECT-RECAP.md   # Project status
    ├── DELEGATION-EXAMPLES.md
    ├── projects/
    ├── patterns/
    ├── research/
    └── decisions/
```

## Verbose Mode

See routing decisions in real-time:

```bash
python automation_brain.py -v "your question"
```

Output:
```
[Brain] Analysis: category=research, complexity=medium, recommended=perplexity
[Brain] Using tool: perplexity
[Brain] Querying Perplexity: llama-3.1-sonar-large-128k-online
[Brain] Tokens: 150 in / 500 out | Cost: $0.0007
```

## Testing

```bash
python test_brain.py
```

## Requirements

- Python 3.10+
- Ollama running locally with models:
  - `deepseek-r1:latest`
  - `qwen2.5:32b`
- API keys for cloud services (optional)
