"""
Stage 3: Normalize Clips
Re-encodes ALL clips to a uniform format before assembly.
This prevents the #1 cause of FFmpeg concat failures: mismatched codecs/fps/resolution.

Usage:
    python video-production/scripts/normalize_clips.py                          # normalize all clips
    python video-production/scripts/normalize_clips.py path/to/clip.mp4        # normalize single clip
    python video-production/scripts/normalize_clips.py --probe path/to/clip.mp4 # probe only (no encode)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_PATH = os.path.join(REPO_ROOT, "video-production", "configs", "normalization_standard.json")
PROBE_REPORT_DIR = os.path.join(REPO_ROOT, "video-production", "logs", "ffprobe_reports")

# Directories containing raw clips to normalize
RAW_CLIP_DIRS = [
    os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "i2v"),
    os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "sadtalker"),
    os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "fantasytalking"),
    os.path.join(REPO_ROOT, "demo-clients", "candle-co", "screen-recordings"),
    os.path.join(REPO_ROOT, "demo-clients", "candle-co", "canva-exports"),
]

NORMALIZED_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "normalized")

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def ffprobe_clip(clip_path):
    """Run ffprobe and return parsed stream info."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        clip_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ffprobe error: {result.stderr.strip()}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"  ffprobe exception: {e}")
        return None


def get_stream_info(probe_data):
    """Extract video and audio stream details from ffprobe output."""
    video = None
    audio = None
    for stream in probe_data.get("streams", []):
        if stream.get("codec_type") == "video" and video is None:
            video = stream
        elif stream.get("codec_type") == "audio" and audio is None:
            audio = stream
    return video, audio


def print_probe_summary(clip_path, probe_data):
    """Print human-readable probe summary."""
    video, audio = get_stream_info(probe_data)
    name = os.path.basename(clip_path)
    duration = probe_data.get("format", {}).get("duration", "?")

    print(f"\n  {name}")
    print(f"    Duration: {float(duration):.2f}s" if duration != "?" else "    Duration: unknown")

    if video:
        w = video.get("width", "?")
        h = video.get("height", "?")
        codec = video.get("codec_name", "?")
        pix_fmt = video.get("pix_fmt", "?")
        # Parse fps from r_frame_rate (e.g. "30/1" or "24000/1001")
        r_fps = video.get("r_frame_rate", "0/1")
        try:
            num, den = r_fps.split("/")
            fps = float(num) / float(den)
        except (ValueError, ZeroDivisionError):
            fps = 0
        print(f"    Video: {w}x{h} @ {fps:.2f}fps, {codec}, {pix_fmt}")
    else:
        print("    Video: NONE")

    if audio:
        acodec = audio.get("codec_name", "?")
        sr = audio.get("sample_rate", "?")
        channels = audio.get("channels", "?")
        print(f"    Audio: {acodec}, {sr}Hz, {channels}ch")
    else:
        print("    Audio: NONE (will add silent track)")


def save_probe_report(clip_path, probe_data):
    """Save ffprobe JSON to logs."""
    os.makedirs(PROBE_REPORT_DIR, exist_ok=True)
    name = os.path.splitext(os.path.basename(clip_path))[0]
    report_path = os.path.join(PROBE_REPORT_DIR, f"{name}_probe.json")
    with open(report_path, "w") as f:
        json.dump(probe_data, f, indent=2)
    return report_path


def normalize_clip(clip_path, config, force=False):
    """Re-encode a single clip to the normalization standard."""
    name = os.path.splitext(os.path.basename(clip_path))[0]
    output_path = os.path.join(NORMALIZED_DIR, f"{name}_norm.mp4")

    if os.path.exists(output_path) and not force:
        print(f"  [SKIP] {os.path.basename(output_path)} already exists (use --force to re-encode)")
        return output_path

    # Probe the source
    probe_data = ffprobe_clip(clip_path)
    if not probe_data:
        print(f"  [FAIL] Could not probe {clip_path}")
        return None

    print_probe_summary(clip_path, probe_data)
    save_probe_report(clip_path, probe_data)

    video_stream, audio_stream = get_stream_info(probe_data)
    if not video_stream:
        print(f"  [FAIL] No video stream in {clip_path}")
        return None

    v = config["video"]
    a = config["audio"]
    vf = config["filters"]["video"]
    af = config["filters"]["audio"]

    # Build FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", clip_path]

    if not audio_stream:
        # Add silent audio source for clips without audio
        cmd += [
            "-f", "lavfi", "-i",
            f"anullsrc=channel_layout=stereo:sample_rate={a['sample_rate']}"
        ]
        # Map video from input 0, audio from input 1
        cmd += ["-map", "0:v:0", "-map", "1:a:0", "-shortest"]
    else:
        cmd += ["-map", "0:v:0", "-map", "0:a:0"]

    # Video encoding
    cmd += [
        "-vf", vf,
        "-c:v", v["codec"],
        "-crf", str(v["crf"]),
        "-preset", v["preset"],
        "-profile:v", v["profile"],
        "-level:v", v["level"],
        "-pix_fmt", v["pixel_format"],
    ]

    # Audio encoding
    cmd += [
        "-af", af,
        "-c:a", a["codec"],
        "-ar", str(a["sample_rate"]),
        "-ac", str(a["channels"]),
        "-b:a", a["bitrate"],
    ]

    # Metadata cleanup
    cmd += ["-movflags", "+faststart"]
    cmd += [output_path]

    print(f"  Encoding -> {os.path.basename(output_path)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            # Print last few lines of stderr for diagnosis
            err_lines = result.stderr.strip().split("\n")
            for line in err_lines[-5:]:
                print(f"    {line}")
            print(f"  [FAIL] FFmpeg exited with code {result.returncode}")
            return None
    except subprocess.TimeoutExpired:
        print(f"  [FAIL] FFmpeg timed out (10 min limit)")
        return None

    # Verify output
    out_probe = ffprobe_clip(output_path)
    if out_probe:
        out_video, out_audio = get_stream_info(out_probe)
        if out_video and out_audio:
            w = out_video.get("width")
            h = out_video.get("height")
            print(f"  [OK] {os.path.basename(output_path)} -> {w}x{h}")
            return output_path
        else:
            print(f"  [FAIL] Output missing video or audio stream")
            return None
    else:
        print(f"  [FAIL] Could not verify output")
        return None


def find_clips(directories):
    """Find all video files in the given directories."""
    clips = []
    for d in directories:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            ext = os.path.splitext(f)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                clips.append(os.path.join(d, f))
    return clips


def main():
    parser = argparse.ArgumentParser(description="Normalize video clips to pipeline standard")
    parser.add_argument("clip", nargs="?", help="Path to a single clip to normalize")
    parser.add_argument("--probe", action="store_true", help="Probe only, don't re-encode")
    parser.add_argument("--force", action="store_true", help="Re-encode even if output exists")
    args = parser.parse_args()

    config = load_config()
    os.makedirs(NORMALIZED_DIR, exist_ok=True)

    print("=" * 60)
    print("  VIDEO PRODUCTION PIPELINE - Stage 3: Normalize Clips")
    print("=" * 60)

    if args.clip:
        # Single clip mode
        clip_path = os.path.abspath(args.clip)
        if not os.path.isfile(clip_path):
            print(f"  [FAIL] File not found: {clip_path}")
            sys.exit(1)

        if args.probe:
            probe_data = ffprobe_clip(clip_path)
            if probe_data:
                print_probe_summary(clip_path, probe_data)
                report = save_probe_report(clip_path, probe_data)
                print(f"\n  Report saved: {report}")
            else:
                sys.exit(1)
        else:
            result = normalize_clip(clip_path, config, force=args.force)
            if not result:
                sys.exit(1)
    else:
        # Batch mode -- normalize all clips in raw directories
        clips = find_clips(RAW_CLIP_DIRS)
        if not clips:
            print("\n  No clips found in raw asset directories.")
            print("  Directories searched:")
            for d in RAW_CLIP_DIRS:
                rel = os.path.relpath(d, REPO_ROOT)
                exists = "exists" if os.path.isdir(d) else "missing"
                print(f"    {rel} ({exists})")
            print("\n  Place raw clips in the directories above, or pass a single clip path.")
            sys.exit(0)

        print(f"\n  Found {len(clips)} clip(s) to normalize:\n")

        results = {"ok": 0, "skip": 0, "fail": 0}
        for clip in clips:
            rel = os.path.relpath(clip, REPO_ROOT)
            print(f"\n--- {rel} ---")
            if args.probe:
                probe_data = ffprobe_clip(clip)
                if probe_data:
                    print_probe_summary(clip, probe_data)
                    save_probe_report(clip, probe_data)
                    results["ok"] += 1
                else:
                    results["fail"] += 1
            else:
                out = normalize_clip(clip, config, force=args.force)
                if out:
                    results["ok"] += 1
                else:
                    results["fail"] += 1

        print(f"\n{'=' * 60}")
        print(f"  RESULTS: {results['ok']} ok, {results['fail']} failed")
        print(f"  Normalized clips: {os.path.relpath(NORMALIZED_DIR, REPO_ROOT)}")
        print(f"{'=' * 60}\n")

        if results["fail"] > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
