import time as t
from datetime import datetime, time


def time_to_datetime(time_of_day: time) -> datetime:
    """Convert a time of day to a datetime object by combining it with the current date."""
    return datetime.combine(datetime.now().date(), time_of_day)


def seconds_until(target: time) -> float:
    """Calculate the number of seconds remaining until the end time."""
    return (time_to_datetime(target) - datetime.now()).total_seconds()


def sleep_until(target: time) -> None:
    """Sleep until the end time is reached."""
    return t.sleep(seconds_until(target))
