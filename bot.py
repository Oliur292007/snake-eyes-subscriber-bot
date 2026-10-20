import os
import json
import math
import requests
from pathlib import Path

from image_generator import generate_milestone_image


# ==========================================
# CONFIGURATION
# ==========================================

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

CHANNEL_ID = "UC3AzQdeDjMfVjyt8ZTNkR3A"

MILESTONE_STEP = 10

STATE_FILE = Path("data/state.json")


# ==========================================
# STATE
# ==========================================

def load_state():
    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not STATE_FILE.exists():
        return None

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception:
        return None


def save_state(state):
    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            state,
            file,
            indent=2
        )


# ==========================================
# YOUTUBE
# ==========================================

def get_subscriber_count():

    url = (
        "https://www.googleapis.com/"
        "youtube/v3/channels"
    )

    params = {
        "part": "statistics",
        "id": CHANNEL_ID,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("items"):
        raise RuntimeError(
            "YouTube channel was not found."
        )

    statistics = data["items"][0]["statistics"]

    return int(
        statistics["subscriberCount"]
    )


# ==========================================
# NEXT MILESTONE
# ==========================================

def get_next_milestone(subscribers):

    return (
        math.ceil(
            subscribers /
            MILESTONE_STEP
        ) * MILESTONE_STEP
    )


# ==========================================
# DISCORD
# ==========================================

def send_discord_announcement(
    milestone,
    next_goal,
    image_path
):

    message = (
        "🎉 **CONGRATULATIONS!** 🎉\n\n"

        f"🐍 **Snake Eyes YT** has reached "
        f"**{milestone:,} Subscribers!**\n\n"

        "❤️ Thank you for your amazing support!\n"

        f"🚀 **Next Goal: "
        f"{next_goal:,} Subscribers!**\n\n"

        "🔗 "
        "https://www.youtube.com/"
        "@snake_eyes_98538"
    )

    with open(
        image_path,
        "rb"
    ) as image_file:

        files = {
            "file": (
                image_path.name,
                image_file,
                "image/png"
            )
        }

        payload = {
            "username":
                "Snake Eyes Subscriber Bot",

            "content":
                message
        }

        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=payload,
            files=files,
            timeout=60
        )

    if response.status_code not in (
        200,
        204
    ):
        raise RuntimeError(
            "Discord webhook failed: "
            f"{response.status_code} "
            f"{response.text}"
        )


# ==========================================
# MAIN
# ==========================================

def main():

    print("=" * 50)
    print("🐍 SNAKE EYES YT SUBSCRIBER BOT")
    print("=" * 50)

    # --------------------------------------
    # Current subscribers
    # --------------------------------------

    subscribers = get_subscriber_count()

    print(
        f"Current subscribers: "
        f"{subscribers:,}"
    )

    # --------------------------------------
    # Load state
    # --------------------------------------

    state = load_state()

    # --------------------------------------
    # FIRST RUN
    # --------------------------------------

    if state is None:

        next_milestone = get_next_milestone(
            subscribers
        )

        state = {
            "last_announced_milestone": 0,

            "next_milestone":
                next_milestone
        }

        save_state(state)

        print(
            "First run detected."
        )

        print(
            f"Next milestone: "
            f"{next_milestone:,}"
        )

        print(
            "No announcement sent."
        )

        return

    # --------------------------------------
    # Existing state
    # --------------------------------------

    next_milestone = int(
        state["next_milestone"]
    )

    last_announced = int(
        state["last_announced_milestone"]
    )

    print(
        f"Next milestone: "
        f"{next_milestone:,}"
    )

    print(
        f"Last announced: "
        f"{last_announced:,}"
    )

    # --------------------------------------
    # Find every milestone reached
    # --------------------------------------

    milestones_to_announce = []

    while subscribers >= next_milestone:

        milestones_to_announce.append(
            next_milestone
        )

        next_milestone += MILESTONE_STEP

    # --------------------------------------
    # Nothing new
    # --------------------------------------

    if not milestones_to_announce:

        print(
            "No new milestone."
        )

        return

    # --------------------------------------
    # Announce each missed/reached milestone
    # --------------------------------------

    for milestone in milestones_to_announce:

        next_goal = (
            milestone +
            MILESTONE_STEP
        )

        print(
            f"🎉 Announcing milestone: "
            f"{milestone:,}"
        )

        # Generate premium image

        image_path = (
            generate_milestone_image(
                milestone=milestone,
                next_goal=next_goal
            )
        )

        print(
            f"Image generated: "
            f"{image_path}"
        )

        # Send Discord message

        send_discord_announcement(
            milestone=milestone,
            next_goal=next_goal,
            image_path=image_path
        )

        print(
            f"✅ {milestone:,} announcement sent."
        )

        # Update last announced milestone

        state[
            "last_announced_milestone"
        ] = milestone

        save_state(state)

    # --------------------------------------
    # Save next target
    # --------------------------------------

    state[
        "next_milestone"
    ] = next_milestone

    save_state(state)

    print(
        f"Next target: "
        f"{next_milestone:,}"
    )

    print(
        "✅ State saved."
    )


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()
