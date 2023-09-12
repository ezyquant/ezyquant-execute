import pytest
from settrade_v2.user import MarketRep

from ezyquant_execution.derivative_context import (
    ExecuteDerivativeContext,
    ExecuteDerivativeContextSymbol,
)

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

    def test_cancel_orders(self, exe_ctx: ExecuteDerivativeContext):
        actual = exe_ctx.cancel_orders()
        print(actual)

    def test_cancel_long_orders(self, exe_ctx: ExecuteDerivativeContext):
        actual = exe_ctx.cancel_long_orders()
        print(actual)

    def test_cancel_short_orders(self, exe_ctx: ExecuteDerivativeContext):
        actual = exe_ctx.cancel_short_orders()
        print(actual)


@pytest.fixture
def exe_ctx_symbol(stt_mkt: MarketRep):
    return ExecuteDerivativeContextSymbol(
        settrade_user=stt_mkt, account_no=D_MKT_ACCOUNT_NO, symbol="S50U23"
    )


class TestDerivativeExecuteContextSymbol:
    def test_market_price(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.market_price
        print(actual)

    def test_best_bid_price(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.best_bid_price
        print(actual)

    def test_best_ask_price(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.best_ask_price
        print(actual)

    def test_place_order(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.place_order(
            side="Long",
            position="Open",
            price_type="Limit",
            price=930,
            volume=1,
            iceberg_vol=0,
            validity_type="Day",
            validity_date_condition=None,
            stop_condition=None,
            stop_symbol=None,
            stop_price=None,
            trigger_session=None,
            bypass_warning=True,
        )
        print(actual)

    def test_volume(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.volume
        print(actual)

    def test_actual_long_volume(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.actual_long_volume
        print(actual)

    def test_actual_short_volume(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.actual_short_volume
        print(actual)

    def test_long_avg_cost(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.long_avg_cost
        print(actual)

    def test_short_avg_cost(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.short_avg_cost
        print(actual)

    def test_long_avg_price(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.long_avg_price
        print(actual)

    def test_short_avg_price(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.short_avg_price
        print(actual)

    def test_long_market_value(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.long_market_value
        print(actual)

    def test_short_market_value(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.short_market_value
        print(actual)

    def test_profit(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.profit
        print(actual)

    def test_long_profit(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.long_profit
        print(actual)

    def test_short_profit(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.short_profit
        print(actual)

    def test_percent_long_profit(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.percent_long_profit
        print(actual)

    def test_percent_short_profit(self, exe_ctx_symbol: ExecuteDerivativeContextSymbol):
        actual = exe_ctx_symbol.percent_short_profit
        print(actual)
