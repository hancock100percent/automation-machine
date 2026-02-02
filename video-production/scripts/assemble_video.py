"""
Stage 4: Assemble Video
Loads a video structure JSON config, builds FFmpeg complex filter commands,
concatenates normalized clips with crossfade transitions and optional audio mixing.

Usage:
    python video-production/scripts/assemble_video.py configs/video1_structure.json
    python video-production/scripts/assemble_video.py configs/video2_structure.json
    python video-production/scripts/assemble_video.py configs/video3_structure.json
    python video-production/scripts/assemble_video.py --all                         # all 3 videos
    python video-production/scripts/assemble_video.py --dry-run configs/video1_structure.json  # show command only
"""

import argparse
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIGS_DIR = os.path.join(REPO_ROOT, "video-production", "configs")
NORMALIZED_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "video-assets", "normalized")
FINAL_DIR = os.path.join(REPO_ROOT, "demo-clients", "candle-co", "final-videos")


def load_structure(config_path):
    """Load a video structure JSON config."""
    with open(config_path, "r") as f:
        return json.load(f)


def resolve_clip_path(clip_source):
    """Resolve a clip source path to absolute path.
    Accepts:
      - 'normalized/filename.mp4' (relative to video-assets)
      - absolute path
      - relative to repo root
    """
    if os.path.isabs(clip_source):
        return clip_source

    # Try normalized dir first
    if clip_source.startswith("normalized/"):
        filename = clip_source.replace("normalized/", "")
        path = os.path.join(NORMALIZED_DIR, filename)
        if os.path.isfile(path):
            return path

    # Try relative to repo root
    path = os.path.join(REPO_ROOT, clip_source)
    if os.path.isfile(path):
        return path

    return None


def get_clip_duration(clip_path):
    """Get duration of a clip via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        clip_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data.get("format", {}).get("duration", 0))
    except Exception:
        pass
    return 0


def build_simple_concat(segments, output_path):
    """Build FFmpeg command for simple concat with crossfade transitions.

    Uses the concat filter with crossfade between segments.
    All clips must already be normalized to the same format.
    """
    clip_paths = []
    fade_durations = []

    for seg in segments:
        clip_source = seg["clip_source"]
        path = resolve_clip_path(clip_source)
        if not path:
            print(f"  [FAIL] Clip not found: {clip_source}")
            return None
        clip_paths.append(path)
        fade_durations.append(seg.get("fade_duration", 0.5))

    n = len(clip_paths)
    if n == 0:
        print("  [FAIL] No clips to assemble")
        return None

    if n == 1:
        # Single clip -- just copy with fade in/out
        cmd = ["ffmpeg", "-y", "-i", clip_paths[0]]
        fade_d = fade_durations[0]
        duration = get_clip_duration(clip_paths[0])
        vf = f"fade=t=in:st=0:d={fade_d},fade=t=out:st={max(0, duration - fade_d)}:d={fade_d}"
        af = f"afade=t=in:st=0:d={fade_d},afade=t=out:st={max(0, duration - fade_d)}:d={fade_d}"
        cmd += ["-vf", vf, "-af", af]
        cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]
        cmd += [output_path]
        return cmd

    # Multi-clip: use xfade for video and acrossfade for audio
    # Build complex filter graph
    inputs = []
    for path in clip_paths:
        inputs += ["-i", path]

    # Get durations for calculating offsets
    durations = []
    for path in clip_paths:
        d = get_clip_duration(path)
        if d <= 0:
            print(f"  [WARN] Could not get duration for {os.path.basename(path)}, using segment config")
        durations.append(d)

    # Build xfade chain
    # Each xfade combines two streams, outputting one
    # offset = cumulative duration - cumulative crossfade durations
    filter_parts = []
    xfade_duration = 0.5  # consistent crossfade length

    # First, add fade-in to first clip
    filter_parts.append(f"[0:v]fade=t=in:st=0:d={xfade_duration}[v0f];")
    filter_parts.append(f"[0:a]afade=t=in:st=0:d={xfade_duration}[a0f];")

    if n == 2:
        # Simple case: 2 clips with one crossfade
        offset = max(0, durations[0] - xfade_duration)
        filter_parts.append(
            f"[v0f][1:v]xfade=transition=fade:duration={xfade_duration}:offset={offset},"
            f"fade=t=out:st={max(0, offset + durations[1] - xfade_duration)}:d={xfade_duration}[vout];"
        )
        filter_parts.append(
            f"[a0f][1:a]acrossfade=d={xfade_duration},"
            f"afade=t=out:st={max(0, offset + durations[1] - xfade_duration)}:d={xfade_duration}[aout]"
        )
    else:
        # Chain xfades for 3+ clips
        # Video chain
        cumulative_offset = 0
        prev_label = "v0f"
        for i in range(1, n):
            offset = max(0, durations[i-1] - xfade_duration) if i == 1 else max(0, durations[i-1] - xfade_duration)
            cumulative_offset += offset if i == 1 else offset

            if i < n - 1:
                out_label = f"vx{i}"
                filter_parts.append(
                    f"[{prev_label}][{i}:v]xfade=transition=fade:duration={xfade_duration}:offset={cumulative_offset}[{out_label}];"
                )
                prev_label = out_label
            else:
                # Last xfade -- add fade-out and output
                total_dur = cumulative_offset + durations[i]
                filter_parts.append(
                    f"[{prev_label}][{i}:v]xfade=transition=fade:duration={xfade_duration}:offset={cumulative_offset},"
                    f"fade=t=out:st={max(0, total_dur - xfade_duration)}:d={xfade_duration}[vout];"
                )

            # Recalculate cumulative for next iteration
            if i < n - 1:
                cumulative_offset += 0  # offset already accumulated

        # Audio chain -- use concat for audio (acrossfade only works with 2 inputs)
        # Simpler: concat all audio with short fades at boundaries
        audio_inputs = ",".join(f"[{i}:a]" for i in range(n))
        filter_parts.append(
            f"{audio_inputs}concat=n={n}:v=0:a=1,"
            f"afade=t=in:st=0:d={xfade_duration},"
            f"afade=t=out:st={max(0, sum(durations) - n * xfade_duration)}:d={xfade_duration}[aout]"
        )

    filter_complex = "\n".join(filter_parts)

    cmd = ["ffmpeg", "-y"]
    cmd += inputs
    cmd += ["-filter_complex", filter_complex]
    cmd += ["-map", "[vout]", "-map", "[aout]"]
    cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "medium",
            "-profile:v", "high", "-level:v", "4.1", "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k"]
    cmd += ["-movflags", "+faststart"]
    cmd += [output_path]

    return cmd


def build_concat_demuxer(segments, output_path):
    """Fallback: use FFmpeg concat demuxer (no transitions, but more reliable).

    This is the safe fallback when complex filter graphs cause issues.
    All clips must be normalized to the same format first.
    """
    clip_paths = []
    for seg in segments:
        path = resolve_clip_path(seg["clip_source"])
        if not path:
            print(f"  [FAIL] Clip not found: {seg['clip_source']}")
            return None
        clip_paths.append(path)

    # Write concat list file
    list_path = os.path.join(FINAL_DIR, "_concat_list.txt")
    with open(list_path, "w") as f:
        for path in clip_paths:
            # Use forward slashes for FFmpeg on Windows
            safe_path = path.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]
    return cmd


def add_background_music(video_path, music_config, output_path):
    """Mix background music into an assembled video."""
    music_source = os.path.join(REPO_ROOT, music_config["source"])
    if not os.path.isfile(music_source):
        if music_config.get("optional", False):
            print(f"  [SKIP] Optional background music not found: {music_config['source']}")
            return video_path
        else:
            print(f"  [FAIL] Background music not found: {music_config['source']}")
            return None

    volume = music_config.get("volume", 0.15)
    fade_in = music_config.get("fade_in", 2.0)
    fade_out = music_config.get("fade_out", 3.0)

    # Get video duration
    duration = get_clip_duration(video_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", music_source,
        "-filter_complex",
        f"[1:a]volume={volume},afade=t=in:st=0:d={fade_in},"
        f"afade=t=out:st={max(0, duration - fade_out)}:d={fade_out}[bg];"
        f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]
    return cmd


def assemble_video(config_path, dry_run=False, use_demuxer=False):
    """Assemble a single video from its structure config."""
    structure = load_structure(config_path)
    meta = structure.get("_meta", {})
    title = meta.get("title", "Unknown")
    output_filename = meta.get("output_filename", "output.mp4")
    segments = structure.get("segments", [])
    audio_layers = structure.get("audio_layers", [])

    print(f"\n{'=' * 60}")
    print(f"  Assembling: {title}")
    print(f"  Segments: {len(segments)}")
    print(f"  Output: {output_filename}")
    print(f"{'=' * 60}")

    # Check all clips exist
    missing = []
    for seg in segments:
        path = resolve_clip_path(seg["clip_source"])
        if not path:
            missing.append(seg["clip_source"])
        else:
            dur = get_clip_duration(path)
            print(f"  [{seg['id']:15s}] {os.path.basename(path)} ({dur:.1f}s)")

    if missing:
        print(f"\n  Missing clips ({len(missing)}):")
        for m in missing:
            print(f"    - {m}")
        print("\n  Run normalize_clips.py first, or check file names.")
        return False

    os.makedirs(FINAL_DIR, exist_ok=True)
    output_path = os.path.join(FINAL_DIR, output_filename)

    # Build assembly command
    if use_demuxer:
        print("\n  Using concat demuxer (no transitions)")
        cmd = build_concat_demuxer(segments, output_path)
    else:
        print("\n  Using xfade transitions")
        cmd = build_simple_concat(segments, output_path)

    if not cmd:
        return False

    if dry_run:
        print("\n  [DRY RUN] FFmpeg command:")
        print(f"  {' '.join(cmd)}")
        return True

    print(f"\n  Running FFmpeg...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            err_lines = result.stderr.strip().split("\n")
            for line in err_lines[-10:]:
                print(f"    {line}")
            print(f"\n  [FAIL] FFmpeg exited with code {result.returncode}")

            # Auto-fallback to demuxer if xfade fails
            if not use_demuxer:
                print("  Falling back to concat demuxer (no transitions)...")
                cmd2 = build_concat_demuxer(segments, output_path)
                if cmd2:
                    result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=300)
                    if result2.returncode == 0:
                        print(f"  [OK] Assembled (demuxer fallback): {output_filename}")
                    else:
                        print(f"  [FAIL] Demuxer fallback also failed")
                        return False
            else:
                return False
        else:
            print(f"  [OK] Assembled: {output_filename}")
    except subprocess.TimeoutExpired:
        print(f"  [FAIL] FFmpeg timed out (5 min)")
        return False

    # Add background music if configured
    for layer in audio_layers:
        music_output = output_path.replace(".mp4", "_music.mp4")
        music_cmd = add_background_music(output_path, layer, music_output)
        if isinstance(music_cmd, str):
            # Returned the input path (music skipped)
            continue
        if music_cmd and not dry_run:
            print(f"\n  Mixing background music...")
            try:
                result = subprocess.run(music_cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    # Replace original with music version
                    os.replace(music_output, output_path)
                    print(f"  [OK] Background music mixed in")
                else:
                    print(f"  [WARN] Music mix failed, keeping video without music")
                    if os.path.exists(music_output):
                        os.remove(music_output)
            except Exception as e:
                print(f"  [WARN] Music mix error: {e}")

    # Final check
    if os.path.isfile(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        duration = get_clip_duration(output_path)
        print(f"\n  Final: {output_filename} ({duration:.1f}s, {size_mb:.1f}MB)")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Assemble video from structure config")
    parser.add_argument("config", nargs="?", help="Path to video structure JSON config")
    parser.add_argument("--all", action="store_true", help="Assemble all 3 videos")
    parser.add_argument("--dry-run", action="store_true", help="Show FFmpeg commands without running")
    parser.add_argument("--demuxer", action="store_true", help="Use concat demuxer (no transitions, more reliable)")
    args = parser.parse_args()

    print("=" * 60)
    print("  VIDEO PRODUCTION PIPELINE - Stage 4: Assemble Video")
    print("=" * 60)

    if args.all:
        configs = [
            os.path.join(CONFIGS_DIR, "video1_structure.json"),
            os.path.join(CONFIGS_DIR, "video2_structure.json"),
            os.path.join(CONFIGS_DIR, "video3_structure.json"),
        ]
        results = []
        for config in configs:
            if os.path.isfile(config):
                ok = assemble_video(config, dry_run=args.dry_run, use_demuxer=args.demuxer)
                results.append((os.path.basename(config), ok))
            else:
                print(f"  [SKIP] Config not found: {config}")
                results.append((os.path.basename(config), False))

        print(f"\n{'=' * 60}")
        print("  ASSEMBLY RESULTS")
        print(f"{'=' * 60}")
        for name, ok in results:
            status = "OK" if ok else "FAIL"
            print(f"  {name:30s} [{status}]")
        print()

    elif args.config:
        config_path = args.config
        if not os.path.isabs(config_path):
            # Try relative to configs dir
            candidate = os.path.join(CONFIGS_DIR, config_path)
            if os.path.isfile(candidate):
                config_path = candidate
            else:
                config_path = os.path.abspath(config_path)

        if not os.path.isfile(config_path):
            print(f"  [FAIL] Config not found: {config_path}")
            sys.exit(1)

        ok = assemble_video(config_path, dry_run=args.dry_run, use_demuxer=args.demuxer)
        if not ok:
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
