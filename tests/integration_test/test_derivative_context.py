import pytest
from settrade_v2.user import MarketRep

from ezyquant_execution.derivative_context import ExecuteDerivativeContext

from .conftest import D_MKT_ACCOUNT_NO

settrade_user = MarketRep(
    app_id="e06ViFUJrZsp7pg6",
    app_secret="GGD8YCW9vMYwa8PzQ+r2UQkZGmstZ6Xyw2T6YgYHsxI=",
    app_code="IC_ORDER",
    broker_id="025",
)


@pytest.fixture
def exe_ctx(stt_mkt: MarketRep):
    return ExecuteDerivativeContext(settrade_user=stt_mkt, account_no=D_MKT_ACCOUNT_NO)


class TestDerivativeExecuteContext:
    def test_successs_get_account_info(self, exe_ctx: ExecuteDerivativeContext):
        actual = exe_ctx.get_account_info()
        print(actual)

    def test_successs_get_portfolios(self, exe_ctx: ExecuteDerivativeContext):

        actual = exe_ctx.get_portfolios()
        print(actual)

    def test_successs_get_trades(self, exe_ctx: ExecuteDerivativeContext):
        actual = exe_ctx.get_trades()
        print(actual)
