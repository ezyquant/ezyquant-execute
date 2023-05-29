import pytest
from settrade_v2 import Investor
from settrade_v2.errors import SettradeError

from ezyquant_execution.context import ExecuteContext, ExecuteContextSymbol

from .conftest import E_INV_ACCOUNT_NO, PIN


@pytest.fixture
def exe_ctx(stt_inv: Investor):
    return ExecuteContext(settrade_user=stt_inv, account_no=E_INV_ACCOUNT_NO, pin=PIN)


class TestExecuteContext:
    def test_ts(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.ts
        print(actual)

    def test_line_available(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.line_available
        print(actual)

    def test_cash_balance(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.cash_balance
        print(actual)

    def test_total_cost_value(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.total_cost_value
        print(actual)

    def test_total_market_value(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.total_market_value
        print(actual)

    def test_pending_order_value(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.pending_order_value
        print(actual)

    def test_port_value(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.port_value
        print(actual)

    def test_cash(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.cash
        print(actual)

    def test_cancel_orders(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.cancel_orders()
        print(actual)

    def test_cancel_buy_orders(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.cancel_buy_orders()
        print(actual)

    def test_cancel_sell_orders(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.cancel_sell_orders()
        print(actual)

    def test_cancel_price_orders(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.cancel_price_orders(price=1.0)
        print(actual)

    def test_get_account_info(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.get_account_info()
        print(actual)

    def test_get_portfolios(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.get_portfolios()
        print(actual)

    def test_get_orders(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.get_orders()
        print(actual)

    def test_get_trades(self, exe_ctx: ExecuteContext):
        actual = exe_ctx.get_trades()
        print(actual)


@pytest.fixture
def exe_ctx_symbol(stt_inv: Investor):
    return ExecuteContextSymbol(
        settrade_user=stt_inv, account_no=E_INV_ACCOUNT_NO, symbol="AOT", pin=PIN
    )


class TestExecuteContextSymbol:
    def test_market_price(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.market_price
        print(actual)

    def test_best_bid_price(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.best_bid_price
        print(actual)

    def test_best_ask_price(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.best_ask_price
        print(actual)

    def test_volume(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.volume
        print(actual)

    def test_actual_volume(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.actual_volume
        print(actual)

    def test_current_volume(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.current_volume
        print(actual)

    def test_cost_price(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.cost_price
        print(actual)

    def test_cost_value(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.cost_value
        print(actual)

    def test_market_value(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.market_value
        print(actual)

    def test_profit(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.profit
        print(actual)

    def test_percent_profit(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.percent_profit
        print(actual)

    def test_buy(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.buy(volume=100, price=60.0)
        print(actual)

    def test_sell(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.sell(volume=100, price=60.0)
        print(actual)

    def test_buy_pct_port(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.buy_pct_port(pct_port=0.5)
        print(actual)

    def test_buy_value(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.buy_value(value=500.0)
        print(actual)

    def test_sell_pct_port(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.sell_pct_port(pct_port=0.5)
        print(actual)

    def test_sell_value(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.sell_value(value=500.0)
        print(actual)

    def test_target_pct_port(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.target_pct_port(pct_port=0.5)
        print(actual)

    def test_target_value(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.target_value(value=500.0)
        print(actual)

    def test_is_buy_sufficient(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.is_buy_sufficient(
            volume=100, price=60.0, pct_commission=0.01
        )
        print(actual)

    def test_is_sell_sufficient(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.is_sell_sufficient(volume=100)
        print(actual)

    def test_get_portfolio(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.get_portfolio()
        print(actual)

    def test_place_order(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.place_order(
            side="Buy",
            volume=100,
            price=60.0,
            qty_open=0,
            trustee_id_type="Local",
            price_type="Limit",
            validity_type="Day",
            bypass_warning=True,
            valid_till_date=None,
            is_round_up_volume=False,
            mode="none",
        )
        print(actual)

    def test_get_quote_symbol(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.get_quote_symbol()
        print(actual)


class TestPlaceOrderMode:
    def test_none(self, exe_ctx_symbol: ExecuteContextSymbol):
        with pytest.raises(SettradeError) as e:
            exe_ctx_symbol.place_order(
                side="Sell",
                volume=10000,
                price_type="MP-MTL",
                mode="none",
            )
        pattern = r"No stock available for sell \[AOT\]"
        e.match(pattern)

    def test_raise(self, exe_ctx_symbol: ExecuteContextSymbol):
        with pytest.raises(ValueError) as e:
            exe_ctx_symbol.place_order(
                side="Sell",
                volume=10000,
                price_type="MP-MTL",
                mode="raise",
            )
        pattern = r"Sell 10000 is not sufficient"
        e.match(pattern)

    def test_skip(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.place_order(
            side="Sell",
            volume=10000,
            price_type="MP-MTL",
            mode="skip",
        )

        assert actual == None

    def test_available(self, exe_ctx_symbol: ExecuteContextSymbol):
        actual = exe_ctx_symbol.place_order(
            side="Sell",
            volume=10000,
            price_type="MP-MTL",
            mode="available",
        )
        print(actual)
