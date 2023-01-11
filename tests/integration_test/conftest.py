import pytest
from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor

E_INV_ACCOUNT_NO = "FT0016E"
PIN = "111111"


@pytest.fixture
def stt_inv() -> Investor:
    return Investor(
        app_id="L4WhzSHqTKh5Ri7R",
        app_secret="UjuYo0k2F2SSx4DNfmWYdeliVfHJj2B2fPMO6E1HYNM=",
        app_code="ALGO",
        broker_id="041",
    )


@pytest.fixture
def stt_rt(stt_inv: Investor) -> RealtimeDataConnection:
    return stt_inv.RealtimeDataConnection()
