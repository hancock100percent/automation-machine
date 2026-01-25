# Task Delegation Examples

Real-world examples of how the Automation Brain routes queries to optimal tools.

---

## Simple Tasks (DeepSeek R1 - Free)

Fast, local processing for straightforward queries.

**Examples:**
- "What is 2+2?"
- "Explain Python lists"
- "Write a function to sort numbers"
- "What does HTTP 404 mean?"
- "List common git commands"
- "Convert 100 Fahrenheit to Celsius"
- "What is a REST API?"
- "Show me a basic for loop in Python"

**Why DeepSeek:**
- Response time < 2 seconds
- Zero cost
- Perfect for simple lookups and explanations
- Handles basic code snippets well

**Command:**
```bash
python automation_brain.py "What is a REST API?"
python automation_brain.py --tool local-deepseek "explain recursion"
```

---

## Medium Tasks (Qwen 2.5 32B - Free)

Powerful local processing for code generation and analysis.

**Examples:**
- "Refactor this 200-line Python script for better performance"
- "Design a database schema for RSS feed monitoring"
- "Explain the trade-offs between MoE and dense models"
- "Write a complete FastAPI endpoint with error handling"
- "Debug this async function that's causing race conditions"
- "Create a CLI parser with argparse for my tool"
- "Implement a binary search tree in Python"
- "Analyze this algorithm's time complexity"

**Why Qwen:**
- Excellent at code generation and refactoring
- Handles longer contexts
- Good at technical explanations
- Still free (local)

**Command:**
```bash
python automation_brain.py "write a FastAPI endpoint for user registration"
python automation_brain.py --tool local-qwen "refactor this code"
```

---

## Web Research (Perplexity Pro - ~$0.001/query)

Real-time web access for current information.

**Examples:**
- "What are the latest AI model releases in January 2026?"
- "Compare current GPU prices for RTX 5060 Ti vs RTX 3090"
- "Find the best RSS parsing libraries in 2026"
- "What's the current price of Bitcoin?"
- "Latest news about Anthropic"
- "Best practices for Python async in 2026"
- "Compare Next.js vs Remix in 2026"
- "What are the trending GitHub repos this week?"

**Why Perplexity:**
- Access to current web data
- Includes citations/sources
- ~1000x cheaper than Claude for research
- Perfect for "latest", "current", "news" queries

**Trigger Keywords:**
- "latest", "current", "2024", "2025", "2026"
- "news", "today", "recent", "price"
- "compare prices", "find", "search for"
- "what are the best", "recommendations"

**Command:**
```bash
python automation_brain.py "latest AI news this week"
python automation_brain.py --tool perplexity "current GPU prices"
```

---

## Complex/Novel Tasks (Claude Sonnet 4 - ~$0.15/query)

Premium cloud processing for the hardest problems.

**Examples:**
- "Design a novel distributed architecture for real-time collaborative editing"
- "Debug this complex multi-threading issue with race conditions"
- "Create a comprehensive business plan for an AI startup"
- "Analyze the security implications of this authentication flow"
- "Design a migration strategy from monolith to microservices"
- "Create an optimal caching strategy for this high-traffic API"
- "Review this code for subtle bugs and edge cases"
- "Design a fault-tolerant system for financial transactions"

**Why Claude:**
- Best reasoning capabilities
- Handles novel/unique problems
- Highest quality output
- Worth the cost for important decisions

**Trigger Keywords:**
- "complex", "novel", "architecture"
- "design system", "comprehensive"
- "multi-step", "analyze deeply"

**Command:**
```bash
python automation_brain.py "design a distributed cache invalidation strategy"
python automation_brain.py --tool claude "review this security implementation"
```

---

## Image Generation (ComfyUI - Free Local)

Local GPU image generation via Stable Diffusion.

**Examples:**
- "Generate an image of a futuristic city at sunset"
- "Create variations of this logo design"
- "Draw a cartoon mascot for my app"
- "Generate a landscape wallpaper"
- "Create an icon set for a weather app"
- "Design a book cover for a sci-fi novel"

**Why ComfyUI:**
- Free (local GPU)
- Full control over workflows
- No API limits
- Private (images stay local)

**Note:** Currently placeholder - generates prompt for manual use.

**Command:**
```bash
python automation_brain.py "generate an image of a robot reading a book"
python automation_brain.py --tool comfyui "create a logo for TechCorp"
```

---

## Database Operations (Supabase - Pending)

Database queries and data management.

**Examples:**
- "Query all users who signed up this week"
- "Store this RSS feed data in the database"
- "Update user preferences for notifications"
- "Find duplicate entries in the logs table"

**Note:** Pending MCP integration. Currently generates SQL via Qwen.

---

## GitHub Operations (Pending MCP)

Repository and code management.

**Examples:**
- "List open issues in my-repo"
- "Create a PR for the feature branch"
- "Search for TODO comments in the codebase"
- "Get the latest release notes"

**Note:** Pending MCP integration.

---

## Cost Comparison

| Task Type | Tool | Typical Cost | Monthly (100/day) |
|-----------|------|--------------|-------------------|
| Simple lookup | DeepSeek | $0.00 | $0.00 |
| Code generation | Qwen | $0.00 | $0.00 |
| Web research | Perplexity | $0.001 | $3.00 |
| Complex analysis | Claude | $0.15 | $450.00 |
| Image generation | ComfyUI | $0.00 | $0.00 |

**Key Strategy:** Route 90%+ of queries to free local models. Use Perplexity for web needs. Reserve Claude for truly complex/novel work.

---

## Routing Override Examples

Force a specific tool when you know better:

```bash
# Force expensive model for important decision
python automation_brain.py --tool claude "simple question but I want best answer"

# Force local when you don't need web data
python automation_brain.py --tool local-qwen "what was announced at GTC 2024"

# Force Perplexity when you need current data
python automation_brain.py --tool perplexity "explain quantum computing"
```

---

*Last updated: 2026-01-18*
