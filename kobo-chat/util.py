import json
import os
import secrets
import string
import urllib.request

PHONE_NOTIFICATION_TOPIC = os.environ.get("GLYPH_NTFY_TOPIC")


def get_base_api():
    return "/api"


def generate_client_id():
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(6)
    )  # 6 characters long


# Get friendly suffix for dates like "13th" and "1st"
def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def format_date_with_ordinal(dt):
    return dt.strftime("%A %b ") + ordinal(dt.day)


def fetch_public_api(room, sender, type_prefix, url, headers={}):
    room.add_system_message(
        f"Fetching {type_prefix} for {sender} <small>(be sure to <a href='.'>Refresh</a> after)</small>"
    )

    try:
        headers = {
            "User-Agent": "ebook-chat/1.0.0 (+https://github.com/horizoncarlo/glyph-epub)",
            "Accept": "application/json",
        }

        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.load(resp)
        return data
    except Exception as e:
        print(f"Failed to get {type_prefix} API at {url}: {e}")

    room.add_system_message(f"Failed to get {type_prefix} :(")
    return {}


def send_phone_notification(room, message, return_url):
    if not PHONE_NOTIFICATION_TOPIC:
        room.add_system_message(
            "<span class='error'>Command failed</span>, contact me to setup the notification integration properly"
        )
        return False

    url = f"https://ntfy.sh/{PHONE_NOTIFICATION_TOPIC}"

    data = message.encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")

    req.add_header("Title", "Glyph Chat")
    req.add_header("Tags", "speaking_head")
    if return_url:
        req.add_header("Actions", f"view, Open Chat, {return_url}")

    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode() == 200
    except Exception as e:
        room.add_system_message(
            f"<span class='error'>Failed to send alert message</span>"
        )
        print(f"Error sending alert phone notification: {e}")
        return False


def check_limit(room, limited_command_name, limit_cap):
    room.limits[limited_command_name] += 1

    if room.limits[limited_command_name] > limit_cap:
        room.add_system_message(f"Used up /{limited_command_name}, try again tomorrow!")
        return False
    return True


def check_unsafe_pass(room, user_guess):
    return _check_pass(room, "GLYPH_PASS_UNSAFE", user_guess)


def _check_pass(room, env_var_name, user_guess):
    if not env_var_name or not user_guess:
        return False

    target = os.environ.get(env_var_name)
    if not target:
        room.add_system_message(
            "<span class='error'>Command failed</span>, contact me to setup the environment password properly"
        )
        return False

    return target == user_guess
