"""Generate Fiverr gig thumbnails from existing AI-generated assets.

Creates 1280x720 thumbnails optimized for Fiverr gig listings.
Uses existing candle-co demo images as showcase materials.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
OUTPUT_DIR = SCRIPT_DIR  # thumbnails go in fiverr-assets/thumbnails/
IMAGES_DIR = os.path.join(REPO_ROOT, "output")

# Fiverr thumbnail dimensions
WIDTH, HEIGHT = 1280, 720

# Fonts
FONT_DIR = "C:/Windows/Fonts"
FONT_BOLD = os.path.join(FONT_DIR, "arialbd.ttf")
FONT_REGULAR = os.path.join(FONT_DIR, "arial.ttf")
FONT_IMPACT = os.path.join(FONT_DIR, "impact.ttf")


def create_gradient(width, height, color1, color2, direction="horizontal"):
    """Create a gradient image."""
    img = Image.new("RGB", (width, height))
    for i in range(width if direction == "horizontal" else height):
        ratio = i / (width if direction == "horizontal" else height)
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        if direction == "horizontal":
            ImageDraw.Draw(img).line([(i, 0), (i, height)], fill=(r, g, b))
        else:
            ImageDraw.Draw(img).line([(0, i), (width, i)], fill=(r, g, b))
    return img


def add_text_with_shadow(draw, position, text, font, fill, shadow_color=(0, 0, 0), offset=3):
    """Draw text with a drop shadow."""
    x, y = position
    draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)


def create_ai_images_thumbnail():
    """Create thumbnail for AI Image Generation gig.

    Layout: 4-image grid on left (60%), text on right (40%) with gradient.
    Showcases the variety of AI-generated product images.
    """
    thumb = Image.new("RGB", (WIDTH, HEIGHT))

    # Best showcase images (candle variety)
    image_files = [
        os.path.join(IMAGES_DIR, "20260125_061654_automation_machine_00010_.png"),  # lavender candles
        os.path.join(IMAGES_DIR, "20260125_061910_automation_machine_00012_.png"),  # product candle
        os.path.join(IMAGES_DIR, "20260125_062127_automation_machine_00014_.png"),  # holiday candle
        os.path.join(IMAGES_DIR, "20260125_074749_automation_machine_00015_.png"),  # artistic candle
    ]

    # Create 2x2 grid on the left side (768x720)
    grid_width = 768
    cell_w, cell_h = grid_width // 2, HEIGHT // 2
    gap = 4  # pixel gap between images

    for idx, img_path in enumerate(image_files):
        if not os.path.exists(img_path):
            print(f"  WARNING: Missing {img_path}")
            continue
        img = Image.open(img_path)
        # Crop to square center, then resize to cell
        side = min(img.width, img.height)
        left = (img.width - side) // 2
        top = (img.height - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((cell_w - gap, cell_h - gap), Image.LANCZOS)

        row, col = divmod(idx, 2)
        x = col * cell_w + (gap // 2)
        y = row * cell_h + (gap // 2)
        thumb.paste(img, (x, y))

    # Right panel: gradient background
    panel_x = grid_width
    panel_w = WIDTH - grid_width
    gradient = create_gradient(panel_w, HEIGHT, (25, 25, 35), (60, 30, 80), "vertical")
    thumb.paste(gradient, (panel_x, 0))

    # Add a subtle border between grid and panel
    draw = ImageDraw.Draw(thumb)
    draw.line([(panel_x, 0), (panel_x, HEIGHT)], fill=(120, 60, 180), width=3)

    # Text on right panel
    title_font = ImageFont.truetype(FONT_IMPACT, 52)
    sub_font = ImageFont.truetype(FONT_BOLD, 26)
    detail_font = ImageFont.truetype(FONT_REGULAR, 22)
    price_font = ImageFont.truetype(FONT_IMPACT, 48)

    text_x = panel_x + 30

    # "AI" badge
    badge_y = 60
    draw.rounded_rectangle(
        [(text_x, badge_y), (text_x + 65, badge_y + 40)],
        radius=8, fill=(120, 60, 200)
    )
    badge_font = ImageFont.truetype(FONT_BOLD, 24)
    draw.text((text_x + 14, badge_y + 6), "AI", font=badge_font, fill=(255, 255, 255))

    # Title
    add_text_with_shadow(draw, (text_x, 120), "Product", title_font, (255, 255, 255), offset=2)
    add_text_with_shadow(draw, (text_x, 175), "Images", title_font, (255, 255, 255), offset=2)

    # Accent line
    draw.rectangle([(text_x, 240), (text_x + 100, 245)], fill=(180, 100, 255))

    # Features
    features = [
        "Photorealistic Quality",
        "Brand-Consistent Style",
        "Commercial License",
        "Multiple Formats",
    ]
    y = 265
    check_color = (140, 230, 140)
    for feat in features:
        draw.text((text_x, y), "+", font=detail_font, fill=check_color)
        draw.text((text_x + 22, y), feat, font=detail_font, fill=(220, 220, 230))
        y += 32

    # Price badge
    price_y = HEIGHT - 130
    draw.rounded_rectangle(
        [(text_x, price_y), (text_x + 200, price_y + 60)],
        radius=12, fill=(40, 180, 80)
    )
    draw.text((text_x + 18, price_y + 4), "From $15", font=price_font, fill=(255, 255, 255))

    # Tagline
    draw.text(
        (text_x, HEIGHT - 55),
        "No Photographer Needed",
        font=sub_font, fill=(180, 180, 200)
    )

    # Save
    out_path = os.path.join(OUTPUT_DIR, "ai-images-thumb.jpg")
    thumb.save(out_path, "JPEG", quality=95)
    print(f"  Saved: {out_path}")
    return out_path


def create_analytics_thumbnail():
    """Create thumbnail for Analytics Dashboard gig.

    Layout: Full-width dark gradient with mock dashboard elements and text.
    Since no real dashboard screenshot exists, create a professional graphic.
    """
    # Dark gradient background
    thumb = create_gradient(WIDTH, HEIGHT, (15, 20, 40), (30, 40, 70), "vertical")
    draw = ImageDraw.Draw(thumb)

    # Mock dashboard elements (left side) -- simplified chart bars
    chart_x, chart_y = 60, 180
    chart_w, chart_h = 520, 380

    # Dashboard frame
    draw.rounded_rectangle(
        [(chart_x - 10, chart_y - 50), (chart_x + chart_w + 10, chart_y + chart_h + 20)],
        radius=12, fill=(25, 30, 55), outline=(60, 70, 110), width=2
    )

    # Mini title bar dots
    for i, color in enumerate([(255, 90, 90), (255, 190, 50), (90, 220, 90)]):
        draw.ellipse(
            [(chart_x + 8 + i * 22, chart_y - 38), (chart_x + 22 + i * 22, chart_y - 24)],
            fill=color
        )

    # Bar chart
    bar_data = [0.45, 0.72, 0.58, 0.88, 0.65, 0.92, 0.78, 0.55, 0.83, 0.70, 0.95, 0.60]
    bar_w = (chart_w - 40) // len(bar_data)
    bar_colors = [
        (80, 140, 255), (100, 160, 255), (80, 140, 255), (120, 180, 255),
        (80, 140, 255), (140, 200, 255), (100, 160, 255), (80, 140, 255),
        (120, 180, 255), (100, 160, 255), (160, 220, 255), (80, 140, 255),
    ]
    for i, (val, color) in enumerate(zip(bar_data, bar_colors)):
        bx = chart_x + 20 + i * bar_w
        bar_height = int(val * (chart_h - 40))
        by = chart_y + chart_h - 10 - bar_height
        draw.rounded_rectangle(
            [(bx + 2, by), (bx + bar_w - 4, chart_y + chart_h - 10)],
            radius=4, fill=color
        )

    # Trend line overlay
    points = []
    for i, val in enumerate(bar_data):
        px = chart_x + 20 + i * bar_w + bar_w // 2
        py = chart_y + chart_h - 10 - int(val * (chart_h - 40)) - 15
        points.append((px, py))
    if len(points) > 1:
        draw.line(points, fill=(255, 200, 60), width=3)
        for px, py in points:
            draw.ellipse([(px - 4, py - 4), (px + 4, py + 4)], fill=(255, 200, 60))

    # Mini stat cards above chart
    stats = [
        ("2.4K", "Followers", (80, 200, 120)),
        ("89%", "Engagement", (80, 140, 255)),
        ("+34%", "Growth", (255, 180, 60)),
    ]
    for i, (val, label, color) in enumerate(stats):
        sx = chart_x + i * 180
        sy = chart_y - 130
        draw.rounded_rectangle(
            [(sx, sy), (sx + 160, sy + 70)],
            radius=8, fill=(30, 35, 60), outline=(50, 60, 90), width=1
        )
        stat_font = ImageFont.truetype(FONT_BOLD, 28)
        label_font = ImageFont.truetype(FONT_REGULAR, 16)
        draw.text((sx + 15, sy + 8), val, font=stat_font, fill=color)
        draw.text((sx + 15, sy + 42), label, font=label_font, fill=(150, 160, 190))

    # Right side: Text content
    text_x = 650
    title_font = ImageFont.truetype(FONT_IMPACT, 54)
    sub_font = ImageFont.truetype(FONT_BOLD, 24)
    detail_font = ImageFont.truetype(FONT_REGULAR, 21)
    price_font = ImageFont.truetype(FONT_IMPACT, 44)

    # Badge
    draw.rounded_rectangle(
        [(text_x, 50), (text_x + 145, 88)],
        radius=8, fill=(80, 140, 255)
    )
    badge_font = ImageFont.truetype(FONT_BOLD, 20)
    draw.text((text_x + 10, 56), "ANALYTICS", font=badge_font, fill=(255, 255, 255))

    # Title
    add_text_with_shadow(draw, (text_x, 110), "Real-Time", title_font, (255, 255, 255), offset=2)
    add_text_with_shadow(draw, (text_x, 165), "Dashboard", title_font, (255, 255, 255), offset=2)

    # Accent line
    draw.rectangle([(text_x, 232), (text_x + 120, 237)], fill=(80, 180, 255))

    # Features
    features = [
        "Track All KPIs",
        "Post Performance",
        "Audience Insights",
        "Growth Metrics",
        "Export Reports",
    ]
    y = 260
    for feat in features:
        draw.text((text_x, y), "+", font=detail_font, fill=(80, 200, 255))
        draw.text((text_x + 22, y), feat, font=detail_font, fill=(200, 210, 230))
        y += 32

    # "Included" badge
    inc_y = HEIGHT - 130
    draw.rounded_rectangle(
        [(text_x, inc_y), (text_x + 310, inc_y + 50)],
        radius=10, fill=(40, 60, 100), outline=(80, 140, 255), width=2
    )
    inc_font = ImageFont.truetype(FONT_BOLD, 22)
    draw.text((text_x + 15, inc_y + 12), "Included with Every Package", font=inc_font, fill=(180, 220, 255))

    # Tagline
    draw.text(
        (text_x, HEIGHT - 55),
        "AI Marketing Automation",
        font=sub_font, fill=(140, 150, 180)
    )

    # Save
    out_path = os.path.join(OUTPUT_DIR, "analytics-thumb.jpg")
    thumb.save(out_path, "JPEG", quality=95)
    print(f"  Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    print("Generating Fiverr gig thumbnails...")
    print()

    print("[1/2] AI Image Generation thumbnail")
    create_ai_images_thumbnail()
    print()

    print("[2/2] Analytics Dashboard thumbnail")
    create_analytics_thumbnail()
    print()

    print("Done! All thumbnails saved to fiverr-assets/thumbnails/")
