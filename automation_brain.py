#!/usr/bin/env python3
"""
Automation Machine Brain - Full Orchestration System
Smart delegation across local LLMs, Perplexity, Claude, and tool integrations.
Local-first approach with cost optimization.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal

import requests
import yaml

# Paths
BASE_DIR = Path("C:/automation-machine")
CONFIG_PATH = BASE_DIR / "config.yaml"
TOOLS_CONFIG_PATH = BASE_DIR / "tools_config.json"
USAGE_LOG_PATH = BASE_DIR / "usage_log.json"
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge-base"
CONVERSATION_LOG_PATH = KNOWLEDGE_BASE_PATH / "research" / "conversation-log.md"

# Task categories for routing
TaskCategory = Literal["research", "code", "reasoning", "image", "video", "database", "general"]


class AutomationBrain:
    """
    Full orchestration brain that delegates tasks to the optimal tool/model
    based on task analysis, cost optimization, and capability matching.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.config = self._load_config()
        self.tools_config = self._load_tools_config()

    def _load_config(self) -> dict:
        """Load main configuration from YAML."""
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)

    def _load_tools_config(self) -> dict:
        """Load tools configuration from JSON."""
        if TOOLS_CONFIG_PATH.exists():
            with open(TOOLS_CONFIG_PATH, "r") as f:
                return json.load(f)
        return {}

    def _log(self, message: str) -> None:
        """Print verbose logging if enabled."""
        if self.verbose:
            print(f"[Brain] {message}")

    # =========================================================================
    # TASK ANALYSIS
    # =========================================================================

    def _analyze_task(self, query: str) -> dict:
        """
        Analyze task to determine requirements and optimal routing.
        Returns analysis dict with category, complexity, needs_web, etc.
        """
        query_lower = query.lower()

        analysis = {
            "query": query,
            "category": "general",
            "complexity": "simple",
            "needs_web": False,
            "needs_image": False,
            "needs_video": False,
            "needs_talking_head": False,
            "needs_database": False,
            "needs_code": False,
            "needs_browser": False,
            "needs_github": False,
            "recommended_tool": "local-deepseek",
        }

        # Detect web research needs
        web_indicators = [
            "latest", "current", "2024", "2025", "2026", "news", "today",
            "recent", "price", "compare prices", "find", "search for",
            "what are the best", "recommendations for", "reviews"
        ]
        if any(indicator in query_lower for indicator in web_indicators):
            analysis["needs_web"] = True
            analysis["category"] = "research"

        # Detect video generation needs (check before image)
        video_indicators = [
            "generate video", "create video", "animate", "animation",
            "video clip", "motion", "image to video", "i2v", "video from"
        ]
        if any(indicator in query_lower for indicator in video_indicators):
            analysis["needs_video"] = True
            analysis["category"] = "video"

        # Detect talking head / avatar needs
        talking_head_indicators = [
            "talking head", "avatar", "lip sync", "lipsync", "sadtalker",
            "speaking video", "face animation", "photo to video with audio"
        ]
        if any(indicator in query_lower for indicator in talking_head_indicators):
            analysis["needs_talking_head"] = True
            analysis["needs_video"] = True
            analysis["category"] = "video"

        # Detect image generation needs
        image_indicators = [
            "generate image", "create image", "draw", "illustration",
            "picture of", "visual", "logo", "design image", "artwork"
        ]
        if any(indicator in query_lower for indicator in image_indicators):
            analysis["needs_image"] = True
            analysis["category"] = "image"

        # Detect code needs
        code_indicators = [
            "code", "function", "script", "program", "implement",
            "debug", "refactor", "write a", "create a class", "api"
        ]
        if any(indicator in query_lower for indicator in code_indicators):
            analysis["needs_code"] = True
            analysis["category"] = "code"

        # Detect database needs
        db_indicators = [
            "database", "supabase", "query", "sql", "store data",
            "retrieve", "insert", "update record"
        ]
        if any(indicator in query_lower for indicator in db_indicators):
            analysis["needs_database"] = True
            analysis["category"] = "database"

        # Detect browser automation needs (Claude in Chrome)
        browser_indicators = [
            "navigate to", "click on", "fill form", "browser", "website",
            "fiverr", "post to", "social media", "login to", "sign in",
            "open page", "web page", "scrape", "automate browser"
        ]
        if any(indicator in query_lower for indicator in browser_indicators):
            analysis["needs_browser"] = True
            analysis["category"] = "browser"

        # Detect GitHub needs
        github_indicators = [
            "github", "repository", "repo", "commit", "pull request", "pr",
            "issue", "branch", "merge", "fork", "clone", "git "
        ]
        if any(indicator in query_lower for indicator in github_indicators):
            analysis["needs_github"] = True
            analysis["category"] = "code"

        # Detect complexity
        complex_indicators = [
            "complex", "novel", "architecture", "design system",
            "comprehensive", "multi-step", "analyze deeply"
        ]
        medium_indicators = [
            "analyze", "explain", "generate", "design", "refactor",
            "create", "implement", "debug"
        ]

        if any(indicator in query_lower for indicator in complex_indicators):
            analysis["complexity"] = "complex"
        elif any(indicator in query_lower for indicator in medium_indicators):
            analysis["complexity"] = "medium"
        else:
            # Length-based fallback
            word_count = len(query.split())
            if word_count > 50:
                analysis["complexity"] = "complex"
            elif word_count > 15:
                analysis["complexity"] = "medium"

        # Determine recommended tool based on analysis
        analysis["recommended_tool"] = self._select_optimal_tool(analysis)

        return analysis

    def _select_optimal_tool(self, analysis: dict) -> str:
        """
        Select the optimal tool based on task analysis.
        Priority: Local free → Perplexity (cheap) → Claude (expensive)
        """
        # Browser automation → Claude in Chrome
        if analysis.get("needs_browser"):
            if self.tools_config.get("claude-in-chrome", {}).get("enabled"):
                return "claude-in-chrome"
            return "local-qwen"  # Fallback to describe browser steps

        # GitHub operations → GitHub CLI/MCP
        if analysis.get("needs_github"):
            if self.tools_config.get("github", {}).get("enabled"):
                return "github"
            return "local-qwen"  # Fallback to describe git commands

        # Video generation → ComfyUI Video
        if analysis.get("needs_video"):
            if self.tools_config.get("comfyui", {}).get("enabled"):
                if analysis.get("needs_talking_head"):
                    return "comfyui-video-talking-head"
                return "comfyui-video"
            return "local-qwen"  # Fallback to describe what to generate

        # Image generation → ComfyUI
        if analysis["needs_image"]:
            if self.tools_config.get("comfyui", {}).get("enabled"):
                return "comfyui"
            return "local-qwen"  # Fallback to describe what to generate

        # Web research → Perplexity
        if analysis["needs_web"]:
            if self.tools_config.get("perplexity", {}).get("enabled"):
                return "perplexity"
            return "local-qwen"  # Fallback (won't have current data)

        # Database operations → Supabase
        if analysis["needs_database"]:
            if self.tools_config.get("supabase", {}).get("enabled"):
                return "supabase"
            return "local-qwen"  # Fallback to generate SQL

        # Code tasks
        if analysis["needs_code"]:
            if analysis["complexity"] == "complex":
                return "claude"
            return "local-qwen"  # Qwen is good at code

        # General routing by complexity
        if analysis["complexity"] == "simple":
            return "local-deepseek"
        elif analysis["complexity"] == "medium":
            return "local-qwen"
        else:
            return "claude"

    # =========================================================================
    # DELEGATION METHODS
    # =========================================================================

    def _delegate_to_local(self, query: str, model: str = "deepseek") -> dict:
        """
        Delegate to local Ollama model.
        Returns: {"response": str, "tokens_in": int, "tokens_out": int, "cost": 0.0}
        """
        if model == "deepseek":
            model_config = self.config["models"]["local"]["deepseek"]
        else:
            model_config = self.config["models"]["local"]["qwen"]

        url = f"{model_config['endpoint']}/api/generate"
        payload = {
            "model": model_config["name"],
            "prompt": query,
            "stream": False
        }

        self._log(f"Querying local {model}: {model_config['name']}")

        try:
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()

            return {
                "response": data.get("response", ""),
                "tokens_in": data.get("prompt_eval_count", len(query.split()) * 2),
                "tokens_out": data.get("eval_count", 100),
                "cost": 0.0,
                "tool": f"local-ollama",
                "model": model_config["name"]
            }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ollama connection failed: {e}")

    def _delegate_to_perplexity(self, query: str) -> dict:
        """
        Delegate web research to Perplexity Pro.
        Returns: {"response": str, "tokens_in": int, "tokens_out": int, "cost": float}
        """
        perplexity_config = self.tools_config.get("perplexity", {})
        api_key = os.environ.get(perplexity_config.get("api_key_env", "PERPLEXITY_API_KEY"))

        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")

        model = perplexity_config.get("model", "sonar-pro")

        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": query}]
        }

        self._log(f"Querying Perplexity: {model}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            tokens_in = data.get("usage", {}).get("prompt_tokens", len(query.split()) * 2)
            tokens_out = data.get("usage", {}).get("completion_tokens", 100)
            cost_per_1m = perplexity_config.get("cost_per_1m_tokens", 1.0)
            cost = ((tokens_in + tokens_out) / 1_000_000) * cost_per_1m

            return {
                "response": data["choices"][0]["message"]["content"],
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost": cost,
                "tool": "perplexity",
                "model": model
            }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"{e.response.status_code}: {error_detail.get('error', {}).get('message', e.response.text)}"
                except Exception:
                    error_msg = f"{e.response.status_code}: {e.response.text[:200]}"
            raise ConnectionError(f"Perplexity API error: {error_msg}. Valid models: sonar, sonar-pro, sonar-reasoning-pro, sonar-deep-research")

    def _delegate_to_claude(self, query: str) -> dict:
        """
        Delegate complex tasks to Claude Sonnet 4.
        Returns: {"response": str, "tokens_in": int, "tokens_out": int, "cost": float}
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        cloud_config = self.config["models"]["cloud"]["claude"]
        model = cloud_config["name"]

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": query}]
        }

        self._log(f"Querying Claude: {model}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            tokens_in = data["usage"]["input_tokens"]
            tokens_out = data["usage"]["output_tokens"]
            cost_in = tokens_in * cloud_config["cost_per_input_token"]
            cost_out = tokens_out * cloud_config["cost_per_output_token"]

            return {
                "response": data["content"][0]["text"],
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost": cost_in + cost_out,
                "tool": "claude",
                "model": model
            }
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Claude connection failed: {e}")

    def _delegate_to_comfyui(self, query: str) -> dict:
        """
        Delegate image generation to ComfyUI on The Machine.
        Generates prompt with local LLM, then executes workflow via API.
        """
        import time
        import uuid

        comfyui_config = self.tools_config.get("comfyui", {})
        endpoint = comfyui_config.get("endpoint", "http://100.64.130.71:8188")
        workflow_path = Path(comfyui_config.get("workflow_path", "C:/automation-machine/workflows/"))
        output_path = Path(comfyui_config.get("output_path", "C:/automation-machine/output/"))

        output_path.mkdir(parents=True, exist_ok=True)

        self._log(f"ComfyUI delegation to {endpoint}")

        # Step 1: Generate optimized prompt using local LLM
        prompt_instruction = (
            f"Create a detailed Stable Diffusion XL prompt for: {query}\n\n"
            "Requirements:\n"
            "- Be specific and descriptive\n"
            "- Include style, lighting, and quality terms\n"
            "- Keep under 200 words\n"
            "- Output ONLY the prompt, no explanations"
        )
        prompt_response = self._delegate_to_local(prompt_instruction, model="qwen")
        generated_prompt = prompt_response["response"].strip()

        self._log(f"Generated prompt: {generated_prompt[:100]}...")

        # Step 2: Load and modify workflow
        workflow_file = workflow_path / "sdxl_basic.json"
        if not workflow_file.exists():
            return {
                "response": f"**Error:** Workflow not found at {workflow_file}\n\n"
                           f"Generated prompt for manual use:\n{generated_prompt}",
                "tokens_in": prompt_response["tokens_in"],
                "tokens_out": prompt_response["tokens_out"],
                "cost": 0.0,
                "tool": "comfyui",
                "model": "local-qwen"
            }

        with open(workflow_file, "r") as f:
            workflow = json.load(f)

        # Inject prompt and random seed
        workflow["6"]["inputs"]["text"] = generated_prompt
        workflow["3"]["inputs"]["seed"] = int(time.time()) % (2**32)

        # Step 3: Queue the prompt
        client_id = str(uuid.uuid4())
        try:
            queue_response = requests.post(
                f"{endpoint}/prompt",
                json={"prompt": workflow, "client_id": client_id},
                timeout=30
            )
            queue_response.raise_for_status()
            prompt_id = queue_response.json().get("prompt_id")
            self._log(f"Queued prompt: {prompt_id}")
        except requests.exceptions.RequestException as e:
            return {
                "response": f"**ComfyUI Connection Error:** {e}\n\n"
                           f"Generated prompt for manual use:\n{generated_prompt}",
                "tokens_in": prompt_response["tokens_in"],
                "tokens_out": prompt_response["tokens_out"],
                "cost": 0.0,
                "tool": "comfyui",
                "model": "local-qwen"
            }

        # Step 4: Poll for completion (max 5 minutes)
        max_wait = 300
        poll_interval = 2
        waited = 0
        output_images = []

        while waited < max_wait:
            try:
                history_response = requests.get(
                    f"{endpoint}/history/{prompt_id}",
                    timeout=10
                )
                history = history_response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            for img in node_output["images"]:
                                output_images.append(img)
                    if outputs:
                        break
            except Exception as e:
                self._log(f"Poll error: {e}")

            time.sleep(poll_interval)
            waited += poll_interval
            self._log(f"Waiting for generation... {waited}s")

        # Step 5: Download and save images
        saved_files = []
        for img_info in output_images:
            filename = img_info.get("filename", "output.png")
            subfolder = img_info.get("subfolder", "")
            img_type = img_info.get("type", "output")

            try:
                img_url = f"{endpoint}/view?filename={filename}&subfolder={subfolder}&type={img_type}"
                img_response = requests.get(img_url, timeout=30)
                img_response.raise_for_status()

                # Save locally
                local_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                local_path = output_path / local_filename
                with open(local_path, "wb") as f:
                    f.write(img_response.content)
                saved_files.append(str(local_path))
                self._log(f"Saved: {local_path}")
            except Exception as e:
                self._log(f"Failed to download {filename}: {e}")

        # Step 6: Return result
        if saved_files:
            response_text = (
                f"**Image Generated Successfully**\n\n"
                f"**Prompt used:**\n{generated_prompt}\n\n"
                f"**Output files:**\n" + "\n".join(f"- {f}" for f in saved_files) + "\n\n"
                f"**Generation time:** ~{waited}s"
            )
        else:
            response_text = (
                f"**Generation timed out or failed**\n\n"
                f"**Prompt used:**\n{generated_prompt}\n\n"
                f"Check ComfyUI at {endpoint} for status."
            )

        return {
            "response": response_text,
            "tokens_in": prompt_response["tokens_in"],
            "tokens_out": prompt_response["tokens_out"],
            "cost": 0.0,
            "tool": "comfyui",
            "model": "sdxl_base_1.0",
            "output_files": saved_files
        }

    def _delegate_to_comfyui_video(self, query: str) -> dict:
        """
        Delegate image-to-video generation to ComfyUI on The Machine.
        Uses Wan2.1 I2V or AnimateDiff workflows.
        """
        import time
        import uuid

        comfyui_config = self.tools_config.get("comfyui", {})
        endpoint = comfyui_config.get("endpoint", "http://100.64.130.71:8188")
        workflow_path = Path(comfyui_config.get("workflow_path", "C:/automation-machine/workflows/"))
        output_path = Path(comfyui_config.get("output_path", "C:/automation-machine/output/"))

        output_path.mkdir(parents=True, exist_ok=True)

        self._log(f"ComfyUI Video delegation to {endpoint}")

        # Step 1: Generate motion prompt using local LLM
        prompt_instruction = (
            f"Create a brief motion description for animating: {query}\n\n"
            "Requirements:\n"
            "- Describe subtle, natural movement\n"
            "- Keep it simple (flame flicker, gentle sway, soft glow)\n"
            "- One sentence, under 20 words\n"
            "- Output ONLY the motion description"
        )
        prompt_response = self._delegate_to_local(prompt_instruction, model="qwen")
        motion_prompt = prompt_response["response"].strip()

        self._log(f"Motion prompt: {motion_prompt}")

        # Step 2: Load video workflow
        workflow_file = workflow_path / "image_to_video.json"
        if not workflow_file.exists():
            # Try AnimateDiff as fallback
            workflow_file = workflow_path / "image_to_video_animatediff.json"

        if not workflow_file.exists():
            return {
                "response": f"**Error:** Video workflow not found.\n\n"
                           f"Expected: `workflows/image_to_video.json` or `workflows/image_to_video_animatediff.json`\n\n"
                           f"**Motion prompt for manual use:**\n{motion_prompt}\n\n"
                           f"**Setup required:**\n"
                           f"1. Install ComfyUI-VideoHelperSuite on The Machine\n"
                           f"2. Download Wan2.1 I2V model\n"
                           f"3. Restart ComfyUI",
                "tokens_in": prompt_response["tokens_in"],
                "tokens_out": prompt_response["tokens_out"],
                "cost": 0.0,
                "tool": "comfyui-video",
                "model": "local-qwen"
            }

        with open(workflow_file, "r") as f:
            workflow = json.load(f)

        # Extract image path from query if provided
        image_path = None
        import re
        path_match = re.search(r'(?:from|image|with)\s+["\']?([^\s"\']+\.(?:png|jpg|jpeg))["\']?', query.lower())
        if path_match:
            image_path = path_match.group(1)

        # Inject motion prompt
        if "3" in workflow and "inputs" in workflow["3"]:
            workflow["3"]["inputs"]["text"] = motion_prompt
        if "7" in workflow and "inputs" in workflow["7"]:
            workflow["7"]["inputs"]["seed"] = int(time.time()) % (2**32)

        # If image path provided, update workflow
        if image_path:
            if "1" in workflow and "inputs" in workflow["1"]:
                workflow["1"]["inputs"]["image"] = image_path

        # Step 3: Queue the workflow
        client_id = str(uuid.uuid4())
        try:
            queue_response = requests.post(
                f"{endpoint}/prompt",
                json={"prompt": workflow, "client_id": client_id},
                timeout=30
            )
            queue_response.raise_for_status()
            prompt_id = queue_response.json().get("prompt_id")
            self._log(f"Queued video prompt: {prompt_id}")
        except requests.exceptions.RequestException as e:
            return {
                "response": f"**ComfyUI Connection Error:** {e}\n\n"
                           f"**Motion prompt for manual use:**\n{motion_prompt}\n\n"
                           f"Ensure ComfyUI is running at {endpoint}",
                "tokens_in": prompt_response["tokens_in"],
                "tokens_out": prompt_response["tokens_out"],
                "cost": 0.0,
                "tool": "comfyui-video",
                "model": "local-qwen"
            }

        # Step 4: Poll for completion (max 10 minutes for video)
        max_wait = 600
        poll_interval = 5
        waited = 0
        output_videos = []

        while waited < max_wait:
            try:
                history_response = requests.get(
                    f"{endpoint}/history/{prompt_id}",
                    timeout=10
                )
                history = history_response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "gifs" in node_output:
                            for vid in node_output["gifs"]:
                                output_videos.append(vid)
                        if "videos" in node_output:
                            for vid in node_output["videos"]:
                                output_videos.append(vid)
                    if outputs:
                        break
            except Exception as e:
                self._log(f"Poll error: {e}")

            time.sleep(poll_interval)
            waited += poll_interval
            self._log(f"Waiting for video generation... {waited}s")

        # Step 5: Download and save videos
        saved_files = []
        for vid_info in output_videos:
            filename = vid_info.get("filename", "output.mp4")
            subfolder = vid_info.get("subfolder", "")
            vid_type = vid_info.get("type", "output")

            try:
                vid_url = f"{endpoint}/view?filename={filename}&subfolder={subfolder}&type={vid_type}"
                vid_response = requests.get(vid_url, timeout=60)
                vid_response.raise_for_status()

                local_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_video_{filename}"
                local_path = output_path / local_filename
                with open(local_path, "wb") as f:
                    f.write(vid_response.content)
                saved_files.append(str(local_path))
                self._log(f"Saved video: {local_path}")
            except Exception as e:
                self._log(f"Failed to download {filename}: {e}")

        # Step 6: Return result
        if saved_files:
            response_text = (
                f"**Video Generated Successfully**\n\n"
                f"**Motion prompt:**\n{motion_prompt}\n\n"
                f"**Output files:**\n" + "\n".join(f"- {f}" for f in saved_files) + "\n\n"
                f"**Generation time:** ~{waited}s"
            )
        else:
            response_text = (
                f"**Video generation pending or in progress**\n\n"
                f"**Motion prompt:**\n{motion_prompt}\n\n"
                f"Check ComfyUI at {endpoint} for status.\n"
                f"Video generation takes longer than images (~2-5 minutes)."
            )

        return {
            "response": response_text,
            "tokens_in": prompt_response["tokens_in"],
            "tokens_out": prompt_response["tokens_out"],
            "cost": 0.0,
            "tool": "comfyui-video",
            "model": "wan2.1-i2v",
            "output_files": saved_files
        }

    def _delegate_to_comfyui_talking_head(self, query: str) -> dict:
        """
        Delegate talking head generation to ComfyUI using SadTalker.
        Requires: face image + audio file
        """
        import time
        import uuid

        comfyui_config = self.tools_config.get("comfyui", {})
        endpoint = comfyui_config.get("endpoint", "http://100.64.130.71:8188")
        workflow_path = Path(comfyui_config.get("workflow_path", "C:/automation-machine/workflows/"))
        output_path = Path(comfyui_config.get("output_path", "C:/automation-machine/output/"))

        output_path.mkdir(parents=True, exist_ok=True)

        self._log(f"ComfyUI Talking Head delegation to {endpoint}")

        # Extract file paths from query
        import re
        image_match = re.search(r'(?:photo|image|face)[:\s]+["\']?([^\s"\']+\.(?:png|jpg|jpeg))["\']?', query.lower())
        audio_match = re.search(r'(?:audio|with)[:\s]+["\']?([^\s"\']+\.(?:wav|mp3|m4a))["\']?', query.lower())

        face_image = image_match.group(1) if image_match else None
        audio_file = audio_match.group(1) if audio_match else None

        # Check for workflow
        workflow_file = workflow_path / "talking_head.json"
        if not workflow_file.exists():
            return {
                "response": f"**Error:** Talking head workflow not found.\n\n"
                           f"Expected: `workflows/talking_head.json`\n\n"
                           f"**Setup required:**\n"
                           f"1. Install ComfyUI-SadTalker nodes on The Machine\n"
                           f"2. Download SadTalker models\n"
                           f"3. Restart ComfyUI\n\n"
                           f"**Manual workflow:**\n"
                           f"1. Open ComfyUI at {endpoint}\n"
                           f"2. Load a SadTalker workflow\n"
                           f"3. Set source image: {face_image or 'your_photo.png'}\n"
                           f"4. Set audio file: {audio_file or 'your_audio.wav'}\n"
                           f"5. Queue prompt",
                "tokens_in": 0,
                "tokens_out": 0,
                "cost": 0.0,
                "tool": "comfyui-video-talking-head",
                "model": "sadtalker"
            }

        if not face_image or not audio_file:
            return {
                "response": f"**Talking Head Generation**\n\n"
                           f"Please provide both required files:\n\n"
                           f"**Usage:**\n"
                           f"```\n"
                           f"python automation_brain.py \"generate talking head photo: path/to/face.png audio: path/to/script.wav\"\n"
                           f"```\n\n"
                           f"**Detected:**\n"
                           f"- Face image: {face_image or 'NOT PROVIDED'}\n"
                           f"- Audio file: {audio_file or 'NOT PROVIDED'}\n\n"
                           f"**Tips:**\n"
                           f"- Face image: well-lit, front-facing, neutral expression\n"
                           f"- Audio: clear voice, quiet room, WAV format preferred",
                "tokens_in": 0,
                "tokens_out": 0,
                "cost": 0.0,
                "tool": "comfyui-video-talking-head",
                "model": "sadtalker"
            }

        with open(workflow_file, "r") as f:
            workflow = json.load(f)

        # Update workflow with provided files
        if "1" in workflow and "inputs" in workflow["1"]:
            workflow["1"]["inputs"]["image"] = face_image
        if "2" in workflow and "inputs" in workflow["2"]:
            workflow["2"]["inputs"]["audio"] = audio_file

        # Queue the workflow
        client_id = str(uuid.uuid4())
        try:
            queue_response = requests.post(
                f"{endpoint}/prompt",
                json={"prompt": workflow, "client_id": client_id},
                timeout=30
            )
            queue_response.raise_for_status()
            prompt_id = queue_response.json().get("prompt_id")
            self._log(f"Queued talking head prompt: {prompt_id}")
        except requests.exceptions.RequestException as e:
            return {
                "response": f"**ComfyUI Connection Error:** {e}\n\n"
                           f"Ensure ComfyUI is running at {endpoint}\n\n"
                           f"**Files to use:**\n"
                           f"- Face: {face_image}\n"
                           f"- Audio: {audio_file}",
                "tokens_in": 0,
                "tokens_out": 0,
                "cost": 0.0,
                "tool": "comfyui-video-talking-head",
                "model": "sadtalker"
            }

        # Poll for completion (max 10 minutes)
        max_wait = 600
        poll_interval = 5
        waited = 0
        output_videos = []

        while waited < max_wait:
            try:
                history_response = requests.get(
                    f"{endpoint}/history/{prompt_id}",
                    timeout=10
                )
                history = history_response.json()

                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "gifs" in node_output:
                            for vid in node_output["gifs"]:
                                output_videos.append(vid)
                        if "videos" in node_output:
                            for vid in node_output["videos"]:
                                output_videos.append(vid)
                    if outputs:
                        break
            except Exception as e:
                self._log(f"Poll error: {e}")

            time.sleep(poll_interval)
            waited += poll_interval
            self._log(f"Waiting for talking head generation... {waited}s")

        # Download and save videos
        saved_files = []
        for vid_info in output_videos:
            filename = vid_info.get("filename", "output.mp4")
            subfolder = vid_info.get("subfolder", "")
            vid_type = vid_info.get("type", "output")

            try:
                vid_url = f"{endpoint}/view?filename={filename}&subfolder={subfolder}&type={vid_type}"
                vid_response = requests.get(vid_url, timeout=60)
                vid_response.raise_for_status()

                local_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_talking_head_{filename}"
                local_path = output_path / local_filename
                with open(local_path, "wb") as f:
                    f.write(vid_response.content)
                saved_files.append(str(local_path))
                self._log(f"Saved talking head video: {local_path}")
            except Exception as e:
                self._log(f"Failed to download {filename}: {e}")

        if saved_files:
            response_text = (
                f"**Talking Head Generated Successfully**\n\n"
                f"**Source:**\n"
                f"- Face: {face_image}\n"
                f"- Audio: {audio_file}\n\n"
                f"**Output files:**\n" + "\n".join(f"- {f}" for f in saved_files) + "\n\n"
                f"**Generation time:** ~{waited}s"
            )
        else:
            response_text = (
                f"**Talking head generation pending**\n\n"
                f"**Source:**\n"
                f"- Face: {face_image}\n"
                f"- Audio: {audio_file}\n\n"
                f"Check ComfyUI at {endpoint} for status."
            )

        return {
            "response": response_text,
            "tokens_in": 0,
            "tokens_out": 0,
            "cost": 0.0,
            "tool": "comfyui-video-talking-head",
            "model": "sadtalker",
            "output_files": saved_files
        }

    def _delegate_to_github(self, query: str) -> dict:
        """
        Delegate GitHub operations using gh CLI.
        Analyzes query intent and executes appropriate gh command.
        """
        import subprocess

        self._log("GitHub delegation via gh CLI")

        # First, use local LLM to determine the appropriate gh command
        command_prompt = f"""Analyze this GitHub request and return ONLY the gh CLI command to execute.
Do not include any explanation, just the command.
If it's a search/read operation, use appropriate gh command.
If it's unclear, use 'gh status' as default.

Request: {query}

Valid commands include:
- gh repo list
- gh repo view [repo]
- gh issue list
- gh issue view [number]
- gh pr list
- gh pr view [number]
- gh search repos [query]
- gh search code [query]
- gh api [endpoint]
- gh status

Return only the command:"""

        try:
            # Get command suggestion from local LLM
            llm_response = self._delegate_to_local(command_prompt, "qwen")
            gh_command = llm_response["response"].strip().split('\n')[0]

            # Safety check - only allow read operations
            safe_commands = ["list", "view", "search", "status", "api repos", "api users"]
            if not any(safe in gh_command for safe in safe_commands):
                gh_command = "gh status"  # Default to safe command

            self._log(f"Executing: {gh_command}")

            # Execute the command
            result = subprocess.run(
                gh_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout[:3000] if len(result.stdout) > 3000 else result.stdout
                response_text = f"**GitHub Query Result**\n\n" \
                               f"Command: `{gh_command}`\n\n" \
                               f"```\n{output}\n```"
            else:
                response_text = f"**GitHub Error**\n\n" \
                               f"Command: `{gh_command}`\n\n" \
                               f"Error: {result.stderr[:500]}\n\n" \
                               f"_Ensure gh CLI is installed and authenticated._"

            return {
                "response": response_text,
                "tokens_in": llm_response["tokens_in"],
                "tokens_out": llm_response["tokens_out"],
                "cost": 0.0,
                "tool": "github",
                "model": "gh-cli + local-qwen"
            }

        except subprocess.TimeoutExpired:
            return {
                "response": "**GitHub Timeout**\n\nCommand took too long to execute.",
                "tokens_in": 0,
                "tokens_out": 0,
                "cost": 0.0,
                "tool": "github",
                "model": "gh-cli"
            }
        except Exception as e:
            return {
                "response": f"**GitHub Error**\n\n{str(e)}\n\n_Ensure gh CLI is installed._",
                "tokens_in": 0,
                "tokens_out": 0,
                "cost": 0.0,
                "tool": "github",
                "model": "gh-cli"
            }

    def _delegate_to_browser(self, query: str) -> dict:
        """
        Delegate browser automation tasks.
        Returns instructions for Claude in Chrome integration.
        """
        self._log("Browser automation request")

        # Use local LLM to generate browser automation steps
        instruction_prompt = f"""Generate step-by-step browser automation instructions for:
{query}

Format as a numbered list of actions like:
1. Navigate to [URL]
2. Click on [element]
3. Fill [field] with [value]
4. etc.

Be specific about selectors and actions."""

        try:
            llm_response = self._delegate_to_local(instruction_prompt, "qwen")

            return {
                "response": f"**Browser Automation Steps**\n\n"
                           f"_For Claude in Chrome execution:_\n\n"
                           f"{llm_response['response']}\n\n"
                           f"---\n"
                           f"_To execute: Open Claude in Chrome extension and paste these steps._",
                "tokens_in": llm_response["tokens_in"],
                "tokens_out": llm_response["tokens_out"],
                "cost": 0.0,
                "tool": "claude-in-chrome",
                "model": "local-qwen (step generation)"
            }
        except Exception as e:
            return {
                "response": f"**Browser Automation Error**\n\n{str(e)}",
                "tokens_in": 0,
                "tokens_out": 0,
                "cost": 0.0,
                "tool": "claude-in-chrome",
                "model": "local-qwen"
            }

    def _delegate_to_supabase(self, query: str) -> dict:
        """
        Delegate database operations to Supabase.
        Placeholder for MCP integration.
        """
        self._log("Supabase delegation (placeholder)")

        # Generate SQL using local model
        sql_response = self._delegate_to_local(
            f"Generate SQL query for: {query}",
            model="qwen"
        )

        return {
            "response": f"**Database Operation Request**\n\n"
                       f"Generated SQL:\n```sql\n{sql_response['response']}\n```\n\n"
                       f"_Note: Supabase MCP integration pending. "
                       f"Enable in tools_config.json after setup._",
            "tokens_in": sql_response["tokens_in"],
            "tokens_out": sql_response["tokens_out"],
            "cost": 0.0,
            "tool": "supabase",
            "model": "local-qwen (sql generation)"
        }

    # =========================================================================
    # KNOWLEDGE BASE
    # =========================================================================

    def search_knowledge_base(self, query: str) -> list[dict]:
        """Search knowledge base for relevant context."""
        results = []
        query_terms = query.lower().split()

        for md_file in KNOWLEDGE_BASE_PATH.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                content_lower = content.lower()

                matches = sum(1 for term in query_terms if term in content_lower)
                if matches > 0:
                    lines = content.split("\n")
                    snippet_lines = []
                    for line in lines:
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

        results.sort(key=lambda x: x["matches"], reverse=True)
        return results[:5]

    # =========================================================================
    # LOGGING & TRACKING
    # =========================================================================

    def _load_usage_log(self) -> dict:
        """Load usage log from JSON."""
        with open(USAGE_LOG_PATH, "r") as f:
            return json.load(f)

    def _save_usage_log(self, log: dict) -> None:
        """Save usage log to JSON."""
        with open(USAGE_LOG_PATH, "w") as f:
            json.dump(log, f, indent=2)

    def _update_usage(self, result: dict, category: str) -> None:
        """Update usage statistics with new query result."""
        log = self._load_usage_log()
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")

        tool = result.get("tool", "unknown")
        model = result.get("model", "unknown")

        # Update summary
        log["summary"]["total_queries"] += 1
        log["summary"]["total_cost_usd"] += result["cost"]

        # Update by-tool stats
        if "by_tool" not in log["summary"]:
            log["summary"]["by_tool"] = {}
        if tool not in log["summary"]["by_tool"]:
            log["summary"]["by_tool"][tool] = {
                "queries": 0, "cost_usd": 0.0, "tokens_in": 0, "tokens_out": 0
            }
        log["summary"]["by_tool"][tool]["queries"] += 1
        log["summary"]["by_tool"][tool]["cost_usd"] += result["cost"]
        log["summary"]["by_tool"][tool]["tokens_in"] += result["tokens_in"]
        log["summary"]["by_tool"][tool]["tokens_out"] += result["tokens_out"]

        # Update daily stats
        if today not in log["summary"]["daily"]:
            log["summary"]["daily"][today] = {"queries": 0, "cost_usd": 0.0}
        log["summary"]["daily"][today]["queries"] += 1
        log["summary"]["daily"][today]["cost_usd"] += result["cost"]

        # Update monthly stats
        if month not in log["summary"]["monthly"]:
            log["summary"]["monthly"][month] = {"queries": 0, "cost_usd": 0.0}
        log["summary"]["monthly"][month]["queries"] += 1
        log["summary"]["monthly"][month]["cost_usd"] += result["cost"]

        # Add to history with enhanced schema
        log["history"].append({
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "model": model,
            "tokens_in": result["tokens_in"],
            "tokens_out": result["tokens_out"],
            "cost_usd": result["cost"],
            "task_category": category
        })

        # Keep only last 1000 entries
        if len(log["history"]) > 1000:
            log["history"] = log["history"][-1000:]

        self._save_usage_log(log)

    def _log_conversation(self, query: str, response: str, tool: str, model: str) -> None:
        """Append to conversation log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"""
---
## [{timestamp}] via {tool} ({model})

**Query:** {query}

**Response:**
{response[:500]}{'...' if len(response) > 500 else ''}

"""
        with open(CONVERSATION_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)

    # =========================================================================
    # MAIN PROCESSING
    # =========================================================================

    def process(self, query: str, force_tool: Optional[str] = None) -> str:
        """
        Main processing pipeline:
        1. Analyze task
        2. Search knowledge base for context
        3. Delegate to optimal tool
        4. Log and track
        5. Return response
        """
        # Step 1: Analyze task
        analysis = self._analyze_task(query)
        self._log(f"Analysis: category={analysis['category']}, "
                  f"complexity={analysis['complexity']}, "
                  f"recommended={analysis['recommended_tool']}")

        # Step 2: Check knowledge base
        kb_results = self.search_knowledge_base(query)
        kb_context = ""
        if kb_results:
            kb_context = "\n\nRelevant context from knowledge base:\n"
            for r in kb_results[:2]:
                kb_context += f"- {r['file']}: {r['snippet'][:100]}...\n"

        enhanced_query = query + kb_context if kb_context else query

        # Step 3: Select tool (forced or recommended)
        tool = force_tool or analysis["recommended_tool"]
        self._log(f"Using tool: {tool}")

        # Step 4: Delegate
        try:
            if tool == "local-deepseek":
                result = self._delegate_to_local(enhanced_query, "deepseek")
            elif tool == "local-qwen":
                result = self._delegate_to_local(enhanced_query, "qwen")
            elif tool == "perplexity":
                result = self._delegate_to_perplexity(enhanced_query)
            elif tool == "claude":
                result = self._delegate_to_claude(enhanced_query)
            elif tool == "comfyui":
                result = self._delegate_to_comfyui(query)
            elif tool == "comfyui-video":
                result = self._delegate_to_comfyui_video(query)
            elif tool == "comfyui-video-talking-head":
                result = self._delegate_to_comfyui_talking_head(query)
            elif tool == "github":
                result = self._delegate_to_github(query)
            elif tool == "claude-in-chrome":
                result = self._delegate_to_browser(query)
            elif tool == "supabase":
                result = self._delegate_to_supabase(query)
            else:
                # Default to local deepseek
                result = self._delegate_to_local(enhanced_query, "deepseek")
        except (ConnectionError, ValueError) as e:
            # Fallback chain: perplexity → qwen → deepseek
            self._log(f"Error with {tool}: {e}. Attempting fallback...")
            if tool in ["claude", "perplexity"]:
                result = self._delegate_to_local(enhanced_query, "qwen")
            elif tool == "local-qwen":
                result = self._delegate_to_local(enhanced_query, "deepseek")
            else:
                raise

        # Step 5: Log everything
        self._update_usage(result, analysis["category"])
        self._log_conversation(query, result["response"], result["tool"], result["model"])

        self._log(f"Tokens: {result['tokens_in']} in / {result['tokens_out']} out | "
                  f"Cost: ${result['cost']:.4f}")

        return result["response"]

    # =========================================================================
    # STATS & INFO
    # =========================================================================

    def show_stats(self) -> None:
        """Display usage statistics."""
        log = self._load_usage_log()
        summary = log["summary"]

        print("\n" + "=" * 60)
        print("AUTOMATION MACHINE - USAGE STATISTICS")
        print("=" * 60)

        print(f"\nTotal Queries: {summary['total_queries']}")
        print(f"Total Cost: ${summary['total_cost_usd']:.4f}")

        # By tool breakdown
        if summary.get("by_tool"):
            print("\n--- By Tool ---")
            for tool, stats in summary["by_tool"].items():
                print(f"\n{tool}:")
                print(f"  Queries: {stats['queries']}")
                print(f"  Tokens: {stats['tokens_in']:,} in / {stats['tokens_out']:,} out")
                print(f"  Cost: ${stats['cost_usd']:.4f}")

        # Legacy model stats (for backwards compatibility)
        if summary.get("models"):
            print("\n--- By Model (Legacy) ---")
            for model, stats in summary["models"].items():
                if stats["queries"] > 0:
                    print(f"\n{model}:")
                    print(f"  Queries: {stats['queries']}")
                    print(f"  Cost: ${stats['cost_usd']:.4f}")

        # Recent daily
        if summary.get("daily"):
            print("\n--- Recent Daily Usage ---")
            recent = sorted(summary["daily"].keys())[-7:]
            for day in recent:
                s = summary["daily"][day]
                print(f"  {day}: {s['queries']} queries, ${s['cost_usd']:.4f}")

        print("\n" + "=" * 60)

    def show_tools(self) -> None:
        """Display available tools and their status."""
        print("\n" + "=" * 60)
        print("AUTOMATION MACHINE - AVAILABLE TOOLS")
        print("=" * 60)

        # Local models
        print("\n--- Local Models (Free) ---")
        print("  deepseek-r1:latest    [ACTIVE] Fast reasoning")
        print("  qwen2.5:32b           [ACTIVE] Powerful code/analysis")

        # Video generation
        print("\n--- Video Generation (Free via ComfyUI) ---")
        print("  comfyui-video         [ACTIVE] Image-to-video (Wan2.1, AnimateDiff)")
        print("  comfyui-video-talking-head [ACTIVE] Talking heads (SadTalker)")

        # External tools
        print("\n--- External Integrations ---")
        for tool_name, config in self.tools_config.items():
            status = "ENABLED" if config.get("enabled") else "DISABLED"
            note = config.get("note", "")
            print(f"  {tool_name:20} [{status}] {note}")

        # Cloud fallback
        print("\n--- Cloud Fallback ---")
        print("  claude-sonnet-4       [ACTIVE] Complex tasks (paid)")

        print("\n" + "=" * 60)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Automation Machine Brain - Full Orchestration System"
    )
    parser.add_argument("query", nargs="?", help="Query to process")
    parser.add_argument("--stats", action="store_true", help="Show usage statistics")
    parser.add_argument("--tools", action="store_true", help="Show available tools")
    parser.add_argument("--tool", choices=[
        "local-deepseek", "local-qwen", "perplexity", "claude",
        "comfyui", "comfyui-video", "comfyui-video-talking-head",
        "github", "supabase", "claude-in-chrome"
    ], help="Force specific tool")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show routing decisions")

    args = parser.parse_args()

    brain = AutomationBrain(verbose=args.verbose)

    if args.stats:
        brain.show_stats()
        return

    if args.tools:
        brain.show_tools()
        return

    if not args.query:
        # Interactive mode
        print("Automation Machine Brain - Interactive Mode")
        print("Commands: 'quit', 'stats', 'tools'")
        print("-" * 40)

        while True:
            try:
                query = input("\n> ").strip()
                if not query:
                    continue
                if query.lower() == "quit":
                    break
                if query.lower() == "stats":
                    brain.show_stats()
                    continue
                if query.lower() == "tools":
                    brain.show_tools()
                    continue

                response = brain.process(query, args.tool)
                print(f"\n{response}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        try:
            response = brain.process(args.query, args.tool)
            print(response)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
