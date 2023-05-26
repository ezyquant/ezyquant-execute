import asyncio
from datetime import time
from threading import Event, Timer
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from settrade_v2.user import Investor, MarketRep

from . import utils
from .context import ExecuteContextSymbol


def execute_on_timer(
    settrade_user: Union[Investor, MarketRep],
    account_no: str,
    signal_dict: Dict[str, Any],
    on_timer: Callable[[ExecuteContextSymbol], None],
    interval: float,
    start_time: time,
    end_time: time,
    pin: Optional[str] = None,
    event: Optional[Event] = None,
):
    """Execute.

    To stop execute on timer,
    raise exception in on_timer to stop immediately,
    or set event.set() to stop after current iteration.

    Parameters
    ----------
    settrade_user : Investor
        settrade sdk user.
    account_no : str
        account number.
    signal_dict : Dict[str, Any]
        signal dictionary. symbol as key and signal as value. this signal will pass to on_timer.
    on_timer : Callable[[ExecuteContextSymbol], None]
        custom function that iterate all symbol in signal_dict.
        if on_timer raise exception, this function will be stopped.
    interval : float
        seconds to sleep between each iteration.
    start_time : time
        time to start.
    end_time : time
        time to end. end time will not interrupt while iteration.
    pin : str, optional
        pin for investor
    event : Event, optional
        event to stop execute on timer
    """
    if event is None:
        event = Event()

    # sleep until start time
    utils.sleep_until(start_time, event=event)

    timer = Timer(utils.seconds_until(end_time), event.set)
    timer.start()

    try:
        ctx_list = [
            ExecuteContextSymbol(
                symbol=k,
                signal=v,
                settrade_user=settrade_user,
                account_no=account_no,
                pin=pin,
            )
            for k, v in signal_dict.items()
        ]

        # execute on_timer
        while not event.wait(interval):
            [on_timer(i) for i in ctx_list]

    finally:
        # note that event.set() and timer.cancel() can be called multiple times
        event.set()
        timer.cancel()


async def async_execute_on_timer(
    settrade_user: Union[Investor, MarketRep],
    account_no: str,
    signal_dict: Dict[str, Any],
    on_timer: Callable[[ExecuteContextSymbol], Awaitable[None]],
    interval: float,
    start_time: time,
    end_time: time,
    pin: Optional[str] = None,
    event: Optional[asyncio.Event] = None,
):
    """Same as execute_on_timer but on_timer is async function."""
    if event is None:
        event = asyncio.Event()

    # sleep until start time
    await utils.async_sleep_until(start_time, event=event)

    timer = Timer(utils.seconds_until(end_time), event.set)
    timer.start()

    try:
        ctx_list = [
            ExecuteContextSymbol(
                symbol=k,
                signal=v,
                settrade_user=settrade_user,
                account_no=account_no,
                pin=pin,
            )
            for k, v in signal_dict.items()
        ]

        # execute on_timer
        while not await utils.async_event_wait(event, interval):
            [await on_timer(i) for i in ctx_list]

    finally:
        # note that event.set() and timer.cancel() can be called multiple times
        event.set()
        timer.cancel()
