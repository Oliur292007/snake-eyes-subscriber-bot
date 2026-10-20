import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

# ==============================
# CONFIGURATION
# ==============================

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

CHANNEL_ID = "UC3AzQdeDjMfVjyt8ZTNkR3A"

MILESTONE_STEP = 10

STATE_FILE = Path("data/state.json")

# ==============================
# STATE MANAGEMENT
# ==============================

def load_state():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not STATE_FILE.exists():
        return {
            "last_announced_milestone": 0
        }

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {
            "last_announced_milestone": 0
        }


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)


# ==============================
# YOUTUBE
# ==============================

def get_subscriber_count():
    params = urllib.parse.urlencode({
        "part": "statistics",
        "id": CHANNEL_ID,
        "key": YOUTUBE_API_KEY
    })

    url = (
        "https://www.googleapis.com/youtube/v3/channels?"
        + params
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Snake-Eyes-Subscriber-Bot/1.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    if not data.get("items"):
        raise RuntimeError("YouTube channel was not found.")

    statistics = data["items"][0]["statistics"]

    return int(statistics["subscriberCount"])


# ==============================
# MILESTONE
# ==============================

def get_reached_milestone(subscribers):
    return (subscribers // MILESTONE_STEP) * MILESTONE_STEP


# ==============================
# DISCORD
# ==============================

def send_discord_message(subscribers, milestone):
    next_goal = milestone + MILESTONE_STEP

    message = {
        "username": "Snake Eyes Subscriber Bot",
        "content": (
            "🎉 **CONGRATULATIONS!** 🎉\n\n"
            f"🐍 **Snake Eyes YT** has reached **{milestone:,} Subscribers!**\n\n"
            "❤️ Thank you everyone for supporting the channel!\n"
            f"🚀 **Next Goal: {next_goal:,} Subscribers!**\n\n"
            "🔗 https://www.youtube.com/@snake_eyes_98538"
        )
    }

    payload = json.dumps(message).encode("utf-8")

    request = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Snake-Eyes-Subscriber-Bot/1.0"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 204):
            raise RuntimeError(
                f"Discord returned HTTP {response.status}"
            )


# ==============================
# MAIN
# ==============================

def main():
    print("========================================")
    print(" Snake Eyes YT Subscriber Bot")
    print("========================================")

    subscribers = get_subscriber_count()

    print(f"Current subscribers: {subscribers:,}")

    state = load_state()

    last_announced = int(
        state.get("last_announced_milestone", 0)
    )

    current_milestone = get_reached_milestone(subscribers)

    print(f"Current milestone: {current_milestone:,}")
    print(f"Last announced: {last_announced:,}")

    # No milestone reached yet
    if current_milestone < MILESTONE_STEP:
        print("No milestone reached yet.")
        return

    # Already announced
    if current_milestone <= last_announced:
        print("No new milestone.")
        return

    # New milestone
    print(
        f"🎉 New milestone detected: "
        f"{current_milestone:,}"
    )

    send_discord_message(
        subscribers,
        current_milestone
    )

    state["last_announced_milestone"] = current_milestone

    save_state(state)

    print("✅ Discord announcement sent.")
    print("✅ State saved.")


if __name__ == "__main__":
    main()
