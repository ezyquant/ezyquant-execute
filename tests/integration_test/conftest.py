import pytest
from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor

APP_CODE = "ALGO_EQ"
BROKER_ID = "025"
PIN = "111111"

INV_APP_ID = "CfVAuVWUwcP1grkG"
INV_APP_SECRET = "AOGH4Zavk0basf6tliHvf1kJuzECnpyoRRiMGpcVEX3O"
E_INV_ACCOUNT_NO = "8300116"


@pytest.fixture
def stt_inv() -> Investor:
    return Investor(
        app_id=INV_APP_ID,
        app_secret=INV_APP_SECRET,
        app_code=APP_CODE,
        broker_id=BROKER_ID,
    )


@pytest.fixture
def stt_rt(stt_inv: Investor) -> RealtimeDataConnection:
    return stt_inv.RealtimeDataConnection()
