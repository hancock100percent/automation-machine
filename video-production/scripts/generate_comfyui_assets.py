"""
Stage 2: Generate ComfyUI Assets
Uploads files to The Machine via SCP, submits video generation jobs
via ComfyUI API, polls for completion, and downloads results.

Usage:
    python video-production/scripts/generate_comfyui_assets.py                 # generate all (FantasyTalking + I2V)
    python video-production/scripts/generate_comfyui_assets.py --fantasy       # FantasyTalking talking head jobs only
    python video-production/scripts/generate_comfyui_assets.py --i2v           # Wan2.1 I2V jobs only
    python video-production/scripts/generate_comfyui_assets.py --i2v-wan22     # Wan2.2 I2V jobs (higher quality)
    python video-production/scripts/generate_comfyui_assets.py --sadtalker     # SadTalker jobs (legacy/deprecated)
    python video-production/scripts/generate_comfyui_assets.py --test          # Test mode (49 frames, faster)
    python video-production/scripts/generate_comfyui_assets.py --status        # check running jobs
"""

import argparse
import json
import math
import os
import random
import subprocess
import sys
import time
from datetime import datetime
import urllib.request
import urllib.error
import urllib.parse
import wave

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


# ─── State Management (Resume Support) ─────────────────────
# State file tracks which jobs/segments are complete so the script can
# resume after interruptions (Claude Code timeouts, SSH drops, etc.).
# Location: video-production/state/generation_progress.json

STATE_DIR = os.path.join(REPO_ROOT, "video-production", "state")
STATE_FILE = os.path.join(STATE_DIR, "generation_progress.json")


def load_state():
    """Load generation progress state from disk."""
    if os.path.isfile(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("  [WARN] Could not read state file, starting fresh")
    return {"last_run": None, "jobs": {}}


def save_state(state):
    """Save generation progress state to disk."""
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def update_job_state(state, job_name, **kwargs):
    """Update a specific job's state and persist to disk."""
    if job_name not in state["jobs"]:
        state["jobs"][job_name] = {
            "status": "pending",
            "job_type": None,
            "segments_total": 0,
            "segments_completed": [],
            "stitched": False,
            "output_path": None,
            "last_updated": None,
        }
    state["jobs"][job_name].update(kwargs)
    state["jobs"][job_name]["last_updated"] = datetime.now().isoformat()
    save_state(state)


def show_resume_status():
    """Display current generation progress from state file."""
    state = load_state()
    print("\n--- Generation Progress (Resume State) ---\n")
    if not state.get("last_run"):
        print("  No previous runs recorded.")
        print(f"  State file: {os.path.relpath(STATE_FILE, REPO_ROOT)}")
        return

    print(f"  Last run: {state['last_run']}")
    print(f"  State file: {os.path.relpath(STATE_FILE, REPO_ROOT)}")

    jobs = state.get("jobs", {})
    if not jobs:
        print("  No jobs tracked yet.")
        return

    print(f"\n  {'Job':<25} {'Status':<15} {'Segments':<15} {'Stitched':<10}")
    print(f"  {'-'*25} {'-'*15} {'-'*15} {'-'*10}")
    for name, info in jobs.items():
        status = info.get("status", "unknown")
        segs = info.get("segments_completed", [])
        total = info.get("segments_total", 0)
        stitched = "Yes" if info.get("stitched") else "No"
        seg_str = f"{len(segs)}/{total}" if total > 0 else "-"
        print(f"  {name:<25} {status:<15} {seg_str:<15} {stitched:<10}")

    # Show what would happen on next run
    print("\n  Next run will:")
    for name, info in jobs.items():
        if info.get("status") == "completed":
            print(f"    [SKIP] {name} (already completed)")
        elif info.get("status") in ("in_progress", "failed", "stitch_failed"):
            segs = info.get("segments_completed", [])
            total = info.get("segments_total", 0)
            remaining = total - len(segs)
            if remaining > 0:
                print(f"    [RESUME] {name} ({remaining} segments remaining)")
            elif not info.get("stitched"):
                print(f"    [STITCH] {name} (all segments done, needs stitching)")
            else:
                print(f"    [RETRY] {name}")

    # Check for jobs not yet tracked
    for job in FANTASYTALKING_JOBS:
        if job["name"] not in jobs:
            print(f"    [NEW] {job['name']} (not started)")


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

    # Resume: skip jobs if we already have enough output clips
    existing_clips = sorted([f for f in os.listdir(OUTPUT_I2V_DIR) if f.lower().endswith('.mp4')])
    if len(existing_clips) >= max_jobs:
        print(f"  [RESUME-SKIP] Already have {len(existing_clips)} clips (target: {max_jobs})")
        return
    elif existing_clips:
        skip = len(existing_clips)
        print(f"  [RESUME] Found {skip} existing clips, skipping first {skip} of {max_jobs} jobs")
        source_images = source_images[skip:]
        max_jobs -= skip

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


# ─── Audio Segmentation Utilities ────────────────────────────

FANTASYTALKING_FPS = 23  # Model's native training FPS
FANTASYTALKING_MAX_FRAMES = 81  # Max frames per clip (Wan2.1 limit)
FANTASYTALKING_MAX_DURATION = FANTASYTALKING_MAX_FRAMES / FANTASYTALKING_FPS  # ~3.52s


def get_audio_duration(wav_path):
    """Get duration of a WAV file in seconds using the wave stdlib module."""
    with wave.open(wav_path, "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / rate


def calculate_num_frames(duration, fps=FANTASYTALKING_FPS):
    """Compute the number of video frames for a given audio duration.

    Wan2.1 requires num_frames = 4k + 1 (e.g., 17, 21, 25, ..., 77, 81).
    Returns the nearest valid frame count that covers the duration.
    """
    raw_frames = int(math.ceil(duration * fps))
    # Wan2.1 constraint: num_frames must be 4k+1
    k = math.ceil((raw_frames - 1) / 4)
    num_frames = 4 * k + 1
    # Clamp to valid range
    num_frames = max(17, min(num_frames, FANTASYTALKING_MAX_FRAMES))
    return num_frames


def segment_audio(wav_path, max_duration=FANTASYTALKING_MAX_DURATION, overlap=0.3):
    """Split a WAV file into segments using FFmpeg.

    Args:
        wav_path: Path to the source WAV file.
        max_duration: Maximum duration per segment in seconds.
        overlap: Overlap between segments in seconds (for crossfade stitching).

    Returns:
        List of paths to segment WAV files, sorted in order.
    """
    duration = get_audio_duration(wav_path)
    if duration <= max_duration:
        return [wav_path]  # No segmentation needed

    base_name = os.path.splitext(os.path.basename(wav_path))[0]
    seg_dir = os.path.join(os.path.dirname(wav_path), f"{base_name}_segments")
    os.makedirs(seg_dir, exist_ok=True)

    # Calculate segment boundaries with overlap
    step = max_duration - overlap
    segments = []
    start = 0.0
    seg_idx = 0

    while start < duration:
        seg_end = min(start + max_duration, duration)
        seg_duration = seg_end - start
        seg_path = os.path.join(seg_dir, f"{base_name}_seg{seg_idx:02d}.wav")

        cmd = [
            "ffmpeg", "-y",
            "-i", wav_path,
            "-ss", f"{start:.3f}",
            "-t", f"{seg_duration:.3f}",
            "-c:a", "pcm_s16le",
            seg_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  [WARN] FFmpeg segment failed: {result.stderr.strip()}")
            break

        segments.append(seg_path)
        print(f"  Segment {seg_idx}: {start:.2f}s - {seg_end:.2f}s -> {os.path.basename(seg_path)}")
        seg_idx += 1
        start += step

        # If remaining audio is too short for a meaningful segment, extend last segment
        if duration - start < 1.0 and start < duration:
            break

    return segments


def stitch_segments(clip_paths, output_path, original_audio_path, crossfade=0.3):
    """Stitch video segments together with crossfade, then replace audio with original.

    Args:
        clip_paths: List of video clip paths in order.
        output_path: Path for the final stitched video.
        original_audio_path: Path to the original full-length audio.
        crossfade: Crossfade duration in seconds between clips.

    Returns:
        Path to the stitched output, or None on failure.
    """
    if len(clip_paths) == 1:
        # Single clip - just mux with original audio
        cmd = [
            "ffmpeg", "-y",
            "-i", clip_paths[0],
            "-i", original_audio_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"  Stitched (single clip): {os.path.basename(output_path)}")
            return output_path
        else:
            print(f"  [FAIL] Stitch failed: {result.stderr.strip()[-200:]}")
            return None

    if len(clip_paths) == 0:
        print("  [FAIL] No clips to stitch")
        return None

    # Multi-clip: use FFmpeg xfade filter for crossfade transitions
    # Build complex filter graph
    inputs = []
    for p in clip_paths:
        inputs += ["-i", p]

    # Build xfade filter chain
    # For N clips, we need N-1 xfade operations
    filter_parts = []
    current_label = "[0:v]"

    for i in range(1, len(clip_paths)):
        next_label = f"[{i}:v]"
        # Calculate offset: where the crossfade starts in the accumulated timeline
        # Each clip overlaps by crossfade seconds with the next
        # We need the duration of each clip to calculate offsets
        out_label = f"[v{i}]" if i < len(clip_paths) - 1 else "[vout]"
        filter_parts.append(
            f"{current_label}{next_label}xfade=transition=fade:duration={crossfade}:offset={{offset_{i}}}{out_label}"
        )
        current_label = out_label

    # We need clip durations to calculate offsets. Probe each clip.
    durations = []
    for p in clip_paths:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json", "-show_format",
            p
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            dur = float(data["format"]["duration"])
            durations.append(dur)
        except Exception as e:
            print(f"  [WARN] Could not probe {os.path.basename(p)}: {e}")
            durations.append(3.0)  # fallback

    # Calculate accumulated offsets
    offsets = []
    accumulated = 0.0
    for i in range(len(durations) - 1):
        accumulated += durations[i] - crossfade
        offsets.append(accumulated)

    # Replace offset placeholders
    filter_str = ";".join(filter_parts)
    for i, offset in enumerate(offsets):
        filter_str = filter_str.replace(f"{{offset_{i+1}}}", f"{offset:.3f}")

    # First pass: stitch video only (no audio)
    temp_video = output_path.replace(".mp4", "_temp_video.mp4")
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_str,
        "-map", "[vout]",
        "-c:v", "libx264", "-crf", "19", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        temp_video
    ]

    print(f"  Stitching {len(clip_paths)} clips with {crossfade}s crossfade...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"  [FAIL] Video stitch failed: {result.stderr.strip()[-200:]}")
        return None

    # Second pass: mux with original audio
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", original_audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-shortest",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    # Clean up temp file
    if os.path.isfile(temp_video):
        os.remove(temp_video)

    if result.returncode == 0:
        print(f"  Stitched: {os.path.basename(output_path)}")
        return output_path
    else:
        print(f"  [FAIL] Audio mux failed: {result.stderr.strip()[-200:]}")
        return None


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


def build_fantasytalking_prompt(photo_filename, audio_filename, test_mode=False, num_frames=None):
    """Build FantasyTalking ComfyUI prompt from workflow template.

    The workflow uses WanVideoWrapper nodes:
    - Node 58 (LoadImage): face photo
    - Node 72 (LoadAudio): audio file
    - Node 73 (FantasyTalkingWav2VecEmbeds): num_frames, fps
    - Node 63 (WanVideoImageToVideoEncode): num_frames
    - Node 69 (WanVideoSampler): seed, steps
    - Node 16 (WanVideoTextEncode): positive/negative prompt

    Args:
        photo_filename: Name of the uploaded photo file.
        audio_filename: Name of the uploaded audio file.
        test_mode: If True, use 49 frames / 20 steps (faster). Production uses 81 frames / 30 steps.
        num_frames: Override frame count (must be 4k+1 for Wan2.1). If None, uses 81 (or 49 in test mode).
    """
    if not os.path.isfile(FANTASYTALKING_WORKFLOW):
        print(f"  [ERROR] FantasyTalking workflow not found: {FANTASYTALKING_WORKFLOW}")
        print("  Create it with: workflows/talking_head_fantasy.json")
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

    # Determine frame count and steps
    if test_mode:
        frames = 49
        steps = 20
    else:
        frames = 81
        steps = 30

    # Override with explicit num_frames if provided
    if num_frames is not None:
        frames = num_frames

    # Enforce fps=23.0 (model's native training FPS)
    prompt["73"]["inputs"]["fps"] = 23.0

    # Update frame count in both nodes that reference it
    prompt["73"]["inputs"]["num_frames"] = frames  # FantasyTalkingWav2VecEmbeds
    prompt["63"]["inputs"]["num_frames"] = frames   # WanVideoImageToVideoEncode
    prompt["69"]["inputs"]["steps"] = steps          # WanVideoSampler
    prompt["78"]["inputs"]["steps"] = steps          # CreateCFGScheduleFloatList

    return prompt


def run_single_fantasytalking_clip(photo_filename, audio_filename, output_dir, test_mode=False, num_frames=None):
    """Generate a single FantasyTalking clip (upload, submit, poll, download).

    Args:
        photo_filename: Filename of the photo already uploaded to ComfyUI.
        audio_filename: Filename of the audio already uploaded to ComfyUI.
        output_dir: Directory to download the result to.
        test_mode: Use reduced frames/steps for faster iteration.
        num_frames: Override frame count (4k+1, max 81).

    Returns:
        Path to the downloaded clip, or None on failure.
    """
    prompt = build_fantasytalking_prompt(photo_filename, audio_filename,
                                         test_mode=test_mode, num_frames=num_frames)
    if not prompt:
        return None

    print("  Submitting to ComfyUI...")
    prompt_id = submit_prompt(prompt)
    if not prompt_id:
        print("  [FAIL] Could not submit prompt")
        return None
    print(f"  Prompt ID: {prompt_id}")

    frame_label = num_frames or (49 if test_mode else 81)
    print(f"  Waiting for generation ({frame_label} frames)...")
    job_data = poll_for_completion(prompt_id)
    if not job_data:
        print("  [FAIL] Job did not complete")
        return None

    print("  Downloading output...")
    files = download_output(prompt_id, job_data, output_dir)
    if files:
        return files[0]
    else:
        print("  [WARN] No files downloaded")
        return None


def run_fantasytalking_jobs(test_mode=False):
    """Run FantasyTalking jobs with automatic audio segmentation and resume support.

    For audio files shorter than ~3.52s (81 frames at 23fps), generates a single clip.
    For longer audio, segments the audio, generates a clip per segment, then stitches
    them together with crossfade and the original full-length audio.

    Resume: Automatically detects existing output files and skips completed jobs/segments.
    State tracked in video-production/state/generation_progress.json.
    Re-run after interruption to pick up where you left off.
    """
    print("\n--- FantasyTalking Jobs (with resume) ---\n")
    print("  NOTE: FantasyTalking uses Wan2.1 I2V backbone -- ~20-45 min per clip")
    print(f"  FPS: {FANTASYTALKING_FPS} | Max frames: {FANTASYTALKING_MAX_FRAMES} | Max duration/segment: {FANTASYTALKING_MAX_DURATION:.2f}s")
    if test_mode:
        print("  TEST MODE: Using reduced frame count for faster iteration")
    os.makedirs(OUTPUT_FANTASYTALKING_DIR, exist_ok=True)

    # Load resume state
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    for job in FANTASYTALKING_JOBS:
        print(f"\nJob: {job['name']} -- {job['description']}")

        # Resume check: skip if final output already exists and is valid
        final_path = os.path.join(OUTPUT_FANTASYTALKING_DIR, f"{job['name']}.mp4")
        if os.path.isfile(final_path) and os.path.getsize(final_path) > 100000:
            size_mb = os.path.getsize(final_path) / (1024 * 1024)
            print(f"  [RESUME-SKIP] Already completed: {os.path.basename(final_path)} ({size_mb:.1f}MB)")
            update_job_state(state, job['name'], status="completed", job_type="fantasytalking",
                           stitched=True, output_path=os.path.relpath(final_path, REPO_ROOT))
            continue

        photo_path = os.path.join(PHOTOS_DIR, job["photo"])
        audio_path = os.path.join(AUDIO_DIR, job["audio"])

        if not os.path.isfile(photo_path):
            print(f"  [SKIP] Photo not found: {job['photo']}")
            continue
        if not os.path.isfile(audio_path):
            print(f"  [SKIP] Audio not found: {job['audio']}")
            continue

        # Get audio duration
        audio_duration = get_audio_duration(audio_path)
        print(f"  Audio duration: {audio_duration:.2f}s")

        # Upload photo (needed for all segments)
        print("  Uploading photo...")
        photo_result = upload_file_to_comfyui(photo_path)
        if not photo_result:
            print("  [FAIL] Photo upload failed, skipping job")
            continue

        # Determine if segmentation is needed
        effective_max = FANTASYTALKING_MAX_DURATION
        if test_mode:
            # In test mode, max duration is 49 frames / 23 fps = ~2.13s
            effective_max = 49 / FANTASYTALKING_FPS

        if audio_duration <= effective_max:
            # Short audio: single clip, compute exact frame count
            num_frames = calculate_num_frames(audio_duration)
            print(f"  Single clip: {num_frames} frames for {audio_duration:.2f}s audio")

            update_job_state(state, job['name'], status="in_progress", job_type="fantasytalking",
                           segments_total=1, segments_completed=[])

            # Upload audio
            audio_result = upload_file_to_comfyui(audio_path)
            if not audio_result:
                print("  [FAIL] Audio upload failed")
                continue

            clip_path = run_single_fantasytalking_clip(
                job["photo"], job["audio"], OUTPUT_FANTASYTALKING_DIR,
                test_mode=test_mode, num_frames=num_frames
            )
            if clip_path:
                # Rename to match job name
                if clip_path != final_path:
                    if os.path.exists(final_path):
                        os.remove(final_path)
                    os.rename(clip_path, final_path)
                print(f"  [OK] {job['name']}: {final_path}")
                update_job_state(state, job['name'], status="completed", stitched=True,
                               segments_completed=[0],
                               output_path=os.path.relpath(final_path, REPO_ROOT))
            else:
                print(f"  [FAIL] {job['name']}: generation failed")
                update_job_state(state, job['name'], status="failed")
        else:
            # Long audio: segment, generate per-segment, stitch
            print(f"  Audio exceeds {effective_max:.2f}s limit -- segmenting...")
            segments = segment_audio(audio_path, max_duration=effective_max)
            print(f"  {len(segments)} segment(s) to generate")

            update_job_state(state, job['name'], status="in_progress", job_type="fantasytalking",
                           segments_total=len(segments),
                           segments_completed=state.get("jobs", {}).get(job['name'], {}).get("segments_completed", []))

            segment_clips = []
            seg_output_dir = os.path.join(OUTPUT_FANTASYTALKING_DIR, f"{job['name']}_segments")
            os.makedirs(seg_output_dir, exist_ok=True)

            for seg_idx, seg_path in enumerate(segments):
                seg_name = os.path.basename(seg_path)
                seg_duration = get_audio_duration(seg_path)
                num_frames = calculate_num_frames(seg_duration)

                # Resume check: see if this segment clip already exists with predictable name
                expected_clip = os.path.join(seg_output_dir, f"{job['name']}_seg{seg_idx:02d}.mp4")
                if os.path.isfile(expected_clip) and os.path.getsize(expected_clip) > 50000:
                    size_mb = os.path.getsize(expected_clip) / (1024 * 1024)
                    print(f"\n  [RESUME-SKIP] Segment {seg_idx}/{len(segments)-1} exists ({size_mb:.1f}MB)")
                    segment_clips.append(expected_clip)
                    continue

                print(f"\n  Segment {seg_idx}/{len(segments)-1}: {seg_name} ({seg_duration:.2f}s, {num_frames} frames)")

                # Upload segment audio
                seg_result = upload_file_to_comfyui(seg_path)
                if not seg_result:
                    print(f"  [FAIL] Segment audio upload failed")
                    continue

                clip_path = run_single_fantasytalking_clip(
                    job["photo"], seg_name, seg_output_dir,
                    test_mode=test_mode, num_frames=num_frames
                )
                if clip_path:
                    # Rename to predictable name for resume detection
                    if clip_path != expected_clip:
                        if os.path.exists(expected_clip):
                            os.remove(expected_clip)
                        os.rename(clip_path, expected_clip)
                        clip_path = expected_clip
                    segment_clips.append(clip_path)
                    print(f"  [OK] Segment {seg_idx} generated -> {os.path.basename(expected_clip)}")

                    # Update state after each segment (survives interruption)
                    completed_segs = [i for i in range(len(segments))
                                      if os.path.isfile(os.path.join(seg_output_dir, f"{job['name']}_seg{i:02d}.mp4"))]
                    update_job_state(state, job['name'], segments_completed=completed_segs)
                else:
                    print(f"  [FAIL] Segment {seg_idx} generation failed")

            # Stitch segments together
            if segment_clips:
                print(f"\n  Stitching {len(segment_clips)} segment clips...")
                result = stitch_segments(segment_clips, final_path, audio_path, crossfade=0.3)
                if result:
                    print(f"  [OK] {job['name']}: {final_path}")
                    update_job_state(state, job['name'], status="completed", stitched=True,
                                   output_path=os.path.relpath(final_path, REPO_ROOT))
                else:
                    print(f"  [FAIL] {job['name']}: stitching failed")
                    update_job_state(state, job['name'], status="stitch_failed")
            else:
                print(f"  [FAIL] {job['name']}: no segments generated successfully")
                update_job_state(state, job['name'], status="failed")

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

    # Show resume state
    show_resume_status()

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
    parser.add_argument("--status", action="store_true", help="Check ComfyUI status + resume progress")
    parser.add_argument("--resume-status", action="store_true", help="Show only resume/progress state")
    parser.add_argument("--test", action="store_true", help="Test mode: 49 frames instead of 81 (saves ~17 min per clip)")
    parser.add_argument("--max-i2v", type=int, default=3, help="Max I2V jobs to run (default: 3)")
    args = parser.parse_args()

    print("=" * 60)
    print("  VIDEO PRODUCTION PIPELINE - Stage 2: Generate Assets")
    print("=" * 60)

    if args.resume_status:
        show_resume_status()
        return

    if args.status:
        check_status()
        return

    # Determine which jobs to run
    # Default (no flags): FantasyTalking + Wan2.1 I2V
    any_flag = args.sadtalker or args.fantasy or args.i2v or args.i2v_wan22
    run_fantasy = args.fantasy or (not any_flag)
    run_i2v = args.i2v or (not any_flag)
    run_st = args.sadtalker  # Legacy, only when explicitly requested
    run_i2v_wan22 = args.i2v_wan22

    if run_fantasy:
        run_fantasytalking_jobs(test_mode=args.test)
    if run_st:
        print("\n  NOTE: SadTalker is deprecated. Consider using --fantasy instead.")
        run_sadtalker_jobs()
    if run_i2v:
        run_i2v_jobs(max_jobs=args.max_i2v, test_mode=args.test)
    if run_i2v_wan22:
        run_i2v_wan22_jobs(max_jobs=args.max_i2v, test_mode=args.test)

    print("\n" + "=" * 60)
    print("  Stage 2 complete. Run normalize_clips.py next.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
