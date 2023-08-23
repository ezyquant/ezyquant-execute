import pytest
from settrade_v2.user import MarketRep

from ezyquant_execution.derivative_context import ExecuteDerivativeContext

from .conftest import D_MKT_ACCOUNT_NO


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
