import time as t
from datetime import time
from typing import Any, Callable, Dict

from settrade_v2.user import Investor

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
    interval : float
        seconds to sleep between each interval.
    start_time : time
        time to start execute algorithm.
    end_time : time
        time to end execute algorithm. end time will not interrupt execute_algorithm.
    """
    # TODO: execute

    # sleep until start time
    t.sleep((start_time - t.localtime()).seconds)

    # execute algorithm
    while t.localtime() < end_time:
        for k, v in signal_dict.items():
            execute_algorithm(
                ExecuteContext(settrade_user=settrade_user, simybol=k, signal=v)
            )
        # TODO: interrupt sleep
        t.sleep(interval)
