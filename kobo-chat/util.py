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
    return dt.strftime("%A ") + ordinal(dt.day)
