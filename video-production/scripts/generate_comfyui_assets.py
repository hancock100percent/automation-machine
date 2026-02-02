"""
Stage 2: Generate ComfyUI Assets
Uploads files to The Machine via SCP, submits video generation jobs
via ComfyUI API, polls for completion, and downloads results.

Usage:
    python video-production/scripts/generate_comfyui_assets.py                 # generate all assets
    python video-production/scripts/generate_comfyui_assets.py --sadtalker     # SadTalker jobs only
    python video-production/scripts/generate_comfyui_assets.py --fantasy       # FantasyTalking jobs (replaces SadTalker)
    python video-production/scripts/generate_comfyui_assets.py --i2v           # Wan2.1 I2V jobs only
    python video-production/scripts/generate_comfyui_assets.py --i2v-wan22     # Wan2.2 I2V jobs (higher quality)
    python video-production/scripts/generate_comfyui_assets.py --test          # Test mode (49 frames, faster)
    python video-production/scripts/generate_comfyui_assets.py --status        # check running jobs
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMFYUI_ENDPOINT = "http://100.64.130.71:8188"
THE_MACHINE_USER = "michael"
THE_MACHINE_HOST = "100.64.130.71"
COMFYUI_INPUT_DIR = "C:/ComfyUI/input"  # Remote path on The Machine

# Local paths
PHOTOS_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "photos")
AUDIO_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "audio")
SAMPLE_IMAGES_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "sample-images")
OUTPUT_I2V_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "i2v")
OUTPUT_SADTALKER_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "sadtalker")

# Workflow templates
I2V_WORKFLOW = os.path.join(REPO_ROOT, "workflows", "image_to_video.json")

# Poll settings
POLL_INTERVAL = 30  # seconds
POLL_TIMEOUT = 3600  # 1 hour max per job


def api_request(path, method="GET", data=None):
    """Make HTTP request to ComfyUI API."""
    url = f"{COMFYUI_ENDPOINT}{path}"
    headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"  API error ({path}): {e}")
        return None
    except Exception as e:
        print(f"  API exception ({path}): {e}")
        return None


def upload_file_to_comfyui(local_path, subfolder="", file_type="input"):
    """Upload a file to ComfyUI via its upload API."""
    filename = os.path.basename(local_path)
    url = f"{COMFYUI_ENDPOINT}/upload/image"

    # Build multipart form data manually
    boundary = f"----PythonBoundary{random.randint(100000, 999999)}"
    body_parts = []

    # File part
    with open(local_path, "rb") as f:
        file_data = f.read()

    body_parts.append(f"--{boundary}\r\n".encode())
    body_parts.append(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode())
    body_parts.append(b"Content-Type: application/octet-stream\r\n\r\n")
    body_parts.append(file_data)
    body_parts.append(b"\r\n")

    # Subfolder part
    if subfolder:
        body_parts.append(f"--{boundary}\r\n".encode())
        body_parts.append(b'Content-Disposition: form-data; name="subfolder"\r\n\r\n')
        body_parts.append(subfolder.encode())
        body_parts.append(b"\r\n")

    # Type part
    body_parts.append(f"--{boundary}\r\n".encode())
    body_parts.append(b'Content-Disposition: form-data; name="type"\r\n\r\n')
    body_parts.append(file_type.encode())
    body_parts.append(b"\r\n")

    # Overwrite part
    body_parts.append(f"--{boundary}\r\n".encode())
    body_parts.append(b'Content-Disposition: form-data; name="overwrite"\r\n\r\n')
    body_parts.append(b"true")
    body_parts.append(b"\r\n")

    body_parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(body_parts)

    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            print(f"  Uploaded: {filename}")
            return result
    except Exception as e:
        print(f"  Upload failed for {filename}: {e}")
        return None


def scp_to_machine(local_path, remote_path):
    """SCP a file to The Machine."""
    remote_target = f"{THE_MACHINE_USER}@{THE_MACHINE_HOST}:{remote_path}"
    cmd = ["scp", "-o", "ConnectTimeout=10", local_path, remote_target]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"  SCP: {os.path.basename(local_path)} → {remote_path}")
            return True
        else:
            print(f"  SCP failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  SCP error: {e}")
        return False


def submit_prompt(prompt_data):
    """Submit a workflow prompt to ComfyUI."""
    result = api_request("/prompt", method="POST", data={"prompt": prompt_data})
    if result and "prompt_id" in result:
        return result["prompt_id"]
    return None


def poll_for_completion(prompt_id):
    """Poll ComfyUI history until job completes or times out."""
    start = time.time()
    while time.time() - start < POLL_TIMEOUT:
        history = api_request(f"/history/{prompt_id}")
        if history and prompt_id in history:
            job = history[prompt_id]
            status = job.get("status", {})
            if status.get("completed", False) or status.get("status_str") == "success":
                return job
            messages = status.get("messages", [])
            for msg in messages:
                if isinstance(msg, list) and len(msg) >= 2:
                    if msg[0] == "execution_error":
                        print(f"  Job failed: {msg[1].get('exception_message', 'unknown error')}")
                        return None
        elapsed = int(time.time() - start)
        print(f"  Polling... ({elapsed}s elapsed)", end="\r")
        time.sleep(POLL_INTERVAL)

    print(f"\n  Timed out after {POLL_TIMEOUT}s")
    return None


def download_output(prompt_id, job_data, output_dir):
    """Download output files from a completed job."""
    outputs = job_data.get("outputs", {})
    downloaded = []
    for node_id, node_output in outputs.items():
        # Check for video outputs (VHS_VideoCombine)
        gifs = node_output.get("gifs", [])
        for item in gifs:
            filename = item.get("filename", "")
            subfolder = item.get("subfolder", "")
            file_type = item.get("type", "output")
            if filename:
                url = f"{COMFYUI_ENDPOINT}/view?filename={urllib.parse.quote(filename)}"
                if subfolder:
                    url += f"&subfolder={urllib.parse.quote(subfolder)}"
                url += f"&type={file_type}"
                local = os.path.join(output_dir, filename)
                try:
                    urllib.request.urlretrieve(url, local)
                    print(f"  Downloaded: {filename}")
                    downloaded.append(local)
                except Exception as e:
                    print(f"  Download failed ({filename}): {e}")

        # Check for image outputs
        images = node_output.get("images", [])
        for item in images:
            filename = item.get("filename", "")
            subfolder = item.get("subfolder", "")
            file_type = item.get("type", "output")
            if filename:
                url = f"{COMFYUI_ENDPOINT}/view?filename={urllib.parse.quote(filename)}"
                if subfolder:
                    url += f"&subfolder={urllib.parse.quote(subfolder)}"
                url += f"&type={file_type}"
                local = os.path.join(output_dir, filename)
                try:
                    urllib.request.urlretrieve(url, local)
                    print(f"  Downloaded: {filename}")
                    downloaded.append(local)
                except Exception as e:
                    print(f"  Download failed ({filename}): {e}")

    return downloaded


# ─── SadTalker Jobs ──────────────────────────────────────────

SADTALKER_JOBS = [
    {
        "name": "v1_intro_avatar",
        "photo": "avatar_photo.jpg",
        "audio": "v1_intro.wav",
        "description": "Video 1 intro talking head (~8s)",
    },
    {
        "name": "v1_outro_avatar",
        "photo": "avatar_photo.jpg",
        "audio": "v1_outro.wav",
        "description": "Video 1 CTA talking head (~15s)",
    },
    {
        "name": "v2_cta_avatar",
        "photo": "avatar_photo.jpg",
        "audio": "v2_cta.wav",
        "description": "Video 2 CTA talking head (~10s)",
    },
    {
        "name": "v3_intro_avatar",
        "photo": "avatar_photo.jpg",
        "audio": "v3_intro.wav",
        "description": "Video 3 intro talking head (~5s)",
    },
]


def build_sadtalker_prompt(photo_filename, audio_filename):
    """Build SadTalker ComfyUI prompt (based on temp_sadtalker_test.ps1 pattern)."""
    return {
        "1": {
            "inputs": {
                "image": photo_filename,
                "upload": "image"
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Load Face Image"}
        },
        "2": {
            "inputs": {
                "audio": audio_filename,
                "upload": None
            },
            "class_type": "ShowAudio",
            "_meta": {"title": "Load Audio"}
        },
        "3": {
            "inputs": {
                "image": ["1", 0],
                "audio": ["2", 0],
                "poseStyle": 0,
                "faceModelResolution": "256",
                "preprocess": "crop",
                "stillMode": False,
                "batchSizeInGeneration": 2,
                "gfpganAsFaceEnhancer": True,
                "useIdleMode": False,
                "idleModeTime": 5,
                "useRefVideo": False,
                "refInfo": "pose"
            },
            "class_type": "SadTalker",
            "_meta": {"title": "SadTalker Generate"}
        },
        "4": {
            "inputs": {
                "text": ["3", 0]
            },
            "class_type": "ShowText",
            "_meta": {"title": "Show Video Path"}
        }
    }


def run_sadtalker_jobs():
    """Run all SadTalker jobs sequentially."""
    print("\n--- SadTalker Jobs ---\n")
    os.makedirs(OUTPUT_SADTALKER_DIR, exist_ok=True)

    for job in SADTALKER_JOBS:
        print(f"\nJob: {job['name']} -- {job['description']}")

        photo_path = os.path.join(PHOTOS_DIR, job["photo"])
        audio_path = os.path.join(AUDIO_DIR, job["audio"])

        if not os.path.isfile(photo_path):
            print(f"  [SKIP] Photo not found: {job['photo']}")
            continue
        if not os.path.isfile(audio_path):
            print(f"  [SKIP] Audio not found: {job['audio']}")
            continue

        # Upload files to ComfyUI
        print("  Uploading files...")
        photo_result = upload_file_to_comfyui(photo_path)
        audio_result = upload_file_to_comfyui(audio_path)
        if not photo_result or not audio_result:
            print("  [FAIL] Upload failed, skipping job")
            continue

        # Submit prompt
        prompt = build_sadtalker_prompt(job["photo"], job["audio"])
        print("  Submitting to ComfyUI...")
        prompt_id = submit_prompt(prompt)
        if not prompt_id:
            print("  [FAIL] Could not submit prompt")
            continue
        print(f"  Prompt ID: {prompt_id}")

        # Poll for completion
        print("  Waiting for generation...")
        job_data = poll_for_completion(prompt_id)
        if not job_data:
            print("  [FAIL] Job did not complete")
            continue

        # Download results
        print("  Downloading output...")
        files = download_output(prompt_id, job_data, OUTPUT_SADTALKER_DIR)
        if files:
            print(f"  [OK] {job['name']}: {len(files)} file(s) downloaded")
        else:
            # SadTalker may output path as text -- check outputs
            outputs = job_data.get("outputs", {})
            for node_id, node_output in outputs.items():
                texts = node_output.get("text", [])
                if texts:
                    print(f"  Output path: {texts}")
                    # Try to SCP the file from The Machine
                    for text_path in texts:
                        if isinstance(text_path, str) and text_path.strip():
                            remote = text_path.strip()
                            local = os.path.join(OUTPUT_SADTALKER_DIR, f"{job['name']}.mp4")
                            print(f"  Attempting SCP from: {remote}")
                            scp_to_machine_download(remote, local)

    print("\n  SadTalker jobs complete.")


def scp_to_machine_download(remote_path, local_path):
    """SCP a file FROM The Machine."""
    remote_target = f"{THE_MACHINE_USER}@{THE_MACHINE_HOST}:{remote_path}"
    cmd = ["scp", "-o", "ConnectTimeout=10", remote_target, local_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"  Downloaded via SCP: {os.path.basename(local_path)}")
            return True
        else:
            print(f"  SCP download failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  SCP download error: {e}")
        return False


# ─── Wan2.1 I2V Jobs ────────────────────────────────────────

def find_i2v_source_images():
    """Find images to animate from sample-images and output directories."""
    images = []
    search_dirs = [
        SAMPLE_IMAGES_DIR,
        os.path.join(REPO_ROOT, "output"),
    ]
    image_exts = {".png", ".jpg", ".jpeg", ".webp"}
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            ext = os.path.splitext(f)[1].lower()
            if ext in image_exts:
                images.append(os.path.join(d, f))
    return images


DEFAULT_MOTION_PROMPT = (
    "Realistic 4K cinematic video of a luxury artisan candle with a gently flickering warm flame. "
    "The flame dances softly with natural randomness, casting warm golden light across the wax surface. "
    "Soft ambient shadows shift slowly on the background wall. Shallow depth of field with the candle "
    "in sharp focus. Subtle warm light rays emanate from the flame. The camera holds steady with an "
    "extremely slow, barely perceptible dolly-in. Warm color temperature, cozy atmosphere, no rapid "
    "movement, photorealistic quality."
)

DEFAULT_NEGATIVE_PROMPT = (
    "static, frozen, no movement, blurry, jittery, distorted, morphing, warped hands, warped fingers, "
    "glitching, flicker, fast motion, unnatural movement, frame skipping, ghosting, double exposure, "
    "low quality, watermark, text overlay, compressed artifacts"
)


def build_i2v_prompt(image_filename, motion_prompt=None, test_mode=False):
    """Build Wan2.1 I2V prompt from workflow template.

    Args:
        image_filename: Name of the uploaded image file.
        motion_prompt: Custom positive prompt. Uses DEFAULT_MOTION_PROMPT if None.
        test_mode: If True, use 49 frames instead of 81 (saves ~17 min per clip).
    """
    with open(I2V_WORKFLOW, "r") as f:
        workflow = json.load(f)

    # Remove metadata key
    prompt = {k: v for k, v in workflow.items() if k != "_meta"}

    # Set the input image
    prompt["5"]["inputs"]["image"] = image_filename

    # Set the motion prompt (expanded 80-120 word prompts for realism)
    prompt["6"]["inputs"]["text"] = motion_prompt or DEFAULT_MOTION_PROMPT

    # Set negative prompt
    prompt["7"]["inputs"]["text"] = DEFAULT_NEGATIVE_PROMPT

    # Use 49 frames for test iterations (saves ~17 min), 81 for production
    if test_mode:
        prompt["9"]["inputs"]["length"] = 49

    # Randomize seed for variety
    prompt["10"]["inputs"]["seed"] = random.randint(1, 2**31)

    return prompt


def run_i2v_jobs(max_jobs=3, test_mode=False):
    """Run Wan2.1 I2V jobs for candle images.

    Args:
        max_jobs: Maximum number of images to process.
        test_mode: If True, use 49 frames (~25 min) instead of 81 (~42 min).
    """
    mode_label = "TEST (49 frames)" if test_mode else "PRODUCTION (81 frames)"
    print(f"\n--- Wan2.1 Image-to-Video Jobs [{mode_label}] ---\n")
    os.makedirs(OUTPUT_I2V_DIR, exist_ok=True)

    source_images = find_i2v_source_images()
    if not source_images:
        print("  No source images found for I2V.")
        print(f"  Place images in: {os.path.relpath(SAMPLE_IMAGES_DIR, REPO_ROOT)}")
        return

    print(f"  Found {len(source_images)} source images, will process up to {max_jobs}:")
    for img in source_images[:max_jobs]:
        print(f"    {os.path.relpath(img, REPO_ROOT)}")

    motion_prompts = [
        (
            "Realistic 4K cinematic video of a luxury artisan candle with a gently flickering warm flame. "
            "The flame dances softly with natural randomness, casting warm golden light across the wax surface. "
            "Soft ambient shadows shift slowly on the background wall. Shallow depth of field with the candle "
            "in sharp focus. Subtle warm light rays emanate from the flame. The camera holds steady with an "
            "extremely slow, barely perceptible dolly-in. Warm color temperature, cozy atmosphere, no rapid "
            "movement, photorealistic quality."
        ),
        (
            "Cinematic close-up of a handcrafted candle burning with a smooth, steady flame. The warm "
            "golden light gently illuminates the textured wax surface, revealing subtle details. Tiny wisps "
            "of heat shimmer rise from the flame tip. Background softly blurred with warm bokeh. Ambient "
            "shadows drift lazily across a wooden surface. Very slow camera push-in, almost imperceptible. "
            "Natural color grading, warm tones, shallow depth of field, professional product video quality."
        ),
        (
            "Elegant product video of a scented candle with a delicate dancing flame. The fire moves with "
            "gentle organic randomness, creating soft flickering highlights on the glass jar. Warm ambient "
            "light fills the scene with a cozy golden glow. Subtle shadow play on the background surface. "
            "Camera holds perfectly still with smooth, gentle exposure breathing. Shallow focus, creamy "
            "bokeh in background. Premium commercial aesthetic, warm color palette, no camera shake."
        ),
    ]

    for i, img_path in enumerate(source_images[:max_jobs]):
        img_name = os.path.basename(img_path)
        prompt_text = motion_prompts[i % len(motion_prompts)]
        print(f"\nJob {i+1}: {img_name}")
        print(f"  Motion: {prompt_text[:60]}...")

        # Upload image to ComfyUI
        print("  Uploading image...")
        result = upload_file_to_comfyui(img_path)
        if not result:
            print("  [FAIL] Upload failed")
            continue

        # Submit prompt
        prompt = build_i2v_prompt(img_name, prompt_text, test_mode=test_mode)
        print("  Submitting to ComfyUI...")
        prompt_id = submit_prompt(prompt)
        if not prompt_id:
            print("  [FAIL] Could not submit prompt")
            continue
        print(f"  Prompt ID: {prompt_id}")
        time_est = "~25 min (49 frames)" if test_mode else "~42 min (81 frames)"
        print(f"  NOTE: Wan2.1 I2V takes {time_est} per clip on RTX 5060 Ti")

        # Poll for completion
        print("  Waiting for generation...")
        job_data = poll_for_completion(prompt_id)
        if not job_data:
            print("  [FAIL] Job did not complete")
            continue

        # Download results
        print("  Downloading output...")
        files = download_output(prompt_id, job_data, OUTPUT_I2V_DIR)
        if files:
            print(f"  [OK] I2V job {i+1}: {len(files)} file(s)")
        else:
            print("  [WARN] No files downloaded -- check ComfyUI output directory")


# ─── FantasyTalking Jobs ─────────────────────────────────────

FANTASYTALKING_WORKFLOW = os.path.join(REPO_ROOT, "workflows", "talking_head_fantasy.json")
OUTPUT_FANTASYTALKING_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "fantasytalking")

FANTASYTALKING_JOBS = [
    {
        "name": "v1_intro_avatar",
        "photo": "avatar_photo.jpg",
        "audio": "v1_intro.wav",
        "description": "Video 1 intro talking head (~8s)",
    },
    {
        "name": "v1_outro_avatar",
        "photo": "avatar_photo.jpg",
        "audio": "v1_outro.wav",
        "description": "Video 1 CTA talking head (~15s)",
    },
    {
        "name": "v2_cta_avatar",
        "photo": "avatar_photo.jpg",
        "audio": "v2_cta.wav",
        "description": "Video 2 CTA talking head (~10s)",
    },
    {
        "name": "v3_intro_avatar",
        "photo": "avatar_photo.jpg",
        "audio": "v3_intro.wav",
        "description": "Video 3 intro talking head (~5s)",
    },
]


def build_fantasytalking_prompt(photo_filename, audio_filename):
    """Build FantasyTalking ComfyUI prompt from workflow template.

    The workflow uses WanVideoWrapper nodes:
    - Node 58 (LoadImage): face photo
    - Node 72 (LoadAudio): audio file
    - Node 69 (WanVideoSampler): has seed parameter
    """
    if not os.path.isfile(FANTASYTALKING_WORKFLOW):
        print(f"  [ERROR] FantasyTalking workflow not found: {FANTASYTALKING_WORKFLOW}")
        print("  Run Priority 1 setup first (install FantasyTalking node + create workflow)")
        return None

    with open(FANTASYTALKING_WORKFLOW, "r") as f:
        workflow = json.load(f)

    prompt = {k: v for k, v in workflow.items() if k != "_meta"}

    # Set input image (node 58 - LoadImage)
    prompt["58"]["inputs"]["image"] = photo_filename

    # Set input audio (node 72 - LoadAudio)
    prompt["72"]["inputs"]["audio"] = audio_filename

    # Randomize seed (node 69 - WanVideoSampler)
    prompt["69"]["inputs"]["seed"] = random.randint(1, 2**31)

    return prompt


def run_fantasytalking_jobs(test_mode=False):
    """Run FantasyTalking jobs (higher quality replacement for SadTalker)."""
    print("\n--- FantasyTalking Jobs ---\n")
    print("  NOTE: FantasyTalking uses Wan2.1 I2V backbone -- ~20-45 min per clip")
    if test_mode:
        print("  TEST MODE: Using reduced frame count for faster iteration")
    os.makedirs(OUTPUT_FANTASYTALKING_DIR, exist_ok=True)

    for job in FANTASYTALKING_JOBS:
        print(f"\nJob: {job['name']} -- {job['description']}")

        photo_path = os.path.join(PHOTOS_DIR, job["photo"])
        audio_path = os.path.join(AUDIO_DIR, job["audio"])

        if not os.path.isfile(photo_path):
            print(f"  [SKIP] Photo not found: {job['photo']}")
            continue
        if not os.path.isfile(audio_path):
            print(f"  [SKIP] Audio not found: {job['audio']}")
            continue

        # Upload files to ComfyUI
        print("  Uploading files...")
        photo_result = upload_file_to_comfyui(photo_path)
        audio_result = upload_file_to_comfyui(audio_path)
        if not photo_result or not audio_result:
            print("  [FAIL] Upload failed, skipping job")
            continue

        # Submit prompt
        prompt = build_fantasytalking_prompt(job["photo"], job["audio"])
        if not prompt:
            continue
        print("  Submitting to ComfyUI...")
        prompt_id = submit_prompt(prompt)
        if not prompt_id:
            print("  [FAIL] Could not submit prompt")
            continue
        print(f"  Prompt ID: {prompt_id}")

        # Poll for completion
        print("  Waiting for generation (this takes 20-45 min)...")
        job_data = poll_for_completion(prompt_id)
        if not job_data:
            print("  [FAIL] Job did not complete")
            continue

        # Download results
        print("  Downloading output...")
        files = download_output(prompt_id, job_data, OUTPUT_FANTASYTALKING_DIR)
        if files:
            print(f"  [OK] {job['name']}: {len(files)} file(s) downloaded")
        else:
            print("  [WARN] No files downloaded -- check ComfyUI output directory")

    print("\n  FantasyTalking jobs complete.")


# ─── Wan2.2 I2V Jobs ────────────────────────────────────────

I2V_WAN22_WORKFLOW = os.path.join(REPO_ROOT, "workflows", "image_to_video_wan22.json")
OUTPUT_I2V_WAN22_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "i2v-wan22")


def build_i2v_wan22_prompt(image_filename, motion_prompt=None, test_mode=False):
    """Build Wan2.2 I2V prompt from workflow template (GGUF models)."""
    if not os.path.isfile(I2V_WAN22_WORKFLOW):
        print(f"  [ERROR] Wan2.2 workflow not found: {I2V_WAN22_WORKFLOW}")
        print("  Run Priority 2 setup first (install ComfyUI-GGUF + download Wan2.2 models)")
        return None

    with open(I2V_WAN22_WORKFLOW, "r") as f:
        workflow = json.load(f)

    prompt = {k: v for k, v in workflow.items() if k != "_meta"}

    # Set input image
    for node_id, node in prompt.items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = image_filename

    # Set motion prompt
    for node_id, node in prompt.items():
        if node.get("class_type") == "CLIPTextEncode":
            title = node.get("_meta", {}).get("title", "")
            if "Positive" in title or "Motion" in title:
                node["inputs"]["text"] = motion_prompt or DEFAULT_MOTION_PROMPT
            elif "Negative" in title:
                node["inputs"]["text"] = DEFAULT_NEGATIVE_PROMPT

    # Randomize seed, optionally reduce frames
    for node_id, node in prompt.items():
        if node.get("class_type") == "KSampler":
            node["inputs"]["seed"] = random.randint(1, 2**31)
        if test_mode and node.get("class_type") == "WanImageToVideo":
            node["inputs"]["length"] = 49

    return prompt


def run_i2v_wan22_jobs(max_jobs=3, test_mode=False):
    """Run Wan2.2 I2V jobs (higher resolution, faster than Wan2.1)."""
    mode_label = "TEST" if test_mode else "PRODUCTION"
    print(f"\n--- Wan2.2 Image-to-Video Jobs [{mode_label}] ---\n")
    print("  NOTE: Wan2.2 GGUF runs at 1024x576 with ~7-15 min per clip")
    os.makedirs(OUTPUT_I2V_WAN22_DIR, exist_ok=True)

    source_images = find_i2v_source_images()
    if not source_images:
        print("  No source images found for I2V.")
        print(f"  Place images in: {os.path.relpath(SAMPLE_IMAGES_DIR, REPO_ROOT)}")
        return

    print(f"  Found {len(source_images)} source images, will process up to {max_jobs}:")
    for img in source_images[:max_jobs]:
        print(f"    {os.path.relpath(img, REPO_ROOT)}")

    # Reuse the same expanded motion prompts
    motion_prompts = [DEFAULT_MOTION_PROMPT] * max_jobs

    for i, img_path in enumerate(source_images[:max_jobs]):
        img_name = os.path.basename(img_path)
        prompt_text = motion_prompts[i % len(motion_prompts)]
        print(f"\nJob {i+1}: {img_name}")

        # Upload image to ComfyUI
        print("  Uploading image...")
        result = upload_file_to_comfyui(img_path)
        if not result:
            print("  [FAIL] Upload failed")
            continue

        # Submit prompt
        prompt = build_i2v_wan22_prompt(img_name, prompt_text, test_mode=test_mode)
        if not prompt:
            continue
        print("  Submitting to ComfyUI...")
        prompt_id = submit_prompt(prompt)
        if not prompt_id:
            print("  [FAIL] Could not submit prompt")
            continue
        print(f"  Prompt ID: {prompt_id}")

        # Poll for completion
        print("  Waiting for generation...")
        job_data = poll_for_completion(prompt_id)
        if not job_data:
            print("  [FAIL] Job did not complete")
            continue

        # Download results
        print("  Downloading output...")
        files = download_output(prompt_id, job_data, OUTPUT_I2V_WAN22_DIR)
        if files:
            print(f"  [OK] Wan2.2 I2V job {i+1}: {len(files)} file(s)")
        else:
            print("  [WARN] No files downloaded -- check ComfyUI output directory")


# ─── Status Check ───────────────────────────────────────────

def check_status():
    """Show current ComfyUI queue and recent history."""
    print("\n--- ComfyUI Status ---\n")

    # Queue
    queue = api_request("/queue")
    if queue:
        running = queue.get("queue_running", [])
        pending = queue.get("queue_pending", [])
        print(f"  Running: {len(running)} job(s)")
        print(f"  Pending: {len(pending)} job(s)")
    else:
        print("  Could not reach ComfyUI API")
        return

    # System stats
    stats = api_request("/system_stats")
    if stats:
        devices = stats.get("devices", [])
        if devices:
            gpu = devices[0]
            vram_total = gpu.get("vram_total", 0) / (1024**3)
            vram_free = gpu.get("vram_free", 0) / (1024**3)
            print(f"  GPU VRAM: {vram_free:.1f}GB free / {vram_total:.1f}GB total")

    # Check what assets we already have
    print("\n  Generated Assets:")
    for label, d in [
        ("SadTalker", OUTPUT_SADTALKER_DIR),
        ("FantasyTalking", OUTPUT_FANTASYTALKING_DIR),
        ("I2V (Wan2.1)", OUTPUT_I2V_DIR),
        ("I2V (Wan2.2)", OUTPUT_I2V_WAN22_DIR),
    ]:
        if os.path.isdir(d):
            files = [f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
            print(f"    {label}: {len(files)} file(s)")
            for f in files:
                size = os.path.getsize(os.path.join(d, f))
                print(f"      {f} ({size / (1024*1024):.1f}MB)")
        else:
            print(f"    {label}: directory not found")


def main():
    parser = argparse.ArgumentParser(description="Generate video assets via ComfyUI")
    parser.add_argument("--sadtalker", action="store_true", help="Run SadTalker jobs only")
    parser.add_argument("--fantasy", action="store_true", help="Run FantasyTalking jobs (replaces SadTalker)")
    parser.add_argument("--i2v", action="store_true", help="Run Wan2.1 I2V jobs only")
    parser.add_argument("--i2v-wan22", action="store_true", help="Run Wan2.2 I2V jobs (higher quality)")
    parser.add_argument("--status", action="store_true", help="Check ComfyUI status")
    parser.add_argument("--test", action="store_true", help="Test mode: 49 frames instead of 81 (saves ~17 min per clip)")
    parser.add_argument("--max-i2v", type=int, default=3, help="Max I2V jobs to run (default: 3)")
    args = parser.parse_args()

    print("=" * 60)
    print("  VIDEO PRODUCTION PIPELINE - Stage 2: Generate Assets")
    print("=" * 60)

    if args.status:
        check_status()
        return

    # Determine which jobs to run
    any_flag = args.sadtalker or args.fantasy or args.i2v or args.i2v_wan22
    run_st = args.sadtalker or (not any_flag)
    run_fantasy = args.fantasy
    run_i2v = args.i2v or (not any_flag)
    run_i2v_wan22 = args.i2v_wan22

    if run_st:
        run_sadtalker_jobs()
    if run_fantasy:
        run_fantasytalking_jobs(test_mode=args.test)
    if run_i2v:
        run_i2v_jobs(max_jobs=args.max_i2v, test_mode=args.test)
    if run_i2v_wan22:
        run_i2v_wan22_jobs(max_jobs=args.max_i2v, test_mode=args.test)

    print("\n" + "=" * 60)
    print("  Stage 2 complete. Run normalize_clips.py next.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
