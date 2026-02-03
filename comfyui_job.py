#!/usr/bin/env python3
"""
ComfyUI Long-Running Job Manager

Handles video generation jobs that can take 1+ hours.
Supports fire-and-forget submission with async status checking.

Usage:
    # Queue a job (returns immediately with job ID)
    python comfyui_job.py queue --workflow image_to_video_wan22 --image candle.png

    # Check job status
    python comfyui_job.py status <prompt_id>

    # Wait for job with progress (use in tmux!)
    python comfyui_job.py wait <prompt_id> --timeout 7200

    # List recent jobs
    python comfyui_job.py list
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# Paths
BASE_DIR = Path("C:/automation-machine")
WORKFLOWS_DIR = BASE_DIR / "workflows"
OUTPUT_DIR = BASE_DIR / "output"
JOBS_LOG = BASE_DIR / "comfyui_jobs.json"

# ComfyUI endpoint (The Machine via Tailscale)
COMFYUI_ENDPOINT = "http://100.64.130.71:8188"


def load_jobs_log() -> dict:
    """Load jobs tracking file."""
    if JOBS_LOG.exists():
        with open(JOBS_LOG, "r") as f:
            return json.load(f)
    return {"jobs": []}


def save_jobs_log(log: dict) -> None:
    """Save jobs tracking file."""
    with open(JOBS_LOG, "w") as f:
        json.dump(log, f, indent=2)


def queue_job(workflow_name: str, image_path: str = None, prompt_text: str = None) -> str:
    """
    Queue a job to ComfyUI and return immediately with the prompt_id.
    """
    # Load workflow
    workflow_file = WORKFLOWS_DIR / f"{workflow_name}.json"
    if not workflow_file.exists():
        print(f"ERROR: Workflow not found: {workflow_file}")
        print(f"Available workflows:")
        for wf in WORKFLOWS_DIR.glob("*.json"):
            print(f"  - {wf.stem}")
        sys.exit(1)

    with open(workflow_file, "r") as f:
        workflow = json.load(f)

    # Remove _meta from root (ComfyUI doesn't accept it)
    workflow.pop("_meta", None)

    # Inject image path if provided
    if image_path:
        # Find LoadImage node and update
        for node_id, node in workflow.items():
            if node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = image_path
                break

    # Inject prompt text if provided
    if prompt_text:
        # Find positive prompt node and update
        for node_id, node in workflow.items():
            if node.get("class_type") == "CLIPTextEncode":
                if "Positive" in node.get("_meta", {}).get("title", ""):
                    node["inputs"]["text"] = prompt_text
                    break

    # Randomize seed
    for node_id, node in workflow.items():
        if "seed" in node.get("inputs", {}):
            node["inputs"]["seed"] = int(time.time()) % (2**32)

    # Queue to ComfyUI
    import uuid
    client_id = str(uuid.uuid4())

    try:
        response = requests.post(
            f"{COMFYUI_ENDPOINT}/prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=30
        )
        response.raise_for_status()
        prompt_id = response.json().get("prompt_id")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to queue job: {e}")
        print(f"Is ComfyUI running at {COMFYUI_ENDPOINT}?")
        sys.exit(1)

    # Log the job
    log = load_jobs_log()
    log["jobs"].append({
        "prompt_id": prompt_id,
        "workflow": workflow_name,
        "image": image_path,
        "queued_at": datetime.now().isoformat(),
        "status": "queued"
    })
    # Keep only last 50 jobs
    log["jobs"] = log["jobs"][-50:]
    save_jobs_log(log)

    return prompt_id


def check_status(prompt_id: str) -> dict:
    """
    Check the status of a job by prompt_id.
    Returns dict with status and output info.
    """
    try:
        # Check history
        response = requests.get(
            f"{COMFYUI_ENDPOINT}/history/{prompt_id}",
            timeout=10
        )
        history = response.json()

        if prompt_id in history:
            job_data = history[prompt_id]
            outputs = job_data.get("outputs", {})

            # Check for video outputs
            videos = []
            for node_id, node_output in outputs.items():
                if "gifs" in node_output:
                    videos.extend(node_output["gifs"])
                if "videos" in node_output:
                    videos.extend(node_output["videos"])

            if videos:
                return {
                    "status": "completed",
                    "videos": videos,
                    "execution_time": job_data.get("status", {}).get("execution_time")
                }
            elif outputs:
                return {"status": "completed", "outputs": outputs}
            else:
                return {"status": "processing"}

        # Check queue
        queue_response = requests.get(f"{COMFYUI_ENDPOINT}/queue", timeout=10)
        queue_data = queue_response.json()

        # Check if in running queue
        running = queue_data.get("queue_running", [])
        for item in running:
            if item[1] == prompt_id:
                return {"status": "running", "position": 0}

        # Check if in pending queue
        pending = queue_data.get("queue_pending", [])
        for i, item in enumerate(pending):
            if item[1] == prompt_id:
                return {"status": "pending", "position": i + 1}

        return {"status": "unknown"}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def wait_for_job(prompt_id: str, timeout: int = 7200, poll_interval: int = 30) -> dict:
    """
    Wait for a job to complete with progress updates.
    Default timeout: 2 hours (7200 seconds)
    """
    print(f"Waiting for job {prompt_id}...")
    print(f"Timeout: {timeout}s ({timeout/60:.0f} min)")
    print(f"Poll interval: {poll_interval}s")
    print("-" * 50)

    start_time = time.time()
    last_status = None

    while True:
        elapsed = time.time() - start_time

        if elapsed > timeout:
            print(f"\nTIMEOUT after {elapsed/60:.1f} minutes")
            return {"status": "timeout", "elapsed": elapsed}

        status = check_status(prompt_id)
        current_status = status.get("status")

        # Print status update
        timestamp = datetime.now().strftime("%H:%M:%S")
        if current_status != last_status:
            print(f"[{timestamp}] Status: {current_status}")
            last_status = current_status
        else:
            # Progress dot
            print(".", end="", flush=True)

        if current_status == "completed":
            print(f"\n\nJOB COMPLETED in {elapsed/60:.1f} minutes!")

            # Download videos
            videos = status.get("videos", [])
            if videos:
                print(f"Videos generated: {len(videos)}")
                downloaded = download_outputs(videos)
                status["downloaded"] = downloaded

            # Update job log
            log = load_jobs_log()
            for job in log["jobs"]:
                if job["prompt_id"] == prompt_id:
                    job["status"] = "completed"
                    job["completed_at"] = datetime.now().isoformat()
                    job["elapsed_seconds"] = elapsed
                    break
            save_jobs_log(log)

            return status

        if current_status == "error":
            print(f"\nERROR: {status.get('message')}")
            return status

        time.sleep(poll_interval)


def download_outputs(videos: list) -> list:
    """Download video outputs from ComfyUI."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = []

    for vid_info in videos:
        filename = vid_info.get("filename", "output.mp4")
        subfolder = vid_info.get("subfolder", "")
        vid_type = vid_info.get("type", "output")

        try:
            url = f"{COMFYUI_ENDPOINT}/view?filename={filename}&subfolder={subfolder}&type={vid_type}"
            response = requests.get(url, timeout=120)
            response.raise_for_status()

            # Save with timestamp
            local_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            local_path = OUTPUT_DIR / local_filename

            with open(local_path, "wb") as f:
                f.write(response.content)

            print(f"  Downloaded: {local_path}")
            downloaded.append(str(local_path))

        except Exception as e:
            print(f"  Failed to download {filename}: {e}")

    return downloaded


def list_jobs(limit: int = 10) -> None:
    """List recent jobs."""
    log = load_jobs_log()
    jobs = log.get("jobs", [])[-limit:]

    print(f"\n{'='*60}")
    print("RECENT COMFYUI JOBS")
    print(f"{'='*60}\n")

    if not jobs:
        print("No jobs found.")
        return

    for job in reversed(jobs):
        prompt_id = job.get("prompt_id", "???")[:8]
        workflow = job.get("workflow", "unknown")
        status = job.get("status", "unknown")
        queued = job.get("queued_at", "???")[:19]
        elapsed = job.get("elapsed_seconds")

        elapsed_str = f" ({elapsed/60:.1f} min)" if elapsed else ""
        print(f"  {prompt_id}...  {workflow:30}  {status:10}  {queued}{elapsed_str}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="ComfyUI Long-Running Job Manager"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Queue command
    queue_parser = subparsers.add_parser("queue", help="Queue a new job")
    queue_parser.add_argument("--workflow", "-w", required=True,
                              help="Workflow name (without .json)")
    queue_parser.add_argument("--image", "-i", help="Input image path")
    queue_parser.add_argument("--prompt", "-p", help="Motion prompt text")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check job status")
    status_parser.add_argument("prompt_id", help="The prompt ID to check")

    # Wait command
    wait_parser = subparsers.add_parser("wait", help="Wait for job completion")
    wait_parser.add_argument("prompt_id", help="The prompt ID to wait for")
    wait_parser.add_argument("--timeout", "-t", type=int, default=7200,
                             help="Timeout in seconds (default: 7200 = 2 hours)")
    wait_parser.add_argument("--poll", type=int, default=30,
                             help="Poll interval in seconds (default: 30)")

    # List command
    list_parser = subparsers.add_parser("list", help="List recent jobs")
    list_parser.add_argument("--limit", "-n", type=int, default=10,
                             help="Number of jobs to show")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test GGUF speed")
    test_parser.add_argument("--image", "-i", help="Test image (optional)")

    args = parser.parse_args()

    if args.command == "queue":
        prompt_id = queue_job(args.workflow, args.image, args.prompt)
        print(f"\nJob queued successfully!")
        print(f"Prompt ID: {prompt_id}")
        print(f"\nTo wait for completion (run in tmux!):")
        print(f"  python comfyui_job.py wait {prompt_id}")
        print(f"\nTo check status:")
        print(f"  python comfyui_job.py status {prompt_id}")

    elif args.command == "status":
        status = check_status(args.prompt_id)
        print(f"\nJob Status: {status.get('status')}")
        if status.get("position"):
            print(f"Queue Position: {status['position']}")
        if status.get("videos"):
            print(f"Videos: {len(status['videos'])}")
        if status.get("execution_time"):
            print(f"Execution Time: {status['execution_time']:.1f}s")

    elif args.command == "wait":
        result = wait_for_job(args.prompt_id, args.timeout, args.poll)
        if result.get("downloaded"):
            print(f"\nOutput files:")
            for f in result["downloaded"]:
                print(f"  {f}")

    elif args.command == "list":
        list_jobs(args.limit)

    elif args.command == "test":
        print("\n" + "="*60)
        print("GGUF SPEED TEST")
        print("="*60)
        print("\nThis will test Wan2.1 I2V GGUF quantized model speed.")
        print("Expected: ~7-15 min (vs ~42 min for fp8)")
        print("\nRUN THIS IN TMUX to avoid timeout!")
        print("  tmux new -s gguf-test")
        print("="*60 + "\n")

        # Use a test image or default
        test_image = args.image or "C:/ComfyUI/input/candle_test.png"

        prompt_id = queue_job("image_to_video_wan22", test_image)
        print(f"\nTest job queued: {prompt_id}")
        print(f"\nWaiting for completion...")

        result = wait_for_job(prompt_id, timeout=7200, poll_interval=30)

        if result.get("status") == "completed":
            elapsed = result.get("elapsed", 0)
            print(f"\n{'='*60}")
            print(f"GGUF TEST COMPLETE")
            print(f"Time: {elapsed/60:.1f} minutes")
            if elapsed < 900:  # Under 15 min
                print("RESULT: FAST! GGUF speedup confirmed.")
            elif elapsed < 2700:  # Under 45 min
                print("RESULT: Moderate. Similar to fp8.")
            else:
                print("RESULT: Slow. May need optimization.")
            print(f"{'='*60}")


if __name__ == "__main__":
    main()
