#!/usr/bin/env python3
"""
Candle Co. Image Generation Script
Generates branded images from the content calendar using ComfyUI.
"""

import json
import sys
from pathlib import Path
from automation_brain import AutomationBrain

CONTENT_CALENDAR = Path("C:/automation-machine/demo-clients/candle-co/content-calendar.json")
OUTPUT_DIR = Path("C:/automation-machine/demo-clients/candle-co/images")


def load_content_calendar():
    """Load the 30-day content calendar."""
    with open(CONTENT_CALENDAR, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_images(start_day: int = 1, end_day: int = 5, verbose: bool = True):
    """
    Generate images for a range of days from the content calendar.

    Args:
        start_day: First day to generate (1-30)
        end_day: Last day to generate (1-30)
        verbose: Show progress
    """
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load calendar
    calendar = load_content_calendar()

    # Initialize brain with ComfyUI
    brain = AutomationBrain(verbose=verbose)

    print(f"\n{'='*60}")
    print("CANDLE CO. IMAGE GENERATION")
    print(f"{'='*60}")
    print(f"Generating images for days {start_day} to {end_day}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    generated = []
    errors = []

    for i, day in enumerate(calendar[start_day-1:end_day], start=start_day):
        print(f"\n--- Day {i}: {day['post_type'].upper()} ---")
        print(f"Date: {day['date']}")
        print(f"Prompt: {day['image_prompt'][:80]}...")

        try:
            # Generate image using ComfyUI via automation_brain
            result = brain.process(
                f"generate image of {day['image_prompt']}",
                force_tool="comfyui"
            )

            print(f"Result: {result[:200]}...")
            generated.append({
                "day": i,
                "date": day["date"],
                "post_type": day["post_type"],
                "status": "success"
            })

        except Exception as e:
            print(f"ERROR: {e}")
            errors.append({
                "day": i,
                "date": day["date"],
                "error": str(e)
            })

    # Summary
    print(f"\n{'='*60}")
    print("GENERATION SUMMARY")
    print(f"{'='*60}")
    print(f"Successful: {len(generated)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  Day {err['day']} ({err['date']}): {err['error']}")

    return generated, errors


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate Candle Co. images from content calendar")
    parser.add_argument("--start", type=int, default=1, help="Start day (1-30)")
    parser.add_argument("--end", type=int, default=5, help="End day (1-30)")
    parser.add_argument("--all", action="store_true", help="Generate all 30 days")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    if args.all:
        start, end = 1, 30
    else:
        start, end = args.start, args.end

    generate_images(start, end, verbose=not args.quiet)


if __name__ == "__main__":
    main()
