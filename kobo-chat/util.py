import json
import urllib.request


def get_base_api():
    return "/api"


# Get friendly suffix for dates like "13th" and "1st"
def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def format_date_with_ordinal(dt):
    return dt.strftime("%A %b ") + ordinal(dt.day)


def fetch_public_api(room, type_prefix, url):
    room.add_system_message(f"Fetching {type_prefix} (be sure to Refresh after)")

    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)
        return data
    except Exception as e:
        pass

    room.add_system_message(f"Failed to get {type_prefix} :(")
    return {}
