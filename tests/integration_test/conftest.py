import pytest
from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor, MarketRep

APP_CODE = "ALGO_EQ"
MKT_APP_CODE = "IC_ORDER"
BROKER_ID = "025"
PIN = "111111"

# fin-mme-t,123456aB
# https://itptest.settrade.com/login.jsp?txtBrokerId=025
INV_APP_ID = "CfVAuVWUwcP1grkG"
INV_APP_SECRET = "AOGH4Zavk0basf6tliHvf1kJuzECnpyoRRiMGpcVEX3O"
E_INV_ACCOUNT_NO = "8300116"

# finnix-v,It12345
# https://apptest.settrade.com/mktrep/login?brokerId=025
MKT_APP_ID = "e06ViFUJrZsp7pg6"
MKT_APP_SECRET = "GGD8YCW9vMYwa8PzQ+r2UQkZGmstZ6Xyw2T6YgYHsxI="
D_MKT_ACCOUNT_NO = "156745-0"


@pytest.fixture
def stt_inv() -> Investor:
    return Investor(
        app_id=INV_APP_ID,
        app_secret=INV_APP_SECRET,
        app_code=APP_CODE,
        broker_id=BROKER_ID,
    )


@pytest.fixture
def stt_mkt() -> MarketRep:
    return MarketRep(
        app_id=MKT_APP_ID,
        app_secret=MKT_APP_SECRET,
        app_code=MKT_APP_CODE,
        broker_id=BROKER_ID,
    )


@pytest.fixture
def stt_rt(stt_mkt: MarketRep) -> RealtimeDataConnection:
    return stt_mkt.RealtimeDataConnection()
