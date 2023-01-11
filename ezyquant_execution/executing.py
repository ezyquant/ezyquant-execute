from datetime import time
from threading import Event, Timer
from typing import Any, Callable, Dict

from settrade_v2.user import Investor

from . import utils
from .context import ExecuteContext


def execute_on_timer(
    settrade_user: Investor,
    account_no: str,
    pin: str,
    signal_dict: Dict[str, Any],
    on_timer: Callable[[ExecuteContext], None],
    interval: float,
    start_time: time,
    end_time: time,
):
    """Execute.

    To stop execute on timer,
    raise exception in on_timer to stop immediately,
    or set event.set() to stop after current iteration.

    Parameters
    ----------
    settrade_user : Investor
        settrade sdk user.
    signal_dict : Dict[str, Any]
        signal dictionary. symbol as key and signal as value. this signal will pass to on_timer.
    on_timer : Callable[[ExecuteContext], None]
        custom function that iterate all symbol in signal_dict.
        if on_timer raise exception, this function will be stopped.
    interval : float
        seconds to sleep between each iteration.
    start_time : time
        time to start.
    end_time : time
        time to end. end time will not interrupt while iteration.
    """
    # sleep until start time
    utils.sleep_until(start_time)

    event = Event()
    timer = Timer(utils.seconds_until(end_time), event.set)
    timer.start()

    try:
        # execute on_timer
        while not event.wait(interval):
            for k, v in signal_dict.items():
                on_timer(
                    ExecuteContext(
                        symbol=k,
                        signal=v,
                        settrade_user=settrade_user,
                        account_no=account_no,
                        pin=pin,
                        event=event,
                    )
                )
    finally:
        # note that event.set() and timer.cancel() can be called multiple times
        event.set()
        timer.cancel()
