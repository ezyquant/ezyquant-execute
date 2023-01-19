from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property
from threading import Event
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import pandas as pd
from settrade_v2.equity import InvestorEquity, MarketRepEquity
from settrade_v2.market import MarketData
from settrade_v2.realtime import RealtimeDataConnection
from settrade_v2.user import Investor, MarketRep

from . import utils
from .entity import SIDE_BUY, SIDE_SELL, EquityOrder, EquityPortfolio, EquityTrade
from .realtime import BidOfferSubscriber

T = TypeVar("T")


@dataclass
class ExecuteContext:
    symbol: str
    """Selected symbol."""
    signal: Any
    """Signal."""
    settrade_user: Union[Investor, MarketRep]
    """Settrade user."""
    account_no: str
    """Account number."""
    event: Event
    """Event object to stop on timer."""
    pin: Optional[str] = None
    """PIN."""
    data: dict = field(default_factory=dict)
    """Data dict for this context."""

    @property
    def ts(self) -> datetime:
        """Current timestamp."""
        return datetime.now()

    """
    Price functions
    """

    @property
    def market_price(self) -> float:
        """Market price."""
        return self.get_quote_symbol()["last"]

    @property
    def best_bid_price(self) -> float:
        """Best bid price."""
        return self._bo_sub.best_bid_price

    @property
    def best_ask_price(self) -> float:
        """Best ask price."""
        return self._bo_sub.best_ask_price

    """
    Account functions
    """

    @property
    def line_available(self) -> float:
        """Line Available."""
        return self.get_account_info()["lineAvailable"]

    @property
    def cash_balance(self) -> float:
        """Cash Balance."""
        return self.get_account_info()["cashBalance"]

    @property
    def total_cost_value(self) -> float:
        """Sum of all stock market value in portfolio."""
        return self.get_portfolios()["totalPortfolio"]["amount"]

    @property
    def total_market_value(self) -> float:
        """Sum of all stock cost value in portfolio."""
        return self.get_portfolios()["totalPortfolio"]["marketValue"]

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

    def buy(
        self,
        volume: float,
        price: float,
        qty_open: int = 0,
        trustee_id_type: str = "Local",
        price_type: str = "Limit",
        validity_type: str = "Day",
        bypass_warning: Optional[bool] = True,
        valid_till_date: Optional[str] = None,
    ) -> dict:
        """Place buy order."""
        volume = utils.round_100(volume)
        if volume == 0:
            return {}
        return self._settrade_equity.place_order(
            side=SIDE_BUY,
            symbol=self.symbol,
            volume=volume,
            price=price,
            qty_open=qty_open,
            trustee_id_type=trustee_id_type,
            price_type=price_type,
            validity_type=validity_type,
            bypass_warning=bypass_warning,
            valid_till_date=valid_till_date,
            **self._pin_acc_no_kw
        )

    def sell(
        self,
        volume: float,
        price: float,
        qty_open: int = 0,
        trustee_id_type: str = "Local",
        price_type: str = "Limit",
        validity_type: str = "Day",
        bypass_warning: Optional[bool] = True,
        valid_till_date: Optional[str] = None,
    ) -> dict:
        """Place sell order."""
        volume = utils.round_100(volume)
        if volume == 0:
            return {}
        return self._settrade_equity.place_order(
            side=SIDE_SELL,
            symbol=self.symbol,
            volume=volume,
            price=price,
            qty_open=qty_open,
            trustee_id_type=trustee_id_type,
            price_type=price_type,
            validity_type=validity_type,
            bypass_warning=bypass_warning,
            valid_till_date=valid_till_date,
            **self._pin_acc_no_kw
        )

    def buy_pct_port(self, pct_port: float) -> dict:
        """Buy from the percentage of the portfolio. calculate the buy volume by pct_port * port_value / best ask price.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.buy_value(self.port_value * pct_port)

    def buy_value(self, value: float) -> dict:
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

    def sell_pct_port(self, pct_port: float) -> dict:
        """Sell from the percentage of the portfolio. calculate the sell volume by pct_port * port_value / best ask price.
        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.sell_value(self.port_value * pct_port)

    def sell_value(self, value: float) -> dict:
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

    def target_pct_port(self, pct_port: float) -> dict:
        """Buy/Sell to make the current position reach the target percentage of
        the portfolio. Calculate the buy/sell volume by compare between the
        best bid/ask price.

        Parameters
        ----------
        pct_port: float
            percentage of the portfolio
        """
        return self.target_value(self.port_value * pct_port)

    def target_value(self, value: float) -> dict:
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

    def cancel_all_orders(self) -> dict:
        """Cancel all orders with the same symbol."""
        return self._cancel_orders()

    def cancel_all_buy_orders(self):
        """Cancel all buy orders with the same symbol."""
        return self._cancel_orders(lambda x: x.side.capitalize() == SIDE_BUY)

    def cancel_all_sell_orders(self):
        """Cancel all sell orders with the same symbol."""
        return self._cancel_orders(lambda x: x.side.capitalize() == SIDE_SELL)

    def cancel_orders_by_price(self, price: float):
        """Cancel all orders with the same symbol and price."""
        return self._cancel_orders(lambda x: x.price == price)

    def _cancel_orders(
        self, condition: Callable[[EquityOrder], bool] = lambda x: True
    ) -> dict:
        """Cancel orders which meet the condition.

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

        if len(order_no_list) == 0:
            return {}
        return self._settrade_equity.cancel_orders(
            order_no_list=order_no_list, **self._pin_acc_no_kw
        )

    """
    Settrade Open API functions
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

    # TODO: remove if unused
    def get_candlestick_df(self, limit: int = 5) -> pd.DataFrame:
        """Get candlestick data.

        Columns: ["lastSequence", "time", "open", "high", "low", "close", "volume", "value"]
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

    def get_quote_symbol(self) -> dict:
        """Get quote symbol."""
        return self._settrade_market_data.get_quote_symbol(symbol=self.symbol)

    def get_account_info(self) -> Dict[str, Any]:
        """Get account info."""
        return self._settrade_equity.get_account_info(**self._acc_no_kw)

    def get_portfolios(self) -> Dict[str, Any]:
        """Get portfolio."""
        return self._settrade_equity.get_portfolios()  # type: ignore

    def get_portfolio_symbol(self) -> Optional[EquityPortfolio]:
        """Get portfolio of the symbol."""
        ports = self.get_portfolios()
        for i in ports["portfolioList"]:
            if i["symbol"] == self.symbol:
                return EquityPortfolio.from_camel_dict(i)
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

    def _filter_list(self, l: List[T], condition: Callable) -> List[T]:
        """Filter list by symbol and condition."""
        return [i for i in l if i.symbol == self.symbol and condition(i)]  # type: ignore
