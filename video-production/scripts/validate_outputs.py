"""
Stage 5: Validate & Export
Runs ffprobe checks on final videos, generates thumbnails, copies to fiverr-assets/.

Usage:
    python video-production/scripts/validate_outputs.py                # validate all final videos
    python video-production/scripts/validate_outputs.py path/to/video.mp4  # validate single video
    python video-production/scripts/validate_outputs.py --export       # validate + copy to fiverr-assets
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FINAL_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "final-videos")
FIVERR_VIDEOS_DIR = os.path.join(REPO_ROOT, "fiverr-assets", "videos")
FIVERR_THUMBS_DIR = os.path.join(REPO_ROOT, "fiverr-assets", "thumbnails")
REPORT_DIR = os.path.join(REPO_ROOT, "video-production", "logs", "validation_reports")

# Expected specs (from normalization standard)
EXPECTED = {
    "video_codec": "h264",
    "width": 1920,
    "height": 1080,
    "pixel_format": "yuv420p",
    "fps_min": 29.9,
    "fps_max": 30.1,
    "audio_codec": "aac",
    "sample_rate": 48000,
    "channels": 2,
}

# Video-specific expectations
VIDEO_SPECS = {
    "ai-marketing-demo.mp4": {"min_duration": 60, "max_duration": 120},
    "ai-images-demo.mp4": {"min_duration": 40, "max_duration": 75},
    "analytics-demo.mp4": {"min_duration": 40, "max_duration": 75},
}

# Thumbnail extraction points (percentage of video duration)
THUMBNAIL_TIME_PERCENT = 0.3  # 30% into the video


def ffprobe_clip(clip_path):
    """Run ffprobe and return parsed data."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        clip_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"  ffprobe error: {e}")
    return None


def validate_video(video_path):
    """Validate a single video against expected specs. Returns (pass, report)."""
    name = os.path.basename(video_path)
    report = {
        "file": name,
        "path": video_path,
        "timestamp": datetime.now().isoformat(),
        "checks": [],
        "passed": True,
    }

    def check(label, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        report["checks"].append({"label": label, "status": status, "detail": detail})
        if not passed:
            report["passed"] = False
        icon = "+" if passed else "X"
        msg = f"  [{icon}] {label}"
        if detail:
            msg += f" -- {detail}"
        print(msg)

    print(f"\n--- Validating: {name} ---")

    # File exists and has size
    if not os.path.isfile(video_path):
        check("File exists", False, "not found")
        return False, report

    size = os.path.getsize(video_path)
    size_mb = size / (1024 * 1024)
    check("File exists", True, f"{size_mb:.1f}MB")

    if size < 1024:
        check("File size", False, "too small (< 1KB)")
        return False, report

    # Probe
    probe = ffprobe_clip(video_path)
    if not probe:
        check("ffprobe readable", False, "could not parse")
        return False, report
    check("ffprobe readable", True)

    # Find streams
    video_stream = None
    audio_stream = None
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "video" and video_stream is None:
            video_stream = stream
        elif stream.get("codec_type") == "audio" and audio_stream is None:
            audio_stream = stream

    # Video checks
    if not video_stream:
        check("Video stream", False, "no video stream found")
        return False, report
    check("Video stream", True)

    codec = video_stream.get("codec_name", "")
    check("Video codec", codec == EXPECTED["video_codec"],
          f"{codec} (expected {EXPECTED['video_codec']})")

    w = video_stream.get("width", 0)
    h = video_stream.get("height", 0)
    check("Resolution", w == EXPECTED["width"] and h == EXPECTED["height"],
          f"{w}x{h} (expected {EXPECTED['width']}x{EXPECTED['height']})")

    pix_fmt = video_stream.get("pix_fmt", "")
    check("Pixel format", pix_fmt == EXPECTED["pixel_format"],
          f"{pix_fmt} (expected {EXPECTED['pixel_format']})")

    # FPS
    r_fps = video_stream.get("r_frame_rate", "0/1")
    try:
        num, den = r_fps.split("/")
        fps = float(num) / float(den)
    except (ValueError, ZeroDivisionError):
        fps = 0
    check("Frame rate", EXPECTED["fps_min"] <= fps <= EXPECTED["fps_max"],
          f"{fps:.2f}fps (expected ~30)")

    # Audio checks
    if not audio_stream:
        check("Audio stream", False, "no audio stream found")
    else:
        check("Audio stream", True)

        acodec = audio_stream.get("codec_name", "")
        check("Audio codec", acodec == EXPECTED["audio_codec"],
              f"{acodec} (expected {EXPECTED['audio_codec']})")

        sr = int(audio_stream.get("sample_rate", 0))
        check("Sample rate", sr == EXPECTED["sample_rate"],
              f"{sr}Hz (expected {EXPECTED['sample_rate']}Hz)")

        channels = int(audio_stream.get("channels", 0))
        check("Channels", channels == EXPECTED["channels"],
              f"{channels} (expected {EXPECTED['channels']})")

    # Duration check
    duration = float(probe.get("format", {}).get("duration", 0))
    check("Duration", duration > 0, f"{duration:.1f}s")

    specs = VIDEO_SPECS.get(name)
    if specs:
        in_range = specs["min_duration"] <= duration <= specs["max_duration"]
        check("Duration range", in_range,
              f"{duration:.1f}s (expected {specs['min_duration']}-{specs['max_duration']}s)")

    report["duration"] = duration
    report["size_mb"] = size_mb

    return report["passed"], report


def generate_thumbnail(video_path, output_dir):
    """Extract a frame as a 1280x720 thumbnail."""
    name = os.path.splitext(os.path.basename(video_path))[0]
    thumb_path = os.path.join(output_dir, f"{name}-thumb.png")

    # Get duration to calculate extraction point
    probe = ffprobe_clip(video_path)
    duration = float(probe.get("format", {}).get("duration", 10)) if probe else 10
    time_point = duration * THUMBNAIL_TIME_PERCENT

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(time_point),
        "-i", video_path,
        "-vframes", "1",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black",
        thumb_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and os.path.isfile(thumb_path):
            size_kb = os.path.getsize(thumb_path) / 1024
            print(f"  Thumbnail: {os.path.basename(thumb_path)} ({size_kb:.0f}KB)")
            return thumb_path
        else:
            print(f"  [FAIL] Thumbnail generation failed")
            return None
    except Exception as e:
        print(f"  [FAIL] Thumbnail error: {e}")
        return None


def save_report(reports):
    """Save validation report to logs."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORT_DIR, f"validation_{timestamp}.json")
    with open(report_path, "w") as f:
        json.dump(reports, f, indent=2)
    print(f"\n  Report saved: {os.path.relpath(report_path, REPO_ROOT)}")
    return report_path


def main():
    parser = argparse.ArgumentParser(description="Validate final video outputs")
    parser.add_argument("video", nargs="?", help="Path to a single video to validate")
    parser.add_argument("--export", action="store_true", help="Copy passing videos to fiverr-assets/")
    parser.add_argument("--thumbnails", action="store_true", help="Generate thumbnails")
    args = parser.parse_args()

    print("=" * 60)
    print("  VIDEO PRODUCTION PIPELINE - Stage 5: Validate & Export")
    print("=" * 60)

    videos = []
    if args.video:
        videos = [os.path.abspath(args.video)]
    else:
        if os.path.isdir(FINAL_DIR):
            for f in sorted(os.listdir(FINAL_DIR)):
                if f.endswith(".mp4") and not f.startswith("_"):
                    videos.append(os.path.join(FINAL_DIR, f))

    if not videos:
        print("\n  No videos found to validate.")
        print(f"  Expected in: {os.path.relpath(FINAL_DIR, REPO_ROOT)}")
        print("  Run assemble_video.py first.")
        sys.exit(0)

    print(f"\n  Validating {len(videos)} video(s)...\n")

    all_reports = []
    all_passed = True

    for video_path in videos:
        passed, report = validate_video(video_path)
        all_reports.append(report)
        if not passed:
            all_passed = False

        # Generate thumbnail
        if args.thumbnails or args.export:
            os.makedirs(FIVERR_THUMBS_DIR, exist_ok=True)
            generate_thumbnail(video_path, FIVERR_THUMBS_DIR)

    # Save report
    save_report(all_reports)

    # Export to fiverr-assets
    if args.export:
        print(f"\n--- Exporting to fiverr-assets/ ---")
        os.makedirs(FIVERR_VIDEOS_DIR, exist_ok=True)
        for report in all_reports:
            if report["passed"]:
                src = report["path"]
                dst = os.path.join(FIVERR_VIDEOS_DIR, report["file"])
                shutil.copy2(src, dst)
                print(f"  [OK] Copied: {report['file']}")
            else:
                print(f"  [SKIP] {report['file']} did not pass validation")

    # Summary
    print(f"\n{'=' * 60}")
    print("  VALIDATION SUMMARY")
    print(f"{'=' * 60}")
    for report in all_reports:
        status = "PASS" if report["passed"] else "FAIL"
        dur = report.get("duration", 0)
        size = report.get("size_mb", 0)
        checks_passed = sum(1 for c in report["checks"] if c["status"] == "PASS")
        checks_total = len(report["checks"])
        print(f"  {report['file']:35s} [{status}] {checks_passed}/{checks_total} checks, {dur:.1f}s, {size:.1f}MB")

    print()
    if all_passed:
        print("  All videos passed validation.")
        if args.export:
            print(f"  Exported to: {os.path.relpath(FIVERR_VIDEOS_DIR, REPO_ROOT)}")
            print(f"  Thumbnails:  {os.path.relpath(FIVERR_THUMBS_DIR, REPO_ROOT)}")
    else:
        print("  Some videos failed validation. Check reports above.")
        sys.exit(1)

    print()


if __name__ == "__main__":
    main()
