from datetime import time
from threading import Event, Timer
from typing import Any, Callable, Dict

import pandas as pd
from settrade_v2.user import Investor

from . import utils
from .context import ExecuteContext


def execute(
    settrade_user: Investor,
    signal_dict: Dict[str, Any],
    execute_algorithm: Callable[[ExecuteContext], None],
    interval: float,
    start_time: time,
    end_time: time,
):
    """Execute.

    Parameters
    ----------
    settrade_user : Investor
        settrade sdk user.
    signal_dict : Dict[str, Any]
        signal dictionary. symbol as key and signal as value. this signal will pass to execute_algorithm.
    execute_algorithm : Callable[[ExecuteContext], None]
        custom algorithm that iterate all symbol in signal_dict.
        if execute_algorithm raise exception, this function will be stopped.
    interval : float
        seconds to sleep between each interval.
    start_time : time
        time to start execute algorithm.
    end_time : time
        time to end execute algorithm. end time will not interrupt execute_algorithm.
    """
    # sleep until start time
    utils.sleep_until(start_time)

    event = Event()
    timer = Timer(utils.seconds_until(end_time), event.set)
    timer.start()

    try:
        # execute algorithm
        while not event.wait(interval):
            for k, v in signal_dict.items():
                # TODO: init ExecuteContext
                execute_algorithm(
                    ExecuteContext(
                        settrade_user=settrade_user,
                        symbol=k,
                        signal=v,
                        ts=pd.Timestamp.now(),
                    )
                )
    finally:
        # note that event.set() and timer.cancel() can be called multiple times
        event.set()
        timer.cancel()
