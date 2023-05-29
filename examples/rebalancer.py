from datetime import datetime, timedelta

from settrade_v2.user import Investor

from ezyquant_execution import execute_on_timer
from ezyquant_execution.context import ExecuteContextSymbol

settrade_user = Investor(
    app_id="CfVAuVWUwcP1grkG",
    app_secret="AOGH4Zavk0basf6tliHvf1kJuzECnpyoRRiMGpcVEX3O",
    app_code="ALGO_EQ",
    broker_id="025",
)
account_no = "8300116"
pin = "111111"

signal_dict = {
    "AOT": 0.2,
    "BBL": 0.2,
    "CPALL": 0.2,
    "DTAC": 0.2,
    "EA": 0.2,
}


def on_timer(ctx: ExecuteContextSymbol):
    ctx.cancel_orders()
    ctx.target_pct_port(ctx.signal)


interval = 10

now = datetime.now()
start_time = now.time()
end_time = (now + timedelta(minutes=1)).time()

execute_on_timer(
    settrade_user=settrade_user,
    account_no=account_no,
    pin=pin,
    signal_dict=signal_dict,
    on_timer=on_timer,
    interval=interval,
    start_time=start_time,
    end_time=end_time,
)
