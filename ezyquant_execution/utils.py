import time as t
from datetime import datetime, time

"""
Time
"""


def time_to_datetime(time_of_day: time) -> datetime:
    """Convert a time of day to a datetime object by combining it with the
    current date."""
    return datetime.combine(datetime.now().date(), time_of_day)


def seconds_until(target_time: time) -> float:
    """Calculate the number of seconds remaining until the end time.

    can be negative if the end time has already passed.
    """
    return (time_to_datetime(target_time) - datetime.now()).total_seconds()


def sleep_until(target_time: time) -> None:
    """Sleep until the end time is reached.

    If the end time has already passed, this function will return
    immediately.
    """
    # Calculate seconds remaining until end time
    seconds_remaining = seconds_until(target_time)

    # Sleep for the remaining time
    if seconds_remaining > 0:
        t.sleep(seconds_remaining)


"""
Round
"""


def round_volume_100(volume: float, round_mode: str = "down") -> int:
    # round down
    if round_mode.lower() == "down":
        return round_down_100(volume)
    # round up
    elif round_mode.lower() == "up":
        return round_up_100(volume)
    # half up
    else:
        if volume % 100 >= 50:
            return round_up_100(volume)
        else:
            return round_down_100(volume)


def round_down_100(f: float) -> int:
    return int((f + 1e-8) // 100 * 100)


def round_up_100(f: float) -> int:
    if f % 100 == 0:
        return int(f)
    else:
        return int(round_down_100(f) + 100)
