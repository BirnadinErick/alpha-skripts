import os
import urllib.parse
import urllib.request
from pathlib import Path

# Path to the .env file
ENV_PATH = Path(__file__).parent / ".telegram.env"
THRESHOLD = 30


def load_env(env_path):
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("\"'")
    return env_vars


def get_battery_percentage():
    for bat in ["BAT0", "BAT1"]:
        path = f"/sys/class/power_supply/{bat}/capacity"
        if os.path.exists(path):
            with open(path, "r") as f:
                return int(f.read().strip())
    return None


def send_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    urllib.request.urlopen(url, data=data)


if __name__ == "__main__":
    env = load_env(ENV_PATH)
    token = env.get("TELEGRAM_TOKEN")
    chat_id = env.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise ValueError(
            "TELEGRAM_TOKEN or TELEGRAM_CHAT_ID missing in .telegram.env file"
        )

    level = get_battery_percentage()
    if level is not None and level <= THRESHOLD:
        send_telegram(token, chat_id, f"Warning: Battery level is at {level}%")
