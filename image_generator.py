from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


# ==============================
# FILES
# ==============================

TEMPLATE = Path("assets/subscriber_template.png")
OUTPUT_DIR = Path("generated")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# FONT
# ==============================

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ==============================
# GENERATE MILESTONE IMAGE
# ==============================

def generate_milestone_image(milestone, next_goal):
    if not TEMPLATE.exists():
        raise FileNotFoundError(
            f"Template not found: {TEMPLATE}"
        )

    image = Image.open(TEMPLATE).convert("RGBA")

    draw = ImageDraw.Draw(image)

    width, height = image.size

    # --------------------------------
    # Subscriber number
    # --------------------------------

    subscriber_text = f"{milestone:,}"

    # Large dynamic subscriber number
    font_size = int(width * 0.105)

    try:
        font = ImageFont.truetype(
            FONT_PATH,
            font_size
        )
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox(
        (0, 0),
        subscriber_text,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center position
    x = (width - text_width) // 2

    # This position is intentionally around
    # the existing "SUBSCRIBERS" section.
    y = int(height * 0.34)

    # Dark outline
    outline_width = max(3, width // 300)

    draw.text(
        (x, y),
        subscriber_text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=outline_width,
        stroke_fill=(0, 0, 0, 255)
    )

    # --------------------------------
    # Next goal
    # --------------------------------

    next_text = f"NEXT GOAL: {next_goal:,}"

    next_font_size = int(width * 0.035)

    try:
        next_font = ImageFont.truetype(
            FONT_PATH,
            next_font_size
        )
    except Exception:
        next_font = ImageFont.load_default()

    next_bbox = draw.textbbox(
        (0, 0),
        next_text,
        font=next_font
    )

    next_width = next_bbox[2] - next_bbox[0]

    next_x = (width - next_width) // 2
    next_y = int(height * 0.82)

    draw.text(
        (next_x, next_y),
        next_text,
        font=next_font,
        fill=(255, 30, 30, 255),
        stroke_width=max(2, width // 500),
        stroke_fill=(0, 0, 0, 255)
    )

    # --------------------------------
    # Save
    # --------------------------------

    output_file = (
        OUTPUT_DIR /
        f"subscriber_{milestone}.png"
    )

    image.convert("RGB").save(
        output_file,
        "PNG",
        optimize=True
    )

    return output_file


# ==============================
# TEST
# ==============================

if __name__ == "__main__":
    output = generate_milestone_image(
        milestone=140,
        next_goal=150
    )

    print(f"Generated: {output}")
