"""
Stage 1: Setup & Validation
Verifies FFmpeg, SSH to The Machine, ComfyUI API, and directory tree.
Run this first before any other pipeline stage.

Usage:
    python video-production/scripts/setup_environment.py
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.request
import urllib.error

# Paths relative to repo root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMFYUI_ENDPOINT = "http://100.64.130.71:8188"
THE_MACHINE_HOST = "100.64.130.71"
THE_MACHINE_USER = "michael"

REQUIRED_DIRS = [
    "video-production/scripts",
    "video-production/configs",
    "video-production/logs/ffprobe_reports",
    "video-production/logs/validation_reports",
    "demo-clients/candle-co/audio",
    "demo-clients/candle-co/photos",
    "demo-clients/candle-co/screen-recordings",
    "demo-clients/candle-co/canva-exports",
    "demo-clients/candle-co/video-assets/i2v",
    "demo-clients/candle-co/video-assets/sadtalker",
    "demo-clients/candle-co/video-assets/normalized",
    "demo-clients/candle-co/final-videos",
    "fiverr-assets/videos",
    "fiverr-assets/thumbnails",
]

REQUIRED_CONFIGS = [
    "video-production/configs/normalization_standard.json",
    "video-production/configs/video1_structure.json",
    "video-production/configs/video2_structure.json",
    "video-production/configs/video3_structure.json",
]

USER_ASSETS = {
    "demo-clients/candle-co/photos/avatar_photo.png": "Avatar photo for SadTalker",
    "demo-clients/candle-co/audio/v1_intro.wav": "Video 1 intro narration (~8s)",
    "demo-clients/candle-co/audio/v1_outro.wav": "Video 1 outro/CTA (~15s)",
    "demo-clients/candle-co/audio/v2_cta.wav": "Video 2 CTA narration (~10s)",
    "demo-clients/candle-co/audio/v3_intro.wav": "Video 3 intro narration (~5s)",
    "demo-clients/candle-co/screen-recordings/demo_marketing.mp4": "Video 1: automation_brain.py terminal demo",
    "demo-clients/candle-co/screen-recordings/demo_comfyui.mp4": "Video 2: ComfyUI image generation demo",
    "demo-clients/candle-co/screen-recordings/demo_dashboard.mp4": "Video 3: Analytics dashboard walkthrough",
    "demo-clients/candle-co/canva-exports/stats_animation.mp4": "Video 1: Stats numbers graphic",
    "demo-clients/candle-co/canva-exports/calendar_preview.mp4": "Video 1: Calendar preview mockup",
    "demo-clients/candle-co/canva-exports/image_montage.mp4": "Video 2: Quick-cut image montage intro",
    "demo-clients/candle-co/canva-exports/ken_burns_slideshow.mp4": "Video 2: 5-image slideshow",
    "demo-clients/candle-co/canva-exports/feature_callouts.mp4": "Video 3: Feature callout boxes",
    "demo-clients/candle-co/canva-exports/cta_text_animation.mp4": "Video 3: CTA text animation",
}


def check_pass(label):
    print(f"  [PASS] {label}")


def check_fail(label, detail=""):
    msg = f"  [FAIL] {label}"
    if detail:
        msg += f" -- {detail}"
    print(msg)


def check_warn(label, detail=""):
    msg = f"  [WARN] {label}"
    if detail:
        msg += f" -- {detail}"
    print(msg)


def check_ffmpeg():
    print("\n--- FFmpeg ---")
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        check_pass(f"ffmpeg found: {ffmpeg_path}")
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True, text=True, timeout=10
            )
            first_line = result.stdout.split("\n")[0]
            check_pass(f"Version: {first_line}")
        except Exception as e:
            check_warn("Could not get ffmpeg version", str(e))
    else:
        check_fail("ffmpeg not found in PATH")
        return False

    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        check_pass(f"ffprobe found: {ffprobe_path}")
    else:
        check_fail("ffprobe not found in PATH")
        return False

    return True


def check_ssh():
    print("\n--- SSH to The Machine ---")
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
             f"{THE_MACHINE_USER}@{THE_MACHINE_HOST}", "echo ok"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and "ok" in result.stdout:
            check_pass(f"SSH connection to {THE_MACHINE_HOST}")
            return True
        else:
            check_fail(f"SSH connection failed", result.stderr.strip())
            return False
    except FileNotFoundError:
        check_fail("ssh command not found")
        return False
    except subprocess.TimeoutExpired:
        check_fail("SSH connection timed out (5s)")
        return False
    except Exception as e:
        check_fail("SSH check error", str(e))
        return False


def check_comfyui():
    print("\n--- ComfyUI API ---")
    try:
        req = urllib.request.Request(
            f"{COMFYUI_ENDPOINT}/system_stats",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            devices = data.get("devices", [])
            if devices:
                gpu = devices[0]
                name = gpu.get("name", "unknown")
                vram_total = gpu.get("vram_total", 0)
                vram_free = gpu.get("vram_free", 0)
                vram_gb = vram_total / (1024**3)
                free_gb = vram_free / (1024**3)
                check_pass(f"ComfyUI API responding at {COMFYUI_ENDPOINT}")
                check_pass(f"GPU: {name} ({vram_gb:.1f}GB total, {free_gb:.1f}GB free)")
            else:
                check_pass(f"ComfyUI API responding (no GPU info)")
            return True
    except urllib.error.URLError as e:
        check_fail(f"ComfyUI API unreachable at {COMFYUI_ENDPOINT}", str(e.reason))
        return False
    except Exception as e:
        check_fail(f"ComfyUI API check error", str(e))
        return False


def check_directories():
    print("\n--- Directory Structure ---")
    all_ok = True
    for d in REQUIRED_DIRS:
        full = os.path.join(REPO_ROOT, d)
        if os.path.isdir(full):
            check_pass(d)
        else:
            os.makedirs(full, exist_ok=True)
            check_pass(f"{d} (created)")
    return all_ok


def check_configs():
    print("\n--- Config Files ---")
    all_ok = True
    for c in REQUIRED_CONFIGS:
        full = os.path.join(REPO_ROOT, c)
        if os.path.isfile(full):
            check_pass(c)
        else:
            check_fail(c, "missing")
            all_ok = False
    return all_ok


def check_user_assets():
    print("\n--- User-Provided Assets ---")
    found = 0
    missing = 0
    for path, desc in USER_ASSETS.items():
        full = os.path.join(REPO_ROOT, path)
        if os.path.isfile(full):
            check_pass(f"{os.path.basename(path)} -- {desc}")
            found += 1
        else:
            check_warn(f"{os.path.basename(path)} -- {desc}", "not yet provided")
            missing += 1
    print(f"\n  Assets: {found} found, {missing} pending")
    return missing == 0


def check_existing_test_video():
    print("\n--- Existing Test Assets ---")
    test_videos = [
        "output/candle_video_00001.mp4",
        "output/i2v_wan_test_00001.mp4",
    ]
    found_any = False
    for v in test_videos:
        full = os.path.join(REPO_ROOT, v)
        if os.path.isfile(full):
            check_pass(f"Test video: {v}")
            found_any = True
        else:
            check_warn(f"Test video: {v}", "not found")
    return found_any


def main():
    print("=" * 60)
    print("  VIDEO PRODUCTION PIPELINE - Stage 1: Setup & Validation")
    print("=" * 60)

    results = {}
    results["ffmpeg"] = check_ffmpeg()
    results["ssh"] = check_ssh()
    results["comfyui"] = check_comfyui()
    results["directories"] = check_directories()
    results["configs"] = check_configs()
    results["user_assets"] = check_user_assets()
    results["test_videos"] = check_existing_test_video()

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    critical = ["ffmpeg", "directories", "configs"]
    optional = ["ssh", "comfyui", "user_assets", "test_videos"]

    all_critical_ok = True
    for key in critical:
        status = "OK" if results[key] else "FAIL"
        if not results[key]:
            all_critical_ok = False
        print(f"  {key:20s} [{status}]")

    for key in optional:
        status = "OK" if results[key] else "PENDING"
        print(f"  {key:20s} [{status}]")

    print()
    if all_critical_ok:
        print("  Pipeline ready for local operations (normalize, assemble, validate).")
        if not results["ssh"] or not results["comfyui"]:
            print("  NOTE: SSH/ComfyUI needed for Stage 2 (asset generation).")
        if not results["user_assets"]:
            print("  NOTE: User assets needed before full pipeline run.")
    else:
        print("  CRITICAL requirements missing. Fix before proceeding.")
        sys.exit(1)

    print()


if __name__ == "__main__":
    main()
