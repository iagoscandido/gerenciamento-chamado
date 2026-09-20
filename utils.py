from datetime import datetime


def get_current_datetime() -> tuple[str, str]:
    """returns a tuple that contains date (%Y-%m-%d) and time (%H:%M)"""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    hour_minute = now.strftime("%H:%M")
    return date, hour_minute
