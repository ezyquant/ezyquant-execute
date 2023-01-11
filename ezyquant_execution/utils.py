import math
import time as t
from datetime import datetime, time
from functools import lru_cache

import numpy as np

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


def round_down_even(f: float) -> float:
    return float((f + 1e-8) // 2 * 2)


def round_up_even(f: float) -> float:
    if f % 2 == 0:
        return float(f)
    else:
        return float(round_down_even(f) + 2)


"""
Price
"""


@lru_cache
def get_price_array() -> np.ndarray:
    l = list()
    l.append(np.arange(start=0.01, stop=2, step=0.01))
    l.append(np.arange(start=2, stop=5, step=0.02))
    l.append(np.arange(start=5, stop=10, step=0.05))
    l.append(np.arange(start=10, stop=25, step=0.1))
    l.append(np.arange(start=25, stop=100, step=0.25))
    l.append(np.arange(start=100, stop=200, step=0.5))
    l.append(np.arange(start=200, stop=400, step=1))
    l.append(np.arange(start=400, stop=800, step=2))
    array = np.concatenate(l).round(2)
    return array


def get_slipped_price(price: float, n_slippage: int) -> float:
    """Return get_slipped_price_round_up."""
    return get_slipped_price_round_up(price=price, n_slippage=n_slippage)


def get_buy_slipped_price(price: float, n_slippage: int) -> float:
    """
    more slip = higher buy price = easier to buy
    return get_slipped_price_round_up(price, slippage)
    """
    return get_slipped_price_round_up(price, n_slippage)


def get_sell_slipped_price(price: float, n_slippage: int) -> float:
    """
    more slip = lower sell price = easier to sell
    return get_slipped_price_round_down(price, -slippage)
    """
    return get_slipped_price_round_down(price, -n_slippage)


@lru_cache
def get_slipped_price_round_up(price: float, n_slippage: int) -> float:
    """Positive n_slippage mean higher price usually use for buy support +- 150
    n_slippage."""
    if math.isnan(price):
        return price
    assert price > 0, "price should be greater than 0"
    # if n_slippage == 0:
    #     return price
    if price > 750:
        price = round_up_even(price)
        return float(price + 2 * n_slippage)

    idx = np.searchsorted(get_price_array(), price)
    idx += n_slippage
    if idx < 0:
        idx = 0
    return get_price_array()[idx]


@lru_cache
def get_slipped_price_round_down(price: float, n_slippage: int) -> float:
    """Positive n_slippage mean higher price usually use for sell support +-
    150 n_slippage."""
    if math.isnan(price):
        return price
    assert price > 0, "price should be greater than 0"
    # if n_slippage == 0:
    #     return price
    if price > 750:
        price = round_down_even(price)
        return float(price + 2 * n_slippage)

    idx = np.searchsorted(get_price_array(), price, side="right")
    idx += n_slippage - 1
    if idx < 0:
        idx = 0
    return get_price_array()[idx]
