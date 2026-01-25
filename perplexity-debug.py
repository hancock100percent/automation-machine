#!/usr/bin/env python3
"""
Perplexity API Debug Script
Tests connection and finds working model names.
"""

import os
import json
import requests

# Check for API key in both possible env var names
API_KEY = os.environ.get("PERPLEXITY_API_KEY") or os.environ.get("PERPLEXITYAI_API_KEY")

if not API_KEY:
    print("ERROR: No API key found!")
    print("Set either PERPLEXITY_API_KEY or PERPLEXITYAI_API_KEY")
    exit(1)

print(f"API Key found: {API_KEY[:8]}...{API_KEY[-4:]}")
print("-" * 50)

# Current model names (as of January 2026)
# See: https://docs.perplexity.ai/getting-started/models
MODELS_TO_TRY = [
    "sonar",                    # Lightweight search ~$1/1M tokens (recommended for cost)
    "sonar-pro",                # Advanced search ~$3/1M tokens (recommended for quality)
    "sonar-reasoning-pro",      # Chain of thought reasoning ~$5/1M tokens
    # Note: sonar-deep-research uses async jobs, different API pattern
]

# Deprecated model names (will return 400 Bad Request)
DEPRECATED_MODELS = [
    "llama-3.1-sonar-small-128k-online",
    "llama-3.1-sonar-large-128k-online",
    "llama-3.1-sonar-huge-128k-online",
]

def test_model(model_name: str) -> dict:
    """Test a specific model name."""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "What is 2+2? Answer with just the number."}
        ]
    }

    print(f"\nTesting model: {model_name}")
    print(f"  URL: {url}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            print(f"  SUCCESS!")
            print(f"  Response: {content[:100]}...")
            print(f"  Usage: {usage}")
            return {"success": True, "model": model_name, "usage": usage}
        else:
            print(f"  FAILED: {response.text[:200]}")
            return {"success": False, "model": model_name, "error": response.text}

    except Exception as e:
        print(f"  ERROR: {e}")
        return {"success": False, "model": model_name, "error": str(e)}


def test_with_litellm(model_name: str) -> dict:
    """Test using LiteLLM library."""
    try:
        from litellm import completion

        # LiteLLM uses different env var name
        os.environ["PERPLEXITYAI_API_KEY"] = API_KEY

        print(f"\nTesting via LiteLLM: perplexity/{model_name}")

        response = completion(
            model=f"perplexity/{model_name}",
            messages=[{"role": "user", "content": "What is 2+2? Answer with just the number."}]
        )

        content = response.choices[0].message.content
        usage = response.usage
        print(f"  SUCCESS!")
        print(f"  Response: {content[:100]}")
        print(f"  Usage: input={usage.prompt_tokens}, output={usage.completion_tokens}")
        return {"success": True, "model": model_name, "method": "litellm"}

    except ImportError:
        print("  LiteLLM not installed, skipping")
        return {"success": False, "error": "litellm not installed"}
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"success": False, "model": model_name, "error": str(e)}


def main():
    print("=" * 50)
    print("PERPLEXITY API DEBUG")
    print("=" * 50)

    working_models = []

    # Test direct API calls
    print("\n--- Testing Direct API ---")
    for model in MODELS_TO_TRY:
        result = test_model(model)
        if result.get("success"):
            working_models.append(model)

    # Test via LiteLLM with first working model
    print("\n--- Testing LiteLLM ---")
    if working_models:
        test_with_litellm(working_models[0])
    else:
        # Try sonar as default
        test_with_litellm("sonar")

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    if working_models:
        print(f"\nWorking models: {working_models}")
        print(f"\nRecommended for automation_brain.py:")
        print(f'  model = "{working_models[0]}"')
    else:
        print("\nNo working models found!")
        print("Check your API key and account status.")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
