import time as t
import warnings
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import pandas as pd
from settrade_v2.context import Context
from settrade_v2.equity import InvestorEquity, MarketRepEquity
from settrade_v2.market import MarketData
from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor, MarketRep

from . import utils
from .entity import (
    PRICE_TYPE,
    SIDE_BUY,
    SIDE_SELL,
    SIDE_TYPE,
    VALIDITY_TYPE,
    BaseAccountInfo,
    CancelOrder,
    EquityOrder,
    EquityPortfolio,
    EquityTrade,
    PortfolioResponse,
    StockQuoteResponse,
)
from .realtime import BidOfferSubscriber, PriceInfoSubscriber

T = TypeVar("T")


def new_refresh(self):
    res = self.request(
        "POST",
        self.refresh_token_path,
        json={"apiKey": self.app_id, "refreshToken": self.refresh_token},
    )
    if not res.ok:
        self.login()  # Added line
        return
    self.token = res.json()["access_token"]
    self.refresh_token = res.json()["refresh_token"]
    self.expired_at = int(t.time()) + res.json()["expires_in"]


# Override refresh method
Context.refresh = new_refresh


@dataclass
class ExecuteContext:
    settrade_user: Union[Investor, MarketRep]
    """Settrade user."""
    account_no: str
    """Account number."""
    symbol: str
    """Selected symbol."""
    signal: Any = None
    """Signal."""
    pin: Optional[str] = None
    """PIN.

    Only for investor.
    """

    @property
    def ts(self) -> datetime:
        """Current timestamp."""
        return datetime.now()

    """
    Price functions
    """

    @property
    def market_price(self) -> Optional[float]:
        """Market price.

        Return 0 at pre-open session.
        """
        return self._po_sub.data.last

    @property
    def best_bid_price(self) -> float:
        """Best bid price."""
        return self._bo_sub.data.best_bid_price

    @property
    def best_ask_price(self) -> float:
        """Best ask price."""
        return self._bo_sub.data.best_ask_price

    """
    Account functions
    """

    @property
    def line_available(self) -> float:
        """Line Available."""
        return self.get_account_info().line_available

    @property
    def cash_balance(self) -> float:
        """Cash Balance."""
        return self.get_account_info().cash_balance

    @property
    def total_cost_value(self) -> float:
        """Sum of all stock market value in portfolio."""
        return self.get_portfolios().total_portfolio.amount

    @property
    def total_market_value(self) -> float:
        """Sum of all stock cost value in portfolio."""
        return self.get_portfolios().total_portfolio.market_value

    @property
    def port_value(self) -> float:
        """Total portfolio value."""
        return self.cash_balance + self.total_market_value

    @property
    def cash(self) -> float:
        """Cash Balance."""
        return self.cash_balance

    """
    Position functions
    """

    @property
    def volume(self) -> float:
        """Actual volume."""
        ps = self.get_portfolio_symbol()
        return ps.actual_volume if ps else 0

    @property
    def cost_price(self) -> float:
        """Cost price.

        return 0.0 if no position.
        """
        ps = self.get_portfolio_symbol()
        return ps.average_price if ps else 0.0

    @property
    def cost_value(self) -> float:
        """Cost value."""
        ps = self.get_portfolio_symbol()
        return ps.amount if ps else 0.0

    @property
    def market_value(self) -> float:
        """Market value of symbol in portfolio."""
        ps = self.get_portfolio_symbol()
        return ps.market_value if ps else 0.0

    """
    Place order functions
    """

    def place_order(
        self,
        side: SIDE_TYPE,
        volume: float,
        price: float,
        qty_open: int = 0,
        trustee_id_type: str = "Local",
        price_type: PRICE_TYPE = "Limit",
        validity_type: VALIDITY_TYPE = "Day",
        bypass_warning: Optional[bool] = True,
        valid_till_date: Optional[str] = None,
    ) -> Optional[EquityOrder]:
        """Place order.

        Round volume to 100. If volume is 0, return None.
        """
        volume = utils.round_100(volume)
        if volume == 0:
            return

        res = self._settrade_equity.place_order(
            symbol=self.symbol,
            side=side,
            volume=volume,
            price=price,
            qty_open=qty_open,
            trustee_id_type=trustee_id_type,
            price_type=price_type,
            validity_type=validity_type,
            bypass_warning=bypass_warning,
            valid_till_date=valid_till_date,
            **self._pin_acc_no_kw,
        )
        return EquityOrder.from_camel_dict(res)

    def buy(self, volume: float, price: float) -> Optional[EquityOrder]:
        """Place buy order."""
        return self.place_order(side=SIDE_BUY, volume=volume, price=price)

    def sell(self, volume: float, price: float) -> Optional[EquityOrder]:
        """Place sell order."""
        return self.place_order(side=SIDE_SELL, volume=volume, price=price)

    def buy_pct_port(self, pct_port: float) -> Optional[EquityOrder]:
        """Buy from the percentage of the portfolio. calculate the buy volume by pct_port * port_value / best ask price.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.buy_value(self.port_value * pct_port)

    def buy_value(self, value: float) -> Optional[EquityOrder]:
        """Buy from the given value. calculate the buy volume by value / best
        ask price.

        Parameters
        ----------
        value: float
            value
        """
        price = self.best_ask_price
        volume = value / price
        return self.buy(volume=volume, price=price)

    def sell_pct_port(self, pct_port: float) -> Optional[EquityOrder]:
        """Sell from the percentage of the portfolio. calculate the sell volume by pct_port * port_value / best ask price.
        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.sell_value(self.port_value * pct_port)

    def sell_value(self, value: float) -> Optional[EquityOrder]:
        """Sell from the given value. calculate the sell volume by value / best
        bid price.

        Parameters
        ----------
        value: float
            value
        """
        price = self.best_bid_price
        volume = value / price
        return self.sell(volume=volume, price=price)

    def target_pct_port(self, pct_port: float) -> Optional[EquityOrder]:
        """Buy/Sell to make the current position reach the target percentage of
        the portfolio. Calculate the buy/sell volume by compare between the
        best bid/ask price.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.target_value(self.port_value * pct_port)

    def target_value(self, value: float) -> Optional[EquityOrder]:
        """Buy/Sell to make the current position reach the target value.
        Calculate the buy/sell volume by compare between the best bid/ask
        price.

        Parameters
        ----------
        value: float
            value
        """
        value -= self.market_value

        if value > 0:
            return self.buy_value(value)
        else:
            return self.sell_value(-value)

    """
    Cancel order functions
    """

    def cancel_orders_symbol(
        self, condition: Callable[[EquityOrder], bool] = lambda x: True
    ) -> List[CancelOrder]:
        """Cancel all orders with this symbol.

        Parameters
        ----------
        condition: Callable[[dict], bool]
            condition function

        Returns
        -------
        dict
            cancel order result
        """
        orders = self.get_orders_symbol(condition)
        order_no_list = [i.order_no for i in orders if i.can_cancel]
        return self._cancel_orders(order_no_list)

    def cancel_buy_orders_symbol(self) -> List[CancelOrder]:
        """Cancel all buy orders with this symbol."""
        return self.cancel_orders_symbol(lambda x: x.side.capitalize() == SIDE_BUY)

    def cancel_sell_orders_symbol(self) -> List[CancelOrder]:
        """Cancel all sell orders with this symbol."""
        return self.cancel_orders_symbol(lambda x: x.side.capitalize() == SIDE_SELL)

    def cancel_price_orders_symbol(self, price: float) -> List[CancelOrder]:
        """Cancel all orders with this symbol and price."""
        return self.cancel_orders_symbol(lambda x: x.price == price)

    def _cancel_orders(self, order_no_list: List[str]) -> List[CancelOrder]:
        if not order_no_list:
            return []

        res = self._settrade_equity.cancel_orders(
            order_no_list=order_no_list, **self._pin_acc_no_kw
        )
        out = [CancelOrder.from_camel_dict(i) for i in res["results"]]

        for i in out:
            if i.error_response is not None:
                warnings.warn(
                    f"Cancel order {i.order_no} failed: {i.error_response['message']}"
                )

        return out

    """
    Settrade SDK functions
    """

    @property
    def _acc_no_kw(self) -> dict:
        return (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, MarketRep)
            else {}
        )

    @property
    def _pin_acc_no_kw(self) -> dict:
        return (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, MarketRep)
            else {"pin": self.pin}
        )

    @property
    def _settrade_equity(self) -> Union[InvestorEquity, MarketRepEquity]:
        kw = (
            {"account_no": self.account_no}
            if isinstance(self.settrade_user, Investor)
            else {}
        )
        return self.settrade_user.Equity(**kw)

    @property
    def _settrade_market_data(self) -> MarketData:
        return self.settrade_user.MarketData()

    @property
    def _settrade_realtime_data_connection(self) -> RealtimeDataConnection:
        return self.settrade_user.RealtimeDataConnection()

    @cached_property
    def _bo_sub(self) -> BidOfferSubscriber:
        return BidOfferSubscriber(
            symbol=self.symbol, rt_conn=self._settrade_realtime_data_connection
        )

    @cached_property
    def _po_sub(self) -> PriceInfoSubscriber:
        return PriceInfoSubscriber(
            symbol=self.symbol, rt_conn=self._settrade_realtime_data_connection
        )

    # TODO: remove if unused
    def get_candlestick_df(self, limit: int = 5) -> pd.DataFrame:
        """Get candlestick data.

        Columns: ["lastSequence", "time", "open", "high", "low", "close", "volume", "value"]

        Example
        -------
        Pre-open
        >>>     lastSequence                      time  open  ...  close    volume         value
        ... 0              0 2023-01-10 00:00:00+07:00  75.5  ...  75.25  29748824  2.234758e+09
        ... 1              0 2023-01-11 00:00:00+07:00  75.0  ...  74.25  42858395  3.189858e+09
        ... 2              0 2023-01-12 00:00:00+07:00  74.0  ...  74.00  33256792  2.466415e+09
        ... 3              0 2023-01-13 00:00:00+07:00  74.0  ...  73.50  41266018  3.042763e+09
        ... 4              0 2023-01-25 00:00:00+07:00  70.0  ...  70.00   2001000  1.500700e+08
        """
        df = pd.DataFrame(
            self._settrade_market_data.get_candlestick(
                symbol=self.symbol, interval="1d", limit=limit
            )
        )
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(
            "Asia/Bangkok"
        )
        return df

    # TODO: remove if unused
    def get_quote_symbol(self) -> StockQuoteResponse:
        """Get quote symbol."""
        res = self._settrade_market_data.get_quote_symbol(symbol=self.symbol)
        return StockQuoteResponse.from_camel_dict(res)

    def get_account_info(self) -> BaseAccountInfo:
        """Get account info."""
        res = self._settrade_equity.get_account_info(**self._acc_no_kw)
        return BaseAccountInfo.from_camel_dict(res)

    def get_portfolios(self) -> PortfolioResponse:
        """Get portfolio."""
        res: Dict[str, Any] = self._settrade_equity.get_portfolios(**self._acc_no_kw)  # type: ignore
        return PortfolioResponse.from_camel_dict(res)

    def get_portfolio_symbol(self) -> Optional[EquityPortfolio]:
        """Get portfolio of the symbol."""
        res = self.get_portfolios()
        for i in res.portfolio_list:
            if i.symbol == self.symbol:
                return i
        return None

    def get_orders_symbol(
        self, condition: Callable[[EquityOrder], bool] = lambda x: True
    ) -> List[EquityOrder]:
        """Get order of the symbol."""
        if isinstance(self._settrade_equity, InvestorEquity):
            out = self._settrade_equity.get_orders()
        else:
            out = self._settrade_equity.get_orders_by_account_no(
                account_no=self.account_no
            )
        out = [EquityOrder.from_camel_dict(i) for i in out]
        out = self._filter_list(out, condition)
        return out

    def get_trades_symbol(
        self, condition: Callable[[EquityTrade], bool] = lambda x: True
    ) -> List[EquityTrade]:
        out = self._settrade_equity.get_trades(**self._acc_no_kw)
        out = [EquityTrade.from_camel_dict(i) for i in out]
        out = self._filter_list(out, condition)
        return out

    def _filter_list(self, l: List[T], condition: Callable = lambda x: True) -> List[T]:
        """Filter list by symbol and condition."""
        return [i for i in l if i.symbol == self.symbol and condition(i)]  # type: ignore
