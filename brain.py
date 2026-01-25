#!/usr/bin/env python3
"""
Automation Machine Brain Orchestrator
Routes queries to appropriate LLM based on complexity.
Local-first approach: deepseek → qwen → claude (fallback)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
import yaml

# Paths
BASE_DIR = Path("C:/automation-machine")
CONFIG_PATH = BASE_DIR / "config.yaml"
USAGE_LOG_PATH = BASE_DIR / "usage_log.json"
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge-base"
CONVERSATION_LOG_PATH = KNOWLEDGE_BASE_PATH / "research" / "conversation-log.md"


def load_config() -> dict:
    """Load configuration from YAML file."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def load_usage_log() -> dict:
    """Load usage statistics from JSON file."""
    with open(USAGE_LOG_PATH, "r") as f:
        return json.load(f)


def save_usage_log(log: dict) -> None:
    """Save usage statistics to JSON file."""
    with open(USAGE_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def detect_complexity(query: str, config: dict) -> str:
    """
    Detect query complexity based on keywords and length.
    Returns: 'simple', 'medium', or 'complex'
    """
    query_lower = query.lower()
    routing = config.get("routing", {})
    keywords = routing.get("keywords", {})

    # Check for complex keywords first (highest priority)
    for keyword in keywords.get("complex", []):
        if keyword in query_lower:
            return "complex"

    # Check for medium keywords
    for keyword in keywords.get("medium", []):
        if keyword in query_lower:
            return "medium"

    # Check for simple keywords
    for keyword in keywords.get("simple", []):
        if keyword in query_lower:
            return "simple"

    # Fallback to length-based detection
    word_count = len(query.split())
    if word_count <= 10:
        return "simple"
    elif word_count <= 50:
        return "medium"
    else:
        return "complex"


def select_model(complexity: str, forced_model: Optional[str] = None) -> tuple[str, dict]:
    """
    Select the appropriate model based on complexity.
    Returns: (model_key, model_config)
    """
    config = load_config()

    # Handle forced model selection
    if forced_model:
        if forced_model == "deepseek":
            return "deepseek", config["models"]["local"]["deepseek"]
        elif forced_model == "qwen":
            return "qwen", config["models"]["local"]["qwen"]
        elif forced_model == "claude":
            return "claude", config["models"]["cloud"]["claude"]

    # Route based on complexity
    if complexity == "simple":
        return "deepseek", config["models"]["local"]["deepseek"]
    elif complexity == "medium":
        return "qwen", config["models"]["local"]["qwen"]
    else:  # complex
        return "claude", config["models"]["cloud"]["claude"]


def query_ollama(prompt: str, model_name: str, endpoint: str) -> tuple[str, int, int]:
    """
    Query local Ollama model.
    Returns: (response_text, input_tokens, output_tokens)
    """
    url = f"{endpoint}/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        response_text = data.get("response", "")
        # Ollama provides token counts in the response
        input_tokens = data.get("prompt_eval_count", len(prompt.split()) * 2)
        output_tokens = data.get("eval_count", len(response_text.split()) * 2)

        return response_text, input_tokens, output_tokens

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to Ollama: {e}")


def query_claude(prompt: str, model_name: str) -> tuple[str, int, int]:
    """
    Query Claude API (cloud fallback).
    Returns: (response_text, input_tokens, output_tokens)
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": model_name,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        response_text = data["content"][0]["text"]
        input_tokens = data["usage"]["input_tokens"]
        output_tokens = data["usage"]["output_tokens"]

        return response_text, input_tokens, output_tokens

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to Claude API: {e}")


def search_knowledge_base(query: str) -> list[dict]:
    """
    Search the knowledge base for relevant content.
    Returns list of matching files with snippets.
    """
    results = []
    query_terms = query.lower().split()

    for md_file in KNOWLEDGE_BASE_PATH.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            content_lower = content.lower()

            # Simple keyword matching
            matches = sum(1 for term in query_terms if term in content_lower)
            if matches > 0:
                # Extract relevant snippet
                lines = content.split("\n")
                snippet_lines = []
                for i, line in enumerate(lines):
                    if any(term in line.lower() for term in query_terms):
                        snippet_lines.append(line.strip())
                        if len(snippet_lines) >= 3:
                            break

                results.append({
                    "file": str(md_file.relative_to(KNOWLEDGE_BASE_PATH)),
                    "matches": matches,
                    "snippet": "\n".join(snippet_lines) if snippet_lines else lines[0][:200]
                })
        except Exception:
            continue

    # Sort by relevance
    results.sort(key=lambda x: x["matches"], reverse=True)
    return results[:5]  # Top 5 results


def log_conversation(query: str, response: str, model: str) -> None:
    """Append conversation to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"""
---
## [{timestamp}] via {model}

**Query:** {query}

**Response:**
{response[:500]}{'...' if len(response) > 500 else ''}

"""

    with open(CONVERSATION_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def update_usage_stats(model_key: str, tokens_in: int, tokens_out: int, cost: float) -> None:
    """Update usage statistics in the log file."""
    log = load_usage_log()
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")

    # Map model keys to log keys
    model_map = {
        "deepseek": "deepseek-r1",
        "qwen": "qwen2.5:32b",
        "claude": "claude-sonnet-4"
    }
    log_key = model_map.get(model_key, model_key)

    # Update summary
    log["summary"]["total_queries"] += 1
    log["summary"]["total_cost_usd"] += cost

    # Update model stats
    if log_key in log["summary"]["models"]:
        log["summary"]["models"][log_key]["queries"] += 1
        log["summary"]["models"][log_key]["tokens_in"] += tokens_in
        log["summary"]["models"][log_key]["tokens_out"] += tokens_out
        log["summary"]["models"][log_key]["cost_usd"] += cost

    # Update daily stats
    if today not in log["summary"]["daily"]:
        log["summary"]["daily"][today] = {"queries": 0, "cost_usd": 0.0}
    log["summary"]["daily"][today]["queries"] += 1
    log["summary"]["daily"][today]["cost_usd"] += cost

    # Update monthly stats
    if month not in log["summary"]["monthly"]:
        log["summary"]["monthly"][month] = {"queries": 0, "cost_usd": 0.0}
    log["summary"]["monthly"][month]["queries"] += 1
    log["summary"]["monthly"][month]["cost_usd"] += cost

    # Add to history
    log["history"].append({
        "timestamp": datetime.now().isoformat(),
        "model": log_key,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": cost
    })

    # Keep only last 1000 history entries
    if len(log["history"]) > 1000:
        log["history"] = log["history"][-1000:]

    save_usage_log(log)


def calculate_cost(model_key: str, tokens_in: int, tokens_out: int, config: dict) -> float:
    """Calculate cost for a query (0 for local models)."""
    if model_key in ["deepseek", "qwen"]:
        return 0.0

    if model_key == "claude":
        cloud_config = config["models"]["cloud"]["claude"]
        cost_in = tokens_in * cloud_config["cost_per_input_token"]
        cost_out = tokens_out * cloud_config["cost_per_output_token"]
        return cost_in + cost_out

    return 0.0


def show_stats() -> None:
    """Display usage statistics."""
    log = load_usage_log()
    summary = log["summary"]

    print("\n" + "=" * 50)
    print("AUTOMATION MACHINE - USAGE STATISTICS")
    print("=" * 50)

    print(f"\nTotal Queries: {summary['total_queries']}")
    print(f"Total Cost: ${summary['total_cost_usd']:.4f}")

    print("\n--- By Model ---")
    for model, stats in summary["models"].items():
        print(f"\n{model}:")
        print(f"  Queries: {stats['queries']}")
        print(f"  Tokens In: {stats['tokens_in']:,}")
        print(f"  Tokens Out: {stats['tokens_out']:,}")
        print(f"  Cost: ${stats['cost_usd']:.4f}")

    # Show recent daily stats
    if summary.get("daily"):
        print("\n--- Recent Daily Usage ---")
        recent_days = sorted(summary["daily"].keys())[-7:]
        for day in recent_days:
            stats = summary["daily"][day]
            print(f"  {day}: {stats['queries']} queries, ${stats['cost_usd']:.4f}")

    print("\n" + "=" * 50)


def process_query(query: str, forced_model: Optional[str] = None, verbose: bool = False) -> str:
    """
    Main query processing pipeline.
    1. Detect complexity
    2. Search knowledge base
    3. Select model
    4. Query model
    5. Log everything
    """
    config = load_config()

    # Step 1: Detect complexity
    complexity = detect_complexity(query, config)
    if verbose:
        print(f"[Complexity: {complexity}]")

    # Step 2: Search knowledge base
    kb_results = search_knowledge_base(query)
    kb_context = ""
    if kb_results:
        kb_context = "\n\nRelevant knowledge base entries:\n"
        for result in kb_results[:3]:
            kb_context += f"- {result['file']}: {result['snippet'][:100]}...\n"

    # Step 3: Select model
    model_key, model_config = select_model(complexity, forced_model)
    if verbose:
        print(f"[Model: {model_config['name']}]")

    # Step 4: Build enhanced prompt
    enhanced_prompt = query
    if kb_context:
        enhanced_prompt = f"{query}\n{kb_context}"

    # Step 5: Query the model
    try:
        if model_key in ["deepseek", "qwen"]:
            response, tokens_in, tokens_out = query_ollama(
                enhanced_prompt,
                model_config["name"],
                model_config["endpoint"]
            )
        else:
            response, tokens_in, tokens_out = query_claude(
                enhanced_prompt,
                model_config["name"]
            )
    except ConnectionError as e:
        # Fallback logic
        if config["routing"].get("fallback_enabled") and model_key != "claude":
            if verbose:
                print(f"[Fallback: {model_key} failed, trying next model]")
            if model_key == "deepseek":
                return process_query(query, forced_model="qwen", verbose=verbose)
            elif model_key == "qwen":
                return process_query(query, forced_model="claude", verbose=verbose)
        raise e

    # Step 6: Calculate cost and log
    cost = calculate_cost(model_key, tokens_in, tokens_out, config)
    update_usage_stats(model_key, tokens_in, tokens_out, cost)
    log_conversation(query, response, model_config["name"])

    if verbose:
        print(f"[Tokens: {tokens_in} in / {tokens_out} out | Cost: ${cost:.4f}]")

    return response


def main():
    parser = argparse.ArgumentParser(
        description="Automation Machine Brain - Intelligent LLM Router"
    )
    parser.add_argument("query", nargs="?", help="Query to process")
    parser.add_argument("--stats", action="store_true", help="Show usage statistics")
    parser.add_argument("--model", choices=["deepseek", "qwen", "claude"],
                        help="Force specific model")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show routing decisions")

    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    if not args.query:
        # Interactive mode
        print("Automation Machine Brain - Interactive Mode")
        print("Type 'quit' to exit, 'stats' to see usage statistics")
        print("-" * 40)

        while True:
            try:
                query = input("\n> ").strip()
                if not query:
                    continue
                if query.lower() == "quit":
                    break
                if query.lower() == "stats":
                    show_stats()
                    continue

                response = process_query(query, args.model, args.verbose)
                print(f"\n{response}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Single query mode
        try:
            response = process_query(args.query, args.model, args.verbose)
            print(response)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
