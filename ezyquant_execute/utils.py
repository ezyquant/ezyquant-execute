import time as t
from datetime import datetime, time


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
