"""
Generate filler clips from existing assets (SDXL images + text cards).

Creates normalized 1920x1080@30fps clips to fill gaps where screen recordings
and Canva exports are missing. Outputs to the normalized/ directory so the
existing assemble_video.py pipeline can use them directly.

Usage:
    python video-production/scripts/generate_filler_clips.py
    python video-production/scripts/generate_filler_clips.py --preview
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
SDXL_DIR = BASE / "output"
NORMALIZED_DIR = BASE / "demo-clients" / "candle-co" / "video-assets" / "normalized"
NORM_CONFIG = BASE / "video-production" / "configs" / "normalization_standard.json"

# Target specs
WIDTH = 1920
HEIGHT = 1080
FPS = 30
CRF = 23


def run_ffmpeg(args, desc=""):
    cmd = ["ffmpeg", "-y"] + args
    print(f"  [ffmpeg] {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr[-300:]}")
        return False
    return True


def run_ffprobe(path):
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0.0
    data = json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", 0))


def image_to_normalized_clip(image_path, output_path, duration=4.0, zoom="in"):
    """Convert a still image to a 1080p@30fps clip with Ken Burns effect + silent audio."""
    if zoom == "in":
        zoompan = (
            f"zoompan=z='min(zoom+0.0004,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration * 25)}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        )
    elif zoom == "out":
        zoompan = (
            f"zoompan=z='if(eq(on,1),1.08,max(zoom-0.0004,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration * 25)}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        )
    else:
        zoompan = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:black"
        )

    args = [
        "-loop", "1", "-i", str(image_path),
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000",
        "-filter_complex",
        f"[0:v]{zoompan},setsar=1,format=yuv420p[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(CRF),
        "-profile:v", "high", "-level:v", "4.1", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        "-t", str(duration), "-shortest",
        str(output_path)
    ]
    return run_ffmpeg(args, f"Image -> {duration}s clip: {image_path.name}")


def text_card_to_normalized_clip(text_lines, output_path, duration=4.0, font_size=56):
    """Create a text-on-dark-background clip at 1080p@30fps with silent audio."""
    drawtext_parts = []
    total_lines = len(text_lines)
    line_height = font_size + 30
    start_y = (HEIGHT - total_lines * line_height) // 2

    for i, line in enumerate(text_lines):
        y_pos = start_y + i * line_height
        escaped = line.replace("'", "\\\\'").replace(":", "\\\\:")
        drawtext_parts.append(
            f"drawtext=text='{escaped}':fontsize={font_size}:fontcolor=white"
            f":x=(w-text_w)/2:y={y_pos}:font=Arial"
        )

    vf = ",".join(drawtext_parts) + ",format=yuv420p"

    args = [
        "-f", "lavfi", "-i",
        f"color=c=0x1a1a2e:s={WIDTH}x{HEIGHT}:d={duration}:r={FPS}",
        "-f", "lavfi", "-i",
        f"anullsrc=channel_layout=stereo:sample_rate=48000",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", str(CRF),
        "-profile:v", "high", "-level:v", "4.1", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        "-t", str(duration), "-shortest",
        str(output_path)
    ]
    return run_ffmpeg(args, f"Text card ({duration}s): {text_lines[0][:40]}...")


def generate_all(preview=False):
    """Generate all filler clips needed for Video 1 assembly."""
    print("\n=== GENERATING FILLER CLIPS FOR VIDEO 1 ===\n")

    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)

    # Find SDXL images
    sdxl_images = sorted(SDXL_DIR.glob("*.png"))
    print(f"  Found {len(sdxl_images)} SDXL images in {SDXL_DIR}")

    clips_to_generate = []

    # 1. "Demo" replacement: tagline text card + SDXL product showcase
    # Instead of a screen recording, we show:
    #   a) Tagline card (3s)
    #   b) SDXL image 1 with Ken Burns (4s)
    #   c) SDXL image 2 with Ken Burns (4s)
    # Total: ~11s replacing the 37s demo (shorter is better for first version)

    clips_to_generate.append({
        "name": "demo_tagline_norm.mp4",
        "type": "text_card",
        "text_lines": ["One command.", "", "AI plans your entire month", "of marketing content."],
        "duration": 3.5,
        "font_size": 54,
    })

    if len(sdxl_images) >= 1:
        clips_to_generate.append({
            "name": "sdxl_showcase_01_norm.mp4",
            "type": "image",
            "source": sdxl_images[0],
            "duration": 4.0,
            "zoom": "in",
        })

    if len(sdxl_images) >= 2:
        clips_to_generate.append({
            "name": "sdxl_showcase_02_norm.mp4",
            "type": "image",
            "source": sdxl_images[3] if len(sdxl_images) > 3 else sdxl_images[1],
            "duration": 4.0,
            "zoom": "out",
        })

    # 2. "Calendar preview" replacement: text card showing what the system generates
    clips_to_generate.append({
        "name": "calendar_preview_norm.mp4",
        "type": "text_card",
        "text_lines": [
            "AI-Generated Content Calendar",
            "",
            "30 unique captions",
            "Platform-optimized hashtags",
            "Custom image prompts",
            "Strategic posting schedule",
        ],
        "duration": 5.0,
        "font_size": 44,
    })

    # 3. "Stats animation" replacement: stats text card
    clips_to_generate.append({
        "name": "stats_animation_norm.mp4",
        "type": "text_card",
        "text_lines": [
            "30 posts generated",
            "5 custom AI images",
            "Under 10 minutes",
            "Total cost\\: $0.04",
        ],
        "duration": 4.5,
        "font_size": 52,
    })

    # Preview mode
    if preview:
        print(f"\n  Would generate {len(clips_to_generate)} clips:\n")
        for clip in clips_to_generate:
            print(f"    {clip['name']:40s} {clip['duration']:.1f}s  ({clip['type']})")
        total = sum(c["duration"] for c in clips_to_generate)
        print(f"\n  Total filler duration: {total:.1f}s")
        print(f"  + v1_intro_avatar_norm.mp4 (~11s)")
        print(f"  + i2v_wan_00001_norm.mp4 (~3s)")
        print(f"  + v1_outro_avatar_norm.mp4 (~12s)")
        print(f"  Estimated final video: ~{total + 11 + 3 + 12:.0f}s")
        return True

    # Generate each clip
    success_count = 0
    for clip in clips_to_generate:
        output = NORMALIZED_DIR / clip["name"]

        if output.exists() and output.stat().st_size > 50000:
            print(f"  [SKIP] Already exists: {clip['name']}")
            success_count += 1
            continue

        if clip["type"] == "text_card":
            ok = text_card_to_normalized_clip(
                clip["text_lines"], output,
                duration=clip["duration"],
                font_size=clip.get("font_size", 56)
            )
        elif clip["type"] == "image":
            ok = image_to_normalized_clip(
                clip["source"], output,
                duration=clip["duration"],
                zoom=clip.get("zoom", "in")
            )
        else:
            print(f"  [SKIP] Unknown type: {clip['type']}")
            continue

        if ok and output.exists():
            size_kb = output.stat().st_size / 1024
            dur = run_ffprobe(output)
            print(f"    -> {clip['name']} ({dur:.1f}s, {size_kb:.0f}KB)")
            success_count += 1
        else:
            print(f"    [FAILED] {clip['name']}")

    print(f"\n  Generated {success_count}/{len(clips_to_generate)} clips")
    return success_count == len(clips_to_generate)


def main():
    parser = argparse.ArgumentParser(description="Generate filler clips from SDXL images and text cards")
    parser.add_argument("--preview", action="store_true", help="Show what would be generated")
    args = parser.parse_args()

    success = generate_all(preview=args.preview)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
