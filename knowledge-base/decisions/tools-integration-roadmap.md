# Tools Integration Roadmap

Architecture Decision Record for tool integration strategy.

**Date:** 2026-01-18
**Status:** Active
**Decision:** Phased integration with MCP where applicable

---

## Overview

The Automation Machine integrates multiple tools for different capabilities. This document outlines the integration phases, decision criteria, and implementation patterns.

---

## Integration Phases

### Phase 2A: Perplexity Pro (In Progress)

**Status:** Active
**Priority:** High
**Cost:** ~$1/1M tokens

**Completed:**
- [x] API integration
- [x] Automatic web research detection
- [x] Cost tracking per query
- [x] Fallback handling

**Pending:**
- [ ] Citation/source extraction
- [ ] Result caching for repeated queries
- [ ] Rate limiting

**Integration Pattern:** Direct REST API

```python
# Perplexity uses standard OpenAI-compatible API
POST https://api.perplexity.ai/chat/completions
{
  "model": "llama-3.1-sonar-large-128k-online",
  "messages": [{"role": "user", "content": "..."}]
}
```

---

### Phase 2B: ComfyUI Connection

**Status:** Placeholder
**Priority:** Medium
**Cost:** Free (local GPU)

**Tasks:**
- [ ] REST API endpoint verification
- [ ] Workflow JSON templates
- [ ] Image result handling
- [ ] Queue management
- [ ] Progress tracking

**Integration Pattern:** Local REST API

```python
# ComfyUI REST API
POST http://localhost:8188/prompt
{
  "prompt": { workflow_json },
  "client_id": "automation-machine"
}

GET http://localhost:8188/history/{prompt_id}
```

**Workflow Location:** `C:/automation-machine/projects/image-generation/`

---

### Phase 2C: GitHub MCP

**Status:** Pending
**Priority:** Medium
**Cost:** Free

**Tasks:**
- [ ] Install GitHub MCP server
- [ ] Configure authentication
- [ ] Test repository operations
- [ ] Integrate with brain routing

**Integration Pattern:** MCP (Model Context Protocol)

```json
// Claude desktop config
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "..."
      }
    }
  }
}
```

**Capabilities:**
- Repository search and management
- Issue/PR creation and updates
- Code search across repos
- Release management

---

### Phase 2D: Supabase MCP

**Status:** Pending
**Priority:** Low
**Cost:** Free tier

**Tasks:**
- [ ] Set up Supabase project
- [ ] Install Supabase MCP server
- [ ] Configure database schema
- [ ] Test CRUD operations
- [ ] Integrate with brain routing

**Integration Pattern:** MCP

```json
// Claude desktop config
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server"],
      "env": {
        "SUPABASE_URL": "...",
        "SUPABASE_KEY": "..."
      }
    }
  }
}
```

**Use Cases:**
- Store automation logs
- Track monitored items (RSS feeds, tokens)
- User preferences
- Query history persistence

---

### Phase 2E: Tool Discovery System

**Status:** Planned
**Priority:** Low

**Concept:** Auto-discover and integrate new tools based on capabilities.

**Tasks:**
- [ ] Define tool capability schema
- [ ] Create tool registry
- [ ] Implement dynamic routing
- [ ] Add tool health checks

---

## Decision Criteria for New Tools

### Must Have
1. **Clear use case** - Solves a specific problem the brain can't handle
2. **Reliable API** - Stable, documented, reasonable uptime
3. **Cost-effective** - Free or significantly cheaper than alternatives
4. **Privacy-respecting** - No unnecessary data collection

### Nice to Have
1. Local/self-hosted option
2. MCP support for seamless integration
3. Caching capabilities
4. Batch processing support

### Red Flags
- Vendor lock-in
- Unclear pricing
- Rate limits that affect automation
- Requires account/signup for every user

---

## Integration Patterns

### Pattern 1: Direct REST API

Best for: Simple, well-documented APIs

```python
def _delegate_to_service(self, query: str) -> dict:
    response = requests.post(
        "https://api.service.com/endpoint",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"query": query}
    )
    return response.json()
```

**Used by:** Perplexity, Claude, Ollama

### Pattern 2: MCP Server

Best for: Complex tools with rich capabilities

```python
# MCP handles the protocol, we just call it
# Brain delegates to MCP-enabled Claude
def _delegate_via_mcp(self, query: str, tool: str) -> dict:
    # Claude with MCP handles the tool calling
    pass
```

**Used by:** GitHub, Supabase (planned)

### Pattern 3: Local Service

Best for: Self-hosted tools

```python
def _delegate_to_local(self, query: str) -> dict:
    response = requests.post(
        "http://localhost:PORT/api",
        json={"prompt": query}
    )
    return response.json()
```

**Used by:** Ollama, ComfyUI

---

## Cost Management

### Budget Allocation

| Tool | Monthly Budget | Alert Threshold |
|------|----------------|-----------------|
| Perplexity | $5 | $3 |
| Claude | $50 | $30 |
| Banana (future) | $20 | $15 |
| **Total** | **$75** | **$48** |

### Cost Tracking Schema

```json
{
  "tool": "perplexity",
  "model": "llama-3.1-sonar-large-128k-online",
  "tokens_in": 150,
  "tokens_out": 500,
  "cost_usd": 0.00065,
  "task_category": "research"
}
```

---

## Security Considerations

1. **API Keys:** Store in environment variables, never in code
2. **MCP:** Use official servers only, verify sources
3. **Local Tools:** Keep updated, monitor for vulnerabilities
4. **Data Flow:** Minimize data sent to cloud services

---

## Next Steps

1. **This Week:** Complete Perplexity citation extraction
2. **Next Week:** Test ComfyUI REST API integration
3. **Future:** Evaluate MCP server options for GitHub/Supabase

---

*Last updated: 2026-01-18*
