from threading import Event

import pytest
from settrade_v2.user import Investor

from ezyquant_execution.context import ExecuteContext

from .conftest import E_INV_ACCOUNT_NO, PIN


@pytest.fixture
def exe_ctx(stt_inv: Investor):
    return ExecuteContext(
        symbol="AOT",
        signal=0.0,
        settrade_user=stt_inv,
        account_no=E_INV_ACCOUNT_NO,
        pin=PIN,
        event=Event(),
    )


class TestExecuteContext:
    def test_ts(self, exe_ctx: ExecuteContext):
        result = exe_ctx.ts
        print(result)

    def test_market_price(self, exe_ctx: ExecuteContext):
        result = exe_ctx.market_price
        print(result)

    def test_best_bid_price(self, exe_ctx: ExecuteContext):
        result = exe_ctx.best_bid_price
        print(result)

    def test_best_ask_price(self, exe_ctx: ExecuteContext):
        result = exe_ctx.best_ask_price
        print(result)

    def test_line_available(self, exe_ctx: ExecuteContext):
        result = exe_ctx.line_available
        print(result)

    def test_cash_balance(self, exe_ctx: ExecuteContext):
        result = exe_ctx.cash_balance
        print(result)

    def test_total_cost_value(self, exe_ctx: ExecuteContext):
        result = exe_ctx.total_cost_value
        print(result)

    def test_total_market_value(self, exe_ctx: ExecuteContext):
        result = exe_ctx.total_market_value
        print(result)

    def test_port_value(self, exe_ctx: ExecuteContext):
        result = exe_ctx.port_value
        print(result)

    def test_cash(self, exe_ctx: ExecuteContext):
        result = exe_ctx.cash
        print(result)

    def test_volume(self, exe_ctx: ExecuteContext):
        result = exe_ctx.volume
        print(result)

    def test_cost_price(self, exe_ctx: ExecuteContext):
        result = exe_ctx.cost_price
        print(result)

    def test_cost_value(self, exe_ctx: ExecuteContext):
        result = exe_ctx.cost_value
        print(result)

    def test_market_value(self, exe_ctx: ExecuteContext):
        result = exe_ctx.market_value
        print(result)

    def test_buy(self, exe_ctx: ExecuteContext):
        exe_ctx.cancel_orders_symbol()
        result = exe_ctx.buy(volume=100, price=exe_ctx.best_bid_price)
        print(result)

    def test_sell(self, exe_ctx: ExecuteContext):
        exe_ctx.cancel_orders_symbol()
        result = exe_ctx.sell(volume=100, price=exe_ctx.best_ask_price)
        print(result)

    def test_buy_pct_port(self, exe_ctx: ExecuteContext):
        exe_ctx.cancel_orders_symbol()
        result = exe_ctx.buy_pct_port(0.1)
        print(result)

    def test_buy_value(self, exe_ctx: ExecuteContext):
        exe_ctx.cancel_orders_symbol()
        result = exe_ctx.buy_value(1000)
        print(result)

    def test_sell_pct_port(self, exe_ctx: ExecuteContext):
        exe_ctx.cancel_orders_symbol()
        result = exe_ctx.sell_pct_port(0.1)
        print(result)

    def test_sell_value(self, exe_ctx: ExecuteContext):
        exe_ctx.cancel_orders_symbol()
        result = exe_ctx.sell_value(1000)
        print(result)

    def test_target_pct_port(self, exe_ctx: ExecuteContext):
        exe_ctx.cancel_orders_symbol()
        result = exe_ctx.target_pct_port(0.1)
        print(result)

    def test_target_value(self, exe_ctx: ExecuteContext):
        exe_ctx.cancel_orders_symbol()
        result = exe_ctx.target_value(1000)
        print(result)

    def test_cancel_orders_symbol(self, exe_ctx: ExecuteContext):
        exe_ctx.buy(volume=100, price=exe_ctx.best_bid_price)
        result = exe_ctx.cancel_orders_symbol()
        print(result)

    def test_cancel_buy_orders_symbol(self, exe_ctx: ExecuteContext):
        exe_ctx.buy(volume=100, price=exe_ctx.best_bid_price)
        result = exe_ctx.cancel_buy_orders_symbol()
        print(result)

    def test_cancel_sell_orders_symbol(self, exe_ctx: ExecuteContext):
        exe_ctx.sell(volume=100, price=exe_ctx.best_ask_price)
        result = exe_ctx.cancel_sell_orders_symbol()
        print(result)

    def test_cancel_price_orders_symbol(self, exe_ctx: ExecuteContext):
        price = exe_ctx.best_bid_price
        exe_ctx.buy(volume=100, price=price)
        result = exe_ctx.cancel_price_orders_symbol(price)
        print(result)

    def test_get_candlestick_df(self, exe_ctx: ExecuteContext):
        result = exe_ctx.get_candlestick_df()
        print(result)

    def test_get_quote_symbol(self, exe_ctx: ExecuteContext):
        result = exe_ctx.get_quote_symbol()
        print(result)

    def test_get_account_info(self, exe_ctx: ExecuteContext):
        result = exe_ctx.get_account_info()
        print(result)

    def test_get_portfolios(self, exe_ctx: ExecuteContext):
        result = exe_ctx.get_portfolios()
        print(result)

    def test_get_portfolio_symbol(self, exe_ctx: ExecuteContext):
        result = exe_ctx.get_portfolio_symbol()
        print(result)

    def test_get_orders_symbol(self, exe_ctx: ExecuteContext):
        result = exe_ctx.get_orders_symbol()
        print(result)

    def test_get_trades_symbol(self, exe_ctx: ExecuteContext):
        result = exe_ctx.get_trades_symbol()
        print(result)
