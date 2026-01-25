#!/usr/bin/env python3
"""
Test suite for Automation Machine Brain Orchestrator
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from brain import (
    load_config,
    load_usage_log,
    detect_complexity,
    select_model,
    search_knowledge_base,
    calculate_cost,
    update_usage_stats,
    USAGE_LOG_PATH,
)


class TestConfigLoading(unittest.TestCase):
    """Test configuration loading."""

    def test_load_config(self):
        """Config file should load successfully."""
        config = load_config()
        self.assertIn("models", config)
        self.assertIn("routing", config)
        self.assertIn("local", config["models"])
        self.assertIn("cloud", config["models"])

    def test_config_has_models(self):
        """Config should have all required models."""
        config = load_config()
        self.assertIn("deepseek", config["models"]["local"])
        self.assertIn("qwen", config["models"]["local"])
        self.assertIn("claude", config["models"]["cloud"])


class TestComplexityDetection(unittest.TestCase):
    """Test query complexity detection."""

    def setUp(self):
        self.config = load_config()

    def test_simple_query_by_keyword(self):
        """Queries with simple keywords should be detected as simple."""
        simple_queries = [
            "quick check on status",
            "list all files",
            "what is the current status",
            "show me the logs",
        ]
        for query in simple_queries:
            complexity = detect_complexity(query, self.config)
            self.assertEqual(complexity, "simple", f"Failed for: {query}")

    def test_medium_query_by_keyword(self):
        """Queries with medium keywords should be detected as medium."""
        medium_queries = [
            "analyze this code",
            "generate a function",
            "explain how this works",
            "write a script to do X",
        ]
        for query in medium_queries:
            complexity = detect_complexity(query, self.config)
            self.assertEqual(complexity, "medium", f"Failed for: {query}")

    def test_complex_query_by_keyword(self):
        """Queries with complex keywords should be detected as complex."""
        complex_queries = [
            "design a complex architecture",
            "this is a novel problem",
            "create something creative",
        ]
        for query in complex_queries:
            complexity = detect_complexity(query, self.config)
            self.assertEqual(complexity, "complex", f"Failed for: {query}")

    def test_fallback_to_length(self):
        """Queries without keywords should fall back to length-based detection."""
        short_query = "hello there"  # No keywords, short
        complexity = detect_complexity(short_query, self.config)
        self.assertEqual(complexity, "simple")


class TestModelSelection(unittest.TestCase):
    """Test model selection logic."""

    def test_simple_routes_to_deepseek(self):
        """Simple complexity should route to deepseek."""
        model_key, config = select_model("simple")
        self.assertEqual(model_key, "deepseek")
        self.assertIn("deepseek", config["name"])

    def test_medium_routes_to_qwen(self):
        """Medium complexity should route to qwen."""
        model_key, config = select_model("medium")
        self.assertEqual(model_key, "qwen")
        self.assertIn("qwen", config["name"])

    def test_complex_routes_to_claude(self):
        """Complex queries should route to claude."""
        model_key, config = select_model("complex")
        self.assertEqual(model_key, "claude")
        self.assertIn("claude", config["name"])

    def test_forced_model_deepseek(self):
        """Forced deepseek should override complexity."""
        model_key, _ = select_model("complex", forced_model="deepseek")
        self.assertEqual(model_key, "deepseek")

    def test_forced_model_qwen(self):
        """Forced qwen should override complexity."""
        model_key, _ = select_model("simple", forced_model="qwen")
        self.assertEqual(model_key, "qwen")

    def test_forced_model_claude(self):
        """Forced claude should override complexity."""
        model_key, _ = select_model("simple", forced_model="claude")
        self.assertEqual(model_key, "claude")


class TestKnowledgeBaseSearch(unittest.TestCase):
    """Test knowledge base search functionality."""

    def test_search_returns_list(self):
        """Search should return a list."""
        results = search_knowledge_base("automation")
        self.assertIsInstance(results, list)

    def test_search_finds_relevant_files(self):
        """Search should find files with matching content."""
        results = search_knowledge_base("model routing")
        # Should find index.md which contains routing info
        if results:
            file_names = [r["file"] for r in results]
            self.assertTrue(
                any("index" in f for f in file_names),
                "Should find index.md for routing queries"
            )

    def test_search_returns_snippets(self):
        """Search results should include snippets."""
        results = search_knowledge_base("deepseek")
        if results:
            self.assertIn("snippet", results[0])


class TestCostCalculation(unittest.TestCase):
    """Test cost calculation logic."""

    def setUp(self):
        self.config = load_config()

    def test_local_models_are_free(self):
        """Local models should have zero cost."""
        cost = calculate_cost("deepseek", 1000, 500, self.config)
        self.assertEqual(cost, 0.0)

        cost = calculate_cost("qwen", 1000, 500, self.config)
        self.assertEqual(cost, 0.0)

    def test_claude_has_cost(self):
        """Claude queries should have calculated cost."""
        cost = calculate_cost("claude", 1000, 500, self.config)
        self.assertGreater(cost, 0.0)

    def test_claude_cost_formula(self):
        """Claude cost should follow the pricing formula."""
        # From config: $3 per 1M input, $15 per 1M output
        cost = calculate_cost("claude", 1000000, 1000000, self.config)
        expected = 3.0 + 15.0  # $3 input + $15 output
        self.assertAlmostEqual(cost, expected, places=2)


class TestUsageTracking(unittest.TestCase):
    """Test usage statistics tracking."""

    def test_usage_log_loads(self):
        """Usage log should load successfully."""
        log = load_usage_log()
        self.assertIn("summary", log)
        self.assertIn("history", log)

    def test_usage_log_has_models(self):
        """Usage log should track all models."""
        log = load_usage_log()
        models = log["summary"]["models"]
        self.assertIn("deepseek-r1", models)
        self.assertIn("qwen2.5:32b", models)
        self.assertIn("claude-sonnet-4", models)


class TestOllamaIntegration(unittest.TestCase):
    """Test Ollama API integration (requires running Ollama)."""

    def test_ollama_connection(self):
        """Test that Ollama is accessible."""
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Ollama not running - skipping integration test")

    def test_deepseek_model_available(self):
        """Test that deepseek model is available."""
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            data = response.json()
            model_names = [m["name"] for m in data.get("models", [])]
            self.assertTrue(
                any("deepseek" in name for name in model_names),
                f"deepseek model not found. Available: {model_names}"
            )
        except requests.exceptions.ConnectionError:
            self.skipTest("Ollama not running - skipping integration test")

    def test_qwen_model_available(self):
        """Test that qwen model is available."""
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            data = response.json()
            model_names = [m["name"] for m in data.get("models", [])]
            self.assertTrue(
                any("qwen" in name for name in model_names),
                f"qwen model not found. Available: {model_names}"
            )
        except requests.exceptions.ConnectionError:
            self.skipTest("Ollama not running - skipping integration test")


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexityDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestModelSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeBaseSearch))
    suite.addTests(loader.loadTestsFromTestCase(TestCostCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestUsageTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestOllamaIntegration))

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
