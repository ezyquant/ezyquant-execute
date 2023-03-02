import math
import re
import time as t
from datetime import datetime, time
from functools import lru_cache
from threading import Event
from typing import Optional

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


def sleep_until(target_time: time, event: Optional[Event] = None) -> None:
    """Sleep until the end time is reached.

    If the end time has already passed, this function will return
    immediately.
    """
    # Calculate seconds remaining until end time
    seconds_remaining = seconds_until(target_time)

    # Sleep for the remaining time
    if seconds_remaining > 0:
        if event is None:
            t.sleep(seconds_remaining)
        else:
            event.wait(seconds_remaining)


"""
Round
"""


def round_100(value: float, is_round_up: bool = False) -> int:
    """Round float to nearest 100.

    Parameters
    ----------
    value : float
        value to round
    is_round_up : bool
        is round up if value is not in 100, else round down.

    Returns
    -------
    int
        value after rounding
    """
    return round_x(value=value, x=100, is_round_up=is_round_up)


def round_even(value: float, is_round_up: bool = False) -> int:
    """Round float to nearest even.

    Parameters
    ----------
    value : float
        value to round
    is_round_up : bool
        is round up if value is not in 100, else round down.

    Returns
    -------
    int
        value after rounding
    """
    return round_x(value=value, x=2, is_round_up=is_round_up)


def round_x(value: float, x: int, is_round_up: bool = False) -> int:
    """Round float to nearest x.

    Parameters
    ----------
    value : float
        value to round
    x : float
        x
    is_round_up : bool
        is round up if value is not in 100, else round down.

    Returns
    -------
    int
        value after rounding
    """
    f = math.ceil if is_round_up else math.floor
    out = f(abs(value) / x) * x
    return out if value > 0 else -out


"""
Price
"""


@lru_cache(maxsize=1)
def _price_array() -> np.ndarray:
    # https://classic.set.or.th/en/products/trading/equity/tradingsystem_p5.html
    ranges = [
        (0.01, 2, 0.01),
        (2, 5, 0.02),
        (5, 10, 0.05),
        (10, 25, 0.1),
        (25, 100, 0.25),
        (100, 200, 0.5),
        (200, 400, 1),
        (400, 800, 2),
    ]

    prices = np.concatenate(
        [np.arange(start, stop, step) for start, stop, step in ranges]
    )
    return np.round(prices, 2)


@lru_cache
def match_tick_price(price: float, n_tick: int, is_round_up: bool = False) -> float:
    """Match price to tick price.

    Parameters
    ----------
    price : float
        price to match
    n_tick : int
        number of tick to move. positive for higher price, negative for lower price. maximum is 150
    is_round_up : bool
        is round up if price is not in tick price, else round down.

    Returns
    -------
    float
        price after matching tick price
    """
    if math.isnan(price):
        return price

    assert price > 0, "price should be greater than 0"

    if price > 750:
        price = round_even(price, is_round_up)
        return float(price + 2 * n_tick)

    idx = (
        np.searchsorted(_price_array(), price, side="left" if is_round_up else "right")
        + n_tick
    )
    if not is_round_up:
        idx -= 1

    if idx < 0:
        idx = 0

    return _price_array()[idx]


def match_tick_price_buy(price: float, n_tick: int) -> float:
    """
    more slip = higher buy price = easier to buy
    return match_tick_price(price=price, n_tick=n_tick, is_round_up=True)
    """
    return match_tick_price(price=price, n_tick=n_tick, is_round_up=True)


def match_tick_price_sell(price: float, n_tick: int) -> float:
    """
    more slip = lower sell price = easier to sell
    return match_tick_price(price=price, n_tick=-n_tick, is_round_up=False)
    """
    return match_tick_price(price=price, n_tick=-n_tick, is_round_up=False)


"""
String
"""


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
