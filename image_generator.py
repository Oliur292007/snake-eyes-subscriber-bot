from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


# ==========================================
# FILES
# ==========================================

TEMPLATE = Path("assets/subscriber_template.png")
OUTPUT_DIR = Path("generated")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# FONT
# ==========================================

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ==========================================
# HELPER
# ==========================================

def load_font(size):
    try:
        return ImageFont.truetype(
            FONT_PATH,
            size
        )
    except Exception:
        return ImageFont.load_default()


def centered_x(draw, text, font, image_width):
    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]

    return (image_width - text_width) // 2


# ==========================================
# GENERATE IMAGE
# ==========================================

def generate_milestone_image(
    milestone,
    next_goal
):
    if not TEMPLATE.exists():
        raise FileNotFoundError(
            f"Template not found: {TEMPLATE}"
        )

    image = Image.open(
        TEMPLATE
    ).convert("RGB")

    draw = ImageDraw.Draw(image)

    width, height = image.size

    # ======================================
    # MILESTONE NUMBER
    # ======================================

    milestone_text = f"{milestone:,}"

    # Large number
    milestone_font = load_font(
        int(width * 0.105)
    )

    x = centered_x(
        draw,
        milestone_text,
        milestone_font,
        width
    )

    # Positioned above "SUBSCRIBERS"
    y = int(height * 0.405)

    # Black shadow
    draw.text(
        (x + 5, y + 5),
        milestone_text,
        font=milestone_font,
        fill=(0, 0, 0),
        stroke_width=5,
        stroke_fill=(0, 0, 0)
    )

    # Main white text
    draw.text(
        (x, y),
        milestone_text,
        font=milestone_font,
        fill=(255, 255, 255),
        stroke_width=3,
        stroke_fill=(120, 0, 0)
    )

    # ======================================
    # NEXT GOAL
    # ======================================

    next_goal_text = (
        f"NEXT GOAL: {next_goal:,}"
    )

    next_font = load_font(
        int(width * 0.034)
    )

    next_x = centered_x(
        draw,
        next_goal_text,
        next_font,
        width
    )

    next_y = int(height * 0.835)

    # Shadow
    draw.text(
        (next_x + 3, next_y + 3),
        next_goal_text,
        font=next_font,
        fill=(0, 0, 0)
    )

    # Red text
    draw.text(
        (next_x, next_y),
        next_goal_text,
        font=next_font,
        fill=(255, 35, 35),
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    # ======================================
    # SAVE
    # ======================================

    output_file = (
        OUTPUT_DIR /
        f"subscriber_{milestone}.png"
    )

    image.save(
        output_file,
        "PNG",
        optimize=True
    )

    return output_file


# ==========================================
# LOCAL TEST
# ==========================================

if __name__ == "__main__":

    output = generate_milestone_image(
        milestone=140,
        next_goal=150
    )

    print(
        f"Generated: {output}"
    )
