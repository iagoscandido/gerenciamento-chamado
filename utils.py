from datetime import datetime


def get_current_timestamp() -> str:
    """Returns current timestap"""
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M")
    return formatted


print(get_current_timestamp())
