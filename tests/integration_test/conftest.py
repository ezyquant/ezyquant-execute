import pytest
from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor

E_INV_ACCOUNT_NO = "8300116"
PIN = "111111"


@pytest.fixture
def stt_inv() -> Investor:
    return Investor(
        app_id="CfVAuVWUwcP1grkG",
        app_secret="AOGH4Zavk0basf6tliHvf1kJuzECnpyoRRiMGpcVEX3O",
        app_code="ALGO_EQ",
        broker_id="025",
    )


@pytest.fixture
def stt_rt(stt_inv: Investor) -> RealtimeDataConnection:
    return stt_inv.RealtimeDataConnection()
